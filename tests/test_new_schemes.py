"""New officially verified schemes (CRA social security pensions + Tamil Pudhalvan).

Each scheme gets an ELIGIBLE case and a NOT_ELIGIBLE / filtered-out case on small hand-made
facts, and the demo personas must give exactly the same results as before these schemes.
"""
import copy
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402

import config  # noqa: E402
from engine import recompute  # noqa: E402
from engine.data import SCHEMES_BY_ID  # noqa: E402

# Family facts with every family-level question already answered, so only the member decides.
FAMILY = {
    "district": "Madurai", "has_ration_card": True, "ration_card_type": "PHH",
    "ration_card_head_member_id": "x1", "kmut_chosen_member_id": None, "land_owner_member_id": None,
    "annual_income": 60000, "electricity_units_per_year": 900, "owns_cultivable_land": False,
    "land_in_own_name": False, "land_acquired_after_2019_02_01_not_inherited": False,
    "wet_land_acres": 0, "dry_land_acres": 0, "owns_four_wheeler_personal_use": False,
    "income_tax_payer_last_year": False, "professional_tax_payer": False,
    "govt_or_psu_or_bank_or_coop_employee_or_pensioner": False, "govt_pension_10000_or_more": False,
    "elected_representative": False, "registered_practising_professional": False, "nri": False,
    "gst_turnover_over_50_lakh": False, "receives_social_security_pension": False,
}


def woman(**kw):
    m = {"id": "x1", "name": "Test", "relation": "self", "spouse_of": None, "on_ration_card": True,
         "gender": "female", "age": 45, "marital_status": "deserted", "is_destitute": True,
         "immovable_property_value": 0, "current_education": "none",
         "has_own_bank_account": True, "bank_aadhaar_seeded": True, "bank_account_active": True,
         "docs": {"aadhaar": True}, "names_as_printed": {}}
    m.update(kw)
    return m


def student(**kw):
    m = {"id": "s1", "name": "Arun", "relation": "son", "spouse_of": None, "on_ration_card": True,
         "gender": "male", "age": 18, "marital_status": "unmarried", "studied_class_6_to_12_in": "government",
         "current_education": "ug", "is_first_higher_ed_course": True, "education_mode": "regular",
         "has_own_bank_account": True, "bank_aadhaar_seeded": True, "bank_account_active": True,
         "docs": {"aadhaar": True, "school_records_6_to_12": True, "college_admission_proof": True},
         "names_as_printed": {}}
    m.update(kw)
    return m


def snap_of(*members, **family):
    fam = copy.deepcopy(FAMILY)
    fam.update(family)
    return recompute({"family": fam, "members": [copy.deepcopy(m) for m in members], "tasks": {}})


def verdict(snap, key):
    return next((v for v in snap["verdicts"] if v["key"] == key), None)


def status(snap, key):
    v = verdict(snap, key)
    return v["status"] if v else None


# ------------------------------------------------------------ data sanity
@pytest.mark.parametrize("sid", ["deserted_women_pension", "unmarried_women_pension", "tamil_pudhalvan"])
def test_enabled_and_official(sid):
    s = SCHEMES_BY_ID[sid]
    assert s["enabled"] is True
    assert s["verification"]["status"] == "official" and s["benefit"]["verification"] == "official"
    assert all(".gov.in" in u for u in s["official_sources"])


def test_pension_amounts_and_group():
    for sid in ("deserted_women_pension", "unmarried_women_pension"):
        s = SCHEMES_BY_ID[sid]
        assert s["benefit"]["amount_per_year"] == 14400
        assert s["exclusive_group"] == "social_security_pension"
        assert sid in SCHEMES_BY_ID["kmut"]["conflicts_with"]
    assert SCHEMES_BY_ID["tamil_pudhalvan"]["benefit"]["amount_per_year"] == 12000


# ------------------------------------------------- destitute / deserted women
def test_divorced_destitute_woman_eligible():
    snap = snap_of(woman(marital_status="divorced", age=35))
    assert status(snap, "deserted_women_pension:x1") == "ELIGIBLE"


