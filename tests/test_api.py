"""API tests (offline: USE_LLM off, no AI quota used). Live AI tests: RUN_LIVE=1."""
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import app as appmod  # noqa: E402
import config  # noqa: E402
import pii_guard  # noqa: E402

client = TestClient(appmod.app)
live = pytest.mark.skipif(os.environ.get("RUN_LIVE") != "1", reason="live AI test: set RUN_LIVE=1")


@pytest.fixture(autouse=True)
def offline(monkeypatch, request):
    if "live" not in request.keywords:
        monkeypatch.setattr(config, "USE_LLM", False)


def load(persona):
    r = client.post(f"/api/demo/{persona}")
    assert r.status_code == 200
    return r.json()


def test_health():
    assert client.get("/api/health").json()["status"] == "ok"


def test_new_session_has_goal_and_first_question():
    r = client.post("/api/session", json={}).json()
    assert [e["type"] for e in r["events"]] == ["goal", "plan"]
    assert r["snapshot"]["next_question"]["id"] == "household"


def test_murugan_direct_load():
    r = load("murugan_family")
    s = r["snapshot"]
    assert s["rupees_per_year"] == 30000 and s["trips"] == {"without": 6, "with": 2}
    assert any("₹0 → ₹30,000" in e["text_en"] for e in r["events"])


def test_card_edit_replans_with_reason():
    sid = load("murugan_family")["session_id"]
    r = client.post("/api/facts", json={"session_id": sid, "path": "family.annual_income", "value": 300000}).json()
    texts = " | ".join(e["text_en"] for e in r["events"])
    assert r["snapshot"]["rupees_per_year"] == 18000
    assert "₹30,000 → ₹18,000" in texts and "Family income below ₹2.5 lakh" in texts


def test_card_edit_rejects_bad_path():
    sid = load("murugan_family")["session_id"]
    r = client.post("/api/facts", json={"session_id": sid, "path": "family.salary", "value": 1})
    assert r.status_code == 400


def test_task_done_replans():
    sid = load("murugan_family")["session_id"]
    r = client.post("/api/task", json={"session_id": sid, "task_id": "m2:bank_account_aadhaar_seeded", "done": True}).json()
    assert any(e["text_en"].startswith("Task removed") and "Selvi" in e["text_en"] for e in r["events"])


def test_privacy_guard_offline_chat():
    sid = client.post("/api/session", json={}).json()["session_id"]
    r = client.post("/api/chat", json={"session_id": sid, "text": "my Aadhaar is 1234 5678 9012"}).json()
    types = [e["type"] for e in r["events"]]
    assert "privacy" in types and "fallback" in types


def test_pii_guard_removes_numbers():
    cleaned, n = pii_guard.clean("Aadhaar 1234-5678-9012, account 12345678901")
    assert n == 2 and not any(ch.isdigit() for ch in cleaned)


def test_meena_doctor():
    r = load("meena")
    assert r["doctor"]["node_id"] == "o_seeding" and r["doctor"]["kind"] == "outcome"


def test_lakshmi_pension_and_doctor():
    r = load("lakshmi_paati")
    assert r["snapshot"]["rupees_per_year"] == 14400
    assert r["doctor"]["node_id"] == "o_fix_doc_and_petition"


def test_doctor_buttons():
    sid = client.post("/api/session", json={}).json()["session_id"]
    step = client.post("/api/doctor", json={"session_id": sid, "entry_id": "kmut_payment_stopped"}).json()["step"]
    assert step["node_id"] == "q_selected_sms"
    step = client.post("/api/doctor", json={"session_id": sid, "answer": "yes"}).json()["step"]
    step = client.post("/api/doctor", json={"session_id": sid, "answer": "dont_know"}).json()["step"]
    assert step["node_id"] == "o_seeding" and step["fix_en"][0].startswith("First check")


@live
@pytest.mark.live
def test_live_correction_replans():
    sid = load("murugan_family")["session_id"]
    r = client.post("/api/chat", json={"session_id": sid, "text": "இல்லங்க, வருமானம் 90,000 இல்ல, 3 லட்சம்."}).json()
    assert r["snapshot"]["facts"]["family"]["annual_income"] == 300000
    assert r["snapshot"]["rupees_per_year"] == 18000


@live
@pytest.mark.live
def test_live_aadhaar_never_reaches_ai(monkeypatch):
    import llm
    seen = []
    real = llm._user_message
    monkeypatch.setattr(llm, "_user_message", lambda *a: seen.append(a[0]) or real(*a))
    sid = client.post("/api/session", json={}).json()["session_id"]
    client.post("/api/chat", json={"session_id": sid, "text": "என் ஆதார் 1234 5678 9012"})
    assert seen and all("1234" not in s for s in seen)
