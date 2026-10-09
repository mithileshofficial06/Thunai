"""Fix layer: missing documents, name consistency, fix plan by office, trips saved."""
import difflib
import re

from engine.data import DOCUMENTS, DOCUMENTS_FILE, OFFICES, SCHEMES_BY_ID, TASKS

CHECK_OFFICE = {"en": "Check in 1 minute (on your phone)", "ta": "1 நிமிடத்தில் சரிபார்க்கவும் (கைபேசியில்)", "trip": False}
BANK_DOCS = ("bank_account_aadhaar_seeded", "student_bank_account_aadhaar_seeded")
LEVEL_ORDER = {"GREEN": 0, "YELLOW": 1, "RED": 2}
NAME_LEVEL_TEXT = DOCUMENTS_FILE["name_check"]["levels"]


def office_info(office_id):
    if office_id == "check":
        return CHECK_OFFICE
    return OFFICES[office_id]


def is_trip(office_id):
    return bool(office_info(office_id).get("trip"))


# ---------------------------------------------------------------- has-document
def has_doc(doc, family, member):
    """True / False / None (unknown), per documents.json doc_fact_map."""
    docs = (member or {}).get("docs") or {}
    if doc == "ration_card":
        return family.get("has_ration_card")
    if doc == "patta_land_record":
        parts = [family.get("land_in_own_name"), docs.get("patta_land_record")]
        if False in parts:
            return False
        return None if None in parts else True
    if doc in BANK_DOCS:
        parts = [(member or {}).get("has_own_bank_account"), (member or {}).get("bank_aadhaar_seeded"),
                 (member or {}).get("bank_account_active")]
        if False in parts:
            return False
        return None if None in parts else True
    return docs.get(doc)


# ------------------------------------------------------------------ name check
def _tokens(name):
    return [t for t in re.sub(r"[.,\-]", " ", name.upper()).split() if t]


def _phonetic(token):
    for a, b in (("KSH", "X"), ("TH", "T"), ("DH", "D"), ("SH", "S"), ("PH", "F"), ("W", "V"), ("EE", "I"), ("OO", "U")):
        token = token.replace(a, b)
    return re.sub(r"(.)\1+", r"\1", token)


def name_check(a, b, relative_name=None):
    """GREEN / YELLOW / RED for two printed names of the same person."""
    ta, tb = _tokens(a), _tokens(b)
    if sorted(ta) == sorted(tb):
        return "GREEN"
    if relative_name:
        rel = relative_name.upper()

        def expand(tokens):
            return sorted(rel if len(t) == 1 and rel.startswith(t) else t for t in tokens)

        if expand(ta) == expand(tb):
            return "YELLOW"
    pa, pb = sorted(map(_phonetic, ta)), sorted(map(_phonetic, tb))
    if pa == pb or "".join(pa) == "".join(pb) or "".join(map(_phonetic, ta)) == "".join(map(_phonetic, tb)):
        return "YELLOW"
    ratio = difflib.SequenceMatcher(None, "".join(pa), "".join(pb)).ratio()
    return "YELLOW" if ratio >= 0.85 else "RED"


def relative_name(member, members):
    """Father's name for a child, husband's / spouse's name otherwise (used to expand initials)."""
    if member.get("relation") in ("daughter", "son"):
        father = next((x for x in members if x.get("gender") == "male" and x.get("relation") in ("self", "spouse")), None)
        return father.get("name") if father else None
    spouse = next((x for x in members if x["id"] == member.get("spouse_of")), None)
    return spouse.get("name") if spouse else None


def _name_reason(level):
    return NAME_LEVEL_TEXT[level]["en"], NAME_LEVEL_TEXT[level]["ta"]


