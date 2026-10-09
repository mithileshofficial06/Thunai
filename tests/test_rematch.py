"""New-scheme re-match (POST /api/admin/rematch): offline, temp sqlite DB, no SMS provider."""
import copy
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import agent  # noqa: E402
import config  # noqa: E402
import routes_auth  # noqa: E402  (before routes_admin)
import routes_admin  # noqa: E402
import sms  # noqa: E402
import store  # noqa: E402
from engine import data, rules  # noqa: E402

app = FastAPI()
app.include_router(routes_auth.router)
app.include_router(routes_admin.router)
client = TestClient(app)

PHONE, PIN = "9876543210", "4821"
NEW_ID = "test_new_scheme"
NEW_TA = "சோதனைத் திட்டம்"


@pytest.fixture(autouse=True)
def db(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "USE_LLM", False)
    monkeypatch.setattr(sms, "provider", lambda: None)  # never reach a real SMS provider from tests
    monkeypatch.setattr(store, "DB_PATH", tmp_path / "test.db")
    store.TOKENS.clear()
    store.init()
    yield


@pytest.fixture
def add_scheme(monkeypatch):
    """enable() makes the re-match's data.reload() also 'find' one extra enabled scheme (a PM-KISAN copy)."""
    real_reload = data.reload
    extra = copy.deepcopy(data.SCHEMES_BY_ID["pm_kisan"])
    extra.update(id=NEW_ID, name_en="Test New Scheme", name_ta=NEW_TA, enabled=True)
    extra.pop("exclusive_group", None)
    extra.pop("conflicts_with", None)

    def reload_with_extra():
        n = real_reload()
        data.SCHEMES.append(extra)
        data.SCHEMES_BY_ID[NEW_ID] = extra
        return n + 1

    def enable():
        monkeypatch.setattr(data, "reload", reload_with_extra)
        return extra

    yield enable
    real_reload()  # back to the real schemes.json (in place) for every other test
    assert NEW_ID not in data.SCHEMES_BY_ID and all(s["id"] != NEW_ID for s in rules.SCHEMES)


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def helper_token():
    return store.new_token(store.login("helper", "helper123")["id"])


def saved_family():
    """A registered family with the Murugan conversation saved through the API: (family token, chat id)."""
    r = client.post("/api/auth/register", json={"phone": PHONE, "pin": PIN, "consent": True})
    assert r.status_code == 200, r.text
    token = r.json()["token"]
    s, _ = agent.new_session()
    agent.load_persona(s, "murugan_family", direct=True)
    r = client.post("/api/history/save", json={"session_id": s["id"]}, headers=auth(token))
    assert r.status_code == 200, r.text
    return token, s["id"]


def rematch(token):
    r = client.post("/api/admin/rematch", headers=auth(token))
    assert r.status_code == 200, r.text
    return r.json()


def stored_eligible(chat_id):
    return next(c["eligible"] for c in store.all_family_chats() if c["chat_id"] == chat_id)


