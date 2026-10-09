# Thunai (துணை) — a Scheme Sathi agent for Tamil Nadu families

**CTRL+AI Inter-College Agentic AI Challenge · PS-10 "Scheme Sathi" · Sri Sairam Engineering College · 9 Oct 2026**

> Other tools tell you which schemes exist. Thunai helps your family **get the money**: it finds what you're owed,
> fixes what would get you rejected, and follows up until it arrives, in Tamil.

**Find → Fix → Follow** · *Rules decide · AI understands · Humans approve*

---

## What it does
| | |
|---|---|
| **Find** | The family talks in Tamil or English (typed or spoken). Two AI models read each message and must agree, quoting the user's words. A deterministic rules engine checks **8 officially verified schemes** for the whole family and shows each rule, its official source and the date checked. |
| **Fix** | Finds missing documents and **name mismatches across documents** (e.g. "S. Revathi" vs "Revathi Sekar"), and plans the fixes **by office** with the fewest visits. Ticking a task re-plans the agent. |
| **Follow** | Drafts **6 kinds of letters** in Tamil + English (application pack, name correction, bank Aadhaar-linking, complaint, KMUT appeal, pension petition). A **signed-in helper must approve** before printing. The **"money stopped?" problem finder** walks yes/no questions to the most likely cause. **"15 days later"** follow-up sends reminders and escalates stuck tasks to a helper; an **SMS outbox** (real SMS when a provider is configured) and WhatsApp share; **re-check of saved families** when new schemes are added. |

The **agent activity log** shows every goal, plan, decision, action and re-plan live.

## Quick start
```powershell
cd scheme-sathi
pip install -r requirements.txt

# Free AI keys (Groq for the two models + Whisper voice; Gemini as backup)
setx GROQ_API_KEY "your-groq-key"
setx GEMINI_API_KEY "your-gemini-key"
# (open a new terminal after setx; on Windows the app also reads keys saved this way)

python -m uvicorn app:app --port 8000
```
Open **http://localhost:8000**.

| Sign in as | How |
|---|---|
| Guest (demo) | **Continue as guest**: nothing is saved |
| Family | **Register** with any 10-digit mobile number starting 6–9 and a 4-digit PIN (consent required) |
| Helper | username `helper`, password `helper123` (approves letters; can check sources and re-check saved families) |

**Demo families** (blue bar): **Murugan** (3 schemes, ₹30,000/yr, visits 6 → 2; edit income to 300000 → ₹18,000), **Revathi** (sample documents with name conflicts), **Meena** ("my ₹1,000 stopped"), **Lakshmi** (pension rejected → petition).

Optional settings: `USE_LLM=0` runs fully offline (scripted questions; demo families still load). Real SMS: `SMS_PROVIDER=twilio`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM` (otherwise messages stay in the outbox). To reset saved accounts, stop the server and delete `thunai.db` (the helper account is re-created).

## How it works
```
Family (text / voice) ─► Privacy guard (removes Aadhaar / bank numbers) ─► 2 AI models must agree (+ evidence, number checks)
        ─► Rules engine (official rules) · Document checker (names, missing docs, trips) · Problem finder (decision trees)
        ─► Letters (templates, no AI) ─► Helper approves ─► Print      ·      Follow-up ─► reminders / escalation / SMS outbox
```
- **Stack:** Python 3.12 · FastAPI · SQLite (accounts, chats, outbox) · Groq (`qwen/qwen3.8-27b` + `openai/gpt-oss-120b`, `whisper-large-v3`) · Gemini 2.5 Flash (backup) · edge-tts (Tamil neural voice) · one HTML/JS page (government-portal style, Tamil + English, phone-friendly).
- **The AI never decides eligibility.** It only extracts facts; rules from official documents decide.
- **Offline:** everything except chat understanding and voice works without internet; the chat falls back to an offline mode.

## Schemes (all checked on official government pages, 9 Oct 2026)
PM-KISAN · Kalaignar Magalir Urimai Thogai · Pudhumai Penn · Tamil Pudhalvan · Destitute Widow Pension · Old Age Pension (IGNOAPS) · Destitute / Deserted Women Pension · Unmarried Women Pension (50+). Each scheme is a JSON rule set in `data/schemes.json` with its sources; adding a scheme needs no code change. Details: `docs/02_DATA_VERIFICATION.md`.

## Privacy and safety
- Never asks for Aadhaar numbers, bank account numbers or OTPs; the privacy guard strips them before any AI call.
- PINs are stored only as PBKDF2 hashes; phone numbers are shown masked; **Delete all my data** removes everything.
- Letters leave account numbers blank; sample documents carry no ID numbers; SMS always say "never share your OTP".
- Thunai **prepares**; the family **submits**; the department **decides**. It cannot see government records, so the problem finder says "most likely cause".

## Tests
```powershell
python -m pytest            # 149 offline tests: engine, API, letters, every problem-finder path, accounts, SMS, re-match, schemes
$env:RUN_LIVE=1; python -m pytest tests/test_api.py tests/test_follow.py   # live AI + voice tests (uses free quota)
```

## Project layout
```
app.py            FastAPI routes + static page        agent.py      the agent loop, letters, helper queue, problem finder
llm.py            two-model understanding (+ backup)   accuracy.py   agreement, evidence and number checks
pii_guard.py      privacy guard                        voice.py      speech-to-text / text-to-speech
store.py          SQLite: users, chats, tokens, outbox sms.py        SMS delivery (provider or outbox)
routes_auth.py    sign-in, history                     routes_admin.py  helper tools (source check, re-match)
engine/           rules, facts, documents, questions, problem finder, letters, follow-up, sources (pure Python)
data/             scheme rules, documents, decision trees, questions, demo families
static/           index.html, app.js, phase2.js, account.js, style.css      templates/  letter page
tests/            pytest suites                        docs/         idea, data, architecture, build plan, pitch, contracts, UI
```

## Honest limits
- Real SMS delivery needs an SMS account (the code path is tested against a simulated service).
- Real OTP login is not used (by design: we use a PIN).
- Thunai does not submit applications or read government databases.
- Tamil text for the newest schemes should be reviewed by a native speaker.
