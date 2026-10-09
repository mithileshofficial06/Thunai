"""Coverage tests (offline, through the HTTP API): every Doctor path, every letter kind,
every demo family, and a smoke check of every route."""
import html as htmllib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import app as appmod  # noqa: E402
import config  # noqa: E402
from engine import letters  # noqa: E402
from engine.data import OFFICES  # noqa: E402

client = TestClient(appmod.app)

HELPER = {"username": "helper", "password": "helper123"}
PERSONAS = ("murugan_family", "revathi_docs", "meena", "lakshmi_paati")
TREE_FILE = json.loads((ROOT / "data" / "doctor_tree.json").read_text(encoding="utf-8"))
TAMIL = re.compile(r"[஀-௿]")


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setattr(config, "USE_LLM", False)


# ------------------------------------------------------------------ helpers
def tree_paths(tree_id):
    """Every walk from the tree's start node to an outcome: [(answers, node_ids)], DFS over yes / no."""
    nodes = TREE_FILE["trees"][tree_id]["nodes"]
    out = []

    def dfs(node_id, answers, seen):
        node = nodes[node_id]
        if node["type"] != "question":
            out.append((tuple(answers), tuple(seen)))
            return
        for a in ("yes", "no"):
            nxt = node[a]
            assert nxt in nodes, f"{tree_id}.{node_id}: '{a}' points to missing node {nxt}"
            assert nxt not in seen, f"{tree_id}: cycle at {node_id} -> {nxt}"
            dfs(nxt, answers + [a], seen + [nxt])

    start = TREE_FILE["trees"][tree_id]["start"]
    dfs(start, [], [start])
    return out


DOCTOR_PATHS = [(e["id"], e["tree"], answers, nodes)
                for e in TREE_FILE["entry_points"] for answers, nodes in tree_paths(e["tree"])]
PATH_IDS = [f"{entry}-{'-'.join(answers)}->{nodes[-1]}" for entry, _, answers, nodes in DOCTOR_PATHS]


def outcome_nodes():
    return {(t, n) for t, tree in TREE_FILE["trees"].items() for n, node in tree["nodes"].items()
            if node["type"] == "outcome"}


def visible_text(page):
    page = re.sub(r"(?is)<(script|style)\b.*?</\1\s*>", " ", page)
    page = re.sub(r"(?s)<!--.*?-->", " ", page)
    page = re.sub(r"(?s)<[^>]+>", " ", page)
    return re.sub(r"\s+", " ", htmllib.unescape(page)).strip()


def letter_bodies(page):
    """(Tamil body, English body) of a letter page, as visible text."""
    letter = page.split('<div class="letter">', 1)[1]
    ta, en = letter.split('<hr class="divider">', 1)
    return visible_text(ta), visible_text(en.split('<div class="footer">', 1)[0])


def new_session():
    r = client.post("/api/session", json={})
    assert r.status_code == 200, r.text
    return r.json()["session_id"]


def load(persona):
    r = client.post(f"/api/demo/{persona}")
    assert r.status_code == 200, r.text
    return r.json()


def plan_tasks(snapshot):
    return {t["task_id"]: o["office_id"] for o in snapshot["plan"] for t in o["tasks"]}


def check_letter_page(draft, where):
    """A fresh draft renders: DRAFT watermark, no Print, a Tamil and an English body, never 'None'."""
    r = client.get(draft["html_url"])
    assert r.status_code == 200, f"{where}: {r.status_code} {r.text[:300]}"
    page = r.text
    assert "DRAFT" in page and 'class="watermark"' in page, where
    assert "window.print" not in page, f"{where}: a draft must not be printable"
    assert "{{" not in page, f"{where}: unfilled template placeholder"
    ta, en = letter_bodies(page)
    assert TAMIL.search(ta), f"{where}: Tamil body has no Tamil text: {ta[:200]}"
    assert re.search(r"[A-Za-z]{4,}", en), f"{where}: English body has no English text: {en[:200]}"
    assert not TAMIL.search(en), f"{where}: Tamil text inside the English body: {en[:300]}"
    title_en, title_ta = letters.KINDS[draft["kind"]]
    text = visible_text(page)
    assert title_en in text and title_ta in text, where
    for label, body in (("page", text), ("ta", ta), ("en", en)):
        hit = re.search(r".{0,60}\bNone\b.{0,60}", body)
        assert hit is None, f"{where}: 'None' printed in the {label} letter text: ...{hit.group(0)}..."
    assert not re.search(r"\d{9,}", text), f"{where}: an ID-like number is printed in the letter"
    return page


