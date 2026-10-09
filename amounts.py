"""Deterministic Tamil/English amount parser: a cross-check for numbers the AI extracts."""
import re

_WORD_NUMBERS = {
    "அரை": 0.5, "ஒன்றரை": 1.5, "இரண்டரை": 2.5, "மூன்றரை": 3.5,
    "ஒரு": 1, "ஒன்று": 1, "ரெண்டு": 2, "இரண்டு": 2, "மூணு": 3, "மூன்று": 3, "நாலு": 4, "நான்கு": 4,
    "அஞ்சு": 5, "ஐந்து": 5, "half": 0.5, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
}
_LAKH = r"(லட்சம்|லட்சத்து|லட்ச|lakh|lakhs|lac|lacs)"
_THOUSAND = r"(ஆயிரம்|ஆயிரத்து|thousand|k)"
_MONTHLY = r"(மாசம்|மாதம்|மாதத்துக்கு|மாசத்துக்கு|month|monthly|a month|per month)"
_TWO_MONTHS = r"(2 மாசத்துக்கு|இரண்டு மாதத்திற்கு|ரெண்டு மாசத்துக்கு|every two months|every 2 months|bi-?monthly)"


def _num(token):
    token = token.strip().replace(",", "")
    if token in _WORD_NUMBERS:
        return _WORD_NUMBERS[token]
    try:
        return float(token)
    except ValueError:
        return None


def amounts(text):
    """All rupee-like amounts in the text, as numbers (lakh/thousand words applied)."""
    t = text.lower()
    found = []
    for m in re.finditer(r"([\d.,]+|" + "|".join(_WORD_NUMBERS) + r")\s*" + _LAKH, t):
        n = _num(m.group(1))
        if n is not None:
            found.append(round(n * 100000))
    for m in re.finditer(r"([\d.,]+|" + "|".join(_WORD_NUMBERS) + r")\s*" + _THOUSAND + r"\b", t):
        n = _num(m.group(1))
        if n is not None:
            found.append(round(n * 1000))
    if not found:
        for m in re.finditer(r"(?<![\d.])(\d{1,3}(?:,\d{2,3})+|\d{3,7})(?![\d.])", t):
            n = _num(m.group(1))
            if n is not None:
                found.append(round(n))
    return found


def annual_income_candidates(text):
    """Possible yearly incomes in the text (monthly amounts ×12)."""
    vals = amounts(text)
    if re.search(_MONTHLY, text.lower()):
        return {v * 12 for v in vals} | set(vals)
    return set(vals)


def electricity_candidates(text):
    """Possible yearly electricity units (every two months ×6, monthly ×12)."""
    t = text.lower()
    nums = [round(float(x)) for x in re.findall(r"(?<![\d.])(\d{2,5})(?![\d.])", t)]
    if re.search(_TWO_MONTHS, t):
        return {n * 6 for n in nums} | set(nums)
    if re.search(_MONTHLY, t):
        return {n * 12 for n in nums} | set(nums)
    return set(nums)
