# Stage 4: Build Plan — Thunai 🔒 FINAL (v5: Phase 2 final scope in §4a; backend first, UI last)

**Day:** 9 Oct 2026 · **Venue:** Alpha Hall, Sri Sairam · **Architecture:** `03_ARCHITECTURE.md` v6 · **UI design:** `07_UI_UX_BRIEF.md` (final)
**Builders:** you + Claude Code · **Teammates:** testing, slides, pitch, Q&A
**Reference (design only):** `docs/01–07` · `data/*.json` · **Never used by the app:** `prep/`

> **Principle: backend first, UI last, in each evaluation phase.**
> - **Phase 1 (→ Eval 1):** build and *test* the backend for H1–H3 → then build its UI.
> - **Phase 2 (→ Eval 2):** build and *test* the backend for H4–H5 → then build their UI tabs.
> The UI is always built on a **finished, tested backend**: no mock data, no guessing, no rework. The UI follows the final design in `07_UI_UX_BRIEF.md`.

---

## 0. Rules for the day
1. **Plan backwards from Evaluation 1** (assumed 11:30; §3 has an 11:00 version).
2. **Backend done = its tests pass AND the API answers correctly from the terminal.** Only then start that phase's UI.
3. **Freeze 25 min before each evaluation**: bug fixes, backup video, rehearsal only.
4. After any engine change: `python tests/test_engine.py` → ALL PASS.
5. Commit at every checkpoint (`git add -A && git commit -m "..."`). Roll back instead of debugging past 15 min.
6. After each checkpoint: a **5-minute Claude Code walkthrough**, so you can explain every file.
7. **You test, Claude Code builds.** Teammates run done-checks too.

---

## 1. Morning, before leaving (7:00–7:45)
- [ ] Laptop 100% + charger · **Ethernet cable** · phone hotspot · ID · formal dress
- [ ] Fresh VS Code → `python prep/tools/test_providers.py` (connectivity check only) → note which models answered
- [ ] **Real-user quote:** call 1–2 people; write their exact words (never invent one)

## 2. Registration (8:30–9:15): ask the organisers
- [ ] Exact time of **Evaluation 1** and **Evaluation 2**
- [ ] *"We researched the scheme rules and wrote a design document last night. Can we use them as reference? No app code is pre-built."* → **Plan A** (yes) / **Plan B** (no)
- [ ] Wi-Fi or Ethernet? Projector or desk demo?
- [ ] Brief teammates on their roles (§7)

---

## 3. Timeline
| Eval 1 at 11:30 | Eval 1 at 11:00 | Block | Layer | Done-check |
|---|---|---|---|---|
| 09:15–09:30 | 09:15–09:25 | **B0** Scaffold (+ Plan B: data) | setup | `/api/health` ok |
| 09:30–10:05 | 09:25–09:55 | **B1** Engine + tests | **backend** | `test_engine.py` ALL PASS |
| 10:05–10:45 | 09:55–10:25 | **B2** AI + accuracy layer + agent + API (H1–H3) | **backend** | API tests pass; accuracy test: 0 wrong facts, ≥ 15/18 automatic |
| 10:45–11:08 | 10:25–10:44 | **B3** UI for H1–H3 | **UI** | Full Eval 1 flow in the browser |
| 11:08–11:12 | 10:44–10:47 | ✅ **CP1** | — | Demo × 2 · privacy · offline |
| 11:12–11:30 | 10:47–11:00 | 🎬 **Freeze** | — | Video · walkthrough · rehearse × 2 |
| **11:30** | **11:00** | **EVALUATION 1** | | |
| 11:45–12:30 | same | **B4a** Backend MUST: letters + helper, Doctor wiring, sample-documents family, voice | **backend** | see §4a B4a |
| 12:30–12:55 | same | **B4b** Backend SHOULD: login + history, SMS outbox + summary, follow-up reminders | **backend** | see §4a B4b |
| 12:55–13:10 | same | 🍛 Lunch | | |
| 13:10–14:05 | same | **B5** UI: Fix · Doctor · Letters · Helper · voice · login/history · SMS outbox | **UI** | Full Eval 2 flow in the browser |
| 14:05–14:15 | same | ✅ **CP2** | — | Full Eval 2 run |
| 14:15–14:35 | same | **B6** Stretch: more verified schemes, source check | both | Only if CP2 passed |
| 14:35–15:00 | same | 🎬 **Freeze** | — | Video · cache warm-up · rehearse × 3 |
| **~15:00** | same | **EVALUATION 2** (ends ~15:20) | | |

