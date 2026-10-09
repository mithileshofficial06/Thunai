"""Accounts, saved chats, login tokens and the SMS outbox (stdlib sqlite3).

PINs are stored only as PBKDF2 hashes. Login tokens are kept in the database (with an in-memory
cache), so a server restart does not log anyone out.
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
TOKENS = {}  # cache: token -> user_id (the tokens table is the source of truth)

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
        cols = {r[1] for r in con.execute("PRAGMA table_info(chats)")}
        if "eligible_json" not in cols:  # added later: schemes the family qualified for at the last check
            con.execute("ALTER TABLE chats ADD COLUMN eligible_json TEXT")
        con.execute("CREATE TABLE IF NOT EXISTS tokens (token TEXT PRIMARY KEY, user_id INTEGER, created TEXT)")
        con.execute("""CREATE TABLE IF NOT EXISTS outbox (
            id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, user_id INTEGER, to_masked TEXT,
            text TEXT, reason TEXT, created TEXT, status TEXT, detail TEXT)""")
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


def phone_of(user_id):
    """Raw phone number of a family account (for SMS); None for helpers or unknown users."""
    row = _user_row(user_id)
    return row["phone"] if row and row["role"] == "family" else None


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


def save_chat(user_id, chat_id, title, facts, events, rupees, eligible=None):
    con = _conn()
    try:
        with con:
            owner = con.execute("SELECT user_id FROM chats WHERE id = ?", (chat_id,)).fetchone()
            if owner and owner["user_id"] != user_id:
                raise PermissionError("chat belongs to another user")
            con.execute("""INSERT INTO chats (id, user_id, title, facts_json, events_json, rupees, updated, eligible_json)
                           VALUES (?,?,?,?,?,?,?,?)
                           ON CONFLICT(id) DO UPDATE SET title=excluded.title, facts_json=excluded.facts_json,
                           events_json=excluded.events_json, rupees=excluded.rupees, updated=excluded.updated,
                           eligible_json=excluded.eligible_json""",
                        (chat_id, user_id, title, json.dumps(facts, ensure_ascii=False),
                         json.dumps(events or [], ensure_ascii=False), int(rupees or 0), _now(),
                         json.dumps(sorted(eligible or []))))
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


def chat_owner(chat_id):
    """(user_id, phone) of the family account that saved this conversation, or (None, None)."""
    con = _conn()
    try:
        row = con.execute("""SELECT u.id, u.phone, u.role FROM chats c JOIN users u ON u.id = c.user_id
                             WHERE c.id = ?""", (chat_id,)).fetchone()
    finally:
        con.close()
    if row is None or row["role"] != "family":
        return None, None
    return row["id"], row["phone"]


def all_family_chats():
    """Every saved family conversation (for the new-scheme re-match)."""
    con = _conn()
    try:
        rows = con.execute("""SELECT c.id, c.user_id, c.title, c.facts_json, c.eligible_json, u.phone
                              FROM chats c JOIN users u ON u.id = c.user_id WHERE u.role = 'family'""").fetchall()
    finally:
        con.close()
    return [{"chat_id": r["id"], "user_id": r["user_id"], "title": r["title"], "phone": r["phone"],
             "facts": json.loads(r["facts_json"] or "null"),
             "eligible": None if r["eligible_json"] is None else json.loads(r["eligible_json"])} for r in rows]


def set_eligible(chat_id, keys):
    con = _conn()
    try:
        with con:
            con.execute("UPDATE chats SET eligible_json = ? WHERE id = ?", (json.dumps(sorted(keys)), chat_id))
    finally:
        con.close()


def delete_user(user_id):
    con = _conn()
    try:
        with con:
            con.execute("DELETE FROM chats WHERE user_id = ?", (user_id,))
            con.execute("DELETE FROM outbox WHERE user_id = ?", (user_id,))
            con.execute("DELETE FROM tokens WHERE user_id = ?", (user_id,))
            con.execute("DELETE FROM users WHERE id = ?", (user_id,))
    finally:
        con.close()
    for t in [t for t, uid in TOKENS.items() if uid == user_id]:
        TOKENS.pop(t, None)


# ----------------------------------------------------------------- tokens
def new_token(user_id):
    token = secrets.token_urlsafe(24)
    con = _conn()
    try:
        with con:
            con.execute("INSERT INTO tokens (token, user_id, created) VALUES (?,?,?)", (token, user_id, _now()))
    finally:
        con.close()
    TOKENS[token] = user_id
    return token


def user_for(token):
    if not token:
        return None
    uid = TOKENS.get(token)
    if uid is None:
        con = _conn()
        try:
            row = con.execute("SELECT user_id FROM tokens WHERE token = ?", (token,)).fetchone()
        finally:
            con.close()
        if row is None:
            return None
        uid = TOKENS[token] = row["user_id"]
    return get_user(uid)


def revoke(token):
    TOKENS.pop(token or "", None)
    con = _conn()
    try:
        with con:
            con.execute("DELETE FROM tokens WHERE token = ?", (token or "",))
    finally:
        con.close()


# ----------------------------------------------------------------- outbox
def mask(phone):
    phone = str(phone or "")
    return phone[:2] + "xxxxxx" + phone[-2:] if len(phone) >= 4 else phone


def add_outbox(session_id, user_id, to_masked, text, reason, status, detail=""):
    con = _conn()
    try:
        with con:
            cur = con.execute("""INSERT INTO outbox (session_id, user_id, to_masked, text, reason, created, status, detail)
                                 VALUES (?,?,?,?,?,?,?,?)""",
                              (session_id, user_id, to_masked, text, reason, _now(), status, detail))
            row = con.execute("SELECT * FROM outbox WHERE id = ?", (cur.lastrowid,)).fetchone()
        return _outbox_public(row)
    finally:
        con.close()


def _outbox_public(row):
    return {"id": row["id"], "session_id": row["session_id"], "to": row["to_masked"], "text": row["text"],
            "reason": row["reason"], "created": row["created"], "status": row["status"], "detail": row["detail"]}


def list_outbox(session_id=None):
    con = _conn()
    try:
        if session_id:
            rows = con.execute("SELECT * FROM outbox WHERE session_id = ? ORDER BY id DESC", (session_id,)).fetchall()
        else:
            rows = con.execute("SELECT * FROM outbox ORDER BY id DESC LIMIT 200").fetchall()
        return [_outbox_public(r) for r in rows]
    finally:
        con.close()