def approve_and_check(draft, where):
    a = client.post("/api/helper/approve", json={"draft_id": draft["draft_id"], **HELPER})
    assert a.status_code == 200, f"{where}: {a.text}"
    a = a.json()
    assert a["draft"]["status"] == "APPROVED" and a["draft"]["approved_by"], where
    page = client.get(draft["html_url"])
    assert page.status_code == 200, where
    assert "window.print" in page.text and 'class="watermark"' not in page.text, where
    assert not re.search(r"\bNone\b", visible_text(page.text)), f"{where}: 'None' printed after approval"


def run_doctor_path(entry_id, tree_id, answers, nodes):
    """Walk one path through the API in a new session; check the outcome, its plan task, letter and
    escalation. Returns (outcome node id, set of letter kinds drafted)."""
    where = f"{entry_id} {'/'.join(answers)} -> {nodes[-1]}"
    sid = new_session()
    r = client.post("/api/doctor", json={"session_id": sid, "entry_id": entry_id})
    assert r.status_code == 200, f"{where}: {r.text}"
    r = r.json()
    assert r["step"]["kind"] == "question" and r["step"]["node_id"] == nodes[0] and r["step"]["tree"] == tree_id, where
    assert r["step"]["en"] and r["step"]["ta"], where
    for i, a in enumerate(answers):
        res = client.post("/api/doctor", json={"session_id": sid, "answer": a})
        assert res.status_code == 200, f"{where} (answer {i + 1}): {res.text}"
        r = res.json()
        assert r["step"]["node_id"] == nodes[i + 1], f"{where}: answer {a} went to {r['step']['node_id']}"
        assert r["doctor"] == r["step"], where

    step, node_id = r["step"], nodes[-1]
    node = TREE_FILE["trees"][tree_id]["nodes"][node_id]
    assert step["kind"] == "outcome" and step["node_id"] == node_id and step["tree"] == tree_id, where
    assert step["path"] == list(nodes), where
    for key in ("cause_en", "cause_ta", "verify_en", "verify_ta"):
        assert isinstance(step[key], str) and step[key].strip(), f"{where}: empty {key}"
    for key in ("fix_en", "fix_ta"):
        assert step[key] and all(isinstance(f, str) and f.strip() for f in step[key]), f"{where}: empty {key}"
    assert len(step["fix_en"]) == len(step["fix_ta"]), f"{where}: fix_en and fix_ta differ in length"
    assert not step["fix_en"][0].startswith("First check"), f"{where}: check-first step without a dont_know"
    assert any(e["text_en"] == f"Most likely cause: {step['cause_en']}" for e in r["events"]), where

    # The fix joins the plan at its office.
    if node["office"] in OFFICES:
        tasks = plan_tasks(r["snapshot"])
        assert tasks.get(f"doctor:{node_id}") == node["office"], f"{where}: plan tasks {tasks}"

    # The letter it suggests can be drafted, rendered and approved.
    drafted = set()
    letter = node.get("draft_letter")
    if letter:
        assert letter in letters.KINDS, f"{where}: draft_letter {letter} has no template"
        sug = next((s for s in r["suggested_letters"] if s["kind"] == letter), None)
        assert sug is not None, f"{where}: {letter} not in suggested_letters {r['suggested_letters']}"
        d = client.post("/api/letter", json={"session_id": sid, "kind": letter,
                                             "member_id": sug["member_id"], "doc_id": sug["doc_id"]})
        assert d.status_code == 200, f"{where}: drafting {letter}: {d.status_code} {d.text}"
        draft = d.json()["draft"]
        assert draft["kind"] == letter and draft["status"] == "DRAFT", where
        check_letter_page(draft, f"{where} [{letter}]")
        approve_and_check(draft, f"{where} [{letter}]")
        drafted.add(letter)
    else:
        assert not any(s["reason_en"].startswith("Problem finder result") for s in r["suggested_letters"]), where

    # Escalation to a human helper.
    escalations = [i for i in r["drafts"] if i["kind"] == "escalation"]
    if node.get("escalate_to_helper"):
        assert escalations, f"{where}: no escalation in drafts {r['drafts']}"
        esc = escalations[0]
        assert esc["status"] == "OPEN" and esc["key"] == f"doctor:{node_id}", where
        assert esc["reason_en"] == f"Problem finder: {step['cause_en']}", where
        assert client.get(f"/letter/{esc['draft_id']}").status_code == 404, f"{where}: escalation rendered as a letter"
        rv = client.post("/api/helper/approve", json={"draft_id": esc["draft_id"], **HELPER})
        assert rv.status_code == 200 and rv.json()["draft"]["status"] == "REVIEWED", where
    else:
        assert not escalations, f"{where}: unexpected escalation {escalations}"

    # No open question after an outcome; a new start takes the old fix out of the plan.
    assert client.post("/api/doctor", json={"session_id": sid, "answer": "yes"}).status_code == 400, where
    again = client.post("/api/doctor", json={"session_id": sid, "entry_id": entry_id})
    assert again.status_code == 200, where
    again = again.json()
    assert again["step"]["node_id"] == nodes[0], where
    assert f"doctor:{node_id}" not in plan_tasks(again["snapshot"]), f"{where}: old fix left in the plan"
    return node_id, drafted


