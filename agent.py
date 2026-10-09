"""Thunai agent: perceive → decide → act → observe → re-plan → respond.

One AI call per turn (llm.py, two models in parallel), checked by accuracy.py.
Every step is returned as an event for the agent panel (shape: docs/06_CONTRACTS.md §2).
"""
import copy
import uuid

import accuracy
import config
import llm
import pii_guard
from engine import diff, recompute
from engine import doctor as doctor_engine
from engine.data import PERSONAS
from engine.documents import task_effect
from engine.facts import empty_facts, patch

SESSIONS = {}


# ------------------------------------------------------------------ helpers
def ev(type_, icon, en, ta=None, **detail):
    return {"type": type_, "icon": icon, "text_en": en, "text_ta": ta or en, "detail": detail}


def new_session(saved_facts=None):
    sid = uuid.uuid4().hex[:12]
    facts = copy.deepcopy(saved_facts) if saved_facts else empty_facts()
    facts.setdefault("tasks", {})
    snap = recompute(facts)
    session = {"id": sid, "facts": facts, "snapshot": snap, "last_question": snap["next_question"],
               "doctor": None, "helper_queue": [], "unconfirmed": [], "pending_ask": []}
    SESSIONS[sid] = session
    return session, goal_events(session)


def goal_events(session):
    head = next((m.get("name") for m in session["facts"]["members"] if m.get("relation") == "self"), None)
    who_en = f"the {head} family" if head else "this family"
    who_ta = f"{head} குடும்பத்திற்கு" if head else "இந்தக் குடும்பத்திற்கு"
    steps = " → ".join(s["en"] for s in session["snapshot"]["plan_steps"])
    steps_ta = " → ".join(s["ta"] for s in session["snapshot"]["plan_steps"])
    return [ev("goal", "", f"Goal: get {who_en} every benefit they are owed, with the fewest trips",
               f"இலக்கு: {who_ta} உரிய அனைத்து நலன்களையும் குறைந்த பயணங்களில் பெற்றுத் தருதல்"),
            ev("plan", "", f"Plan: {steps}", f"திட்டம்: {steps_ta}")]


def compact_card(facts):
    members = [{k: v for k, v in m.items() if k not in ("names_as_printed",)} for m in facts["members"]]
    return {"family": facts["family"], "members": members}


def open_tasks(snapshot):
    return [{"task_id": t["task_id"], "label": t["en"]} for o in snapshot["plan"] for t in o["tasks"] if not t["done"]]


def check_events(snap):
    out = []
    verdicts = snap["verdicts"]
    word = {"ELIGIBLE": ("eligible", "தகுதி"), "NEED_INFO": ("needs information", "தகவல் தேவை"),
            "NOT_ELIGIBLE": ("not eligible", "தகுதி இல்லை")}
    if verdicts:
        en = "; ".join(f"{v['name_en'].split(' (')[0]}{' (' + v['member_name'] + ')' if v['member_name'] else ''}: {word[v['status']][0]}" for v in verdicts)
        ta = "; ".join(f"{v['name_ta'].split(' (')[0]}{' (' + v['member_name'] + ')' if v['member_name'] else ''}: {word[v['status']][1]}" for v in verdicts)
        out.append(ev("tool", "", f"Checked eligibility: {en}", f"தகுதி சரிபார்க்கப்பட்டது: {ta}"))
    if snap["missing_documents"] or snap["matrix"]:
        n_missing = len(snap["missing_documents"])
        risky = [m["member_name"] for m in snap["matrix"] if m["level"] != "GREEN"]
        en = f"Checked documents: {n_missing} missing" + (f"; name mismatch risk for {', '.join(risky)}" if risky else "; names consistent")
        ta = f"ஆவணங்கள் சரிபார்க்கப்பட்டன: {n_missing} இல்லை" + (f"; பெயர் வேறுபாடு அபாயம்: {', '.join(risky)}" if risky else "; பெயர்கள் பொருந்துகின்றன")
        out.append(ev("tool", "", en, ta))
    if snap["plan"]:
        route_en = " > ".join(o["office_en"] for o in snap["plan"])
        route_ta = " > ".join(o["office_ta"] for o in snap["plan"])
        t = snap["trips"]
        out.append(ev("tool", "", f"Planned fixes: {route_en}. Office visits {t['without']} to {t['with']}",
                      f"திட்டமிடப்பட்டது: {route_ta}. அலுவலகப் பயணங்கள் {t['without']} இலிருந்து {t['with']}"))
    return out


