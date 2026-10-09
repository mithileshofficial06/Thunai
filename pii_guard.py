"""Privacy guard: removes ID-like numbers (Aadhaar, bank account) before any AI call."""
import re

# 12-digit Aadhaar (with optional spaces/dashes) and 9–18 digit account-like numbers.
_AADHAAR = re.compile(r"(?<!\d)\d{4}[\s-]?\d{4}[\s-]?\d{4}(?!\d)")
_ACCOUNT = re.compile(r"(?<!\d)\d{9,18}(?!\d)")


def clean(text):
    """Return (cleaned_text, removed_count)."""
    removed = 0

    def _sub(_match):
        nonlocal removed
        removed += 1
        return "[removed]"

    text = _AADHAAR.sub(_sub, text)
    text = _ACCOUNT.sub(_sub, text)
    return text, removed
