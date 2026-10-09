"""Engine tests: the demo numbers and edge cases from docs/03_ARCHITECTURE.md §7."""
import copy
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402

from engine import diff, recompute  # noqa: E402
from engine.data import DOCUMENTS_FILE, PERSONAS  # noqa: E402
from engine.documents import name_check  # noqa: E402
from engine.facts import patch  # noqa: E402


def facts_of(persona):
    f = copy.deepcopy(PERSONAS[persona]["facts"])
    f.setdefault("tasks", {})
    return f


def status(snap, key):
    return next((v["status"] for v in snap["verdicts"] if v["key"] == key), None)


@pytest.fixture
def murugan():
    return recompute(facts_of("murugan_family"))


# ------------------------------------------------------------------ Murugan
def test_murugan_verdicts(murugan):
    eligible = {v["key"] for v in murugan["verdicts"] if v["status"] == "ELIGIBLE"}
    assert eligible == {"pm_kisan", "kmut:m2", "pudhumai_penn:m3"}


def test_murugan_rupees(murugan):
    assert murugan["rupees_per_year"] == 30000


def test_murugan_trips(murugan):
    assert murugan["trips"] == {"without": 6, "with": 2}


def test_murugan_plan_order(murugan):
    offices = [o["office_id"] for o in murugan["plan"]]
    assert offices == ["bank_branch", "esevai_csc", "online"]
    bank = murugan["plan"][0]
    assert len(bank["tasks"]) == 2 and len(bank["unblocks"]) == 2
    assert len(murugan["plan"][1]["tasks"]) == 3


def test_murugan_matrix(murugan):
    levels = {m["member_name"]: m["level"] for m in murugan["matrix"]}
    assert levels == {"Murugan": "GREEN", "Selvi": "GREEN", "Kavya": "YELLOW"}


def test_murugan_missing_documents(murugan):
    missing = {(d["member_name"], d["doc_id"]) for d in murugan["missing_documents"]}
    assert missing == {("Selvi", "bank_account_aadhaar_seeded"), ("Kavya", "student_bank_account_aadhaar_seeded")}


def test_murugan_kmut_head_is_selvi(murugan):
    assert status(murugan, "kmut:m2") == "ELIGIBLE"
    assert status(murugan, "kmut:m1") is None and status(murugan, "kmut:m3") is None


def test_murugan_no_more_questions(murugan):
    assert murugan["next_question"] is None


# ------------------------------------------------------------ re-plan on income
def test_income_correction_replans(murugan):
    f, old, new = patch(murugan["facts"], "family.annual_income", 300000)
    assert (old, new) == (90000, 300000)
    after = recompute(f)
    assert status(after, "kmut:m2") == "NOT_ELIGIBLE"
    assert after["rupees_per_year"] == 18000
    assert after["trips"] == {"without": 4, "with": 2}
    texts = " | ".join(e["text_en"] for e in diff(murugan, after))
    assert "₹30,000 → ₹18,000" in texts
    assert "Eligible → Not eligible" in texts
    assert "Family income below ₹2.5 lakh" in texts


def test_task_done_replans(murugan):
    f, _, _ = patch(murugan["facts"], "member:m2.bank_aadhaar_seeded", True)
    after = recompute(f)
    removed = [e for e in diff(murugan, after) if e["text_en"].startswith("Task no longer needed")]
    assert removed and "Selvi" in removed[0]["text_en"]


# ------------------------------------------------------------------ Lakshmi
def test_lakshmi_one_pension_counted():
    snap = recompute(facts_of("lakshmi_paati"))
    assert status(snap, "destitute_widow_pension:l1") == "ELIGIBLE"
    assert status(snap, "old_age_pension:l1") == "ELIGIBLE"
    assert status(snap, "kmut:l1") == "ELIGIBLE"
    assert snap["rupees_per_year"] == 14400
    kmut = next(v for v in snap["verdicts"] if v["key"] == "kmut:l1")
    assert kmut["counted"] is False and kmut["conflict_note"]


def test_lakshmi_name_yellow():
    snap = recompute(facts_of("lakshmi_paati"))
    assert {m["member_name"]: m["level"] for m in snap["matrix"]} == {"Lakshmi": "YELLOW"}


# --------------------------------------------------------------- name check
@pytest.mark.parametrize("case", DOCUMENTS_FILE["name_check"]["test_cases"], ids=lambda c: f"{c['a']} vs {c['b']}")
def test_name_check_cases(case):
    assert name_check(case["a"], case["b"], case["parent_or_spouse"]) == case["expect"]


# ---------------------------------------------------------------- edge cases
def test_unknown_head_no_kmut_card():
    f = facts_of("murugan_family"); f["family"]["ration_card_head_member_id"] = None
    snap = recompute(f)
    assert not any(v["scheme_id"] == "kmut" for v in snap["verdicts"])
    assert snap["next_question"]["id"] == "ration_card_head"


def test_tractor_excludes_kmut():
    f = facts_of("murugan_family"); f["family"]["owns_four_wheeler_personal_use"] = True
    assert status(recompute(f), "kmut:m2") == "NOT_ELIGIBLE"


def test_aided_school_need_info():
    f = facts_of("murugan_family"); f["members"][2]["studied_class_6_to_12_in"] = "government_aided"
    assert status(recompute(f), "pudhumai_penn:m3") == "NEED_INFO"


def test_unknown_income_need_info():
    f = facts_of("murugan_family"); f["family"]["annual_income"] = None
    snap = recompute(f)
    assert status(snap, "kmut:m2") == "NEED_INFO"
    assert snap["next_question"]["id"] == "income"


def test_mixed_land_need_info():
    f = facts_of("murugan_family"); f["family"]["wet_land_acres"] = 1
    assert status(recompute(f), "kmut:m2") == "NEED_INFO"


def test_income_tax_excludes_pm_kisan():
    f = facts_of("murugan_family"); f["family"]["income_tax_payer_last_year"] = True
    assert status(recompute(f), "pm_kisan") == "NOT_ELIGIBLE"


def test_empty_family_asks_household():
    snap = recompute(None)
    assert snap["next_question"]["id"] == "household" and snap["rupees_per_year"] == 0


# --------------------------------------------------------------- validation
def test_patch_rejects_unknown_field():
    with pytest.raises(ValueError):
        patch(facts_of("murugan_family"), "family.salary", 5)


def test_patch_rejects_derived_field():
    with pytest.raises(ValueError):
        patch(facts_of("murugan_family"), "member:m2.is_kmut_head_of_family", True)


def test_patch_coerces_numbers():
    f, _, new = patch(facts_of("murugan_family"), "family.annual_income", "1,50,000")
    assert new == 150000


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
