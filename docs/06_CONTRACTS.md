# Contracts — Thunai (design spec: API shapes and data shapes)

**Purpose:** a *design document* that fixes the exact shapes the backend returns and the UI renders, so pieces built in the hall plug together without surprises. This is a specification, not code. Changing a shape means updating this file first.

## 1. API (plain JSON, `http://localhost:8000`)
| Method & path | Request body | Response |
|---|---|---|
| `POST /api/session` | `{"saved_facts"?: {...}, "saved_tasks"?: {...}}` | `{"session_id", "snapshot": Snapshot, "events": [Event]}` |
| `POST /api/chat` | `{"session_id", "text", "lang": "ta"\|"en"}` | `{"events": [Event], "snapshot": Snapshot, "reply": {"en", "ta"}}` |
| `POST /api/facts` | `{"session_id", "path", "value"}` e.g. `family.annual_income`, `member:m3.names_as_printed.aadhaar` | `{"events", "snapshot"}` |
| `POST /api/task` | `{"session_id", "task_id", "done": bool}` | `{"events", "snapshot"}` |
| `POST /api/doctor` | `{"session_id", "entry_id"?, "answer"?: "yes"\|"no"\|"dont_know"}` | `{"events", "step": DoctorStep}` |
| `POST /api/letter` | `{"session_id", "kind": "application_pack"\|"appeal_kmut"\|"appeal_pension", "member_id"?}` | `{"draft": Draft}` |
| `GET /api/helper/queue` · `POST /api/helper/approve` | `{"draft_id"}` | `{"items": [Draft]}` · `{"draft": Draft}` |
| `GET /letter/{draft_id}` | — | printable HTML |
| `POST /api/demo/{persona}` | `?direct=1` optional · `murugan_family` \| `meena` \| `lakshmi_paati` | `{"events", "snapshot", "reply"}` |
| `POST /api/simulate` (S1) | `{"session_id", "days": 15}` | `{"events": [Event]}` |

## 2. Event: one line in the agent panel
```json
{ "type": "goal | plan | decided | tool | replan | privacy | fallback | autonomous | reply | error",
  "icon": "🎯 | 📋 | 🧠 | 🔧 | 🔁 | 🔒 | ⚠️ | 🤖 | 💬 | ❌",
  "text_en": "update_facts  income: 90,000 → 3,00,000",
  "text_ta": "update_facts  வருமானம்: 90,000 → 3,00,000",
  "detail": { "provider": "groq-qwen", "latency_ms": 640 } }
```

## 3. Snapshot: everything the UI renders
```json
{
  "facts": { "family": {}, "members": [] },
  "plan_steps": [ {"id": "learn", "en": "Learn the family", "ta": "குடும்பத்தை அறிதல்", "done": true} ],
  "verdicts": [ { "scheme_id": "kmut", "member_id": "m2", "member_name": "Selvi",
      "status": "ELIGIBLE | NEED_INFO | NOT_ELIGIBLE", "name_en": "", "name_ta": "", "benefit_en": "", "benefit_ta": "",
      "amount_per_year": 12000, "counted": true,
      "reasons": [ {"en": "", "ta": "", "ok": true} ],
      "source_url": "", "verification": "official", "checked_on": "2026-10-09", "conflict_note": null } ],
  "rupees_per_year": 30000,
  "matrix": [ { "member_id": "m3", "member_name": "Kavya", "level": "GREEN | YELLOW | RED",
      "cells": [ {"doc_id": "", "doc_en": "", "doc_ta": "", "name_printed": "", "level": "", "reason_en": "", "reason_ta": ""} ] } ],
  "missing_documents": [ {"member_id": "", "member_name": "", "doc_id": "", "en": "", "ta": "", "office": "", "where_en": "", "where_ta": ""} ],
  "plan": [ { "office_id": "bank_branch", "office_en": "", "office_ta": "", "unblocks": ["kmut", "pudhumai_penn"],
      "tasks": [ {"task_id": "m2:bank_account_aadhaar_seeded", "member_name": "", "en": "", "ta": "", "bring_en": "", "bring_ta": "", "done": false} ] } ],
  "trips": { "without": 6, "with": 2 },
  "next_question": { "id": "", "en": "", "ta": "" }
}
```
`reasons[].ok`: `true` met · `false` not met (or an exclusion that applies) · `null` needs info / confirm.

## 4. DoctorStep and Draft
```json
{ "kind": "question", "node_id": "q_seeded", "en": "", "ta": "" }
{ "kind": "outcome", "node_id": "o_seeding", "cause_en": "", "cause_ta": "", "verify_en": "", "verify_ta": "",
  "fix_en": [""], "fix_ta": [""], "office": "bank_branch", "draft_letter": "bank_seeding_request | null",
  "escalate_to_helper": false, "needs_helper_approval": false, "path": ["q_selected_sms", "q_seeded", "o_seeding"] }

{ "draft_id": "d1", "kind": "appeal_pension", "member_name": "Lakshmi", "status": "DRAFT | APPROVED",
  "reason": "", "created_at": "2026-10-09T13:20:00", "html_url": "/letter/d1" }
```

## 5. Module signatures (pure functions; easy to test)
```python
# engine/__init__.py
def recompute(facts: dict) -> dict                      # → Snapshot
def diff(old: dict, new: dict) -> list[dict]            # → [Event type "replan"]
# engine/doctor.py
def entry_points() -> list[dict]
def start(entry_id: str) -> dict                        # → DoctorStep
def answer(path: list[str], answer: str) -> dict        # → DoctorStep ("dont_know" follows "no")
# engine/letters.py
def render_application_pack(facts, verdicts, plan, lang="both") -> str   # HTML page
def render_appeal(facts, member_id, kind, outcome, lang="both") -> str   # HTML page
def available_kinds() -> list[str]                      # hides buttons for missing templates
# engine/proactive.py  (S1)
def simulate(facts, plan, appeals, days, today) -> list[dict]   # → [Event type "autonomous"]
```

## 6. Expected values the API must return (checked by `tests/test_api.py`)
| Request | Expected |
|---|---|
| Murugan intake (9 Tamil lines or `/api/demo/murugan_family`) | ₹30,000 · 3 ELIGIBLE · Kavya YELLOW · plan 🏦 bank (2 tasks) → 🏢 e-Sevai (3) → 📱 online · trips 6 → 2 |
| Income → ₹3 lakh | KMUT ❌ · ₹18,000 · trips 4 → 2 · re-plan events |
| Meena Doctor (yes, no) | path q_selected_sms → q_seeded → o_seeding |
| Lakshmi | ₹14,400 · appeal draft → approve → printable letter containing "Lakshmi" |

The UI is built **after** these pass, against the real API (backend first, UI last).
