"""Phase 2 tests (offline): letters + helper approval, Doctor wiring, the sample-documents family."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import app as appmod  # noqa: E402
import config  # noqa: E402

client = TestClient(appmod.app)


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setattr(config, "USE_LLM", False)


def load(persona):
    r = client.post(f"/api/demo/{persona}")
    assert r.status_code == 200
    return r.json()


def draft(sid, kind, **extra):
    r = client.post("/api/letter", json={"session_id": sid, "kind": kind, **extra})
    assert r.status_code == 200, r.text
    return r.json()


def texts(r):
    return " | ".join(e["text_en"] for e in r["events"])


# ------------------------------------------------------------------ P1 letters
def test_murugan_application_pack_names_all_three_schemes():
    r = load("murugan_family")
    assert "application_pack" in [s["kind"] for s in r["suggested_letters"]]
    d = draft(r["session_id"], "application_pack")
    assert d["draft"]["status"] == "DRAFT" and "Waiting for helper approval" in texts(d)
    html = client.get(d["draft"]["html_url"]).text
    for name in ("PM-KISAN", "Kalaignar Magalir Urimai Thogai", "Pudhumai Penn", "விண்ணப்பத் தொகுப்பு"):
        assert name in html
    assert "DRAFT" in html and "window.print" not in html
    assert d["snapshot"]["plan_steps"][-1]["done"] is True  # packs step done


def test_approve_removes_watermark_and_allows_print():
    r = load("murugan_family")
    d = draft(r["session_id"], "bank_seeding_request", member_id="m2")
    assert d["draft"]["member_name"] == "Selvi"
    a = client.post("/api/helper/approve", json={"draft_id": d["draft"]["draft_id"], "helper_name": "Priya"}).json()
    assert a["draft"]["status"] == "APPROVED" and "Priya approved" in a["events"][0]["text_en"]
    html = client.get(d["draft"]["html_url"]).text
    assert "window.print" in html and 'class="watermark"' not in html and "Priya" in html
    assert "Selvi" in html and "NPCI" in html


def test_letter_never_invents_numbers():
    r = load("murugan_family")
    html = client.get(draft(r["session_id"], "bank_seeding_request", member_id="m2")["draft"]["html_url"]).text
    assert "________" in html  # account number, bank and branch left blank for the family to write


def test_letter_that_does_not_apply_is_refused():
    r = load("murugan_family")
    bad = client.post("/api/letter", json={"session_id": r["session_id"], "kind": "appeal_pension"})
    assert bad.status_code == 400
    assert client.post("/api/letter", json={"session_id": r["session_id"], "kind": "nonsense"}).status_code == 400


def test_same_letter_twice_reuses_the_draft():
    r = load("murugan_family")
    a = draft(r["session_id"], "application_pack")["draft"]["draft_id"]
    b = draft(r["session_id"], "application_pack")["draft"]["draft_id"]
    assert a == b


def test_helper_queue_lists_drafts():
    r = load("murugan_family")
    d = draft(r["session_id"], "application_pack")
    items = client.get("/api/helper/queue", params={"session_id": r["session_id"]}).json()["items"]
    assert [i["draft_id"] for i in items] == [d["draft"]["draft_id"]]
    assert client.get("/letter/doesnotexist").status_code == 404


# -------------------------------------------------------------- P2 Doctor
def test_meena_doctor_suggests_bank_letter_and_plans_the_bank_visit():
    r = load("meena")
    assert r["doctor"]["node_id"] == "o_seeding"
    assert "bank_seeding_request" in [s["kind"] for s in r["suggested_letters"]]
    assert r["snapshot"]["plan"][0]["office_id"] == "bank_branch"
    d = draft(r["session_id"], "bank_seeding_request")
    assert "Meena" in client.get(d["draft"]["html_url"]).text


def test_lakshmi_appeal_contains_name_and_reason():
    r = load("lakshmi_paati")
    assert r["doctor"]["node_id"] == "o_fix_doc_and_petition"
    d = draft(r["session_id"], "appeal_pension")
    html = client.get(d["draft"]["html_url"]).text
    assert "Lakshmi" in html and "death certificate not attached" in html and "Special Tahsildar" in html


def test_doctor_via_api_dont_know_follows_no():
    sid = client.post("/api/session", json={}).json()["session_id"]
    r = client.post("/api/doctor", json={"session_id": sid, "entry_id": "kmut_payment_stopped"}).json()
    assert r["step"]["node_id"] == "q_selected_sms"
    r = client.post("/api/doctor", json={"session_id": sid, "answer": "yes"}).json()
    r = client.post("/api/doctor", json={"session_id": sid, "answer": "dont_know"}).json()
    assert r["step"]["node_id"] == "o_seeding" and r["step"]["fix_en"][0].startswith("First check")
    assert "Most likely cause" in texts(r)
    assert client.post("/api/doctor", json={"session_id": sid, "answer": "yes"}).status_code == 400  # no open question


def test_doctor_escalation_goes_to_helper_queue():
    sid = client.post("/api/session", json={}).json()["session_id"]
    client.post("/api/doctor", json={"session_id": sid, "entry_id": "kmut_payment_stopped"})
    for a in ("yes", "yes", "yes", "no"):  # selected, seeded, active, no change -> unclear -> grievance + helper
        r = client.post("/api/doctor", json={"session_id": sid, "answer": a}).json()
    assert r["step"]["node_id"] == "o_passbook_and_grievance"
    kinds = [i["kind"] for i in r["drafts"]]
    assert "escalation" in kinds and "grievance" in [s["kind"] for s in r["suggested_letters"]]


# ------------------------------------------------------- P3 sample documents
def test_revathi_document_problems_found():
    r = load("revathi_docs")
    s = r["snapshot"]
    assert s["matrix"][0]["level"] == "RED"
    assert {m["doc_id"] for m in s["missing_documents"]} == {"husband_death_certificate", "bank_account_aadhaar_seeded"}
    offices = {o["office_id"]: [t["task_id"] for t in o["tasks"]] for o in s["plan"]}
    # The pension checks Aadhaar, death certificate and passbook names: the passbook fix joins the bank visit.
    assert {"r1:bank_account_aadhaar_seeded", "r1:fix_name:bank_passbook"} <= set(offices["bank_branch"])
    assert "local_body" in offices and "esevai_csc" in offices
    assert s["trips"] == {"without": 4, "with": 3}
    kinds = {(x["kind"], x["doc_id"]) for x in r["suggested_letters"]}
    assert {("name_correction_request", "ration_card"), ("bank_seeding_request", None), ("application_pack", None)} <= kinds


def test_revathi_sample_cards_are_marked_and_have_no_numbers():
    cards = client.get("/api/sample_docs/revathi_docs").json()["cards"]
    assert len(cards) == 4 and all(c["sample"] for c in cards)
    import re
    assert not re.search(r"\d{9,}", str(cards))


def test_revathi_name_letter_and_fix_tick_replans():
    r = load("revathi_docs")
    sid = r["session_id"]
    html = client.get(draft(sid, "name_correction_request", member_id="r1", doc_id="ration_card")["draft"]["html_url"]).text
    assert "S. Revathi" in html and "Revathi Sekar" in html and "Taluk Supply Officer" in html
    t = client.post("/api/task", json={"session_id": sid, "task_id": "r1:fix_name:bank_passbook", "done": True}).json()
    assert "Completed: Revathi, Correct the name on the Bank passbook" in texts(t)
    cells = {c["doc_id"]: c["name_printed"] for c in t["snapshot"]["matrix"][0]["cells"]}
    assert cells["bank_passbook"] == "Revathi Sekar"  # now printed as on Aadhaar
    tasks = [x["task_id"] for o in t["snapshot"]["plan"] for x in o["tasks"]]
    assert "r1:fix_name:bank_passbook" not in tasks


# --------------------------------------------------------- follow-up + voice
def test_summary_sms_goes_to_outbox_with_otp_warning():
    r = load("murugan_family")
    m = client.post("/api/sms/summary", json={"session_id": r["session_id"], "lang": "en"}).json()["message"]
    assert "30,000" in m["text"] and "OTP" in m["text"] and len(m["text"]) <= 480
    msgs = client.get("/api/outbox", params={"session_id": r["session_id"]}).json()["messages"]
    assert msgs[0]["id"] == m["id"] and msgs[0]["status"] == "outbox"


def test_simulate_15_days_reminds_and_escalates_to_helper():
    r = load("murugan_family")
    s = client.post("/api/simulate", json={"session_id": r["session_id"], "days": 15}).json()
    assert s["events"] and all(e["type"] == "autonomous" for e in s["events"])
    assert any(i["kind"] == "escalation" for i in s["drafts"])
    again = client.post("/api/simulate", json={"session_id": r["session_id"], "days": 15}).json()
    assert sum(i["kind"] == "escalation" for i in again["drafts"]) == 1  # not duplicated
    assert len(client.get("/api/outbox", params={"session_id": r["session_id"]}).json()["messages"]) >= 2


def test_voice_routes_reject_empty_input():
    assert client.post("/api/tts", json={"text": "  "}).status_code == 400
    assert client.post("/api/stt", files={"audio": ("a.webm", b"", "audio/webm")}).status_code == 400