def test_deserted_woman_needs_office_check_for_5_years():
    snap = snap_of(woman(marital_status="deserted", age=40))
    v = verdict(snap, "deserted_women_pension:x1")
    assert v["status"] == "NEED_INFO"
    assert any(r["ok"] is None and "5 years" in r["en"] for r in v["reasons"])


def test_deserted_woman_under_30_not_eligible():
    assert status(snap_of(woman(age=28)), "deserted_women_pension:x1") == "NOT_ELIGIBLE"


def test_deserted_woman_with_property_not_eligible():
    snap = snap_of(woman(marital_status="divorced", immovable_property_value=250000))
    assert status(snap, "deserted_women_pension:x1") == "NOT_ELIGIBLE"


def test_deserted_pension_filtered_out_for_married_and_men():
    assert status(snap_of(woman(marital_status="married")), "deserted_women_pension:x1") is None
    assert status(snap_of(woman(gender="male", marital_status="divorced")), "deserted_women_pension:x1") is None


# ------------------------------------------------------ unmarried women 50+
def test_unmarried_destitute_woman_50_eligible():
    snap = snap_of(woman(marital_status="unmarried", age=55))
    assert status(snap, "unmarried_women_pension:x1") == "ELIGIBLE"
    assert status(snap, "deserted_women_pension:x1") is None


def test_unmarried_woman_not_destitute_not_eligible():
    snap = snap_of(woman(marital_status="unmarried", age=55, is_destitute=False))
    assert status(snap, "unmarried_women_pension:x1") == "NOT_ELIGIBLE"


def test_unmarried_pension_filtered_out_under_50():
    assert status(snap_of(woman(marital_status="unmarried", age=49)), "unmarried_women_pension:x1") is None


def test_one_pension_per_person_and_kmut_conflict():
    # Unmarried, destitute, 65: old-age + unmarried pension + KMUT all eligible → only ₹14,400 counted.
    snap = snap_of(woman(marital_status="unmarried", age=65))
    for key in ("unmarried_women_pension:x1", "old_age_pension:x1", "kmut:x1"):
        assert status(snap, key) == "ELIGIBLE"
    assert snap["rupees_per_year"] == 14400
    assert verdict(snap, "kmut:x1")["counted"] is False and verdict(snap, "kmut:x1")["conflict_note"]


# ------------------------------------------------------------ Tamil Pudhalvan
def test_tamil_pudhalvan_govt_school_boy_eligible():
    snap = snap_of(woman(marital_status="married", is_destitute=False, immovable_property_value=300000),
                   student())
    assert status(snap, "tamil_pudhalvan:s1") == "ELIGIBLE"
    assert verdict(snap, "tamil_pudhalvan:s1")["counted"] is True


def test_tamil_pudhalvan_private_school_not_eligible():
    assert status(snap_of(student(studied_class_6_to_12_in="private")), "tamil_pudhalvan:s1") == "NOT_ELIGIBLE"


def test_tamil_pudhalvan_second_course_not_eligible():
    assert status(snap_of(student(is_first_higher_ed_course=False)), "tamil_pudhalvan:s1") == "NOT_ELIGIBLE"


def test_tamil_pudhalvan_pg_not_eligible():
    assert status(snap_of(student(current_education="pg")), "tamil_pudhalvan:s1") == "NOT_ELIGIBLE"


@pytest.mark.parametrize("school", ["government_aided", "rte_private_6_8_then_government_9_12"])
def test_tamil_pudhalvan_aided_or_rte_need_info(school):
    assert status(snap_of(student(studied_class_6_to_12_in=school)), "tamil_pudhalvan:s1") == "NEED_INFO"


def test_tamil_pudhalvan_distance_need_info():
    assert status(snap_of(student(education_mode="distance")), "tamil_pudhalvan:s1") == "NEED_INFO"


def test_tamil_pudhalvan_filtered_out_for_girls_and_non_students():
    girl = student(gender="female")
    snap = snap_of(girl)
    assert status(snap, "tamil_pudhalvan:s1") is None
    assert status(snap, "pudhumai_penn:s1") == "ELIGIBLE"
    assert status(snap_of(student(current_education="none")), "tamil_pudhalvan:s1") is None


