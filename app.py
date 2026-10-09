"""Thunai web app: FastAPI routes (plain JSON) + the static single-page UI."""
from typing import Any, Optional

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import agent
import config
import sms
import store
import voice
from engine import doctor as doctor_engine
from engine import notify, proactive

app = FastAPI(title="Thunai — Scheme Sathi agent")


class SessionIn(BaseModel):
    saved_facts: Optional[dict] = None


class ChatIn(BaseModel):
    session_id: str
    text: str
    lang: str = "ta"
    from_voice: bool = False


class FactIn(BaseModel):
    session_id: str
    path: str
    value: Any


class TaskIn(BaseModel):
    session_id: str
    task_id: str
    done: bool = True


class DoctorIn(BaseModel):
    session_id: str
    entry_id: Optional[str] = None
    answer: Optional[str] = None


class LetterIn(BaseModel):
    session_id: str
    kind: str
    member_id: Optional[str] = None
    doc_id: Optional[str] = None


class SimIn(BaseModel):
    session_id: str
    days: int = 15


class SummaryIn(BaseModel):
    session_id: str
    lang: str = "ta"


class TtsIn(BaseModel):
    text: str
    lang: str = "ta"


class ApproveIn(BaseModel):
    draft_id: str
    username: Optional[str] = None  # helper sign-in, when the page is not logged in as a helper
    password: Optional[str] = None
    helper_name: Optional[str] = None  # ignored: the name comes from the helper's account


def _session(session_id):
    s = agent.SESSIONS.get(session_id)
    if s is None:
        raise HTTPException(404, "session not found — start a new session")
    return s


def _out(session, events, snapshot, reply=None):
    data = {"session_id": session["id"], "events": events, "snapshot": snapshot,
            "unconfirmed": session["unconfirmed"], "pending_ask": session["pending_ask"],
            "doctor": session["doctor"]["step"] if session["doctor"] else None,
            "suggested_letters": agent.letter_suggestions(session),
            "drafts": agent.helper_queue(session["id"])}
    if reply is not None:
        data["reply"] = reply
    return data


@app.get("/api/health")
def health():
    return {"status": "ok", "use_llm": config.USE_LLM,
            "groq_key": bool(config.GROQ_API_KEY), "gemini_key": bool(config.GEMINI_API_KEY)}


@app.post("/api/session")
def new_session(body: SessionIn):
    session, events = agent.new_session(body.saved_facts)
    return _out(session, events, session["snapshot"])


@app.post("/api/chat")
def chat(body: ChatIn):
    s = _session(body.session_id)
    if not body.text.strip():
        raise HTTPException(400, "empty message")
    events, snapshot, reply = agent.handle(s, body.text, body.lang, body.from_voice)
    return _out(s, events, snapshot, reply)


@app.post("/api/facts")
def edit_fact(body: FactIn):
    s = _session(body.session_id)
    try:
        events, snapshot = agent.edit_fact(s, body.path, body.value)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return _out(s, events, snapshot)


@app.post("/api/task")
def task(body: TaskIn):
    s = _session(body.session_id)
    events, snapshot = agent.set_task(s, body.task_id, body.done)
    return _out(s, events, snapshot)


@app.get("/api/doctor/entries")
def doctor_entries():
    return {"entries": doctor_engine.entry_points()}


@app.post("/api/doctor")
def doctor(body: DoctorIn):
    """Start the problem finder (entry_id) or answer its question (yes / no / dont_know)."""
    s = _session(body.session_id)
    if body.entry_id:
        if body.entry_id not in doctor_engine.ENTRY_TREE:
            raise HTTPException(400, "unknown entry_id")
        events = agent.doctor_start(s, body.entry_id)
        old, new = agent._apply_snapshot(s)  # a previous outcome's task leaves the plan
        events += agent.diff(old, new)
    elif body.answer in ("yes", "no", "dont_know") and s["doctor"] and s["doctor"]["step"]["kind"] == "question":
        events = agent.doctor_answer(s, body.answer)
    else:
        raise HTTPException(400, "give entry_id, or answer yes / no / dont_know to an open question")
    return {**_out(s, events, s["snapshot"]), "step": s["doctor"]["step"]}


@app.post("/api/letter")
def letter(body: LetterIn):
    s = _session(body.session_id)
    try:
        events, draft = agent.create_letter(s, body.kind, body.member_id, body.doc_id)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {**_out(s, events, s["snapshot"]), "draft": draft}


@app.get("/api/helper/queue")
def helper_queue(session_id: Optional[str] = None):
    return {"items": agent.helper_queue(session_id)}


def _bearer(authorization):
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return None


def _helper(authorization, username=None, password=None):
    """Only a helper may approve: a helper login token, or the helper's username + password."""
    user = store.user_for(_bearer(authorization))
    if user and user["role"] == "helper":
        return user
    if username and password:
        user = store.login(username, password)
        if user and user["role"] == "helper":
            return user
        raise HTTPException(401, "wrong helper username or password")
    raise HTTPException(401, "helper sign-in required to approve")


@app.post("/api/helper/approve")
def helper_approve(body: ApproveIn, authorization: Optional[str] = Header(None)):
    helper = _helper(authorization, body.username, body.password)
    try:
        events, draft = agent.approve(body.draft_id, helper.get("name") or "Helper")
    except KeyError as exc:
        raise HTTPException(404, "draft not found") from exc
    return {"events": events, "draft": draft}


