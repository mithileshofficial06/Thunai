"""Accounts + saved chats (stdlib sqlite3). PINs are stored only as PBKDF2 hashes.

Tokens live in memory (TOKENS); a server restart logs everyone out, which is fine for the demo.
"""
import datetime as dt
import hashlib
import hmac
import json
import re
import secrets
import sqlite3

import config

DB_PATH = config.ROOT / "thunai.db"
ITERATIONS = 100_000
TOKENS = {}  # token -> user_id

HELPER_USERNAME, HELPER_PASSWORD, HELPER_NAME = "helper", "helper123", "Priya"


def _now():
    return dt.datetime.now().isoformat(timespec="seconds")


def _conn():
    con = sqlite3.connect(str(DB_PATH))
    con.row_factory = sqlite3.Row
    return con


def _hash(pin, salt_hex):
    return hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), bytes.fromhex(salt_hex), ITERATIONS).hex()


def init():
    with _conn() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, phone TEXT UNIQUE, pin_hash TEXT, salt TEXT,
            role TEXT, name TEXT, created TEXT)""")
        con.execute("""CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY, user_id INTEGER, title TEXT, facts_json TEXT,
            events_json TEXT, rupees INTEGER, updated TEXT)""")
        exists = con.execute("SELECT 1 FROM users WHERE phone = ?", (HELPER_USERNAME,)).fetchone()
    con.close()
    if not exists:
        _insert(HELPER_USERNAME, HELPER_PASSWORD, "helper", HELPER_NAME)


def normalize_phone(phone):
    p = re.sub(r"[\s\-]", "", str(phone or ""))
    if p.startswith("+91"):
        p = p[3:]
    elif len(p) == 12 and p.startswith("91"):
        p = p[2:]
    if not re.fullmatch(r"[6-9]\d{9}", p):
        raise ValueError("Phone number must be 10 digits starting with 6, 7, 8 or 9")
    return p


def _insert(phone, pin, role, name):
    salt = secrets.token_bytes(16).hex()
    con = _conn()
    try:
        with con:
            cur = con.execute("INSERT INTO users (phone, pin_hash, salt, role, name, created) VALUES (?,?,?,?,?,?)",
                              (phone, _hash(pin, salt), salt, role, name or "", _now()))
        return cur.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError("An account with this phone number already exists") from None
    finally:
        con.close()


def public_user(row):
    phone = row["phone"] or ""
    masked = phone[:2] + "xxxxxx" + phone[-2:] if len(phone) >= 4 else phone
    return {"id": row["id"], "phone_masked": masked, "role": row["role"], "name": row["name"]}


def _user_row(user_id):
    con = _conn()
    try:
        return con.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    finally:
        con.close()


def get_user(user_id):
    row = _user_row(user_id)
    return public_user(row) if row else None


def register(phone, pin, role="family", name=""):
    if role not in ("family", "helper"):
        raise ValueError("Role must be 'family' or 'helper'")
    pin = str(pin or "")
    if role == "family":
        phone = normalize_phone(phone)
        if not re.fullmatch(r"\d{4}", pin):
            raise ValueError("PIN must be exactly 4 digits")
    else:
        phone = str(phone or "").strip()
        if not phone:
            raise ValueError("Username is required")
        if len(pin) < 4:
            raise ValueError("Password must be at least 4 characters")
    return get_user(_insert(phone, pin, role, name))


def login(phone_or_username, pin):
    ident = str(phone_or_username or "").strip()
    try:
        ident = normalize_phone(ident)
    except ValueError:
        pass  # a helper username, not a phone number
    con = _conn()
    try:
        row = con.execute("SELECT * FROM users WHERE phone = ?", (ident,)).fetchone()
    finally:
        con.close()
    if row is None:
        _hash(str(pin or ""), "00" * 16)  # same work either way: no timing hint that the account exists
        return None
    if not hmac.compare_digest(_hash(str(pin or ""), row["salt"]), row["pin_hash"]):
        return None
    return public_user(row)


# ------------------------------------------------------------------ chats
def _chat_public(row, full=False):
    out = {"chat_id": row["id"], "title": row["title"], "updated": row["updated"], "rupees_per_year": row["rupees"]}
    if full:
        out["facts"] = json.loads(row["facts_json"] or "null")
        out["events"] = json.loads(row["events_json"] or "[]")
    return out


def save_chat(user_id, chat_id, title, facts, events, rupees):
    con = _conn()
    try:
        with con:
            owner = con.execute("SELECT user_id FROM chats WHERE id = ?", (chat_id,)).fetchone()
            if owner and owner["user_id"] != user_id:
                raise PermissionError("chat belongs to another user")
            con.execute("""INSERT INTO chats (id, user_id, title, facts_json, events_json, rupees, updated)
                           VALUES (?,?,?,?,?,?,?)
                           ON CONFLICT(id) DO UPDATE SET title=excluded.title, facts_json=excluded.facts_json,
                           events_json=excluded.events_json, rupees=excluded.rupees, updated=excluded.updated""",
                        (chat_id, user_id, title, json.dumps(facts, ensure_ascii=False),
                         json.dumps(events or [], ensure_ascii=False), int(rupees or 0), _now()))
            row = con.execute("SELECT * FROM chats WHERE id = ?", (chat_id,)).fetchone()
        return _chat_public(row)
    finally:
        con.close()


def list_chats(user_id):
    con = _conn()
    try:
        rows = con.execute("SELECT * FROM chats WHERE user_id = ? ORDER BY updated DESC, rowid DESC", (user_id,)).fetchall()
        return [_chat_public(r) for r in rows]
    finally:
        con.close()


def get_chat(user_id, chat_id):
    con = _conn()
    try:
        row = con.execute("SELECT * FROM chats WHERE id = ? AND user_id = ?", (chat_id, user_id)).fetchone()
        return _chat_public(row, full=True) if row else None
    finally:
        con.close()


def delete_user(user_id):
    con = _conn()
    try:
        with con:
            con.execute("DELETE FROM chats WHERE user_id = ?", (user_id,))
            con.execute("DELETE FROM users WHERE id = ?", (user_id,))
    finally:
        con.close()
    for t in [t for t, uid in TOKENS.items() if uid == user_id]:
        TOKENS.pop(t, None)


# ----------------------------------------------------------------- tokens
def new_token(user_id):
    token = secrets.token_urlsafe(24)
    TOKENS[token] = user_id
    return token


def user_for(token):
    uid = TOKENS.get(token or "")
    return get_user(uid) if uid is not None else None


def revoke(token):
    TOKENS.pop(token or "", None)
