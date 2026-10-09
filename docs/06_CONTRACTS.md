# Contracts — Thunai (API shapes and data shapes) · v2 (after Evaluation 1)

**Purpose:** fixes the exact shapes the backend returns and the UI renders, so pieces plug together without surprises. Changing a shape means updating this file first.

**v2 changes:**
- Letters (6 kinds), suggestions and helper approval.
- Doctor responses carry the snapshot.
- Sample documents.
- New Follow endpoints: login, history, SMS outbox, follow-up, re-match.
- Source check.
- UiPath hand-off removed.

## 1. API (plain JSON, `http://localhost:8000`)
**Session responses** (`Out`) always contain: `session_id, events, snapshot, unconfirmed, pending_ask, doctor, suggested_letters, drafts` (+ `reply` for chat and demo).

| Method & path | Request body | Response |
|---|---|---|
| `POST /api/session` | `{"saved_facts"?}` | `Out` (GOAL + PLAN events) |
| `POST /api/chat` | `{"session_id", "text", "lang": "ta"\|"en", "from_voice"?: bool}` | `Out` + `reply: {en, ta}` |
| `POST /api/facts` | `{"session_id", "path", "value"}` e.g. `family.annual_income`, `member:m3.names_as_printed.aadhaar` | `Out` |
| `POST /api/task` | `{"session_id", "task_id", "done": bool}` | `Out` |
| `GET /api/doctor/entries` | — | `{"entries": [{id, en, ta, tree}]}` |
| `POST /api/doctor` | `{"session_id", "entry_id"?, "answer"?: "yes"\|"no"\|"dont_know"}` | `Out` + `step: DoctorStep` (400 if no open question) |
| `POST /api/letter` | `{"session_id", "kind", "member_id"?, "doc_id"?}` | `Out` + `draft: Draft` (400 if the letter doesn't apply) |
| `GET /api/helper/queue` | `?session_id=` optional | `{"items": [Draft]}` (newest first) |
| `POST /api/helper/approve` | `{"draft_id"}` + helper login token, **or** `{"draft_id", "username", "password"}` of a helper account | `{"events", "draft": Draft}` · 401 without a helper sign-in (only helpers approve; the approver's name comes from the account) |
| `GET /letter/{draft_id}` | — | printable HTML (DRAFT watermark until approved; Print only when approved) |
| `GET /api/sample_docs/{persona}` | — | `{"persona", "cards": [SampleCard]}` |
| `POST /api/demo/{persona}` | `?session_id=` `?live=1` optional · `murugan_family` \| `revathi_docs` \| `meena` \| `lakshmi_paati` | `Out` + `reply` |
| `POST /api/stt` | multipart `audio`, `lang` | `{"text", "ms"}` |
| `POST /api/tts` | `{"text", "lang"}` | `audio/mpeg` (cached) |
| `POST /api/auth/register` | `{"phone", "pin", "consent": true}` | `{"token", "user": User}` |
| `POST /api/auth/login` · `/api/auth/logout` | `{"phone", "pin"}` (helper: `{"username", "password"}`) | `{"token", "user"}` · `{}` |
| `GET /api/history` · `GET /api/history/{chat_id}` | header `Authorization: Bearer <token>` | `{"chats": [ChatSummary]}` · `Out` (reopened session) |
| `DELETE /api/me` | token | `{"deleted": true}` |
| `POST /api/sms/summary` | `{"session_id", "lang"}` (+ family login token → sent to that number) | `{"events", "message": OutboxMessage}` |
| `GET /api/outbox` | `?session_id=` optional | `{"messages": [OutboxMessage]}` |
| `POST /api/simulate` | `{"session_id", "days": 15}` | `Out` (events of type `autonomous`) |
| `POST /api/rematch` | — | `{"events", "messages": [OutboxMessage]}` |
| `GET /api/admin/check_sources` (stretch, helper) | — | `{"results": [{scheme_id, status: "unchanged"\|"changed"\|"unreachable", url, checked_at}]}` |

## 2. Event: one line in the activity log
```json
{ "type": "goal | plan | decided | tool | replan | privacy | fallback | autonomous | reply | error",
  "icon": "",
  "text_en": "Estimated benefit: ₹30,000 → ₹18,000 per year",
  "text_ta": "மதிப்பிடப்பட்ட நன்மை: ₹30,000 → ₹18,000 / ஆண்டு",
  "detail": { "provider": "qwen + gpt-oss", "checks": "2 models agreed; evidence and numbers verified" } }
```
`icon` is always empty (no emojis); the UI shows a text label per `type`: Goal, Plan, Decision, Action, Re-plan, Privacy, Offline, Follow-up (automatic), Reply, Error.

## 3. Snapshot: everything the UI renders
```json
{
  "facts": { "family": {}, "members": [], "tasks": {} },
  "plan_steps": [ {"id": "learn", "en": "Learn the family", "ta": "குடும்பத்தை அறிதல்", "done": true} ],
  "verdicts": [ { "key": "kmut:m2", "scheme_id": "kmut", "member_id": "m2", "member_name": "Selvi",
      "status": "ELIGIBLE | NEED_INFO | NOT_ELIGIBLE", "name_en": "", "name_ta": "", "benefit_en": "", "benefit_ta": "",
      "amount_per_year": 12000, "counted": true,
      "reasons": [ {"en": "", "ta": "", "ok": true} ],
      "source_url": "", "verification": "official", "checked_on": "2026-10-09", "conflict_note": null } ],
  "rupees_per_year": 30000,
  "matrix": [ { "member_id": "m3", "member_name": "Kavya", "level": "GREEN | YELLOW | RED",
      "cells": [ {"doc_id": "", "doc_en": "", "doc_ta": "", "name_printed": "", "level": "", "reason_en": "", "reason_ta": ""} ] } ],
  "missing_documents": [ {"member_id": "", "member_name": "", "doc_id": "", "en": "", "ta": "", "office": "", "where_en": "", "where_ta": ""} ],
  "plan": [ { "office_id": "bank_branch", "office_en": "", "office_ta": "", "unblocks": ["kmut", "pudhumai_penn"],
      "tasks": [ {"task_id": "m2:bank_account_aadhaar_seeded", "member_name": "", "short_en": "", "short_ta": "",
                  "en": "", "ta": "", "bring_en": "", "bring_ta": "", "kind": "fix | check | apply", "done": false} ] } ],
  "trips": { "without": 6, "with": 2 },
  "next_question": { "id": "", "en": "", "ta": "" }
}
```
**Task ids:**
- `<member>:<document>`: get or fix a document;
- `<member>:fix_name:<document>`: correct a printed name at the office that issued the document;
- `<member>:apply:<scheme>`: apply;
- `<member>:check_bank`: 1-minute online check;
- `doctor:<outcome>`: the fix from a Doctor outcome.

Ticking `fix_name` sets the printed name to the Aadhaar name. A finished task that leaves the plan is logged as **"Completed"**.

## 4. DoctorStep, Suggestion, Draft, SampleCard
```json
{ "kind": "question", "tree": "kmut_payment", "node_id": "q_seeded", "en": "", "ta": "", "path": ["q_selected_sms", "q_seeded"] }
{ "kind": "outcome", "node_id": "o_seeding", "cause_en": "", "cause_ta": "", "verify_en": "", "verify_ta": "",
  "fix_en": [""], "fix_ta": [""], "office": "bank_branch", "draft_letter": "bank_seeding_request | null",
  "escalate_to_helper": false, "source": "KMUT FAQ 2, 6 (official)", "path": ["q_selected_sms", "q_seeded", "o_seeding"] }

{ "kind": "name_correction_request", "member_id": "r1", "doc_id": "ration_card", "en": "", "ta": "",
  "reason_en": "Revathi: name on Ration card ('S. Revathi') differs from Aadhaar ('Revathi Sekar'); risk of rejection", "reason_ta": "" }

{ "draft_id": "a1b2c3d4", "kind": "application_pack | bank_seeding_request | name_correction_request | grievance | appeal_kmut | appeal_pension | escalation",
  "member_id": "r1", "doc_id": "ration_card", "member_name": "Revathi",
  "status": "DRAFT | APPROVED (letters) · OPEN | REVIEWED (escalations)",
  "reason": "", "reason_en": "", "reason_ta": "", "title_en": "", "title_ta": "",
  "created_at": "2026-10-09T13:20:00", "html_url": "/letter/a1b2c3d4", "approved_by": "Priya", "session_id": "" }

{ "doc_id": "ration_card", "doc_en": "Ration card (family card)", "doc_ta": "", "name_printed": "S. Revathi",
  "lines_en": ["Head of family", "Card type: PHH"], "lines_ta": [], "status": "have | missing", "sample": true }
```

## 4b. Follow shapes (F1–F3)
```json
{ "user": { "id": 1, "phone_masked": "98xxxxxx10", "role": "family | helper", "name": "" } }
{ "chat": { "chat_id": "", "title": "Murugan family", "updated": "2026-10-09T14:02:00", "rupees_per_year": 30000 } }
{ "message": { "id": 1, "session_id": "", "to": "98xxxxxx10 | (guest: no number)", "text": "Thunai: ...",
               "reason": "summary | reminder | deadline | escalation | new_scheme",
               "created": "2026-10-09T14:05:00", "status": "outbox | sent | failed", "detail": "" } }
```
**SMS delivery (`sms.py`):** every message is stored in the `outbox` table. When `SMS_PROVIDER=twilio` and the three Twilio settings are present, a message to a logged-in family is also **sent** (status `sent` / `failed`); otherwise it stays `outbox` (the prototype default; real SMS needs a paid or trial SMS account). Login tokens are stored in the `tokens` table, so a server restart keeps users logged in.

Phone numbers are shown masked in every response. The PIN is never returned. Outbox messages never contain ID numbers and always end with the "never share your OTP" line.

## 5. Module signatures (pure functions where possible; easy to test)
```python
# engine/__init__.py
def recompute(facts, packs_ready=False) -> dict          # → Snapshot
def diff(old, new) -> list[dict]                         # → [Event type "replan"]
# engine/doctor.py
def entry_points() -> list[dict]
def start(entry_id) -> dict                              # → DoctorStep
def answer(tree, path, reply, unsure=False) -> dict      # → DoctorStep ("dont_know" follows "no")
# engine/letters.py
def suggestions(facts, snapshot, doctor_step=None, case=None) -> list[dict]   # → [Suggestion]
def render(kind, facts, snapshot, member_id=None, doc_id=None, doctor_step=None, case=None, today=None) -> dict
def page(letter, approved, helper_name=None) -> str      # A4 HTML page
# engine/notify.py (F2)
def summary_sms(snapshot, lang="ta") -> str              # ≤ 480 characters
# engine/proactive.py (F3)
def simulate(snapshot, drafts, days) -> list[dict]       # → [Event type "autonomous"] + outbox texts
def rematch(saved_families) -> list[dict]               # newly ELIGIBLE → messages
# store.py (F1)
def register(phone, pin) / login(phone, pin) / save_chat(user, session) / list_chats(user) / delete_user(user)
```

## 6. Expected values (checked by `tests/test_api.py`, `tests/test_phase2.py`)
| Request | Expected |
|---|---|
| Murugan (`/api/demo/murugan_family`) | ₹30,000 · 3 Eligible · Kavya YELLOW · plan bank (2 tasks) → e-Sevai → online · trips 6 → 2 |
| Income → ₹3 lakh | KMUT Not eligible · ₹18,000 · trips 4 → 2 · re-plan events |
| Murugan application pack | names all 3 schemes; DRAFT until approved; approve → Print, helper name in the footer |
| Revathi | name check RED · missing: death certificate + bank linking · passbook fix in the bank visit · trips 4 → 3 · letters: name correction (ration card), bank linking, application pack |
| Revathi tick `r1:fix_name:bank_passbook` | "Completed: Revathi, Correct the name on the Bank passbook" |
| Meena | path q_selected_sms → q_seeded → o_seeding · bank visit in the plan · bank letter suggested, contains "Meena" |
| Lakshmi | ₹14,400 · o_fix_doc_and_petition · pension petition contains "Lakshmi" and the rejection reason |
| KMUT payment: yes, yes, yes, no | o_passbook_and_grievance · escalation in the helper queue · grievance suggested |

The UI is built **after** these pass, against the real API (backend first, UI last).