**Phase 2 is defined by §4a (v5).** The old B4–B6 text below §4a is kept only for reference; UiPath is dropped.

---

## 4. Blocks: copy-paste instructions for Claude Code

### B0: Scaffold (09:15–09:30)
**Plan B only, first:**
> Recreate `data/schemes.json`, `data/documents.json`, `data/doctor_tree.json`, `data/questions.json`, `data/personas.json` from the rules and tables in `docs/02_DATA_VERIFICATION.md`, `docs/01_IDEA.md` and `docs/03_ARCHITECTURE.md` §7.

**Then:**
> Read `docs/03_ARCHITECTURE.md` and `docs/06_CONTRACTS.md`. Do not use anything in `prep/`. Create the skeleton per architecture §5: `config.py` (provider chain Groq `qwen/qwen3.8-27b` → Gemini `gemini-2.5-flash` with thinking_budget=0 → Groq `openai/gpt-oss-120b`; 8 s timeouts; `USE_LLM` flag; keys from env `GROQ_API_KEY`, `GEMINI_API_KEY`), `app.py` (FastAPI serving `static/` at `/` and `GET /api/health`), empty `engine/` modules, `tests/`, an empty `static/` folder with `vendor/tailwindcss-play-3.4.17.js` copied into it. `git init`, commit, run uvicorn on port 8000 and check `/api/health`.

**Done-check:** `http://localhost:8000/api/health` → ok.

---

### B1: Engine + tests (09:30–10:05), backend 🔑
> Build the deterministic engine per `docs/03_ARCHITECTURE.md` §7 and the shapes in `docs/06_CONTRACTS.md` §3–5, using the rules in `data/`: `engine/facts.py` (`patch(facts, path, value)` validating `family.<field>`, `member:<id>.<field>`, `member:<id>.docs.<doc>`, `member:<id>.names_as_printed.<doc>`, `task:<task_id>.done`; derived facts: KMUT head of family per `schemes.json` derived_facts, mixed land); `engine/rules.py` (verdicts per `_meta.verdict_algorithm` with TA/EN reasons marked ok true/false/null, source url, verification, checked date; ₹ total per `_meta.total_rules` incl. exclusive groups and conflicts); `engine/documents.py` (has-document per `documents.json` doc_fact_map; name check per `name_check.algorithm`, must pass its `test_cases`; matrix; missing documents; fix plan grouped by office, ordered by schemes unblocked, online checks first, task ids `<member>:<doc_or_task>`; trips per `trips_algorithm`); `engine/questions.py` (next question per `questions.json`); `engine/__init__.py` (`recompute(facts) -> Snapshot`, `diff(old, new) -> list[Event]` for verdict changes, ₹ change, tasks added/removed, trips change). Write `tests/test_engine.py` checking every expected result and edge case in architecture §7 plus the name-check test cases. Run until ALL PASS.

**Done-check:** `python tests/test_engine.py` → ALL PASS (Murugan ₹30,000 · trips 6 → 2 · ₹18,000 at income 3L · Lakshmi ₹14,400).
**Cut rule:** none; this block is non-negotiable.

---

### B2: AI + accuracy layer + agent + API for H1–H3 (10:05–10:45), backend
> Build per `docs/03_ARCHITECTURE.md` §6, §6.2a and §8, `docs/06_CONTRACTS.md` §1–4, and the "understand" prompt with its few-shot examples in `docs/05_PROMPTS_AND_PITCH.md` §1: `pii_guard.py` (remove 12-digit and 9–18-digit numbers; report removal); `amounts.py` (deterministic Tamil/English amount parser: லட்சம்/lakh, ஆயிரம்/thousand, ஒன்றரை/இரண்டரை/அரை, monthly ×12, every two months ×6); `llm.py` (`understand(text, card, last_question) -> dict | None`: small cache in `llm_cache.json` keyed by hash(text + compact card); calls **Groq `qwen/qwen3.8-27b` (reasoning_effort "none") and Groq `openai/gpt-oss-120b` (reasoning_effort "low") in parallel**, JSON mode, temperature 0, 8 s timeout; if one fails, Gemini 2.5 flash (JSON, thinking_budget=0) replaces it; returns both results + providers + ms); `accuracy.py` (per §6.2a: normalise paths, keep only allowed paths/actions, evidence must appear in the message, range/type checks, `amounts.py` cross-check, two-model agreement → `accepted` facts + `ask` list of clarifying questions with options; single-model mode marks facts "please confirm"); `agent.py` (`handle(session, text)` exactly per §6.3, events in the contract shape with the wording in `05_PROMPTS_AND_PITCH.md` §2, reply composed per §1.4; auto-add update_facts; offline mode when understand returns None; `load_persona(session, name, direct)` feeding `scripted_answers_ta` through `handle`, or loading facts directly). API routes: `/api/session`, `/api/chat`, `/api/facts`, `/api/task`, `/api/demo/{persona}`. In-memory sessions. Write `tests/test_api.py` using FastAPI's TestClient that: posts the 9 Murugan Tamil lines and checks verdicts, ₹30,000 and trips 6 → 2; posts "இல்லங்க, வருமானம் 90,000 இல்ல, 3 லட்சம்." and checks KMUT NOT_ELIGIBLE, ₹18,000 and replan events; posts "my Aadhaar is 1234 5678 9012" and checks the privacy event and that the AI never received the number; checks `/api/demo/murugan_family?direct=1` works with `USE_LLM=False`. Also write `tests/test_understand.py` that runs every case in `data/eval_utterances.json` through `llm.understand` + `accuracy.py` and checks: **0 wrong facts applied on all 18** and **≥ 15/18 applied automatically** (the rest must produce a clarifying question); plus unit tests for `amounts.py` ("ஒன்றரை லட்சம்" → 150000, "மாசம் 8000" → 96000/yr, "150 units every two months" → 900).