def member_name_check(member, members, docs):
    """Worst level across a member's printed names + one cell per document (compared to the first)."""
    printed = member.get("names_as_printed") or {}
    names = [(d, printed[d]) for d in docs if printed.get(d)]
    if len(names) < 2:
        return None, []
    rel = relative_name(member, members)
    worst, cells = "GREEN", []
    base = names[0][1]
    for i, (doc, nm) in enumerate(names):
        level = "GREEN"
        for _, other in names:
            lv = name_check(nm, other, rel)
            if LEVEL_ORDER[lv] > LEVEL_ORDER[level]:
                level = lv
        if LEVEL_ORDER[level] > LEVEL_ORDER[worst]:
            worst = level
        en, ta = _name_reason(level)
        cells.append({"doc_id": doc, "doc_en": DOCUMENTS[doc]["en"], "doc_ta": DOCUMENTS[doc]["ta"],
                      "name_printed": nm, "level": level, "reason_en": en, "reason_ta": ta})
    return worst, cells


# ------------------------------------------------------------- problems + plan
def _bring(office_id):
    if office_id == "bank_branch":
        return "Aadhaar, bank passbook", "ஆதார், வங்கிப் புத்தகம்"
    if office_id == "esevai_csc":
        return "Aadhaar, ration card, Application Pack", "ஆதார், குடும்ப அட்டை, விண்ணப்பத் தொகுப்பு"
    if office_id == "check":
        return "Phone", "கைபேசி"
    return "Aadhaar", "ஆதார்"


def task_effect(task_id):
    """Fact patches that marking this task Done implies (so the plan re-plans)."""
    member_id, _, what = task_id.partition(":")
    if what in BANK_DOCS:
        return [(f"member:{member_id}.has_own_bank_account", True),
                (f"member:{member_id}.bank_aadhaar_seeded", True),
                (f"member:{member_id}.bank_account_active", True)]
    if what == "pmkisan_ekyc":
        return [(f"member:{member_id}.pmkisan_ekyc_done", True)]
    if what == "check_bank":
        return []
    if what in DOCUMENTS and what not in ("ration_card",):
        if what == "patta_land_record":
            return [("family.land_in_own_name", True), (f"member:{member_id}.docs.patta_land_record", True)]
        return [(f"member:{member_id}.docs.{what}", True)]
    if what == "ration_card":
        return [("family.has_ration_card", True)]
    return []  # apply tasks: only the done flag


