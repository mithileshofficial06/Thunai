"""The single 'understand' AI step: two models in parallel (they must agree), Gemini as backup.

Returns raw model outputs; accuracy.py decides what is accepted. The AI never decides eligibility.
"""
import concurrent.futures as cf
import hashlib
import json
import threading
import time

import config

SYSTEM_PROMPT = (config.ROOT / "prompts" / "understand_system.txt").read_text(encoding="utf-8")
_cache_lock = threading.Lock()
_groq = None
_gemini = None


def _groq_client():
    global _groq
    if _groq is None and config.GROQ_API_KEY:
        from groq import Groq

        _groq = Groq(api_key=config.GROQ_API_KEY, timeout=config.LLM_TIMEOUT_S, max_retries=0)
    return _groq


def _gemini_client():
    global _gemini
    if _gemini is None and config.GEMINI_API_KEY:
        from google import genai

        _gemini = genai.Client(api_key=config.GEMINI_API_KEY)
    return _gemini


def _user_message(text, card, last_question, open_tasks, diagnosis):
    return (f"FAMILY CARD (current): {json.dumps(card, ensure_ascii=False)}\n"
            f"OPEN TASKS: {json.dumps(open_tasks, ensure_ascii=False) if open_tasks else 'none'}\n"
            f"LAST QUESTION ASKED: {last_question or 'none'}\n"
            f"DIAGNOSIS IN PROGRESS: {diagnosis or 'none'}\n"
            f"USER MESSAGE: {text}")


def _call_groq(model, user):
    client = _groq_client()
    if client is None:
        raise RuntimeError("no Groq key")
    extra = {"reasoning_effort": "none"} if "qwen" in model else {"reasoning_effort": "low"}
    r = client.chat.completions.create(
        model=model, temperature=0, response_format={"type": "json_object"}, **extra,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}])
    return json.loads(r.choices[0].message.content)


def _call_gemini(model, user):
    client = _gemini_client()
    if client is None:
        raise RuntimeError("no Gemini key")
    from google.genai import types

    r = client.models.generate_content(
        model=model, contents=user,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, response_mime_type="application/json",
                                           temperature=0, thinking_config=types.ThinkingConfig(thinking_budget=0),
                                           http_options=types.HttpOptions(timeout=max(10, config.LLM_TIMEOUT_S) * 1000)))
    return json.loads(r.text)


PROVIDERS = {
    "qwen": (_call_groq, config.GROQ_PRIMARY_MODEL),
    "gpt-oss": (_call_groq, config.GROQ_SECOND_MODEL),
    "gemini": (_call_gemini, config.GEMINI_BACKUP_MODEL),
}


def _run(name, user):
    fn, model = PROVIDERS[name]
    t = time.time()
    try:
        data = fn(model, user)
        if not isinstance(data, dict):
            raise ValueError("not a JSON object")
        return {"provider": name, "ms": int((time.time() - t) * 1000), "data": data}
    except Exception as exc:  # any provider error → the next provider takes over
        return {"provider": name, "ms": int((time.time() - t) * 1000), "error": f"{type(exc).__name__}: {str(exc)[:160]}"}


def _cache_key(text, card, last_question):
    raw = json.dumps([text, card, last_question], ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _cache_get(key):
    with _cache_lock:
        if config.LLM_CACHE_FILE.exists():
            try:
                return json.loads(config.LLM_CACHE_FILE.read_text(encoding="utf-8")).get(key)
            except json.JSONDecodeError:
                return None
    return None


def _cache_put(key, value):
    with _cache_lock:
        data = {}
        if config.LLM_CACHE_FILE.exists():
            try:
                data = json.loads(config.LLM_CACHE_FILE.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                data = {}
        data[key] = value
        config.LLM_CACHE_FILE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def understand(text, card, last_question=None, open_tasks=None, diagnosis=None):
    """Return {'results': [ok results...], 'errors': [...], 'cached': bool} or None if no model answered."""
    if not config.USE_LLM:
        return None
    key = _cache_key(text, card, last_question)
    hit = _cache_get(key)
    if hit:
        return {**hit, "cached": True}

    user = _user_message(text, card, last_question, open_tasks, diagnosis)
    with cf.ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda n: _run(n, user), ["qwen", "gpt-oss"]))
    ok = [r for r in results if "data" in r]
    errors = [r for r in results if "error" in r]
    if len(ok) < 2:  # replace a failed model with Gemini
        backup = _run("gemini", user)
        (ok if "data" in backup else errors).append(backup)
    if not ok:
        return None
    out = {"results": ok, "errors": errors}
    _cache_put(key, out)
    return {**out, "cached": False}
