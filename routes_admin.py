"""Admin routes. Prototype: no auth -- protect before any real deployment."""
from fastapi import APIRouter

from engine import sources

router = APIRouter()


@router.get("/api/admin/check_sources")
def check_sources():
    return {
        "results": sources.check_all(fetcher=sources.fetch),
        "note_en": "Changed pages need review by a person; rules are never changed automatically.",
        "note_ta": "மாறிய பக்கங்களை ஒருவர் சரிபார்க்க வேண்டும்; விதிகள் தானாக மாற்றப்படுவதில்லை.",
    }