**Done-check:** `python tests/test_api.py` and `python tests/test_understand.py` → ALL PASS (0 wrong facts). **The backend for Eval 1 is now complete.**
**Cut rule:** AI misbehaving after 15 min → `USE_LLM=False` + direct persona loading; mark the AI tests as skipped; fix the AI after CP1.

---

### B3: UI for H1–H3 (10:45–11:08), UI
> The backend for H1–H3 is finished and tested. Now build the UI: `static/index.html`, `static/app.js`, `static/style.css`, following **`docs/07_UI_UX_BRIEF.md` closely** (two faces: calm family side, dark agent panel; colours, Tamil-first fonts, layout, components, motion, microcopy) and calling the real API per `docs/06_CONTRACTS.md`. Include for now: top bar (wordmark, TA/EN toggle, persona buttons, Clear), consent banner, chat column, family card with member chips and tap-to-edit facts (POST /api/facts), scheme cards, ₹ meter (count animation), trips, and the agent panel replaying `events` 250 ms apart with the marigold re-plan glow and the card flip. Desktop 3 columns; phone bottom tabs; `?present=1` presentation mode. Save facts + tasks in localStorage and restore on reload. Leave Fix / Doctor / Letters / Helper as empty tabs for Phase 2.

**Done-check:** Load Murugan → events replay → 3 scheme cards → ₹30,000 → tap income → 300000 → glow + card flip + ₹ counts to 18,000. Two Tamil lines typed live work.
**Cut rule:** at 11:00 → stop styling; the panel, cards, ₹ meter and re-plan must work.

### ✅ CP1 (11:08–11:12)
- [ ] Demo × 2 · 2 Tamil lines live · 12-digit number → 🔒 · network off → offline mode
- [ ] `tests/test_engine.py` + `tests/test_api.py` ALL PASS · commit "cp1"
- [ ] *"Give me a 5-minute walkthrough of every file and how a chat message flows through them."*

### 🎬 Freeze before Eval 1 (11:12–11:30)
- [ ] Backup video (2 min): `Win + Alt + R` or OBS
- [ ] Run the Murugan lines once (warms the cache)
- [ ] Rehearse the Eval 1 script (`05_PROMPTS_AND_PITCH.md` §4) twice, ≤ 5 min · open `?present=1`

### EVALUATION 1: "It understands and decides"
Per `05_PROMPTS_AND_PITCH.md` §4. Teammate 1 writes down every judge comment.

---

## 4a. Phase 2 final scope (v5): what to build, part by part

**Progress (9 Oct):** **P1, P2 and P3 are done** (commit `fc363a5`, 52 tests pass). Next: P4.
**Mapping to `01_IDEA.md` v2:** P1–P3 = H4/H5 · P4 = H6 · P5 = F1 · P6 = F2 · P7 = F3 · P8 = S1 · P9 = S2.

**Changes since v4:**
- UiPath robot dropped. Thunai **prepares** the application; the family or helper **submits** it on the official site.
- UI is the government-portal style, with no emojis.
- Added after the judge's and team's input: login + chat history, a sample-documents family, SMS outbox + summary, follow-up reminders, more verified schemes, and a source check.

