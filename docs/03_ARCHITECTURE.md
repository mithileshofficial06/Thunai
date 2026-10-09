# Stage 3: Architecture — Thunai 🔒 FINAL (v7, 9 Oct 2026, after Evaluation 1)

> **v7 changes (match `01_IDEA.md` v2 and `04_BUILD_PLAN.md` §4a):**
> - UiPath dropped.
> - The UI is the government-portal style.
> - Letters: 6 kinds, drafted from templates, helper approval.
> - The Doctor feeds the plan and the letters.
> - Revathi sample-documents family.
> - Name fixes go to the issuing office.
> - New: **login + history** (`store.py`, SQLite), **SMS outbox** (`engine/notify.py`), **follow-up + re-match** (`engine/proactive.py`), **source check**, more verified schemes.
> - Storage moves from browser-only to **SQLite for logged-in users** (guest mode is unchanged).

**Goal of this design:** deliver **exactly the planned product** (Find → Fix → Follow, H1–H5, a polished mobile-first page, a live agent panel) **within ~5 hours**, with **all app code written in the hall**.
**Runs on:** your laptop · **AI cost:** ₹0 (free tiers) · **Builders:** you + Claude Code (main session + background subagents)

> **Why this design (v6) over the alternatives:**
> - *FastAPI + one custom HTML/JS page*, not Streamlit: the users are families on **phones**; a custom page gives a mobile-first UI, a smooth agent-panel replay, an editable family card, saved progress (SQLite for logged-in users) and a polished look that stands out to judges. Streamlit's reload model fights all four.
> - *Backend first, UI last (per evaluation phase):* the backend for each phase is finished and tested before its UI is built, so the UI sits on real, tested data: no mocks, no rework. The UI follows the final design in `07_UI_UX_BRIEF.md`.
> - *Compliance:* everything prepared tonight is design or research (`docs/`, `data/`). All code is written during the event; `prep/` is never used by the app (§13).

---

## 1. PS-10 → architecture (every requirement has a module)
| PS-10 requirement | What the user sees | Module(s) | Piece |
|---|---|---|---|
| **Multilingual AI agent** | Tamil / English chat; Tamil questions, verdicts, fix steps, letters; agent panel: 🎯 goal → 📋 plan → 🧠 AI decision → 🔧 tools → 🔁 re-plan | `llm.py`, `agent.py`, `data/*.json` | H1, H3 |
| **Learns the situation through conversation** | Whole-family interview; live family card; tap a value to correct it → re-plan | `llm.py` → `update_facts`, `engine/questions.py`, `engine/facts.py` | H1 |
| **Checks eligibility against scheme rules** | Scheme cards ✅❓❌, rule quoted, official source, ₹ unlocked | `engine/rules.py` + `data/schemes.json` | H2 |
| **Lists the missing documents** | Missing documents + where to get them; Consistency Matrix 🟢🟡🔴 | `engine/documents.py` + `data/documents.json` | H4 |
| **Prepares the application** | Application pack + 5 letters (name correction, bank linking, complaint, KMUT appeal, pension petition) → DRAFT → helper approves → print | `engine/letters.py`, `templates/letter.html`, helper queue | H5 |
| **Tracks pending actions** | Fix plan by office with Done (re-plan on Done); Doctor adds its fix to the plan; login + history; SMS outbox; "15 days later" follow-up; new-scheme re-match | `engine/documents.py`, `engine/doctor.py`, `store.py`, `engine/notify.py`, `engine/proactive.py` | H4, H5, F1–F3 |

All six are met by H1–H6; F1–F3 strengthen "tracks pending actions".

---

## 2. Design principles
1. **Rules decide · AI understands and chooses actions · humans approve.**
2. **One AI call per turn**: facts + ordered actions + reason + one-line acknowledgement, as JSON (~1 s, fits free quotas).
3. **Event-driven re-planning**: any fact change (chat, card edit, Done) re-runs the engine; the panel shows the diff ("₹30,000 → ₹18,000"). Never depends on the AI choosing to re-plan.
4. **Verified Tamil for anything important** (from `data/`); the AI writes only the acknowledgement.
5. **The demo can't die**: Groq → Gemini → Groq (2nd model) → offline mode → "Load persona (direct)" → backup video.
6. **Backend first, UI last**: each phase's backend is completed and tested (engine tests + API tests) before its UI; fixed contracts (`06_CONTRACTS.md`) tell the UI exactly what the API returns.

