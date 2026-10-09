"""Eligibility rules engine: deterministic verdicts from data/schemes.json.

The AI never decides eligibility; this module does, condition by condition.
"""
from engine.data import SCHEMES, SCHEMES_BY_ID

ELIGIBLE, NEED_INFO, NOT_ELIGIBLE = "ELIGIBLE", "NEED_INFO", "NOT_ELIGIBLE"


def value_of(path, family, member):
    """Read 'family.x' / 'member.x' (dotted) from the derived facts; None when unknown."""
    root, key = path.split(".", 1)
    src = family if root == "family" else member
    if src is None:
        return None
    cur = src
    for part in key.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def test(cond, family, member):
    """True / False, or None when the needed fact is unknown."""
    v = value_of(cond["field"], family, member)
    if v is None:
        return None
    x, op = cond["value"], cond["op"]
    try:
        if op == "==":
            return v == x
        if op == "!=":
            return v != x
        if op == "<":
            return v < x
        if op == "<=":
            return v <= x
        if op == ">":
            return v > x
        if op == ">=":
            return v >= x
        if op == "in":
            return v in x
    except TypeError:
        return None
    raise ValueError(f"unknown operator {op}")


def applicant_of(scheme, family, members):
    """For family-scope schemes, the member who applies (e.g. the landholder for PM-KISAN)."""
    if not scheme.get("applicant"):
        return None
    applicant_id = value_of(scheme["applicant"], family, None)
    return next((m for m in members if m["id"] == applicant_id), None)


def evaluate(derived):
    """All verdicts for the family. Returns a list of verdict dicts (key, status, reasons, ...)."""
    family, members = derived["family"], derived["members"]
    out = []
    for s in SCHEMES:
        targets = [None] if s["scope"] == "family" else members
        for m in targets:
            if m is not None:
                checks = [test(c, family, m) for c in s.get("beneficiary_member_filter", [])]
                if not all(r is True for r in checks):
                    continue  # not relevant to this member (or still unknown → a question asks it)
                person = m
            else:
                person = applicant_of(s, family, members)

            reasons = []
            exclusion_hit = False
            for c in s.get("exclusions", []):
                if test(c, family, person) is True:
                    exclusion_hit = True
                    reasons.append({"en": c["text_en"], "ta": c["text_ta"], "ok": False})
            elig = []
            for c in s["eligibility"]:
                r = test(c, family, person)
                elig.append(r)
                reasons.append({"en": c["text_en"], "ta": c["text_ta"], "ok": r})
            flags = []
            for c in s.get("need_info_flags", []):
                r = test(c, family, person)
                if r is True:
                    flags.append(True)
                    reasons.append({"en": c["text_en"], "ta": c["text_ta"], "ok": None})

            if exclusion_hit or False in elig:
                status = NOT_ELIGIBLE
            elif None in elig or flags:
                status = NEED_INFO
            else:
                status = ELIGIBLE

            key = s["id"] + (f":{m['id']}" if m is not None else "")
            out.append({
                "key": key,
                "scheme_id": s["id"],
                "member_id": person["id"] if person else None,
                "member_name": person.get("name") if person else None,
                "status": status,
                "name_en": s["name_en"],
                "name_ta": s["name_ta"],
                "benefit_en": s["benefit"].get("display_en", ""),
                "benefit_ta": s["benefit"].get("display_ta", ""),
                "amount_per_year": s["benefit"].get("amount_per_year", 0),
                "counted": False,
                "reasons": reasons,
                "source_url": (s.get("official_sources") or [None])[0],
                "verification": s["verification"]["status"],
                "checked_on": s["verification"]["checked_on"],
                "conflict_note": None,
            })
    _apply_totals(out)
    return out


def _apply_totals(verdicts):
    """Mark which ELIGIBLE verdicts count toward the ₹ total (exclusive groups, conflicts)."""
    eligible = sorted([v for v in verdicts if v["status"] == ELIGIBLE], key=lambda v: -v["amount_per_year"])
    counted, seen_groups = [], set()
    for v in eligible:
        group = SCHEMES_BY_ID[v["scheme_id"]].get("exclusive_group")
        if group:
            gk = (group, v["member_id"])
            if gk in seen_groups:
                continue
            seen_groups.add(gk)
        counted.append(v)
    # conflicts_with: keep only the higher amount, and explain the choice
    for v in list(counted):
        if v not in counted:
            continue
        rivals = [o for o in counted if o["scheme_id"] in SCHEMES_BY_ID[v["scheme_id"]].get("conflicts_with", [])]
        if rivals:
            group = [v] + rivals
            best = max(group, key=lambda z: z["amount_per_year"])
            note_scheme = SCHEMES_BY_ID[v["scheme_id"]]
            for z in group:
                z["conflict_note"] = note_scheme.get("conflict_note")
                if z is not best and z in counted:
                    counted.remove(z)
    for v in counted:
        v["counted"] = True


def rupees_per_year(verdicts):
    return sum(v["amount_per_year"] for v in verdicts if v["counted"])
