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