---

## 3. System diagram
```
┌────────────────────────────── Browser: one custom page (mobile-first) ──────────────────────────────┐
│ Header: Thunai · TA/EN · Login/History · Start over │ Navy bar: Murugan · Revathi · Meena · Lakshmi │
│ ┌─── Chat 🎤 🔊 ─────┐ ┌──── Family card + Results ─────────────┐ ┌──── Agent panel ────────────┐  │
│ │ messages + input    │ │ family card (tap to edit)               │ │ 🎯 GOAL                       │  │
│ │                     │ │ scheme cards ✅❓❌ · ₹ meter           │ │ 📋 PLAN ✓ ✓ ◻                 │  │
│ │                     │ │ tabs: Fix · Doctor · Letters · Helper   │ │ 🧠 DECIDED actions + reason   │  │
│ └─────────────────────┘ └─────────────────────────────────────────┘ │ 🔧 TOOL · 🔁 RE-PLAN · 🔒     │  │
│ Guest: session only · Logged in: chats saved in SQLite (thunai.db)   └──────────────────────────────┘  │
│ Phone: the same page as tabs (Chat · Family · Results · Fix · Agent)                                   │
└──────────────▲───────────────────────────────────────────────────────────────┬──────────────────────┘
               │ JSON {events[], snapshot, reply}  (UI replays events ~250 ms apart)  │ JSON POST
┌──────────────┴───────────────────────────────────────────────────────────────▼──────────────────────┐
│ FastAPI app.py                                                                                        │
│  /api/chat ─► PII guard ─► AGENT (agent.py)                                                            │
│     ① PERCEIVE + DECIDE  llm.understand() ─► {facts, actions[], reason, ack}                           │
│          Groq qwen ─► Gemini 2.5 Flash ─► Groq gpt-oss ─► None (offline mode)   + small cache          │
│     ② ACT       update_facts · start_doctor · doctor_answer · mark_task_done ·                          │
│                 prepare_application · draft_appeal · escalate_to_helper · explain                       │
│     ③ OBSERVE   engine.recompute() ─► snapshot                                                          │
│     ④ RE-PLAN   engine.diff(old, new) ─► 🔁 events                                                       │
│     ⑤ RESPOND   ack + changes + next question (verified TA/EN)                                          │
│  ENGINE engine/*.py (pure Python, deterministic) ◄── data/*.json (researched, official sources)         │
│  LETTERS engine/letters.py (templates, no AI) → helper queue → approve → /letter/{id} printable          │
│  FOLLOW  store.py (users, chats, outbox in SQLite) · engine/notify.py (SMS text) · engine/proactive.py   │
│  Sessions: in-memory {facts, tasks, doctor, case, helper_queue, snapshot}; saved per user when logged in │
└──────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Tech stack & tools (all free; installed and tested on this laptop, 9 Oct)
| Layer | Tool | Why this one | Tested |
|---|---|---|---|
| Language | **Python 3.12** | One language for engine, AI and API; Claude Code is fastest in it | ✅ installed |
| Web API | **FastAPI** + **Uvicorn** | Simple JSON endpoints, automatic request validation, serves the page | ✅ |
| Validation | **Pydantic v2** (comes with FastAPI) | Validates request bodies **and the AI's JSON** (accuracy layer) | ✅ |
| AI understanding #1 + #2 (run together, must agree) | **Groq** `qwen/qwen3.8-27b` (reasoning off) + `openai/gpt-oss-120b` (reasoning low) | Fast (0.6–1.8 s), free, both on one key; agreement gives 0 wrong facts in the 18-case test | ✅ 17/18 · 15/18 |
| AI backup | **Gemini** `gemini-2.5-flash`, `thinking_budget=0` | Separate free account; replaces a model that errors | ✅ 1.7 s |
| 🎤 Voice input | **Groq Whisper `whisper-large-v3`** (`language="ta"`), recorded in the browser with **MediaRecorder** | Works in any browser; free; 94–95% on Tamil sentences in 0.6–1.3 s. `turbo` rejected (59% on numbers) | ✅ |
| 🔊 Voice output | **edge-tts** with **`ta-IN-PallaviNeural`** (female; `ValluvarNeural` male as an option) → MP3, cached by text | Natural Microsoft neural Tamil; free, no key. The laptop has **no Tamil system voice**, so browser speech synthesis can't speak Tamil | ✅ 1.6–2 s |
| Frontend | One `index.html` + vanilla `app.js` + `style.css` | No build step; full control of the "Two faces" design | — |
| Styling | **Tailwind Play 3.4.17**, local file in `vendor/` | Fast styling, works offline | ✅ saved |
| Tamil font | **Nirmala UI** (Windows system font) | Renders Tamil well, offline | ✅ installed |
| Letters / pack | `templates/letter.html` + `engine/letters.py` → browser **Print / Save as PDF** | No PDF library; deterministic text, so names and numbers are exact | ✅ |
| Storage | Server memory (guest) + **SQLite** via Python's built-in `sqlite3` (`thunai.db`, gitignored) | No install, no server; users, chats, outbox | — |
| PIN hashing | `hashlib.pbkdf2_hmac` + random salt (standard library) | PIN never stored in plain text | — |
| SMS | **Outbox only** (`config.SMS_PROVIDER = None`) + `wa.me` share link | Real SMS needs money + DLT registration | — |
| Tests | **pytest** | Clear pass/fail for engine, API, accuracy and modules | ✅ 9.1 |
| Version control | **git** | Checkpoint commits, instant rollback | ✅ 2.55 |
| Dev | VS Code + **Claude Code**; Chrome DevTools device mode (phone view) | Build + mobile testing | ✅ Chrome installed |
| Backup video | Xbox Game Bar (`Win + Alt + R`) or OBS | Demo safety net | built in |
| Screenshots / UI checks | **Playwright** with the installed Chrome | Verifies the pages during the build (not part of the app) | ✅ |
| **Python packages** | `fastapi uvicorn pydantic groq google-genai edge-tts pytest` | | ✅ all installed |

**Not used, and why:** local Hugging Face models (IndicWhisper / IndicTTS) need PyTorch (~2 GB) and run 10–30 s per sentence on this laptop's CPU, so they're on the **roadmap** for a private, government-hosted version. Browser Web Speech API: Chrome-only and untested for Tamil here; Whisper is measured. Paid APIs: not affordable.

### 4a. Voice mode (input + output)
```
🎤 hold-to-talk (MediaRecorder) → POST /api/stt (audio) → Groq Whisper large-v3 (ta)
   → transcript shown in the input box (editable) → user taps Send (or auto-send after 3 s)
   → normal turn (PII guard → two-model understanding → accuracy layer → engine)