# ------------------------------------------- demo personas must not change
EXPECTED = {
    "murugan_family": (30000, {"without": 6, "with": 2}, None,
                       [("kmut:m2", "ELIGIBLE"), ("pm_kisan", "ELIGIBLE"), ("pudhumai_penn:m3", "ELIGIBLE")]),
    "revathi_docs": (14400, {"without": 4, "with": 3}, None,
                     [("destitute_widow_pension:r1", "ELIGIBLE"), ("kmut:r1", "ELIGIBLE"), ("pm_kisan", "NOT_ELIGIBLE")]),
    "lakshmi_paati": (14400, {"without": 3, "with": 3}, None,
                      [("destitute_widow_pension:l1", "ELIGIBLE"), ("kmut:l1", "ELIGIBLE"),
                       ("old_age_pension:l1", "ELIGIBLE"), ("pm_kisan", "NOT_ELIGIBLE")]),
    "meena": (0, {"without": 1, "with": 1}, "household", [("pm_kisan", "NEED_INFO")]),
}


@pytest.mark.parametrize("name", list(EXPECTED))
def test_demo_personas_unchanged(name, monkeypatch):
    monkeypatch.setattr(config, "USE_LLM", False)
    import agent
    s, _ = agent.new_session()
    agent.load_persona(s, name, direct=True)
    snap = s["snapshot"]
    rupees, trips, question, verdicts = EXPECTED[name]
    assert snap["rupees_per_year"] == rupees
    assert snap["trips"] == trips
    assert (snap["next_question"] or {}).get("id") == question
    assert sorted((v["key"], v["status"]) for v in snap["verdicts"]) == verdicts
    agent.SESSIONS.pop(s["id"], None)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))



# ------------------------------------------------- the chat asks what the new schemes need
_DONE_FAMILY = {"has_ration_card": True, "ration_card_head_member_id": "x1", "owns_cultivable_land": False,
                "annual_income": 20000, "electricity_units_per_year": 300,
                **{k: False for k in ("owns_four_wheeler_personal_use", "income_tax_payer_last_year", "professional_tax_payer",
                                      "govt_or_psu_or_bank_or_coop_employee_or_pensioner", "govt_pension_10000_or_more",
                                      "elected_representative", "registered_practising_professional", "nri",
                                      "gst_turnover_over_50_lakh", "receives_social_security_pension")}}


def _next_q(member):
    from engine import recompute
    member = {"id": "x1", "name": "X", "relation": "self", **member}
    return (recompute({"family": dict(_DONE_FAMILY), "members": [member], "tasks": {}})["next_question"] or {}).get("id")


def test_studies_question_is_asked_for_sons_too():
    from engine import recompute
    members = [{"id": "x1", "name": "Amma", "relation": "self", "gender": "female", "age": 45, "marital_status": "widowed",
                "current_education": "none", "is_destitute": False, "immovable_property_value": 0},
               {"id": "x2", "name": "Arun", "relation": "son", "gender": "male", "age": 19, "marital_status": "unmarried"}]
    q = recompute({"family": dict(_DONE_FAMILY), "members": members, "tasks": {}})["next_question"]
    assert q["id"] == "studies" and q["member_id"] == "x2" and "Arun" in q["en"]


def test_support_question_for_deserted_or_divorced_women_30_plus():
    assert _next_q({"gender": "female", "age": 40, "marital_status": "divorced", "current_education": "none"}) == "widow_destitute"
    assert _next_q({"gender": "female", "age": 35, "marital_status": "deserted", "current_education": "none"}) == "widow_destitute"


def test_support_question_for_unmarried_women_50_plus_only():
    assert _next_q({"gender": "female", "age": 55, "marital_status": "unmarried", "current_education": "none"}) == "widow_destitute"
    assert _next_q({"gender": "female", "age": 45, "marital_status": "unmarried", "current_education": "none"}) != "widow_destitute"
