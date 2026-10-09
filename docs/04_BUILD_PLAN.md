# Stage 4: Build Plan — Thunai 🔒 FINAL (v4: backend first, UI last)

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
| 11:45–12:40 | same | **B4** Backend for H4–H5 + voice (Fix, Doctor, letters, helper, STT/TTS) | **backend** (+ MOD-1 subagent in parallel) | API tests: trips 6 → 2; Meena → o_seeding; Lakshmi letter; approve; TTS → STT round trip |
| 12:40–13:00 | same | 🍛 Lunch | | |
| 13:00–13:55 | same | **B5** UI for Fix · Doctor · Letters · Helper + 🎤🔊 voice | **UI** | Full Eval 2 flow in the browser, incl. voice |
| 13:55–14:05 | same | ✅ **CP2** | — | Full Eval 2 run |
| 14:05–14:35 | same | **B6** Stretch: S1 ⏩ (backend → button) → S5 🤖 | both | Only if CP2 passed |
| 14:35–15:00 | same | 🎬 **Freeze** | — | Video · cache warm-up · rehearse × 3 |
| **~15:00** | same | **EVALUATION 2** | | |

If Eval 2 is earlier than 15:00: drop B6, then English-only letters.

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