🔊 reply text (verified Tamil from data + one-line ack) → POST /api/tts → edge-tts Pallavi → MP3 (cached) → plays
```
- **Voice numbers must be confirmed:** any number that came from speech is shown as "please confirm: ₹3,00,000?" before it changes a verdict (Whisper misheard "90,000" as "900,000" in testing).
- **Speaker toggle 🔊** in the top bar; voice output reads the reply (not the agent panel).
- **Pre-generate** the demo replies' audio once (cache), so the demo voice plays instantly.
- **Fallbacks:** mic error / no internet → typing still works; TTS error → text only.

---

## 5. Folder structure (all code written in the hall)
```
scheme-sathi/
├── app.py              # FastAPI routes + serves static/
├── config.py           # provider order, model ids, timeouts, USE_LLM
├── llm.py              # understand(): cache → Groq qwen → Gemini → Groq gpt-oss → None; checks
├── agent.py            # handle(): perceive → decide → act → recompute → diff → reply; events
├── pii_guard.py        # removes Aadhaar-like / account-like numbers before any AI call
├── voice.py            # /api/stt (Groq Whisper) + /api/tts (edge-tts, MP3 cache in tts_cache/)
├── store.py            # SQLite: users (phone, PIN hash, role), chats, outbox; delete my data
├── amounts.py          # deterministic Tamil/English number parser (cross-check for the AI)
├── accuracy.py         # two-model agreement, evidence check, range checks → accepted / ask
├── engine/
│   ├── __init__.py     # recompute(facts) → snapshot · diff(old, new) → re-plan events
│   ├── facts.py        # patch with path validation, derived facts (KMUT head, mixed land)
│   ├── rules.py        # verdicts + TA/EN reasons, totals (exclusive groups, conflicts)
│   ├── documents.py    # has-doc, name check, matrix, missing docs, fix plan by office, trips
│   ├── questions.py    # next question (TA/EN)
│   ├── doctor.py       # decision-tree walk
│   ├── letters.py      # suggestions + 6 letter kinds (TA/EN HTML), DRAFT until approved
│   ├── notify.py       # summary SMS text (Tamil/English), outbox messages
│   └── proactive.py    # "15 days later" reminders, escalation; re-match after a scheme change
├── templates/          # letter.html (A4 page, DRAFT watermark, Print after approval)
├── static/             # index.html · app.js · style.css · tailwind (local) — built last in each phase
├── tests/              # test_engine.py · test_api.py · test_understand.py (live) · test_phase2.py
├── data/               # researched scheme rules (official sources)
├── docs/               # design: 01 idea · 02 data · 03 architecture · 04 build plan · 05 prompts & pitch · 06 contracts
├── vendor/             # third-party library files (Tailwind Play 3.4.17, MIT), for offline use
└── prep/               # night-before scripts; NEVER used by the app (§13)
```

---

## 6. The agent

### 6.1 One AI call: perceive + decide
Input: user message (after PII guard) · compact family card · last question · allowed fact paths · allowed actions.
Output (JSON, checked in code):
```json
{ "language": "ta",
  "facts": [ {"path": "family.annual_income", "value": 300000} ],
  "actions": ["update_facts", "explain"],
  "reason": "User corrected the income; update and explain what changed",
  "doctor_entry": null, "doctor_answer": null, "task_done": null, "escalate_reason": null,
  "ack": "சரி, வருமானத்தை ₹3 லட்சமாக மாற்றினேன்." }