def analyse(derived, verdicts):
    """Missing documents, matrix, fix plan and trips for the counted schemes."""
    family, members = derived["family"], derived["members"]
    done_flags = derived.get("tasks", {})
    by_member = {m["id"]: m for m in members}
    counted = [v for v in verdicts if v["counted"]]

    missing, office_tasks, matrix_docs = [], {}, {}
    trips_without = 0

    def add_task(office, scheme_id, task):
        entry = office_tasks.setdefault(office, {"unblocks": set(), "tasks": {}})
        entry["unblocks"].add(scheme_id)
        task["done"] = bool(done_flags.get(task["task_id"]))
        entry["tasks"].setdefault(task["task_id"], task)

    for v in counted:
        s = SCHEMES_BY_ID[v["scheme_id"]]
        m = by_member.get(v["member_id"])
        if m is None:
            continue
        name = m.get("name") or m["id"]
        count = 0
        apply_office = s.get("where_to_apply")
        if apply_office and is_trip(apply_office):
            count += 1

        for doc in s.get("required_documents", []):
            have = has_doc(doc, family, m)
            info = DOCUMENTS[doc]
            if have is False:
                office = info["if_missing"]["office"]
                count += 1
                missing.append({"member_id": m["id"], "member_name": name, "doc_id": doc,
                                "en": info["en"], "ta": info["ta"], "office": office,
                                "where_en": info["if_missing"]["en"], "where_ta": info["if_missing"]["ta"]})
                be, bt = _bring(office)
                add_task(office, s["id"], {"task_id": f"{m['id']}:{doc}", "member_name": name,
                                           "en": info["if_missing"]["en"], "ta": info["if_missing"]["ta"],
                                           "bring_en": be, "bring_ta": bt, "kind": "fix"})
            elif have is None and doc in BANK_DOCS and info.get("check_in_1_minute"):
                c = info["check_in_1_minute"]
                add_task("check", s["id"], {"task_id": f"{m['id']}:check_bank", "member_name": name,
                                            "en": f"Check if {name}'s Aadhaar is linked to the bank: {c['en']}",
                                            "ta": f"{name} — வங்கியுடன் ஆதார் இணைப்பைச் சரிபார்க்கவும்: {c['ta']}",
                                            "bring_en": "Phone", "bring_ta": "கைபேசி", "kind": "check", "url": c.get("url")})

        for t in s.get("required_tasks", []):
            info = TASKS[t]
            field = info["done_fact"].split(".", 1)[1]
            if m.get(field) is not True:
                count += 1
                be, bt = _bring(info["office"])
                add_task(info["office"], s["id"], {"task_id": f"{m['id']}:{t}", "member_name": name,
                                                   "en": f"{info['en']}: {info['how_en']}", "ta": f"{info['ta']}: {info['how_ta']}",
                                                   "bring_en": be, "bring_ta": bt, "kind": "fix"})

        level, _ = member_name_check(m, members, s.get("name_check_documents", []))
        if level == "YELLOW":
            count += 1
        elif level == "RED":
            count += 1
            add_task("aadhaar_centre", s["id"], {"task_id": f"{m['id']}:fix_name", "member_name": name,
                                                 "en": "Correct the name so it matches on all documents",
                                                 "ta": "எல்லா ஆவணங்களிலும் பெயர் ஒன்றாக இருக்கும்படி திருத்தவும்",
                                                 "bring_en": "Aadhaar + the other document", "bring_ta": "ஆதார் + மற்ற ஆவணம்", "kind": "fix"})
        if apply_office:
            be, bt = _bring(apply_office)
            add_task(apply_office, s["id"], {"task_id": f"{m['id']}:apply:{s['id']}", "member_name": name,
                                             "en": f"Apply for {s['name_en']}" if apply_office != "online" else s.get("how_to_apply_en", ""),
                                             "ta": f"{s['name_ta']} — விண்ணப்பிக்கவும்" if apply_office != "online" else s.get("how_to_apply_ta", ""),
                                             "bring_en": be, "bring_ta": bt, "kind": "apply"})
        trips_without += count

    plan = []
    for office_id, entry in office_tasks.items():
        info = office_info(office_id)
        tasks = list(entry["tasks"].values())
        plan.append({"office_id": office_id, "office_en": info["en"], "office_ta": info["ta"],
                     "unblocks": sorted(entry["unblocks"]), "tasks": tasks,
                     "_fix_count": sum(1 for t in tasks if t["kind"] != "apply")})

    def order(o):
        if o["office_id"] == "check":
            return (0, 0, 0)
        if o["office_id"] == "online":
            return (2, 0, 0)
        return (1, -len(o["unblocks"]), -o["_fix_count"])

    plan.sort(key=order)
    for o in plan:
        o.pop("_fix_count")

    trip_offices = {o["office_id"] for o in plan if is_trip(o["office_id"])
                    and any(not t["done"] for t in o["tasks"])}
    trips_with = len({o["office_id"] for o in plan if is_trip(o["office_id"])}) if plan else 0

    # Names are checked for every ELIGIBLE scheme (the family may choose any of them),
    # while trips and the plan use only the counted schemes.
    for v in verdicts:
        if v["status"] == "ELIGIBLE" and v["member_id"] in by_member:
            matrix_docs.setdefault(v["member_id"], set()).update(
                SCHEMES_BY_ID[v["scheme_id"]].get("name_check_documents", []))
    matrix = []
    for member_id, docs in matrix_docs.items():
        m = by_member[member_id]
        level, cells = member_name_check(m, members, sorted(docs))
        if level:
            matrix.append({"member_id": member_id, "member_name": m.get("name") or member_id, "level": level, "cells": cells})

    return {"missing_documents": missing, "plan": plan, "matrix": matrix,
            "trips": {"without": trips_without, "with": trips_with}, "open_trip_offices": sorted(trip_offices)}