def draft_persona_letters(persona):
    """Load a demo family, draft + render + approve every letter it is offered. Returns the kinds drafted."""
    r = load(persona)
    sid, offered = r["session_id"], r["suggested_letters"]
    assert offered, f"{persona}: no letters suggested"
    kinds = set()
    for s in offered:
        where = f"{persona} [{s['kind']} member={s['member_id']} doc={s['doc_id']}]"
        d = client.post("/api/letter", json={"session_id": sid, "kind": s["kind"],
                                             "member_id": s["member_id"], "doc_id": s["doc_id"]})
        assert d.status_code == 200, f"{where}: {d.status_code} {d.text}"
        draft = d.json()["draft"]
        assert (draft["kind"], draft["member_id"], draft["doc_id"]) == (s["kind"], s["member_id"], s["doc_id"]), \
            f"{where}: got the draft for {(draft['kind'], draft['member_id'], draft['doc_id'])}"
        assert draft["status"] == "DRAFT" and draft["html_url"] == f"/letter/{draft['draft_id']}", where
        check_letter_page(draft, where)
        approve_and_check(draft, where)
        kinds.add(s["kind"])
    return kinds


# ------------------------------------------------------------- 1. the Doctor
def test_doctor_entries_match_the_tree_file():
    r = client.get("/api/doctor/entries")
    assert r.status_code == 200
    entries = r.json()["entries"]
    assert [(e["id"], e["tree"]) for e in entries] == [(e["id"], e["tree"]) for e in TREE_FILE["entry_points"]]
    assert all(e["en"] and e["ta"] for e in entries)
    assert {e["tree"] for e in entries} == set(TREE_FILE["trees"]), "a tree has no entry point"


def test_dfs_covers_every_outcome_node():
    leaves = {(tree, nodes[-1]) for _, tree, _, nodes in DOCTOR_PATHS}
    assert leaves == outcome_nodes(), f"unreachable outcomes: {outcome_nodes() - leaves}"


@pytest.mark.parametrize("entry_id,tree_id,answers,nodes", DOCTOR_PATHS, ids=PATH_IDS)
def test_doctor_path(entry_id, tree_id, answers, nodes):
    run_doctor_path(entry_id, tree_id, answers, nodes)


def test_dont_know_follows_no_and_adds_a_check_first_step():
    checked = 0
    for entry in TREE_FILE["entry_points"]:
        tree_id = entry["tree"]
        tree = TREE_FILE["trees"][tree_id]["nodes"]
        prefixes = {}  # question node -> yes/no answers that reach it
        for answers, nodes in tree_paths(tree_id):
            for i, n in enumerate(nodes[:-1]):
                prefixes.setdefault(n, answers[:i])
        for q, prefix in prefixes.items():
            sid = new_session()
            client.post("/api/doctor", json={"session_id": sid, "entry_id": entry["id"]})
            for a in prefix:
                assert client.post("/api/doctor", json={"session_id": sid, "answer": a}).status_code == 200
            r = client.post("/api/doctor", json={"session_id": sid, "answer": "dont_know"})
            assert r.status_code == 200, r.text
            step = r.json()["step"]
            target = tree[tree[q]["no"]]
            assert step["node_id"] == tree[q]["no"], f"{tree_id}.{q}: dont_know went to {step['node_id']}"
            if target["type"] == "outcome":
                assert step["fix_en"][0] == f"First check: {target['verify_en']}", f"{tree_id}.{q}"
                assert step["fix_ta"][0].startswith("முதலில் சரிபார்க்கவும்: "), f"{tree_id}.{q}"
                assert step["fix_en"][1:] == target["fix_en"] and step["fix_ta"][1:] == target["fix_ta"], f"{tree_id}.{q}"
            checked += 1
    assert checked == sum(1 for t in TREE_FILE["trees"].values() for n in t["nodes"].values() if n["type"] == "question")


def test_doctor_rejects_bad_answers():
    sid = new_session()
    assert client.post("/api/doctor", json={"session_id": sid, "answer": "yes"}).status_code == 400  # nothing open
    client.post("/api/doctor", json={"session_id": sid, "entry_id": "kmut_rejected"})
    assert client.post("/api/doctor", json={"session_id": sid, "answer": "maybe"}).status_code == 400
    assert client.post("/api/doctor", json={"session_id": sid}).status_code == 400
    assert client.post("/api/doctor", json={"session_id": "nosuchsession", "entry_id": "kmut_rejected"}).status_code == 404