**Already built (do not rebuild):**
- `engine/doctor.py` + `/api/doctor`
- `/api/task` (tick a task → re-plan events)
- `member:<id>.names_as_printed.<doc>` facts
- `analyse()`: name matrix, fix plan by office, trips
- `load_persona()` and the Meena / Lakshmi buttons

**Honesty rules (apply to every part):**
- No real or realistic government document images. Sample documents are **data cards marked "SAMPLE"**, with no Aadhaar or bank numbers.
- Thunai never submits to a government site, never sees government records, and never asks for Aadhaar, bank or OTP numbers.
- Doctor outcomes say **"most likely cause"**.
- Letters stay **DRAFT** until a helper approves them.
- No real SMS is sent (it needs money and DLT registration). Messages go to an **SMS outbox** shown on screen; a provider can be plugged in later. The WhatsApp share link is free and works now.
- A scheme is **enabled only with an official source + checked date**; otherwise it stays disabled.

### Parts

| # | Part | Layer | Priority |
|---|---|---|---|
| P1 | Letters + helper approval | backend | MUST · ✅ done |
| P2 | Doctor → letter / helper wiring | backend | MUST · ✅ done |
| P3 | Sample-documents family ("Revathi") | backend + data | MUST · ✅ done |
| P4 | Voice: speech-to-text + text-to-speech | backend | MUST |
| P5 | Login + chat history | backend | SHOULD |
| P6 | SMS outbox + summary SMS + WhatsApp share | backend | SHOULD |
| P7 | Follow-up: "15 days later" reminders + new-scheme re-match | backend | SHOULD |
| P8 | More verified schemes (target 8–9) | data + tests | STRETCH (links gathered earlier by a teammate) |
| P9 | Source check (did the official page change?) | backend | STRETCH |
| U1–U8 | UI for all of the above | UI | as their part |

#### P1: Letters + helper approval (MUST)

**Code:** `engine/letters.py` + `templates/*.html`.
- Letters are **deterministic templates** filled from facts. They are written in polite, simple official Tamil plus English and read as human-written, but no AI is used, so names and numbers are always exact.

**Kinds:**
- `application_pack`: per eligible scheme, the facts, documents checklist, where to apply and the official link.
- `name_correction_request`
- `bank_seeding_request`
- `grievance`: KMUT portal / CM Helpline text.
- `appeal_kmut`
- `appeal_pension`
- `available_kinds()` hides any kind that isn't built.

**Endpoints:**
- `POST /api/letter {session_id, kind, member_id}` → draft into the helper queue, plus an agent event "Drafted …, waiting for helper approval".
- `GET /api/helper/queue`
- `POST /api/helper/approve {letter_id}`
- `GET /letter/{id}`: A4 page; DRAFT watermark until approved; Print only when approved.

**Done-check:**
- The Murugan application pack names all 3 schemes.
- Lakshmi's appeal contains "Lakshmi".
- Approve → no watermark.

#### P2: Doctor wiring (MUST)
- A Doctor outcome with `draft_letter` offers that letter (P1). `escalate_to_helper` adds a helper-queue item with the reason.
- The outcome's office is added to the fix plan.
- `/api/demo/meena` and `/api/demo/lakshmi_paati` play their full flows.

**Done-check:**
- Meena: yes → no → `o_seeding` → bank seeding letter draft.
- Lakshmi → appeal draft.

#### P3: Sample-documents family "Revathi" (MUST)
**Data:** a new persona `revathi_docs` in `data/personas.json`, with documents as SAMPLE cards (document, name as printed, DOB, address; no numbers).