def test_new_scheme_alerts_family_once(add_scheme):
    _, chat_id = saved_family()
    helper = helper_token()

    first = rematch(helper)  # nothing new since the save
    assert (first["checked"], first["baselined"], first["alerted"]) == (1, 0, 0)
    assert first["results"] == [] and first["messages"] == []
    assert len(first["events"]) == 1 and first["events"][0]["type"] == "autonomous"
    assert first["schemes_enabled"] == len([s for s in data.SCHEMES_FILE["schemes"] if s.get("enabled", True)])

    extra = add_scheme()
    second = rematch(helper)
    assert (second["checked"], second["alerted"]) == (1, 1)
    assert second["schemes_enabled"] == first["schemes_enabled"] + 1
    (res,) = second["results"]
    assert res["chat_id"] == chat_id and res["title"].endswith(" family")
    assert res["new"] == [{"key": NEW_ID, "name_en": "Test New Scheme", "name_ta": NEW_TA, "member_name": "Murugan",
                           "benefit_en": extra["benefit"]["display_en"], "benefit_ta": extra["benefit"]["display_ta"]}]
    (msg,) = second["messages"]
    assert msg["text"].startswith(routes_admin.SMS_HEAD) and msg["text"].endswith(routes_admin.SMS_TAIL)
    assert NEW_TA in msg["text"] and "OTP" in msg["text"] and len(msg["text"]) <= 480
    assert msg["status"] == "outbox" and msg["reason"] == "new_scheme" and msg["session_id"] == chat_id
    assert "xxxxxx" in msg["to"] and msg["to"] == "98xxxxxx10"
    assert PHONE not in json.dumps(second, ensure_ascii=False)  # the raw number never leaves the server
    assert [e["type"] for e in second["events"]] == ["autonomous", "autonomous"]
    assert "1 family newly eligible" in second["events"][0]["text_en"] and second["events"][0]["text_ta"]
    assert "Test New Scheme" in second["events"][1]["text_en"] and NEW_TA in second["events"][1]["text_ta"]
    assert NEW_ID in stored_eligible(chat_id)
    assert len(store.list_outbox(chat_id)) == 1

    third = rematch(helper)  # already announced: no duplicate SMS
    assert third["alerted"] == 0 and third["messages"] == [] and third["results"] == []
    assert len(store.list_outbox(chat_id)) == 1


def test_chat_without_record_is_baselined_not_alerted(add_scheme):
    _, chat_id = saved_family()
    con = store._conn()  # a chat saved before eligibility was recorded
    with con:
        con.execute("UPDATE chats SET eligible_json = NULL")
    con.close()
    add_scheme()
    helper = helper_token()
    body = rematch(helper)
    assert (body["checked"], body["baselined"], body["alerted"]) == (1, 1, 0) and body["messages"] == []
    assert "starting point" in body["events"][0]["text_en"]
    assert NEW_ID in stored_eligible(chat_id)
    again = rematch(helper)
    assert (again["baselined"], again["alerted"]) == (0, 0)
    assert store.list_outbox(chat_id) == []


def test_rematch_is_helper_only():
    family, _ = saved_family()
    r = client.post("/api/admin/rematch")
    assert r.status_code == 401 and r.json()["detail"] == "please log in as a helper"
    assert client.post("/api/admin/rematch", headers=auth("bogus")).status_code == 401
    r = client.post("/api/admin/rematch", headers=auth(family))
    assert r.status_code == 403 and r.json()["detail"] == "helper sign-in required"


def test_sms_text_is_capped():
    item = {"name_ta": "நீண்ட திட்டப் பெயர் (விளக்கம்)", "member_name": "Selvi", "benefit_ta": "மாதம் ₹1,000 " * 5}
    text = routes_admin._sms_text([item] * 10)
    assert len(text) <= 480 and text.startswith(routes_admin.SMS_HEAD) and text.endswith(routes_admin.SMS_TAIL)
    assert "மேலும்" in text and "(விளக்கம்)" not in text
    huge = routes_admin._sms_text([dict(item, benefit_ta="அ" * 2000)])
    assert len(huge) <= 480 and huge.endswith(routes_admin.SMS_TAIL)


def test_reload_updates_in_place():
    before = [id(x) for x in (data.SCHEMES, data.SCHEMES_BY_ID, data.FACT_SCHEMA, data.SCHEMES_FILE)]
    n = data.reload()
    assert [id(x) for x in (data.SCHEMES, data.SCHEMES_BY_ID, data.FACT_SCHEMA, data.SCHEMES_FILE)] == before
    assert n == len(data.SCHEMES) and rules.SCHEMES is data.SCHEMES and rules.SCHEMES_BY_ID is data.SCHEMES_BY_ID
    assert data.SCHEMES_FILE["fact_schema"] is data.FACT_SCHEMA
    assert set(data.SCHEMES_BY_ID) == {s["id"] for s in data.SCHEMES_FILE["schemes"]}
