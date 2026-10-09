"""Thunai voice: speech-to-text (Groq Whisper) and text-to-speech (edge-tts, cached MP3)."""
import asyncio
import hashlib
import time

import config


def transcribe(audio_bytes: bytes, filename: str, lang: str = "ta") -> dict:
    """Transcribe audio with Groq Whisper. Returns {"text": str, "ms": int}."""
    if not config.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not set: voice input is unavailable")
    import groq

    client = groq.Groq(api_key=config.GROQ_API_KEY, max_retries=0)
    t0 = time.perf_counter()
    r = client.audio.transcriptions.create(
        file=(filename, audio_bytes),
        model=config.STT_MODEL,
        language=lang if lang in ("ta", "en") else "ta",
        temperature=0,
    )
    return {"text": (r.text or "").strip(), "ms": int((time.perf_counter() - t0) * 1000)}


def speak(text: str, lang: str = "ta") -> bytes:
    """Synthesise speech with edge-tts; MP3 is cached by sha1(voice + text). Returns MP3 bytes."""
    import edge_tts

    text = (text or "").strip()[:600]
    if not text:
        raise ValueError("nothing to speak")
    voice = config.TTS_VOICE_EN if lang == "en" else config.TTS_VOICE_TA
    config.TTS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = config.TTS_CACHE_DIR / (hashlib.sha1((voice + "\n" + text).encode("utf-8")).hexdigest() + ".mp3")
    if path.exists() and path.stat().st_size > 0:
        return path.read_bytes()
    tmp = path.with_suffix(".part")
    asyncio.run(edge_tts.Communicate(text, voice).save(str(tmp)))
    tmp.replace(path)
    return path.read_bytes()