def _reply_lines(old, new, events, extra_en=None, extra_ta=None):
    en, ta = [], []
    ov = {v["key"]: v for v in (old or {}).get("verdicts", [])}
    for v in new["verdicts"]:
        before = ov.get(v["key"], {}).get("status")
        if v["status"] == before:
            continue
        who = f" ({v['member_name']})" if v["member_name"] else ""
        if v["status"] == "ELIGIBLE":
            en.append(f"Eligible: {v['name_en'].split(' (')[0]}{who}, {v['benefit_en']}")
            ta.append(f"தகுதி உண்டு: {v['name_ta'].split(' (')[0]}{who}, {v['benefit_ta']}")
        elif v["status"] == "NOT_ELIGIBLE" and before:
            failed = next((r for r in v["reasons"] if r["ok"] is False), None)
            en.append(f"Not eligible: {v['name_en'].split(' (')[0]}{who}" + (f" ({failed['en']})" if failed else ""))
            ta.append(f"தகுதி இல்லை: {v['name_ta'].split(' (')[0]}{who}" + (f" ({failed['ta']})" if failed else ""))
    if (old or {}).get("rupees_per_year", 0) != new["rupees_per_year"] and new["rupees_per_year"]:
        en.append(f"Estimated benefit: about ₹{new['rupees_per_year']:,} per year")
        ta.append(f"மதிப்பிடப்பட்ட நன்மை: ஆண்டுக்கு சுமார் ₹{new['rupees_per_year']:,}")
    if (old or {}).get("trips") != new["trips"] and new["trips"]["without"]:
        en.append(f"Office visits needed: {new['trips']['with']} (instead of {new['trips']['without']})")
        ta.append(f"தேவையான அலுவலகப் பயணங்கள்: {new['trips']['with']} ({new['trips']['without']} க்குப் பதிலாக)")
    if extra_en:
        en.extend(extra_en)
        ta.extend(extra_ta)
    return en, ta


def _apply_snapshot(session):
    old = session["snapshot"]
    new = recompute(session["facts"], packs_ready=any(d.get("kind") == "application_pack" for d in session["helper_queue"]))
    session["snapshot"] = new
    session["last_question"] = new["next_question"]
    return old, new


