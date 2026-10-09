# Thunai (துணை) — a Scheme Sathi agent for Tamil Nadu families

CTRL+AI Inter-College Agentic AI Challenge · PS-10 · 9 Oct 2026

**Find → Fix → Follow:** an AI agent that finds the government schemes a family qualifies for, fixes the
paperwork problems that get applications rejected or payments stopped, and follows up on pending actions,
in Tamil. *Rules decide · AI understands · humans approve.*

## Repository contents before the event (design + research only)
- `docs/` — idea, verified data report, architecture, build plan, prompts & pitch, API contracts, UI/UX brief
- `data/` — scheme rules researched from official government sources, documents, decision trees,
  question bank, demo personas, accuracy test sentences
- `vendor/` — third-party library (Tailwind CSS Play 3.4.17, MIT) for offline use

All application code is written during the event.

## Run (after the build)
```
pip install fastapi uvicorn pydantic groq google-genai edge-tts pytest
set GROQ_API_KEY=...   set GEMINI_API_KEY=...
uvicorn app:app --port 8000
```
