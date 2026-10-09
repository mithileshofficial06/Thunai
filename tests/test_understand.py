"""Accuracy test (live AI): data/eval_utterances.json through llm.understand + accuracy.check.

Pass rule: 0 wrong facts applied on all cases, and at least 15/18 fully understood automatically
(the rest must become a clarifying question, never a wrong fact). Run: RUN_LIVE=1 pytest tests/test_understand.py -s
"""
import json
import os
import pathlib
import re
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402

import accuracy  # noqa: E402
import config  # noqa: E402
import llm  # noqa: E402
import pii_guard  # noqa: E402

EVAL = json.loads((config.DATA_DIR / "eval_utterances.json").read_text(encoding="utf-8"))
PACE_S = float(os.environ.get("EVAL_PACE_S", "8"))  # free tier: 8,000 tokens/min per model


def norm(v):
    if isinstance(v, str):
        return v.strip().lower()
    if isinstance(v, float) and v.is_integer():
        return int(v)
    return v


def run_case(case):
    card = EVAL["_meta"]["cards"][case["card"]]
    facts = {"family": dict(card["family"]), "members": [dict(m) for m in card["members"]], "tasks": {}}
    text, _ = pii_guard.clean(case["input"])
    bundle = llm.understand(text, card, None)
    if bundle is None:
        return "error", "no model answered", None
    dec = accuracy.check(bundle, facts, text)
    applied = {**dec["accepted"], **dec["unconfirmed"]}
    asked = {q["path"] for q in dec["ask"]}
    wrong, missing = [], []
    for path, want in case.get("expect_facts", {}).items():
        if path in applied:
            if norm(applied[path]) != norm(want):
                wrong.append(f"{path}={applied[path]!r} (want {want!r})")
        elif path not in asked:
            missing.append(path)
    if case.get("forbid_any_facts") and applied:
        wrong.append(f"unexpected facts {list(applied)}")
    if re.search(r"\d{9,}", json.dumps(bundle, ensure_ascii=False).replace(" ", "")):
        wrong.append("long digit run reached the AI output")
    for a in case.get("expect_actions_include", []):
        if a not in dec["actions"]:
            missing.append(f"action {a}")
    if case.get("expect_doctor_entry") and dec["doctor_entry"] != case["expect_doctor_entry"]:
        missing.append(f"doctor_entry={dec['doctor_entry']}")
    if wrong:
        return "WRONG", "; ".join(wrong), dec
    if missing or any(p in asked for p in case.get("expect_facts", {})):
        return "asked/missed", "; ".join(missing) or f"asked about {sorted(asked)}", dec
    return "auto", "", dec


@pytest.mark.live
@pytest.mark.skipif(os.environ.get("RUN_LIVE") != "1", reason="live AI test: set RUN_LIVE=1")
def test_accuracy_eval():
    counts = {"auto": 0, "asked/missed": 0, "WRONG": 0, "error": 0}
    for i, case in enumerate(EVAL["cases"]):
        if i:
            time.sleep(PACE_S)
        outcome, why, dec = run_case(case)
        counts[outcome] += 1
        prov = " + ".join(dec["providers"]) if dec else "-"
        print(f"{case['id']}: {outcome:13s} {prov:45s} {why}")
    print("TOTAL:", counts)
    assert counts["WRONG"] == 0, "a wrong fact would have been applied"
    assert counts["auto"] >= 15
