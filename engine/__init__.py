"""Thunai engine: recompute(facts) -> snapshot, diff(old, new) -> re-plan events.

Pure, deterministic Python over the researched rules in data/. No AI here.
"""
from engine.documents import analyse
from engine.facts import derive, empty_facts
from engine.questions import next_question
from engine.rules import evaluate, rupees_per_year

PLAN_STEPS = [
    ("learn", "Learn the family", "குடும்பத்தை அறிதல்"),
    ("schemes", "Check schemes", "திட்டங்களைச் சரிபார்த்தல்"),
    ("documents", "Check documents", "ஆவணங்களைச் சரிபார்த்தல்"),
    ("trips", "Plan the fewest trips", "குறைந்த பயணத் திட்டம்"),
    ("packs", "Prepare the application packs", "விண்ணப்பத் தொகுப்புகள் தயாரித்தல்"),
]


def recompute(facts, packs_ready=False):
    """Full snapshot for the UI (shape: docs/06_CONTRACTS.md §3)."""
    facts = facts or empty_facts()
    facts.setdefault("tasks", {})
    derived = derive(facts)
    verdicts = evaluate(derived)
    fix = analyse(derived, verdicts)
    question = next_question(derived, verdicts)

    learned = bool(derived["members"]) and derived["family"].get("annual_income") is not None
    checked = learned and bool(verdicts) and not any(v["status"] == "NEED_INFO" for v in verdicts)
    done = {
        "learn": learned,
        "schemes": checked,
        "documents": checked and question is None,
        "trips": checked and question is None and bool(fix["plan"]),
        "packs": packs_ready,
    }
    return {
        "facts": facts,
        "plan_steps": [{"id": i, "en": en, "ta": ta, "done": done[i]} for i, en, ta in PLAN_STEPS],
        "verdicts": verdicts,
        "rupees_per_year": rupees_per_year(verdicts),
        "matrix": fix["matrix"],
        "missing_documents": fix["missing_documents"],
        "plan": fix["plan"],
        "trips": fix["trips"],
        "next_question": question,
    }


STATUS_TEXT = {"ELIGIBLE": ("✅ eligible", "✅ தகுதி"), "NEED_INFO": ("❓ need info", "❓ தகவல் தேவை"),
               "NOT_ELIGIBLE": ("❌ not eligible", "❌ தகுதி இல்லை"), None: ("—", "—")}


def _event(en, ta, **detail):
    return {"type": "replan", "icon": "🔁", "text_en": en, "text_ta": ta, "detail": detail}


def diff(old, new):
    """Re-plan events describing what changed between two snapshots."""
    events = []
    old = old or {"verdicts": [], "rupees_per_year": 0, "plan": [], "trips": {"without": 0, "with": 0}}
    ov = {v["key"]: v for v in old["verdicts"]}
    nv = {v["key"]: v for v in new["verdicts"]}
    for key in list(nv) + [k for k in ov if k not in nv]:
        a, b = ov.get(key), nv.get(key)
        sa, sb = (a or {}).get("status"), (b or {}).get("status")
        if sa == sb:
            continue
        v = b or a
        who = f" ({v['member_name']})" if v.get("member_name") else ""
        failed = [r for r in (b or {}).get("reasons", []) if r["ok"] is False]
        why_en = f" — \"{failed[0]['en']}\" not met" if sb == "NOT_ELIGIBLE" and failed else ""
        why_ta = f" — \"{failed[0]['ta']}\" பொருந்தவில்லை" if sb == "NOT_ELIGIBLE" and failed else ""
        events.append(_event(
            f"{v['name_en']}{who}: {STATUS_TEXT[sa][0]} → {STATUS_TEXT[sb][0]}{why_en}",
            f"{v['name_ta']}{who}: {STATUS_TEXT[sa][1]} → {STATUS_TEXT[sb][1]}{why_ta}",
            scheme_id=v["scheme_id"], old=sa, new=sb))
    if old["rupees_per_year"] != new["rupees_per_year"]:
        events.append(_event(f"₹{old['rupees_per_year']:,} → ₹{new['rupees_per_year']:,} per year",
                             f"₹{old['rupees_per_year']:,} → ₹{new['rupees_per_year']:,} / ஆண்டு",
                             old=old["rupees_per_year"], new=new["rupees_per_year"]))

    def task_map(snap):
        return {t["task_id"]: t for o in snap["plan"] for t in o["tasks"]}

    ot, nt = task_map(old), task_map(new)
    if not ot and nt:  # first plan: one summary line instead of one line per task
        events.append(_event(f"Plan created: {len(nt)} tasks across {len(new['plan'])} places",
                             f"திட்டம் உருவானது: {len(new['plan'])} இடங்களில் {len(nt)} பணிகள்", tasks=len(nt)))
        nt_new = set()
    else:
        nt_new = nt.keys() - ot.keys()
    for tid in nt_new:
        t = nt[tid]
        events.append(_event(f"New task: {t['member_name']} — {t['en']}", f"புதிய பணி: {t['member_name']} — {t['ta']}", task_id=tid))
    for tid in ot.keys() - nt.keys():
        t = ot[tid]
        events.append(_event(f"Task removed: {t['member_name']} — {t['en']}", f"பணி நீக்கப்பட்டது: {t['member_name']} — {t['ta']}", task_id=tid))
    for tid in nt.keys() & ot.keys():
        if nt[tid]["done"] and not ot[tid]["done"]:
            t = nt[tid]
            events.append(_event(f"Done ✓ {t['member_name']} — {t['en']}", f"முடிந்தது ✓ {t['member_name']} — {t['ta']}", task_id=tid))
    if old["trips"] != new["trips"] and (new["trips"]["without"] or old["trips"]["without"]):
        events.append(_event(f"Office trips: {new['trips']['without']} → {new['trips']['with']}",
                             f"அலுவலகப் பயணங்கள்: {new['trips']['without']} → {new['trips']['with']}",
                             old=old["trips"], new=new["trips"]))
    return events