# ------------------------------------------------------------------- a turn
def handle(session, text, lang="ta", from_voice=False):
    events = []
    cleaned, removed = pii_guard.clean(text)
    if removed:
        events.append(ev("privacy", "", f"Privacy: removed {removed} number(s) before sending to the AI",
                         f"தனியுரிமை: AI-க்கு அனுப்பும் முன் {removed} எண் நீக்கப்பட்டது"))

    lq = session["last_question"]
    diag = session["doctor"]
    bundle = llm.understand(cleaned, compact_card(session["facts"]), lq["en"] if lq else None,
                            open_tasks(session["snapshot"]),
                            f"{diag['entry_id']}: {diag['step'].get('en', '')}" if diag and diag["step"]["kind"] == "question" else None)

    if bundle is None:
        events.append(ev("fallback", "", "Offline mode: AI service unavailable. Continuing with direct questions.",
                         "இணையமில்லா முறை: கேள்விகளை நேரடியாகத் தொடர்கிறேன்."))
        q = session["last_question"]
        reply = {"en": f"Next: {q['en']}" if q else "Please update the family card directly.",
                 "ta": f"அடுத்து: {q['ta']}" if q else "குடும்ப அட்டையை நேரடியாகத் திருத்தவும்."}
        return events, session["snapshot"], reply

    dec = accuracy.check(bundle, session["facts"], cleaned, from_voice=from_voice)
    providers = "cached" if bundle.get("cached") else " + ".join(dec["providers"])
    events.append(ev("decided", "", f"Decision: {', '.join(dec['actions']) or 'reply only'}. {dec['reason']}",
                     f"முடிவு: {', '.join(dec['actions']) or 'பதில் மட்டும்'}",
                     provider=providers, checks=dec["summary"],
                     errors=[f"{e['provider']}: {e['error'][:80]}" for e in bundle.get("errors", [])]))
    for path, why in dec["rejected"][:3]:
        events.append(ev("tool", "", f"accuracy check: ignored {path} ({why})", f"துல்லியச் சரிபார்ப்பு: {path} தவிர்க்கப்பட்டது"))

    extra_en, extra_ta = [], []
    old_snapshot = session["snapshot"]
    changed = False

    for action in dec["actions"]:
        if action == "update_facts":
            lines = []
            for path, value in list(dec["accepted"].items()) + list(dec["unconfirmed"].items()):
                try:
                    session["facts"], old_v, new_v = patch(session["facts"], path, value)
                except ValueError as exc:
                    lines.append(f"{path}: rejected ({exc})")
                    continue
                if old_v != new_v:
                    lines.append(f"{path.split('.', 1)[-1].replace('_', ' ')}: {new_v}")
                    changed = True
                if path in dec["unconfirmed"] and path not in session["unconfirmed"]:
                    session["unconfirmed"].append(path)
                elif path in dec["accepted"] and path in session["unconfirmed"]:
                    session["unconfirmed"].remove(path)
            if lines:
                events.append(ev("tool", "", "Updated facts: " + "; ".join(lines[:6]) + (" and more" if len(lines) > 6 else "")))
        elif action == "start_doctor" and dec["doctor_entry"]:
            step = doctor_engine.start(dec["doctor_entry"])
            session["doctor"] = {"entry_id": dec["doctor_entry"], "tree": step["tree"], "path": step["path"], "step": step}
            events.append(ev("tool", "", f"run_doctor  {dec['doctor_entry']}", f"run_doctor  {dec['doctor_entry']}"))
            extra_en.append(step["en"]); extra_ta.append(step["ta"])
        elif action == "doctor_answer" and session["doctor"] and dec["doctor_answer"]:
            d = session["doctor"]
            step = doctor_engine.answer(d["tree"], d["path"], dec["doctor_answer"])
            d.update(path=step["path"], step=step)
            events.append(ev("tool", "", f"doctor_step  answer: {dec['doctor_answer']} → {step['node_id']}"))
            e2, t2 = doctor_reply(step)
            extra_en += e2; extra_ta += t2
        elif action == "mark_task_done" and dec["task_done"]:
            changed |= mark_task(session, dec["task_done"], events)
        elif action == "escalate_to_helper":
            reason = dec["escalate_reason"] or "Needs a human helper"
            session["helper_queue"].append({"draft_id": uuid.uuid4().hex[:6], "kind": "escalation", "member_name": None,
                                            "status": "OPEN", "reason": reason})
            events.append(ev("tool", "", f"escalate_to_helper  {reason}", f"உதவியாளரிடம் அனுப்பப்பட்டது: {reason}"))
        elif action == "explain":
            for v in session["snapshot"]["verdicts"]:
                if v["status"] != "ELIGIBLE":
                    r = next((r for r in v["reasons"] if r["ok"] is not True), None)
                    if r:
                        extra_en.append(f"{v['name_en']}: {r['en']}")
                        extra_ta.append(f"{v['name_ta']}: {r['ta']}")
        elif action in ("prepare_application", "draft_appeal"):
            events.append(ev("tool", "", f"{action}  → open the Letters tab to create the draft",
                             f"{action}  → கடிதங்கள் பகுதியில் வரைவு தயாரிக்கவும்"))

    for q in dec["ask"]:
        extra_en.append(q["en"]); extra_ta.append(q["ta"])
    session["pending_ask"] = dec["ask"]

    old, new = _apply_snapshot(session)
    if changed:
        events += check_events(new)
        events += diff(old_snapshot, new)

    en, ta = _reply_lines(old_snapshot, new, events, extra_en, extra_ta)
    nq = new["next_question"]
    if nq and not dec["ask"] and not (session["doctor"] and session["doctor"]["step"]["kind"] == "question"):
        en.append(f"Next: {nq['en']}"); ta.append(f"அடுத்து: {nq['ta']}")
    ack = dec["ack"]
    reply = {"en": "\n".join(([ack] if ack and dec["language"] == "en" else []) + en),
             "ta": "\n".join(([ack] if ack and dec["language"] == "ta" else []) + ta)}
    return events, new, reply


