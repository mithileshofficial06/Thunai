"""SMS delivery tests: outbox by default, real provider path tested against a simulated SMS service."""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import httpx  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import app as appmod  # noqa: E402
import config  # noqa: E402
import sms  # noqa: E402
import store  # noqa: E402

client = TestClient(appmod.app)


@pytest.fixture(autouse=True)
def tmp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DB_PATH", tmp_path / "t.db")
    store.TOKENS.clear()
    store.init()
    monkeypatch.setattr(config, "USE_LLM", False)
    monkeypatch.setattr(config, "SMS_PROVIDER", None)


def twilio_on(monkeypatch):
    monkeypatch.setattr(config, "SMS_PROVIDER", "twilio")
    monkeypatch.setattr(config, "TWILIO_ACCOUNT_SID", "ACtest")
    monkeypatch.setattr(config, "TWILIO_AUTH_TOKEN", "secret")
    monkeypatch.setattr(config, "TWILIO_FROM", "+15550001111")


def test_outbox_when_no_provider():
    m = sms.deliver("s1", 7, "9876543210", "Thunai: hello. Never share your OTP.", "summary")
    assert m["status"] == "outbox" and m["to"] == "98xxxxxx10" and "no SMS provider" in m["detail"]
    assert store.list_outbox("s1")[0]["id"] == m["id"]


def test_guest_has_no_number():
    m = sms.deliver("s2", None, None, "text", "reminder")
    assert m["status"] == "outbox" and m["to"].startswith("(guest")


def test_provider_sends_with_indian_number(monkeypatch):
    twilio_on(monkeypatch)
    seen = {}

    def handler(request):
        seen["url"] = str(request.url)
        seen["form"] = dict(x.split("=", 1) for x in request.content.decode().split("&"))
        return httpx.Response(201, json={"sid": "SM123"})

    m = sms.deliver("s3", 1, "9876543210", "Thunai test", "summary", transport=httpx.MockTransport(handler))
    assert m["status"] == "sent" and m["detail"] == "SM123"
    assert "/Accounts/ACtest/Messages.json" in seen["url"]
    assert seen["form"]["To"] == "%2B919876543210" and seen["form"]["Body"] == "Thunai+test"


def test_provider_error_is_kept_as_failed(monkeypatch):
    twilio_on(monkeypatch)
    m = sms.deliver("s4", 1, "9876543210", "x", "summary",
                    transport=httpx.MockTransport(lambda r: httpx.Response(400, json={"message": "bad"})))
    assert m["status"] == "failed" and "400" in m["detail"]
    assert "secret" not in json.dumps(m)  # credentials never leak into the outbox


def test_summary_goes_to_the_logged_in_family_number():
    r = client.post("/api/auth/register", json={"phone": "9123456780", "pin": "1357", "consent": True}).json()
    sid = client.post("/api/demo/murugan_family").json()["session_id"]
    m = client.post("/api/sms/summary", json={"session_id": sid, "lang": "en"},
                    headers={"Authorization": f"Bearer {r['token']}"}).json()["message"]
    assert m["to"] == "91xxxxxx80" and m["status"] == "outbox" and "30,000" in m["text"]
    guest = client.post("/api/sms/summary", json={"session_id": sid, "lang": "en"}).json()["message"]
    assert guest["to"].startswith("(guest")
    assert len(client.get("/api/outbox", params={"session_id": sid}).json()["messages"]) == 2


def test_token_survives_restart():
    r = client.post("/api/auth/register", json={"phone": "9988776655", "pin": "2468", "consent": True}).json()
    store.TOKENS.clear()  # what a server restart does to the in-memory cache
    assert client.get("/api/me", headers={"Authorization": f"Bearer {r['token']}"}).status_code == 200
