"""Thunai web app: FastAPI routes (plain JSON) + the static single-page UI."""
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import agent
import config
from engine import doctor as doctor_engine

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


def _session(session_id):
    s = agent.SESSIONS.get(session_id)
    if s is None:
        raise HTTPException(404, "session not found — start a new session")
    return s


def _out(session, events, snapshot, reply=None):
    data = {"session_id": session["id"], "events": events, "snapshot": snapshot,
            "unconfirmed": session["unconfirmed"], "pending_ask": session["pending_ask"],
            "doctor": session["doctor"]["step"] if session["doctor"] else None}
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
    s = _session(body.session_id)
    if body.entry_id:
        step = doctor_engine.start(body.entry_id)
        s["doctor"] = {"entry_id": body.entry_id, "tree": step["tree"], "path": step["path"], "step": step}
        events = [agent.ev("tool", "", f"run_doctor  {body.entry_id}")]
    elif body.answer and s["doctor"]:
        d = s["doctor"]
        step = doctor_engine.answer(d["tree"], d["path"], body.answer)
        d.update(path=step["path"], step=step)
        events = [agent.ev("tool", "", f"doctor_step  answer: {body.answer} → {step['node_id']}")]
    else:
        raise HTTPException(400, "give entry_id or answer")
    return {"events": events, "step": s["doctor"]["step"]}


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


# Mounted last so /api routes take priority.
app.mount("/", StaticFiles(directory=config.STATIC_DIR, html=True), name="static")