@app.get("/letter/{draft_id}", response_class=HTMLResponse)
def letter_page(draft_id: str):
    try:
        return agent.letter_page(draft_id)
    except KeyError as exc:
        raise HTTPException(404, "letter not found") from exc


@app.get("/api/sample_docs/{persona}")
def sample_docs(persona: str):
    """Sample document cards for a demo family (clearly marked SAMPLE; no Aadhaar or bank numbers)."""
    p = agent.PERSONAS.get(persona)
    if p is None:
        raise HTTPException(404, "unknown persona")
    from engine.data import DOCUMENTS
    cards = [{**c, "doc_en": DOCUMENTS[c["doc_id"]]["en"], "doc_ta": DOCUMENTS[c["doc_id"]]["ta"], "sample": True}
             for c in p.get("sample_documents", [])]
    return {"persona": persona, "cards": cards}


@app.post("/api/demo/{persona}")
def demo(persona: str, session_id: Optional[str] = None, live: bool = False):
    """Load a demo family. Default: facts load directly (instant, no AI quota).
    `?live=1` sends the scripted Tamil answers through the AI agent instead."""
    direct = not live
    if persona not in agent.PERSONAS:
        raise HTTPException(404, "unknown persona")
    if session_id and session_id in agent.SESSIONS:
        s, events = agent.SESSIONS[session_id], []
    else:
        s, events = agent.new_session()
    e, snapshot, reply = agent.load_persona(s, persona, direct=direct)
    return _out(s, events + e, snapshot, reply)


# ------------------------------------------------------------------ voice
@app.post("/api/stt")
def stt(audio: UploadFile = File(...), lang: str = Form("ta")):
    data = audio.file.read()
    if not data:
        raise HTTPException(400, "empty audio")
    try:
        return voice.transcribe(data, audio.filename or "speech.webm", lang)
    except Exception as exc:  # network / key problems: the UI falls back to typing
        raise HTTPException(503, f"speech service unavailable: {str(exc)[:120]}") from exc


@app.post("/api/tts")
def tts(body: TtsIn):
    if not body.text.strip():
        raise HTTPException(400, "empty text")
    try:
        return Response(voice.speak(body.text, body.lang), media_type="audio/mpeg")
    except Exception as exc:
        raise HTTPException(503, f"voice service unavailable: {str(exc)[:120]}") from exc


# ------------------------------------------------------------ follow-up
def _recipient(session_id, authorization):
    """(user_id, phone) of the family this session belongs to; (None, None) for a guest."""
    user = store.user_for(_bearer(authorization))
    if user and user["role"] == "family":
        return user["id"], store.phone_of(user["id"])
    return store.chat_owner(session_id)


def _sms_event(msg, what_en, what_ta):
    if msg["status"] == "sent":
        return agent.ev("tool", "", f"{what_en}: SMS sent to {msg['to']}", f"{what_ta}: {msg['to']} எண்ணுக்குக் குறுஞ்செய்தி அனுப்பப்பட்டது")
    if msg["status"] == "failed":
        return agent.ev("error", "", f"{what_en}: SMS could not be sent ({msg['detail']}); kept in the outbox",
                        f"{what_ta}: குறுஞ்செய்தி அனுப்ப முடியவில்லை; outbox-இல் உள்ளது")
    return agent.ev("tool", "", f"{what_en}: SMS prepared in the outbox (never share your OTP)",
                    f"{what_ta}: குறுஞ்செய்தி outbox-இல் தயாரானது (OTP எச்சரிக்கையுடன்)")


@app.post("/api/sms/summary")
def sms_summary(body: SummaryIn, authorization: Optional[str] = Header(None)):
    s = _session(body.session_id)
    uid, phone = _recipient(s["id"], authorization)
    text = notify.summary_sms(s["snapshot"], body.lang if body.lang in ("ta", "en") else "ta")
    msg = sms.deliver(s["id"], uid, phone, text, "summary")
    return {"events": [_sms_event(msg, "Summary of benefits and next steps", "நன்மைகள், அடுத்த படிகள் சுருக்கம்")], "message": msg}


@app.get("/api/outbox")
def outbox(session_id: Optional[str] = None):
    return {"messages": store.list_outbox(session_id)}


@app.post("/api/simulate")
def simulate(body: SimIn, authorization: Optional[str] = Header(None)):
    """'N days later': the agent follows up on its own (reminders, deadlines, escalation)."""
    s = _session(body.session_id)
    uid, phone = _recipient(s["id"], authorization)
    result = proactive.simulate(s["snapshot"], agent.helper_queue(s["id"]), max(1, min(body.days, 60)))
    events = result["events"]
    for e in events:
        d = e.get("detail") or {}
        if d.get("escalate") and all(i.get("key") != "follow:escalation" for i in s["helper_queue"]):
            agent._queue_escalation(s, d.get("reason_en", "Task open too long"), d.get("reason_ta") or d.get("reason_en", ""), "follow:escalation")
    for m in result["messages"]:
        sms.deliver(s["id"], uid, phone, m["text"], m["reason"])
    return _out(s, events, s["snapshot"])


# Accounts + history (F1) and the official source check (S2).
import routes_admin  # noqa: E402
import routes_auth  # noqa: E402

app.include_router(routes_auth.router)
app.include_router(routes_admin.router)

# Mounted last so /api routes take priority.
app.mount("/", StaticFiles(directory=config.STATIC_DIR, html=True), name="static")
