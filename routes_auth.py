"""Login (phone + 4-digit PIN), helper login, and saved conversation history.

Mount in app.py BEFORE the static mount:  app.include_router(routes_auth.router)
"""
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

import agent
import store
from engine import recompute

router = APIRouter()
store.init()


class RegisterIn(BaseModel):
    phone: str
    pin: str
    consent: bool = False
    name: str = ""


class LoginIn(BaseModel):
    phone: str
    pin: str


class SaveIn(BaseModel):
    session_id: str
    events: Optional[list] = None


def _token(authorization: Optional[str]):
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return None


def current_user(authorization: Optional[str] = Header(None)):
    user = store.user_for(_token(authorization))
    if user is None:
        raise HTTPException(401, "please log in")
    return user


def helper_user(authorization: Optional[str] = Header(None)):
    """Dependency for helper-only routes: 401 without a valid token, 403 for a family account."""
    user = store.user_for(_token(authorization))
    if user is None:
        raise HTTPException(401, "please log in as a helper")
    if user.get("role") != "helper":
        raise HTTPException(403, "helper sign-in required")
    return user


@router.post("/api/auth/register")
def register(body: RegisterIn):
    if not body.consent:
        raise HTTPException(400, "consent is required to save your family's details")
    try:
        user = store.register(body.phone, body.pin, "family", body.name)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"token": store.new_token(user["id"]), "user": user}


@router.post("/api/auth/login")
def login(body: LoginIn):
    user = store.login(body.phone, body.pin)
    if user is None:
        raise HTTPException(401, "wrong phone number or PIN")
    return {"token": store.new_token(user["id"]), "user": user}


@router.post("/api/auth/logout")
def logout(authorization: Optional[str] = Header(None)):
    store.revoke(_token(authorization))
    return {}


@router.get("/api/me")
def me(user=Depends(current_user)):
    return {"user": user}


@router.delete("/api/me")
def delete_me(authorization: Optional[str] = Header(None), user=Depends(current_user)):
    store.delete_user(user["id"])
    store.revoke(_token(authorization))
    return {"deleted": True}


def _title(facts):
    head = next((m.get("name") for m in (facts or {}).get("members", []) if m.get("relation") == "self" and m.get("name")), None)
    return f"{head} family" if head else "Conversation"


@router.post("/api/history/save")
def save(body: SaveIn, user=Depends(current_user)):
    s = agent.SESSIONS.get(body.session_id)
    if s is None:
        raise HTTPException(404, "session not found")
    events = (body.events or [])[-200:]
    # what the family qualifies for right now: the new-scheme re-match compares against this
    # Recomputed with the CURRENT rules (not the session's possibly older snapshot), so a scheme added
    # after this session started is recorded too and the re-match never alerts the same family twice.
    eligible = [v["key"] for v in recompute(s["facts"])["verdicts"] if v["status"] == "ELIGIBLE"]
    try:
        chat = store.save_chat(user["id"], s["id"], _title(s["facts"]), s["facts"], events,
                               s["snapshot"].get("rupees_per_year", 0), eligible=eligible)
    except PermissionError:
        raise HTTPException(404, "session not found")
    return {"chat": chat}


@router.get("/api/history")
def history(user=Depends(current_user)):
    return {"chats": store.list_chats(user["id"])}


@router.get("/api/history/{chat_id}")
def reopen(chat_id: str, user=Depends(current_user)):
    chat = store.get_chat(user["id"], chat_id)
    if chat is None:
        raise HTTPException(404, "conversation not found")
    # same id as the saved chat, so later autosaves update this conversation instead of adding a copy
    session, events = agent.new_session(chat["facts"], sid=chat_id)
    return {"session_id": session["id"], "events": chat["events"] + events, "snapshot": session["snapshot"],
            "unconfirmed": [], "pending_ask": [], "doctor": None,
            "suggested_letters": agent.letter_suggestions(session), "drafts": agent.helper_queue(chat_id),
            "title": chat["title"]}
