"""Auth + history tests (offline, temp sqlite DB; app.py is not modified)."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import agent  # noqa: E402
import config  # noqa: E402
import routes_auth  # noqa: E402
import store  # noqa: E402

auth_app = FastAPI()
auth_app.include_router(routes_auth.router)
client = TestClient(auth_app)

PHONE, PIN = "98765 43210", "4821"


@pytest.fixture(autouse=True)
def db(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "USE_LLM", False)
    monkeypatch.setattr(store, "DB_PATH", tmp_path / "test.db")
    store.TOKENS.clear()
    store.init()
    yield


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def register(phone=PHONE, pin=PIN, consent=True):
    return client.post("/api/auth/register", json={"phone": phone, "pin": pin, "consent": consent})


def murugan_session():
    s, _ = agent.new_session()
    agent.load_persona(s, "murugan_family", direct=True)
    return s


def no_secret(resp_text):
    con = store._conn()
    rows = con.execute("SELECT pin_hash, salt FROM users").fetchall()
    con.close()
    for r in rows:
        assert r["pin_hash"] not in resp_text and r["salt"] not in resp_text
    assert "pin_hash" not in resp_text and '"salt"' not in resp_text


def test_register_login_save_history_reopen():
    r = register()
    assert r.status_code == 200, r.text
    no_secret(r.text)
    assert r.json()["user"]["phone_masked"] == "98xxxxxx10"
    r = client.post("/api/auth/login", json={"phone": "+91 9876543210", "pin": PIN})
    assert r.status_code == 200
    no_secret(r.text)
    token = r.json()["token"]
    assert client.get("/api/me", headers=auth(token)).json()["user"]["role"] == "family"

    s = murugan_session()
    evs = [{"type": "reply", "icon": "", "text_en": "hi", "text_ta": "hi", "detail": {}}]
    r = client.post("/api/history/save", json={"session_id": s["id"], "events": evs}, headers=auth(token))
    assert r.status_code == 200, r.text
    chat = r.json()["chat"]
    assert chat["chat_id"] == s["id"] and chat["rupees_per_year"] == 30000
    assert chat["title"].endswith(" family")

    r = client.get("/api/history", headers=auth(token))
    chats = r.json()["chats"]
    assert len(chats) == 1 and chats[0]["rupees_per_year"] == 30000
    no_secret(r.text)

    r = client.get(f"/api/history/{s['id']}", headers=auth(token))
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["snapshot"]["rupees_per_year"] == 30000
    assert out["session_id"] != s["id"] and out["session_id"] in agent.SESSIONS
    assert out["events"][0]["text_en"] == "hi" and out["title"] == chat["title"]
    no_secret(r.text)


def test_wrong_pin_401():
    register()
    assert client.post("/api/auth/login", json={"phone": PHONE, "pin": "0000"}).status_code == 401
    assert client.post("/api/auth/login", json={"phone": "9000000000", "pin": PIN}).status_code == 401


def test_bad_phone_and_pin_400():
    assert register(phone="12345").status_code == 400
    assert register(phone="5876543210").status_code == 400
    assert register(pin="12a4").status_code == 400
    assert register().status_code == 200
    assert register().status_code == 400  # duplicate


def test_no_consent_400():
    assert register(consent=False).status_code == 400


def test_helper_login():
    r = client.post("/api/auth/login", json={"phone": "helper", "pin": "helper123"})
    assert r.status_code == 200
    user = r.json()["user"]
    assert user["role"] == "helper" and user["name"] == "Priya"
    assert client.post("/api/auth/login", json={"phone": "helper", "pin": "nope"}).status_code == 401


def test_auth_required_and_unknown_session():
    assert client.get("/api/me").status_code == 401
    assert client.get("/api/history", headers=auth("bogus")).status_code == 401
    token = register().json()["token"]
    assert client.post("/api/history/save", json={"session_id": "nope"}, headers=auth(token)).status_code == 404
    assert client.get("/api/history/nope", headers=auth(token)).status_code == 404


def test_other_user_cannot_open_chat():
    t1 = register().json()["token"]
    s = murugan_session()
    client.post("/api/history/save", json={"session_id": s["id"]}, headers=auth(t1))
    t2 = register(phone="9123456780").json()["token"]
    assert client.get(f"/api/history/{s['id']}", headers=auth(t2)).status_code == 404
    assert client.get("/api/history", headers=auth(t2)).json()["chats"] == []


def test_delete_me():
    token = register().json()["token"]
    s = murugan_session()
    client.post("/api/history/save", json={"session_id": s["id"]}, headers=auth(token))
    uid = client.get("/api/me", headers=auth(token)).json()["user"]["id"]
    r = client.delete("/api/me", headers=auth(token))
    assert r.json() == {"deleted": True}
    assert client.get("/api/me", headers=auth(token)).status_code == 401
    assert store.list_chats(uid) == []
    assert client.post("/api/auth/login", json={"phone": PHONE, "pin": PIN}).status_code == 401


def test_logout():
    token = register().json()["token"]
    assert client.post("/api/auth/logout", headers=auth(token)).json() == {}
    assert client.get("/api/me", headers=auth(token)).status_code == 401
