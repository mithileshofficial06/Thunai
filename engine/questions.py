"""Next question: the first question in ask_order whose facts are still unknown and relevant."""
from engine.data import QUESTIONS_FILE, SCHEMES_BY_ID
from engine.documents import BANK_DOCS, has_doc

Q = QUESTIONS_FILE["questions"]
EXCLUSION_FIELDS = Q["exclusion_sweep"]["sets"]


def _q(qid, member=None, doc_list=None):
    q = Q[qid]
    en, ta = q["en"], q["ta"]
    if member is not None:
        nm = member.get("name") or member["id"]
        en, ta = en.replace("{name}", nm), ta.replace("{name}", nm)
    if doc_list is not None:
        en = en.replace("{document_list}", ", ".join(d["en"] for d in doc_list))
        ta = ta.replace("{document_list}", ", ".join(d["ta"] for d in doc_list))
    return {"id": qid, "en": en, "ta": ta, "member_id": member["id"] if member else None}


def next_question(derived, verdicts):
    fam, members = derived["family"], derived["members"]
    relevant = [v for v in verdicts if v["status"] in ("ELIGIBLE", "NEED_INFO")]

    if not members:
        return _q("household")
    if fam.get("has_ration_card") is None:
        return _q("ration_card")
    if fam.get("has_ration_card") and fam.get("ration_card_head_member_id") is None:
        return _q("ration_card_head")
    if fam.get("ration_card_head_member_id") and all(m.get("is_kmut_head_of_family") is None for m in members):
        return _q("kmut_chosen")
    if fam.get("owns_cultivable_land") is None:
        return _q("land")
    if fam.get("owns_cultivable_land") and fam.get("land_acquired_after_2019_02_01_not_inherited") is None:
        return _q("land_cutoff")
    if fam.get("annual_income") is None:
        return _q("income")
    if any(fam.get(f.split(".", 1)[1]) is None for f in EXCLUSION_FIELDS):
        return _q("exclusion_sweep")
    if any(m.get("is_kmut_head_of_family") for m in members) and fam.get("electricity_units_per_year") is None:
        return _q("electricity")
    for m in members:
        if m.get("gender") == "female" and 16 <= (m.get("age") or 0) <= 30 and m.get("current_education") is None:
            return _q("studies", m)
    for m in members:
        if (m.get("marital_status") == "widowed" or (m.get("age") or 0) >= 60) and m.get("is_destitute") is None:
            return _q("widow_destitute", m)

    by_id = {m["id"]: m for m in members}
    for v in relevant:
        m = by_id.get(v["member_id"])
        if m is None:
            continue
        if m.get("has_own_bank_account") is None or (m.get("has_own_bank_account") and m.get("bank_aadhaar_seeded") is None):
            return _q("bank_status", m)
    for v in relevant:
        m = by_id.get(v["member_id"])
        if v["scheme_id"] == "pm_kisan" and m is not None and m.get("pmkisan_ekyc_done") is None:
            return _q("pmkisan_ekyc", m)
    for v in relevant:
        m = by_id.get(v["member_id"])
        if m is None:
            continue
        unknown = [d for d in SCHEMES_BY_ID[v["scheme_id"]].get("required_documents", [])
                   if d not in BANK_DOCS and d != "ration_card" and has_doc(d, fam, m) is None]
        if unknown:
            from engine.data import DOCUMENTS
            return _q("documents_have", m, [DOCUMENTS[d] for d in unknown])
    return None