# ---------------------------------------------------------- 2. letter kinds
@pytest.mark.parametrize("persona", PERSONAS)
def test_persona_letters_draft_render_and_approve(persona):
    assert draft_persona_letters(persona)


def test_every_outcome_and_every_letter_kind_is_reached():
    reached, kinds = set(), set()
    for entry_id, tree_id, answers, nodes in DOCTOR_PATHS:
        node_id, drafted = run_doctor_path(entry_id, tree_id, answers, nodes)
        reached.add((tree_id, node_id))
        kinds |= drafted
    for p in PERSONAS:
        kinds |= draft_persona_letters(p)
    assert reached == outcome_nodes()
    assert kinds == set(letters.KINDS), f"never drafted: {set(letters.KINDS) - kinds}"


# --------------------------------------------------- 3. personas + chat
@pytest.mark.parametrize("persona", PERSONAS + ("fresh",))
def test_persona_loads_and_offline_chat_always_replies(persona):
    if persona == "fresh":
        r = client.post("/api/session", json={}).json()
    else:
        r = load(persona)
        snap = r["snapshot"]
        assert snap and snap["verdicts"] and snap["plan"] and snap["plan_steps"], f"{persona}: empty snapshot"
        assert r["reply"]["en"].strip() and r["reply"]["ta"].strip(), f"{persona}: empty reply on load"
    sid = r["session_id"]

    def say(text, lang):
        c = client.post("/api/chat", json={"session_id": sid, "text": text, "lang": lang})
        assert c.status_code == 200, c.text
        c = c.json()
        assert c["reply"]["en"].strip() and c["reply"]["ta"].strip(), f"{persona}: empty reply to {text!r}: {c['reply']}"
        assert c["snapshot"], persona
        return c

    for text, lang in (("We are four people in the family and we live in Madurai.", "en"),
                       ("எங்கள் குடும்பத்தில் நான்கு பேர் இருக்கிறோம்.", "ta")):
        say(text, lang)
        say(text, lang)  # the same message again: nothing changes, still an answer
    aadhaar = "My Aadhaar number is 2345 6789 0123"
    c = say(aadhaar, "en")
    assert any(e["type"] == "privacy" for e in c["events"]), f"{persona}: no privacy event"
    assert "2345 6789 0123" not in json.dumps(c, ensure_ascii=False), f"{persona}: Aadhaar number echoed back"


# ------------------------------------------------------- 4. route smoke
def test_route_smoke():
    h = client.get("/api/health")
    assert h.status_code == 200 and h.json()["status"] == "ok" and h.json()["use_llm"] is False

    cards = client.get("/api/sample_docs/revathi_docs")
    assert cards.status_code == 200
    cards = cards.json()["cards"]
    assert len(cards) == 4 and all(c["sample"] and c["doc_en"] and c["doc_ta"] for c in cards)

    r = load("murugan_family")
    sid = r["session_id"]
    sim = client.post("/api/simulate", json={"session_id": sid, "days": 15})
    assert sim.status_code == 200
    events = sim.json()["events"]
    assert events and all(e["type"] == "autonomous" for e in events)

    for lang in ("en", "ta"):
        sms = client.post("/api/sms/summary", json={"session_id": sid, "lang": lang})
        assert sms.status_code == 200, sms.text
        assert sms.json()["message"]["status"] == "outbox" and sms.json()["message"]["text"]
    out = client.get("/api/outbox", params={"session_id": sid})
    assert out.status_code == 200 and out.json()["messages"]
    assert client.get("/api/outbox").status_code == 200
    assert client.get("/api/helper/queue").status_code == 200

    assert client.post("/api/tts", json={"text": ""}).status_code == 400
    assert client.post("/api/demo/nobody").status_code == 404
    assert client.get("/api/sample_docs/nobody").status_code == 404
    assert client.post("/api/doctor", json={"session_id": sid, "entry_id": "no_such_entry"}).status_code == 400
    assert client.post("/api/letter", json={"session_id": sid, "kind": "no_such_kind"}).status_code == 400
    assert client.get("/letter/unknown").status_code == 404
    assert client.post("/api/chat", json={"session_id": sid, "text": "   "}).status_code == 400
    assert client.post("/api/chat", json={"session_id": "nosuchsession", "text": "hi"}).status_code == 404

    did = client.post("/api/letter", json={"session_id": sid, "kind": "application_pack"}).json()["draft"]["draft_id"]
    assert client.post("/api/helper/approve", json={"draft_id": did}).status_code == 401
    assert client.post("/api/helper/approve", json={"draft_id": did, "username": "helper", "password": "x"}).status_code == 401
    assert client.post("/api/helper/approve", json={"draft_id": "nosuchdraft", **HELPER}).status_code == 404
