"""Loads the researched rule data once (data/*.json)."""
import json

import config


def _load(name):
    with open(config.DATA_DIR / name, encoding="utf-8") as fh:
        return json.load(fh)


SCHEMES_FILE = _load("schemes.json")
DOCUMENTS_FILE = _load("documents.json")
DOCTOR_FILE = _load("doctor_tree.json")
QUESTIONS_FILE = _load("questions.json")
PERSONAS = _load("personas.json")

SCHEMES = [s for s in SCHEMES_FILE["schemes"] if s.get("enabled", True)]
SCHEMES_BY_ID = {s["id"]: s for s in SCHEMES_FILE["schemes"]}
FACT_SCHEMA = SCHEMES_FILE["fact_schema"]
OFFICES = DOCUMENTS_FILE["offices"]
DOCUMENTS = DOCUMENTS_FILE["documents"]
TASKS = DOCUMENTS_FILE["tasks"]


def _replace(target, new):
    """Make dict `target` equal to `new` in place: add/overwrite first, then drop stale keys,
    so a request running at the same moment never finds a key missing."""
    target.update(new)
    for key in [k for k in target if k not in new]:
        del target[key]


def reload():
    """Re-read data/schemes.json (e.g. after a helper enables a scheme) and update SCHEMES_FILE,
    SCHEMES, SCHEMES_BY_ID and FACT_SCHEMA IN PLACE -- other modules imported them by name.
    Returns the number of enabled schemes."""
    new = _load("schemes.json")
    _replace(SCHEMES_BY_ID, {s["id"]: s for s in new["schemes"]})  # before SCHEMES: every listed scheme has an entry
    SCHEMES[:] = [s for s in new["schemes"] if s.get("enabled", True)]
    _replace(FACT_SCHEMA, new["fact_schema"])
    new["fact_schema"] = FACT_SCHEMA  # keep SCHEMES_FILE["fact_schema"] the same object as FACT_SCHEMA
    _replace(SCHEMES_FILE, new)
    return len(SCHEMES)
