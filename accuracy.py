"""Accuracy layer: decides which AI-extracted facts are safe to apply.

Checks (docs/03_ARCHITECTURE.md §6.2a): path normalisation · allowed paths/actions · evidence quote ·
type/range · number cross-check · two-model agreement. Anything doubtful becomes a clarifying question.
"""
import re

import amounts
from engine.facts import patch

ALLOWED_ACTIONS = ["update_facts", "start_doctor", "doctor_answer", "mark_task_done",
                   "prepare_application", "draft_appeal", "escalate_to_helper", "explain"]
DOCTOR_ENTRIES = {"kmut_payment_stopped", "kmut_rejected", "pmkisan_stopped", "pension_rejected"}
RANGES = {"age": (0, 110), "annual_income": (0, 10_000_000), "wet_land_acres": (0, 100),
          "dry_land_acres": (0, 100), "electricity_units_per_year": (0, 20_000), "immovable_property_value": (0, 100_000_000)}
LABELS = {
    "annual_income": ("the yearly family income", "ஆண்டு குடும்ப வருமானம்"),
    "electricity_units_per_year": ("electricity units per year", "ஆண்டு மின் யூனிட்"),
    "age": ("the age", "வயது"),
    "wet_land_acres": ("wet land (acres)", "நன்செய் நிலம் (ஏக்கர்)"),
    "dry_land_acres": ("dry land (acres)", "புன்செய் நிலம் (ஏக்கர்)"),
}


def normalise_path(path):
    path = (path or "").strip()
    path = re.sub(r"^family:", "family.", path)
    path = re.sub(r"^(member:[a-z]+\d+):", r"\1.", path)
    return path


def _norm_value(v):
    if isinstance(v, str):
        return v.strip().lower()
    if isinstance(v, float) and v.is_integer():
        return int(v)
    return v


def _field(path):
    return path.rsplit(".", 1)[-1]


def _valid_fact(facts, path, value, text):
    """Return (ok, coerced_value, reason)."""
    try:
        _, _, coerced = patch(facts, path, value)
    except ValueError as exc:
        return False, None, str(exc)
    field = _field(path)
    if field in RANGES and isinstance(coerced, (int, float)):
        lo, hi = RANGES[field]
        if not lo <= coerced <= hi:
            return False, None, f"{field} out of range"
    if field == "annual_income" and isinstance(coerced, (int, float)):
        cands = amounts.annual_income_candidates(text)
        if cands and coerced not in cands:
            return False, coerced, f"income {coerced} not found in the message ({sorted(cands)})"
    if field == "electricity_units_per_year" and isinstance(coerced, (int, float)):
        cands = amounts.electricity_candidates(text)
        if cands and coerced not in cands:
            return False, coerced, f"units {coerced} not found in the message ({sorted(cands)})"
    return True, coerced, ""


def _facts_by_path(result, facts, text):
    """Valid facts from one model: {path: (value, evidence_ok)}, plus a list of rejections."""
    good, rejected = {}, []
    lowered = text.lower()
    for f in result.get("facts") or []:
        if not isinstance(f, dict):
            continue
        path = normalise_path(f.get("path"))
        evidence = (f.get("evidence") or "").strip()
        if not evidence or evidence.lower() not in lowered:
            rejected.append((path, "no evidence in the message"))
            continue
        ok, value, why = _valid_fact(facts, path, f.get("value"), text)
        if not ok:
            rejected.append((path, why))
            continue
        good[path] = value
    return good, rejected


def check(result_bundle, facts, text, from_voice=False):
    """Combine the model outputs into a decision.

    Returns dict: accepted {path: value}, unconfirmed {path: value}, ask [questions], actions,
    doctor_entry, doctor_answer, task_done, escalate_reason, ack, language, reason, summary, providers.
    """
    results = [r for r in result_bundle["results"]]
    primary = results[0]["data"]
    per_model = [_facts_by_path(r["data"], facts, text) for r in results]

    accepted, unconfirmed, ask = {}, {}, []
    rejected = [rej for _, rejs in per_model for rej in rejs]
    paths = []
    for good, _ in per_model:
        for p in good:
            if p not in paths:
                paths.append(p)
    two = len(per_model) >= 2
    for p in paths:
        vals = [good[p] for good, _ in per_model if p in good]
        distinct = {repr(_norm_value(v)) for v in vals}
        if _field(p) == "name":
            # Names never decide eligibility; keep the English spelling (needed to expand initials).
            latin = [v for v in vals if isinstance(v, str) and v.isascii()]
            accepted[p] = latin[0] if latin else vals[0]
            continue
        if len(distinct) > 1:
            ask.append(_clarify(p, vals))
        elif two and len(vals) == len(per_model):
            accepted[p] = vals[0]
        else:
            unconfirmed[p] = vals[0]  # only one model gave it: applied but shown "please confirm"

    if from_voice:  # numbers heard by speech recognition always need a tap to confirm
        for p in [p for p in accepted if isinstance(accepted[p], (int, float)) and not isinstance(accepted[p], bool)]:
            unconfirmed[p] = accepted.pop(p)

    actions = []
    for r in results:
        for a in r["data"].get("actions") or []:
            if a in ALLOWED_ACTIONS and a not in actions:
                actions.append(a)
    actions = actions[:4]
    if (accepted or unconfirmed) and "update_facts" not in actions:
        actions.insert(0, "update_facts")

    def first(key, allowed=None):
        for r in results:
            v = r["data"].get(key)
            if v and (allowed is None or v in allowed):
                return v
        return None

    agree_note = "2 models agreed" if two else "1 model (please confirm)"
    summary = f"{agree_note}; evidence and numbers verified" if not rejected else f"{agree_note}; {len(rejected)} item(s) dropped by checks"
    return {
        "accepted": accepted, "unconfirmed": unconfirmed, "ask": ask, "rejected": rejected,
        "actions": actions,
        "doctor_entry": first("doctor_entry", DOCTOR_ENTRIES),
        "doctor_answer": first("doctor_answer", {"yes", "no", "dont_know"}),
        "task_done": first("task_done"),
        "escalate_reason": first("escalate_reason"),
        "ack": primary.get("ack") or "",
        "language": primary.get("language") if primary.get("language") in ("ta", "en") else "ta",
        "reason": primary.get("reason") or "",
        "summary": summary,
        "providers": [f"{r['provider']} · {r['ms']} ms" for r in results],
    }


def _clarify(path, values):
    field = _field(path)
    en_label, ta_label = LABELS.get(field, (field.replace("_", " "), field.replace("_", " ")))
    shown = []
    for v in values:
        s = f"₹{v:,}" if field == "annual_income" and isinstance(v, (int, float)) else str(v)
        if s not in shown:
            shown.append(s)
    return {"path": path, "options": list(dict.fromkeys(values)),
            "en": f"Please confirm {en_label}: {' or '.join(shown)}?",
            "ta": f"{ta_label} — {' அல்லது '.join(shown)}? உறுதிப்படுத்தவும்."}