```

### 6.2 Tools the AI can choose
| Action | Runs | Trigger example |
|---|---|---|
| `update_facts` | `engine/facts.py` → `recompute()` | any fact given or corrected |
| `start_doctor` / `doctor_answer` | `engine/doctor.py` | "My ₹1,000 stopped" / "yes, I got the SMS" |
| `mark_task_done` | done flag → `recompute()` | "Selvi's account is linked now" |
| `prepare_application` | `engine/letters.py` → helper queue | "Prepare the form" |
| `draft_appeal` | `engine/letters.py` → helper queue | rejection within the appeal window |
| `escalate_to_helper` | helper queue | conflicting facts, distress, case outside the rules |
| `explain` | reply | "why?", "what next?" |

**Code guards:** unknown paths / actions dropped (shown as "ignored"); max 4 actions; facts without `update_facts` → added automatically; the AI never outputs eligibility.

### 6.2a Accuracy layer: "Thunai never acts on a guess"
No AI is right 100% of the time, so every extracted fact must pass **all** of these before it can change a verdict:

| # | Check | How | If it fails |
|---|---|---|---|
| 1 | **Two-model agreement** | Groq `qwen/qwen3.8-27b` and Groq `openai/gpt-oss-120b` run **in parallel** (~1 s total); a fact is accepted only if both return the same path + value (numbers equal, strings equal after normalising). Gemini replaces a model that errors | Disagreement → **clarifying question with both options as buttons** ("Is the income ₹3,00,000 or ₹30,000?") |
| 2 | **Evidence quote** | Each fact carries `evidence`: the exact words from the user's message; code checks the words appear in the message | Fact dropped (shown as "ignored: no evidence") |
| 3 | **Number cross-check** | `amounts.py` parses amounts deterministically (லட்சம் / lakh ×1,00,000; ஆயிரம் / thousand ×1,000; "மாசம் / per month" ×12; "2 மாதம் / every two months" ×6 for electricity; ஒன்றரை = 1.5, இரண்டரை = 2.5) and compares with the AI value | Mismatch → clarifying question |
| 4 | **Range & type checks** | age 0–110 · income 0–1,00,00,000 · acres 0–100 · units 0–20,000 · enums only · member ids exist | Fact dropped + clarifying question |
| 5 | **Unsure → ask** | The AI lists anything ambiguous in `unclear`; the agent asks about it next | — |
| 6 | **Visible + correctable** | Accepted facts appear on the family card highlighted for one turn ("✓ I understood: income ₹90,000"); one tap corrects → re-plan | — |

**Single-model mode** (only one model answered): facts that pass checks 2–4 are applied but shown as **"please confirm"** on the card; the eligibility card says "based on unconfirmed answers" until the user taps ✓.

**Accuracy test set:** `data/eval_utterances.json` (18 Tamil + English sentences with expected facts, actions and forbidden outputs). Panel events show the checks: "🧠 2 models agreed · evidence ✓ · numbers ✓".

**Measured on this laptop (night of 9 Oct, prompt in `05_PROMPTS_AND_PITCH.md` §1.1, path normalisation + reasoning off):**
| | Correct alone | Applied automatically (both agreed and correct) | Asked the user instead | **Wrong facts applied** |
|---|---|---|---|---|
| Qwen + GPT-OSS pair | Qwen **17/18** · GPT-OSS **15/18** | **15/18** | 3/18 | **0/18** |

- First version of the prompt scored Qwen 11/18 and GPT-OSS 5/18; the fixes (exact path format, "only new facts", Tamil mapping hints, reasoning off) raised it to the numbers above.
- The 3 "asked" cases were disagreements (e.g. GPT-OSS misread "வருமான வரி கட்டல" = *did not* pay income tax). The agreement check caught them: **the user was asked, not given a wrong answer.**
- **Pass rule for `tests/test_understand.py` (B2):** 0 wrong facts applied on all 18 cases **and** at least 15/18 applied automatically. Optional morning check: Qwen + Gemini as the pair (`EVAL_MODELS=qwen/qwen3.8-27b,gemini-2.5-flash python prep/tools/eval_check.py`).
- **Speed:** single turns took 0.6–1.8 s; back-to-back test bursts slowed to 10–20 s (free-tier rate limit). Normal conversation is spaced out; the demo uses the cache for rehearsed lines.
- **Path normalisation** (guard in `accuracy.py`): `family:x` → `family.x`, `member:m1:x` → `member:m1.x` before validation.

### 6.3 Turn flow (`agent.handle(session, text)`)
```
1. pii_guard(text)                → 🔒 event if a number was removed
2. llm.understand(...)            → two models in parallel → accuracy.py checks (§6.2a)
                                  → 🧠 DECIDED (actions, reason, "2 models agreed · evidence ✓ · numbers ✓")
   disagreement / failed check    → ❓ clarifying question with options (no fact applied)
   None (all AI down)             → ⚠️ offline mode: reply = next question; card stays editable
