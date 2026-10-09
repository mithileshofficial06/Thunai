"""Thunai web app: FastAPI routes + the static single-page UI."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import config

app = FastAPI(title="Thunai — Scheme Sathi agent")


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "use_llm": config.USE_LLM,
        "groq_key": bool(config.GROQ_API_KEY),
        "gemini_key": bool(config.GEMINI_API_KEY),
    }


# Mounted last so /api routes take priority.
app.mount("/", StaticFiles(directory=config.STATIC_DIR, html=True), name="static")