**Problems built in:**
- Aadhaar says "Revathi Sekar", the ration card "S. Revathi", the passbook "REVATHI S" (name conflict).
- The husband's death certificate is not with her (missing).
- *(An income certificate is not in our verified document rules for these schemes, so it isn't used.)*
- Aadhaar is not linked to the bank account in use.

**Endpoint:** `GET /api/sample_docs/{persona}` returns the cards.

**Expected:**
- The matrix shows a name risk.
- The fix plan groups the tasks into the fewest visits.
- Letters are offered: `name_correction_request` and `bank_seeding_request`.
- If a problem stays stuck, a `grievance` is offered.
- The exact scheme list is whatever the rules engine says; never hard-code verdicts.

**Done-check (passed):**
- name check RED;
- missing: death certificate + bank linking;
- the passbook name fix happens in the bank visit (each name fix goes to the office that issued the document);
- trips **4 → 3**;
- the name correction and bank letters are suggested;
- ticking a fix leads to "Completed".

#### P4: Voice (MUST)
**Code:** `voice.py` per `03_ARCHITECTURE.md` §4a.
- `POST /api/stt`: Groq `whisper-large-v3`, "ta"/"en" → `{text, ms}`.
- `POST /api/tts`: edge-tts `ta-IN-PallaviNeural` / `en-IN-NeerjaNeural` → MP3, cached in `tts_cache/`.
- Numbers that came from voice are always marked "please confirm".

**Done-check:** TTS → STT round trip ≥ 85% similar.

#### P5: Login + chat history (SHOULD)
**Storage:** `store.py` with stdlib `sqlite3` → `thunai.db` (gitignored).
- `users(phone, pin_hash, role, created)`: PIN hashed with `hashlib.pbkdf2_hmac` + salt.
- `chats(id, user, title, facts_json, events_json, updated)`.

**Beneficiary login:** phone + 4-digit PIN.
- Why not OTP: real OTP SMS costs money, and the app tells people never to share an OTP.

**Helper login:** username + password. One demo helper account is seeded.

**Endpoints:**
- `/api/auth/register`, `/api/auth/login` → token (random, server memory), `/api/auth/logout`
- `/api/history`: the user's chats, newest first.
- `/api/history/{id}`: reopen a chat with its facts, plan and events.
- `DELETE /api/me`: delete all of the user's data.
- Helper-only routes check the role.

**Privacy:**
- Consent checkbox at registration.
- The phone number is never sent to the AI (`pii_guard` already strips 9–18-digit numbers).
- **The demo buttons keep working without login (guest)**, so the demo never blocks on a login screen.

**Done-check:**
- Register → chat → logout → login → the chat is listed and reopens identically.
- A wrong PIN is refused.
- A beneficiary can't call the helper routes.

#### P6: SMS outbox + summary (SHOULD)
**Code:** `engine/notify.py`.
- `summary_sms(snapshot, lang)`: ≤ 3 SMS segments in Tamil, for example: "Thunai: eligible for 3 schemes (about ₹30,000/year). Next: Bank — link Aadhaar; Panchayat office — death certificate. Never share your OTP."
- Outbox table `outbox(id, phone, text, reason, created)`.

**Endpoints:**
- `POST /api/sms/summary`
- `GET /api/outbox`
- `config.SMS_PROVIDER = None` → outbox only.

**UI:** "Send summary" + "Share on WhatsApp" (`https://wa.me/?text=`, free).

**Done-check:** the summary contains the ₹ figure and the first office; it's ≤ 480 characters.

#### P7: Follow-up reminders + new-scheme re-match (SHOULD)
**Code:** `engine/proactive.py`, `simulate(state, days)`:
- each open task → a reminder;
- a KMUT appeal within 5 days of its 30-day deadline → an urgent reminder;
- a task open > 14 days → escalate to the helper with a reason.

**Re-match:** `rematch()` re-runs `recompute()` for every saved family against the current `schemes.json`. A family that is newly ELIGIBLE gets "New scheme for you: …" in the outbox.

**Endpoints:** `POST /api/simulate {session_id, days}`, `POST /api/rematch`. Events are tagged "Follow-up (automatic)".

**Done-check:** simulate 15 days on Murugan → reminders + an outbox SMS. Enable a test scheme → rematch → the matching family gets one SMS.

#### P8: More verified schemes (STRETCH; links gathered earlier)
**Candidates:**
- Tamil Pudhalvan (currently disabled)
- TN differently-abled maintenance allowance
- TN unmarried / deserted women pension
- PM Matru Vandana Yojana

**Rules:**
- **Official source + checked date or it stays disabled.** Rules come from the official text only.
- Each new scheme needs: `required_documents`, `where_to_apply`, `official_sources`, `verification`, one ELIGIBLE test and one NOT_ELIGIBLE test.
- No code change, only `data/schemes.json` (+ `documents.json`).

#### P9: Source check (STRETCH)
- `GET /api/admin/check_sources` (helper only): fetch each `official_sources` URL (5 s timeout) and compare the hash of its text with `data/source_hashes.json`.
- Result per scheme: "unchanged", "**changed: needs review**", or "unreachable".
- Data older than 30 days → "information may be old".
- **It never edits rules**; a person reviews and updates `schemes.json`.

#### UI parts (B5): government style, real API only

| # | UI | Contents |
|---|---|---|
| U1 | **Fix tab** | People × documents table (Match / Name risk / Missing, with the reason on click); "name as printed" form; missing documents with where to get each; fix plan per office (what to bring, "unblocks N schemes", Done checkbox → re-plan in the activity log); "visits 2 (instead of 6)" |
| U2 | **Doctor tab** | 4 entry buttons; Yes / No / Don't know; outcome: most likely cause, "check in 1 minute" link, numbered fix steps, "Draft letter" button |
| U3 | **Letters + Helper tabs** | Draft list; A4 preview with DRAFT watermark; helper queue with the agent's reason; Approve → Print |
| U4 | **Voice** | Mic button next to the chat input (transcript is editable before sending); speaker toggle in the header; "please confirm" on spoken numbers |
| U5 | **Login + history** | Login / Register (phone + PIN, consent), "Continue as guest"; "Previous conversations" list; "Delete my data"; helper login |
| U6 | **SMS outbox + follow-up** | Outbox panel (to, message, reason, time); "Send summary", "Share on WhatsApp"; "Simulate 15 days later" button |
| U7 | **Sample documents** | Revathi button in the navy bar; SAMPLE document cards above the Fix table |
| U8 | (stretch) **Admin** | Source check results, "needs review" tags |

### Order, done-checks and cut rules
- **B4a (11:45–12:30):** P1 → P2 → P3 → P4.
  - P1 templates can run as a background subagent while P3 is built.
  - Done: `pytest` ALL PASS, plus the P1–P4 done-checks from the terminal. **Commit + push.**
- **B4b (12:30–12:55):** P5 → P6 → P7.
  - Done: P5–P7 done-checks. **Commit + push.**
- **B5 (13:10–14:05):** U1 → U2 → U3 → U7 → U4 → U6 → U5.
  - Done: the full Eval 2 story below works in the browser. **Commit + push.**
- **CP2 (14:05–14:15):** the full story twice; all tests pass; commit "cp2" + push.
- **B6 (14:15–14:35):** P8 → P9 → U8. Commit + push each.

**Cut order if late:** P9 → P8 (keep 5 schemes) → P7 re-match → P5 helper login (the helper tab works without login) → P5 entirely (the history list then uses this browser only) → speech-to-text (keep text-to-speech).

**Never cut:** P1, P2, P3, U1–U3, the re-plan and the activity log.

### Eval 2 demo story (about 5 min)
1. **Login** with phone + PIN → "Previous conversations" shows the earlier Murugan chat → reopen it. *(Memory)*
2. **Revathi (sample documents)** → the Fix tab shows the name conflict, the missing death certificate and the unlinked bank → fix plan in the fewest visits → tick a task → the activity log re-plans. *(Find problems, fix them)*
3. **Draft the name correction letter** → helper logs in → approves → Print. *(Humans approve)*
4. **Meena: money stopped** → 3 questions → "Aadhaar not linked to the account you use" → bank seeding letter. *(Doctor)*
5. **Simulate 15 days later** → reminders + SMS outbox; **Send summary** / WhatsApp share. *(Follow until resolved)*
6. **Voice:** speak a Tamil sentence → the reply is spoken in Tamil. *(Inclusion)*
7. (If built) **Source check** → every scheme shows its official link + checked date. *(Trust)*

**Must exist at the end (v5):**
- Root files: `app.py config.py llm.py agent.py accuracy.py pii_guard.py amounts.py voice.py store.py`
- Engine: `engine/{__init__,data,facts,rules,documents,questions,doctor,letters,notify,proactive}.py`
- Letters: `templates/*.html`
- Front end: `static/{index.html,app.js,style.css,tailwindcss-play-3.4.17.js}`
- Data: `data/*.json`
- Tests: `tests/test_engine.py test_api.py test_understand.py test_modules.py test_phase2.py`, all passing
- Generated at runtime, gitignored: `thunai.db tts_cache/ llm_cache.json`

**Team roles (v5):**
- The former UiPath teammate gathers official links for the P8 schemes during B4 and runs the done-checks.
- Teammate 1 keeps the bug list and records the backup video.
- Teammate 2 prepares the Eval 2 slides and Q&A.

---

### B4: Backend for H4–H5 + voice (11:45–12:40), backend (+ MOD-1 in parallel)
**First, the modules subagent (backend work, in parallel):**
> Use a background subagent to build `engine/doctor.py`, `engine/letters.py`, `templates/` and `tests/test_modules.py`. Task for it: "Implement the pure functions in `docs/06_CONTRACTS.md` §5: `doctor.entry_points / start / answer` over `data/doctor_tree.json` ('dont_know' follows 'no'; outcomes in the DoctorStep shape incl. `path`); `letters.render_application_pack`, `letters.render_appeal`, `letters.available_kinds` producing complete printable A4 HTML (Tamil + English) using the templates and rules in `docs/05_PROMPTS_AND_PITCH.md` §3 and the look of letters in `docs/07_UI_UX_BRIEF.md` §5 (paper style, DRAFT / வரைவு watermark until approved). Appeal kinds: `appeal_kmut` and `appeal_pension`. No network, no global state, UTF-8. Tests: Meena's path ends at `o_seeding`, Lakshmi's at `o_fix_doc_and_petition`; each letter contains the member's name. Only edit those files."

**Then, main session:**
> Complete the backend for H4–H5 per `docs/03_ARCHITECTURE.md` §6.2 and §8 and `docs/06_CONTRACTS.md`: make sure `/api/facts` accepts `member:<id>.names_as_printed.<doc>` and `/api/task` toggles done flags, both returning re-plan events; add `/api/doctor` (entry + answers → DoctorStep) and wire the agent's `start_doctor` / `doctor_answer` actions; when MOD-1 is done, add `/api/letter` (drafts into the helper queue: application_pack from verdicts + plan, appeal from the Doctor outcome), `/api/helper/queue`, `/api/helper/approve`, `/letter/{id}` (printable page; Print only when APPROVED; hide kinds not in `available_kinds()`), and make `/api/demo/meena` and `/api/demo/lakshmi_paati` run their flows. Also, for the UiPath robot (`docs/08_UIPATH_ROBOT.md`): when a helper approves an Application Pack, write `handoff/application.json` with exactly the keys in §3 (for the KMUT applicant), create `static/mock_esevai.html` with exactly the field ids in §4 (plain HTML, "DEMO, NOT A GOVERNMENT SITE" banner), and add `GET /api/robot/status` that reads `handoff/robot_result.json` and returns a 🤖 event ("UiPath robot filled the e-Sevai form; waiting for the human to submit"). Also add `voice.py` per `docs/03_ARCHITECTURE.md` §4a: `POST /api/stt` (multipart audio → Groq `whisper-large-v3`, language "ta" or "en" → `{text, ms}`) and `POST /api/tts` (`{text, lang}` → edge-tts `ta-IN-PallaviNeural` / `en-IN-NeerjaNeural` → `audio/mpeg`, cached in `tts_cache/` by hash of text + voice); numbers in a turn that came from voice are marked "please confirm" by the accuracy layer. Extend `tests/test_api.py`: `/api/tts` returns MP3 bytes for a Tamil sentence; `/api/stt` transcribes that MP3 back with ≥ 85% similarity; Murugan trips 6 → 2, Kavya YELLOW, bank visit first with 2 tasks; ticking Selvi's task produces replan events; Meena → yes → no → o_seeding; Lakshmi → appeal draft → approve → `/letter/{id}` returns HTML containing "Lakshmi"; Murugan application pack contains all 3 schemes.

**Done-check:** `python tests/test_modules.py` and `python tests/test_api.py` → ALL PASS. **The backend for Eval 2 is now complete.**
**Cut rule:** 12:30 and the letters aren't done → English-only letters.

### 🍛 Lunch (12:40–13:00)

---

### B5: UI for Fix · Doctor · Letters · Helper + voice (13:00–13:55), UI
> The backend for H4–H5 is finished and tested. Build the four tabs in `static/` following `docs/07_UI_UX_BRIEF.md` §5–§7 and calling the real API: **Fix** (Consistency Matrix with coloured dots and tap-for-reason; a small "name as printed" form per person; missing documents with where to get each one; fix-plan cards by office 🏦 🏢 📱 with "unblocks N schemes", what to bring and Done checkboxes that trigger re-plan events in the agent panel; "🚌 6 → 2" with a how-we-count tooltip), **Doctor** (4 big entry buttons; Yes / No / Don't know cards; outcome card with cause, a "check in 1 minute" link button and numbered fix steps), **Letters** (create an Application Pack or appeal → paper preview with DRAFT watermark), **Helper** (queue with the agent's reason, green Approve → watermark disappears, Print button). Add Load Meena / Load Lakshmi to the top bar. On phones these live inside the Fix and Schemes tabs. **Voice mode** (`03_ARCHITECTURE.md` §4a): a large 🎤 hold-to-talk button next to the chat input (MediaRecorder → `/api/stt` → transcript placed in the input box, editable, auto-send after 3 s unless edited; recording indicator; hidden if the browser blocks the mic) and a 🔊 speaker toggle in the top bar (when on, each reply is played via `/api/tts`; numbers from voice show a "please confirm" chip).

**Done-check:** Murugan → Fix: Kavya 🟡 · 🏦 Bank (2 tasks) first · **6 → 2** · tick a task → panel re-plans · Meena → yes → no → "Aadhaar not linked to the account you use" · Lakshmi → DRAFT → Approve → Print preview · Murugan → Application Pack prints · **speak a Tamil sentence → transcript appears → reply is spoken in Tamil**.
**Cut rule:** 13:45 → skip the names form (the personas contain names) and keep the rest.

### ✅ CP2 (13:55–14:05)
- [ ] Full Eval 2 run: Murugan (Find → re-plan → Fix → trips → Pack) → Meena (Doctor) → Lakshmi (appeal → approve → print)
- [ ] All tests ALL PASS · commit "cp2" · 5-minute walkthrough of the new files

---

### B6: Stretch (14:05–14:35, only if CP2 passed): backend first, then the button
**S1 ⏩ Proactive:**
> Backend: add `engine/proactive.py` (`simulate` per `06_CONTRACTS.md` §5) and `POST /api/simulate`: after N days each To-do task → 🤖 reminder; a KMUT appeal within 5 days of its 30-day deadline → urgent reminder; a task open > 14 days → escalate to the helper queue with a reason; add a test. Then UI: a "⏩ 15 days later" button whose events play in the agent panel as 🤖 AUTONOMOUS.

**S5 🤖 Robot fallback (only if the UiPath robot isn't ready):**
> Create `robot/fill.py` (Playwright) that opens `http://localhost:8000/mock_esevai.html` in a visible browser and fills it field by field from `handoff/application.json`, slowly, stopping before Submit (a human submits). (Needs `pip install playwright` + `playwright install chromium`.)

**Cut rule:** 14:35 → stash unfinished work; freeze.

### 🎬 Freeze before Eval 2 (14:35–15:00)
- [ ] Bug fixes only · backup video (3 min) · run all 3 personas once (cache) · rehearse the Eval 2 script (`05` §5) × 3 · `?present=1` · Clear before judges arrive

### EVALUATION 2: "It fixes and follows through"
Per `05_PROMPTS_AND_PITCH.md` §5; Q&A per §6.

---

## 5. If something breaks
| Problem | Immediate action |
|---|---|
| AI failing | Automatic backups; if all fail, `USE_LLM=False` + Load persona (direct). Say: "the rules engine never needs the AI to decide." |
| Wi-Fi down | Ethernet → hotspot → offline mode → backup video |
| Backend crash | Restart uvicorn (5 s) → backup video |
| UI shows wrong / empty data | Check the API response in the browser (Network tab) against `06_CONTRACTS.md`; the backend is tested, so fix the UI field name |
| Engine test fails after a change | `git checkout -- engine/<file>.py` |
| Behind schedule | Apply the block's cut rule; never cut B1, B2's tests, the agent panel or the re-plan |

## 6. Reporting bugs to Claude Code
**What you did → what you expected → what you saw:** "I clicked Load Murugan; expected ₹30,000; the meter shows ₹0; the Network tab shows `rupees_per_year: 30000`."

## 7. Team roles
| Person | During the build | During evaluations |
|---|---|---|
| **You** | Drive Claude Code; check every done-check; understand every file (walkthroughs) | Live demo + technical answers |
| **Teammate 1** | Run done-checks with you; keep the bug list; record backup videos; note judge comments | Problem + evidence + impact |
| **Teammate 2** | 5 slides (`05` §7); rehearse timing | Q&A on research, sources, responsible AI |
| **UiPath builder** (whichever teammate knows UiPath best) | Builds the **UiPath e-Sevai form-filler robot** in parallel per `docs/08_UIPATH_ROBOT.md` (Studio installed before 9:00) | Runs the robot live in Eval 2 and explains "agent decides → UiPath robot acts → human approves" |

## 8. Must exist at the end
```
app.py config.py llm.py llm_cache.json agent.py pii_guard.py amounts.py accuracy.py voice.py tts_cache/
engine/__init__.py facts.py rules.py documents.py questions.py doctor.py letters.py (proactive.py)
templates/*.html · static/index.html app.js style.css tailwindcss-play-3.4.17.js
tests/test_engine.py · tests/test_api.py · tests/test_understand.py · tests/test_modules.py (ALL PASS) · data/*.json · docs/*
```