3. run each action                → 🔧 TOOL events
4. snapshot = engine.recompute()  → 🔧 check_eligibility / check_documents / plan_fixes events
5. engine.diff(last, snapshot)    → 🔁 RE-PLAN events (verdict, ₹, task, trip changes)
6. reply = ack + changes + next question → {events, snapshot, reply}
```

### 6.4 What judges see for one turn
```
🎯 GOAL     Get the Murugan family every benefit they're owed, with the fewest trips
📋 PLAN     ✓ Learn the family  ✓ Check schemes  ◻ Check documents  ◻ Plan trips  ◻ Prepare packs
🧠 DECIDED  update_facts → explain   "User corrected the income"   (Qwen · 0.6 s)
🔧 TOOL     update_facts  income: 90,000 → 3,00,000
🔧 TOOL     check_eligibility  KMUT (Selvi): ✅ → ❌  "Family income below ₹2.5 lakh" not met
🔁 RE-PLAN  ₹30,000 → ₹18,000 · Selvi's bank task removed · trips 4 → 2
```

---

## 7. The engine (pure Python, deterministic; written and tested in B1)
```
recompute(facts) → derived facts → verdicts (TA/EN reasons, source) → ₹ total (exclusive groups,
conflicts) → missing documents · name matrix · fix plan by office · trips {without, with} → next question
```
**Expected results** (from the verified rules in `02_DATA_VERIFICATION.md`; checked by `tests/test_engine.py`):
| Case | Expected |
|---|---|
| Murugan family | PM-KISAN ✅ · KMUT (Selvi) ✅ · Pudhumai Penn (Kavya) ✅ · **₹30,000** · Kavya 🟡 · plan 🏦 Bank (2 tasks) → 🏢 e-Sevai (3) → 📱 online · **trips 6 → 2** |
| Murugan, income ₹3 lakh | KMUT ❌ · **₹18,000** · trips 4 → 2 |
| Lakshmi Paati | widow + old-age pension ✅ (counted once); KMUT conflicts → **₹14,400** |
| Meena (Doctor) | yes → no → **o_seeding** ("Aadhaar not linked to the account you use") |
| Edge cases | unknown ration-card head → no KMUT card · tractor → KMUT ❌ · aided school → Pudhumai ❓ · unknown income → KMUT ❓ · income tax → PM-KISAN ❌ |

---

## 8. API (plain JSON; exact shapes in `06_CONTRACTS.md`)
| Method & path | Returns |
|---|---|
| `POST /api/session` | `{session_id, snapshot, events}` (GOAL + PLAN) |
| `POST /api/chat` `{session_id, text, lang}` | `{events, snapshot, reply}` |
| `POST /api/facts` `{session_id, path, value}` | `{events, snapshot}` |
| `POST /api/task` `{session_id, task_id, done}` | `{events, snapshot}` |
| `POST /api/doctor` `{session_id, entry_id?, answer?}` | `{events, snapshot, step, suggested_letters, drafts}` |
| `POST /api/letter` `{session_id, kind, member_id?, doc_id?}` | `{events, snapshot, draft}` → `GET /letter/{id}` printable page |
| `GET /api/helper/queue?session_id=` · `POST /api/helper/approve {draft_id, helper_name}` | `{items}` · `{events, draft}` |
| `GET /api/sample_docs/{persona}` | `{cards}` (SAMPLE, no numbers) |
| `POST /api/demo/{persona}` (`?live=1` = through the AI) | `{events, snapshot, reply}` |
| `POST /api/stt` (multipart audio) · `POST /api/tts {text, lang}` | `{text, ms}` · `audio/mpeg` (cached) |
| `POST /api/auth/register` · `/login` · `/logout` | `{token, user}` |
| `GET /api/history` · `GET /api/history/{id}` · `DELETE /api/me` | chats list · reopen a chat · delete all my data |
| `POST /api/sms/summary` · `GET /api/outbox` | outbox message · messages |
| `POST /api/simulate {session_id, days}` · `POST /api/rematch` | follow-up events · re-match events |
| `GET /api/admin/check_sources` (helper, stretch) | per scheme: unchanged / changed: needs review / unreachable |

Every session response also carries `suggested_letters` and `drafts`, so the UI never guesses which letters apply.

---

## 9. Screens
| Area | Contents | Piece |
|---|---|---|
| Header + navy bar | Thunai · TA/EN · Login / History · Start over · demo families (Murugan, Revathi, Meena, Lakshmi) | H1, F1 |
| Chat | Messages + input; 🎤 hold-to-talk + 🔊 speaker toggle (voice mode, B5) | H1 / Eval 2 |
| Family card | Members + key facts; tap a value to correct → re-plan | H1 |
| Results | Scheme cards (✅❓❌ · rule · source · "checked 9 Oct 2026" · conflict note) · **₹ meter** | H2 |
| Agent activity | Plan stepper + text-labelled log (Goal, Plan, Action, Decision, Re-plan, Follow-up, Privacy) | H3 |
| Fix tab | Sample document cards (Revathi) · name check table · missing documents · fix plan by office with Done · visits saved | H4 |
| Doctor tab | 4 entry buttons → Yes / No / Don't know → outcome (cause · check in 1 minute · fix steps · Draft letter) | H5 |
| Letters + Helper | Suggested letters → DRAFT preview → helper Approve → Print | H5 |
| Follow | SMS outbox · Send summary · Share on WhatsApp · "Simulate 15 days later" | F2, F3 |
| Login + History | Phone + PIN (consent), guest, previous conversations, delete my data; helper login | F1 |

Desktop / projector: 3 columns. Phone: bottom tab bar (same page).

---

## 10. Privacy & safety
- **PII guard** before every AI call (12-digit and 9–18-digit numbers removed) → 🔒 event.
- No Aadhaar / bank / OTP in any question.
- Consent: *"We never ask for an Aadhaar number, bank number or OTP. Your answers are sent to a free AI service to understand them. If you log in, your family's details are saved under your phone number; you can delete them at any time."*
- **Login data:** phone number + PBKDF2-hashed PIN + family facts + chats. Never Aadhaar, bank or OTP. `DELETE /api/me` removes everything. Guest mode keeps nothing after the session.
- **Sample documents** are data cards marked SAMPLE with no ID numbers; Thunai never reads or stores real documents.
- **SMS:** outbox only; messages contain no ID numbers and always say "never share your OTP".
- Free tiers may train on prompts → no ID numbers sent; demo families fictional. Pitch: "Production would use a paid or government-hosted model; the AI is isolated in one file."
- Letters stay DRAFT until a helper approves; account numbers are left blank to be written by hand; the agent never submits anything.

---

## 11. Failure modes & fallbacks
| Failure | What happens |
|---|---|
| Groq limit / preview model removed | Gemini answers (panel: "backup: Gemini") |
| Gemini fails too | Groq gpt-oss |
| All AI down / no internet | Offline mode (next question; card editable) + "Load persona (direct)" |
| AI extracts a wrong fact | Visible on the card → tap → correct → re-plan |
| Invalid JSON / unknown path or action | Dropped by guards → next provider → offline mode |
| Backend crash | Restart Uvicorn (5 s) → backup video |
| Letter does not apply | Not suggested; the API refuses it (400), so no empty letter is shown |
| SQLite or login error | Guest mode keeps working (demo buttons need no login) |
| Wi-Fi drops | Ethernet → hotspot → offline mode → backup video (Tailwind is local) |

---

## 12. Build pieces → modules (timings in 04_BUILD_PLAN)
| Piece | Modules | Eval |
|---|---|---|
| **H1** Chat + family card + re-plan on edit + Load persona | `app.py`, `config.py`, `llm.py`, `agent.py`, `pii_guard.py`, `engine/facts.py`, `engine/questions.py`, `static/` | 1 |
| **H2** Scheme cards + ₹ | `engine/rules.py`, Results UI | 1 |
| **H3** Agent panel | `agent.py` events, panel UI | 1 |
| **H4** Fix tab | `engine/documents.py`, Fix tab UI | 2 |
| **H5** Doctor + pack + letters + helper + print | `engine/doctor.py`, `engine/letters.py`, `templates/letter.html`, tabs UI | 2 |
| **H6** Voice | `voice.py`, mic + speaker UI | 2 |
| **F1** Login + history | `store.py`, login UI | 2 |
| **F2** SMS outbox + summary | `engine/notify.py`, outbox UI | 2 |
| **F3** Follow-up + re-match | `engine/proactive.py`, "15 days later" button | 2 |
| **S1–S2** More schemes · source check | `data/schemes.json`, `/api/admin/check_sources` | stretch |

---

## 13. Compliance
- **Prepared tonight:** design docs (`docs/`) and researched scheme rules from official sources (`data/`). Night-before scripts are in `prep/` and are **never imported or copied** by the app.
- **Ask at registration:** "We researched the scheme rules and wrote a design document last night. Can we use them as reference? No app code is pre-built."
- **Plan A (allowed):** use `docs/` + `data/` as reference; write all code in the hall.
- **Plan B (stricter):** use `docs/` as notes; recreate `data/` in the hall from the tables in `02_DATA_VERIFICATION.md` (~10 min).
- **Explaining the code:** after each checkpoint, a 5-minute Claude Code walkthrough; teammates own testing, slides and Q&A.

## 14. Setup status
- [x] Gemini + Groq keys saved · [x] fastapi, uvicorn, google-genai, groq installed · [x] provider check passed on this laptop · [x] git 2.55 available · [x] Tailwind saved in `vendor/` (offline)
- [ ] Morning: re-run `prep/tools/test_providers.py` (connectivity check only); fix model names in `config.py` if needed
- [ ] Charger · **Ethernet cable** · phone hotspot

## 15. Dropped: UiPath robot
The UiPath e-Sevai form-filler (`docs/08_UIPATH_ROBOT.md`) was **dropped after Evaluation 1** to keep the team on the core journey. Thunai **prepares** the application pack and letters; the family or helper **submits** on the official site. Roadmap line for judges: "an RPA robot could fill the e-Sevai form from the approved pack, still stopping before Submit for a human."
