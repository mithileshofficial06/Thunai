"""Follow-up tests (offline): SMS summary, proactive simulation. Live voice round trip: RUN_LIVE=1."""
import difflib
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402

import config  # noqa: E402

config.USE_LLM = False
import agent  # noqa: E402
from engine import notify, proactive  # noqa: E402


@pytest.fixture(scope="module")
def snap():
    config.USE_LLM = False
    s, _ = agent.new_session()
    agent.load_persona(s, "murugan_family", direct=True)
    return s["snapshot"]


@pytest.mark.parametrize("lang", ["ta", "en"])
def test_summary_sms(snap, lang):
    text = notify.summary_sms(snap, lang)
    assert "30,000" in text and "OTP" in text and len(text) <= 480
    assert text.startswith("துணை:" if lang == "ta" else "Thunai:")


def test_summary_nothing_eligible():
    text = notify.summary_sms({"verdicts": [], "plan": [], "rupees_per_year": 0}, "en")
    assert text.startswith("Thunai:") and text.endswith("Never share your OTP.")


def test_reminder_sms(snap):
    office = snap["plan"][0]
    for lang in ("ta", "en"):
        text = notify.reminder_sms(office["tasks"][0], office["office_ta"], office["office_en"], lang)
        assert "OTP" in text and len(text) <= 480


def test_simulate(snap):
    out = proactive.simulate(snap, [], 15)
    assert all(e["type"] == "autonomous" for e in out["events"])
    assert any(e["detail"].get("escalate") for e in out["events"])
    assert len([m for m in out["messages"] if m["reason"] == "reminder"]) >= 2


def test_simulate_deadline_no_escalation(snap):
    out = proactive.simulate(snap, [{"id": "d1", "kind": "appeal_kmut", "status": "DRAFT"}], 5)
    assert any("25 days left" in e["text_en"] for e in out["events"])
    assert not any(e["detail"].get("escalate") for e in out["events"])
    assert any(m["reason"] == "deadline" for m in out["messages"])


@pytest.mark.skipif(os.environ.get("RUN_LIVE") != "1", reason="live voice test: set RUN_LIVE=1")
def test_voice_round_trip():
    import voice

    sentence = "வணக்கம், என் பெயர் செல்வி. நான் மகளிர் உரிமைத் தொகைக்கு விண்ணப்பிக்க வேண்டும்."
    audio = voice.speak(sentence, "ta")
    assert len(audio) > 1000
    got = voice.transcribe(audio, "speech.mp3", "ta")["text"]

    def norm(s):
        return "".join(ch for ch in s if ch.isalnum() or ch in "்ாிீுூெேைொோௌஂ")

    assert difflib.SequenceMatcher(None, norm(sentence), norm(got)).ratio() >= 0.85, got