def doctor_reply(step):
    if step["kind"] == "question":
        return [step["en"]], [step["ta"]]
    en = [f"Most likely cause: {step['cause_en']}", f"Check: {step['verify_en']}"] + [f"• {f}" for f in step["fix_en"]]
    ta = [f"பெரும்பாலும் காரணம்: {step['cause_ta']}", f"சரிபார்க்க: {step['verify_ta']}"] + [f"• {f}" for f in step["fix_ta"]]
    return en, ta


def mark_task(session, task_id, events):
    known = {t["task_id"] for o in session["snapshot"]["plan"] for t in o["tasks"]}
    if task_id not in known:
        events.append(ev("tool", "", f"mark_task_done  ignored unknown task {task_id}"))
        return False
    for path, value in task_effect(task_id):
        session["facts"], _, _ = patch(session["facts"], path, value)
    session["facts"], _, _ = patch(session["facts"], f"task:{task_id}.done", True)
    events.append(ev("tool", "", f"mark_task_done  {task_id}", f"பணி முடிந்தது: {task_id}"))
    return True


# ------------------------------------------------------- direct (no-AI) edits
def edit_fact(session, path, value):
    session["facts"], old_v, new_v = patch(session["facts"], path, value)
    if path in session["unconfirmed"]:
        session["unconfirmed"].remove(path)
    if old_v == new_v:  # nothing changed (e.g. a confirmation tap): no re-plan noise
        return [ev("tool", "", f"confirmed {path}: {new_v}", f"உறுதி செய்யப்பட்டது: {path}: {new_v}")], session["snapshot"]
    events = [ev("tool", "", f"Updated on the family card: {path.split('.')[-1].replace('_', ' ')} {old_v if old_v is not None else '(empty)'} to {new_v}",
                 f"குடும்ப அட்டையில் திருத்தம்: {path.split('.')[-1].replace('_', ' ')} {old_v if old_v is not None else '(காலி)'} இலிருந்து {new_v}")]
    old, new = _apply_snapshot(session)
    events += check_events(new) + diff(old, new)
    return events, new


def set_task(session, task_id, done):
    events = []
    if done:
        mark_task(session, task_id, events)
    else:
        session["facts"], _, _ = patch(session["facts"], f"task:{task_id}.done", False)
    old, new = _apply_snapshot(session)
    events += diff(old, new)
    return events, new


# ----------------------------------------------------------------- personas
def load_persona(session, name, direct=False):
    p = PERSONAS[name]
    events, reply = [], {"en": "", "ta": ""}
    if "facts" in p and (direct or not config.USE_LLM or "scripted_answers_ta" not in p):
        session["facts"] = copy.deepcopy(p["facts"])
        session["facts"].setdefault("tasks", {})
        session["unconfirmed"] = []
        events.append(ev("tool", "", f"Loaded demo family: {p['label_en']}", f"குடும்பம் ஏற்றப்பட்டது: {p['label_ta']}"))
        old, new = _apply_snapshot(session)
        events += check_events(new) + diff(old, new)
        en, ta = _reply_lines(old, new, events)
        reply = {"en": "\n".join(en), "ta": "\n".join(ta)}
    elif "scripted_answers_ta" in p:
        for line in p["scripted_answers_ta"]:
            e, _, reply = handle(session, line, "ta")
            events.append(ev("reply", "", f"User: {line}", f"பயனர்: {line}"))
            events += e
    if p.get("doctor_entry"):
        step = doctor_engine.start(p["doctor_entry"])
        session["doctor"] = {"entry_id": p["doctor_entry"], "tree": step["tree"], "path": step["path"], "step": step}
        events.append(ev("tool", "", f"run_doctor  {p['doctor_entry']}"))
        for node, ans in p.get("scripted_answers", {}).items():
            d = session["doctor"]
            if d["step"]["kind"] != "question" or d["step"]["node_id"] != node:
                break
            step = doctor_engine.answer(d["tree"], d["path"], ans)
            d.update(path=step["path"], step=step)
            events.append(ev("tool", "", f"doctor_step  {node}: {ans} → {step['node_id']}"))
        en, ta = doctor_reply(session["doctor"]["step"])
        reply = {"en": "\n".join(([reply["en"]] if reply["en"] else []) + en),
                 "ta": "\n".join(([reply["ta"]] if reply["ta"] else []) + ta)}
    return events, session["snapshot"], reply
