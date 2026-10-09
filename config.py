"""Thunai configuration: AI providers, timeouts and feature flags.

All model names live here so they can be swapped in one place if a free model changes.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
STATIC_DIR = ROOT / "static"
HANDOFF_DIR = ROOT / "handoff"
LLM_CACHE_FILE = ROOT / "llm_cache.json"
TTS_CACHE_DIR = ROOT / "tts_cache"


def _env(name: str) -> str:
    """Read an environment variable; on Windows fall back to the saved user variable
    (keys saved with `setx` are not visible to terminals opened before they were saved)."""
    value = os.environ.get(name, "")
    if value or os.name != "nt":
        return value
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            return winreg.QueryValueEx(key, name)[0]
    except OSError:
        return ""


GROQ_API_KEY = _env("GROQ_API_KEY")
GEMINI_API_KEY = _env("GEMINI_API_KEY")

# Two models run in parallel and must agree (accuracy layer); Gemini replaces one that errors.
GROQ_PRIMARY_MODEL = "qwen/qwen3.8-27b"
GROQ_SECOND_MODEL = "openai/gpt-oss-120b"
GEMINI_BACKUP_MODEL = "gemini-2.5-flash"
LLM_TIMEOUT_S = 8

# Voice
STT_MODEL = "whisper-large-v3"
TTS_VOICE_TA = "ta-IN-PallaviNeural"
TTS_VOICE_EN = "en-IN-NeerjaNeural"

# SMS: outbox only unless a provider is configured (SMS_PROVIDER=twilio + the three Twilio settings).
SMS_PROVIDER = _env("SMS_PROVIDER").strip().lower() or None
TWILIO_ACCOUNT_SID = _env("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = _env("TWILIO_AUTH_TOKEN")
TWILIO_FROM = _env("TWILIO_FROM")

# Set USE_LLM=0 to run fully offline (scripted questions + direct persona loading).
USE_LLM = os.environ.get("USE_LLM", "1") != "0"
