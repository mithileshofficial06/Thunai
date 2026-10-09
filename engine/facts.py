"""Family facts: validated patching and derived facts.

Fact paths:
  family.<field>
  member:<id>.<field>
  member:<id>.docs.<doc_id>
  member:<id>.names_as_printed.<doc_id>
  task:<task_id>.done
"""
import copy
import re

from engine.data import DOCUMENTS, FACT_SCHEMA

UNKNOWN = None


def empty_facts():
    return {"family": {}, "members": [], "tasks": {}}


def _field_type(description):
    """Infer the type of a schema field from its description string."""
    d = description.strip().lower()
    if d.startswith("number"):
        return ("number", None)
    if d.startswith("bool"):
        return ("bool", None)
    if d.startswith("member id") or d.startswith("string") or "derived" in d:
        return ("string", None)
    head = description.split("(")[0]
    if "|" in head:
        options = [o.strip() for o in head.split("|") if o.strip()]
        return ("enum", options)
    return ("string", None)


def _coerce(kind, options, value, path):
    if value is None:
        return None
    if kind == "number":
        if isinstance(value, bool):
            raise ValueError(f"{path}: expected a number")
        if isinstance(value, (int, float)):
            return int(value) if float(value).is_integer() else float(value)
        text = str(value).replace(",", "").replace("₹", "").strip()
        try:
            num = float(text)
        except ValueError as exc:
            raise ValueError(f"{path}: expected a number, got {value!r}") from exc
        return int(num) if num.is_integer() else num
    if kind == "bool":
        if isinstance(value, bool):
            return value
        text = str(value).strip().lower()
        if text in ("true", "yes", "1", "ஆம்"):
            return True
        if text in ("false", "no", "0", "இல்லை"):
            return False
        raise ValueError(f"{path}: expected true/false, got {value!r}")
    if kind == "enum":
        text = str(value).strip()
        for opt in options:
            if text.lower() == opt.lower():
                return opt
        raise ValueError(f"{path}: {value!r} is not one of {options}")
    return str(value).strip()


def _member(facts, member_id, create=False):
    for m in facts["members"]:
        if m["id"] == member_id:
            return m
    if not create:
        return None
    m = {"id": member_id}
    facts["members"].append(m)
    return m


def get(facts, path):
    """Read a value by fact path (None when unknown)."""
    if path.startswith("family."):
        return facts["family"].get(path.split(".", 1)[1])
    if path.startswith("task:"):
        task_id = path[len("task:"):].rsplit(".", 1)[0]
        return facts.get("tasks", {}).get(task_id)
    m = re.match(r"^member:([A-Za-z0-9_]+)\.(.+)$", path)
    if not m:
        return None
    member = _member(facts, m.group(1))
    if member is None:
        return None
    cur = member
    for part in m.group(2).split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def patch(facts, path, value):
    """Return (new_facts, old_value, new_value) after a validated change. Raises ValueError."""
    facts = copy.deepcopy(facts)
    facts.setdefault("tasks", {})
    if path.startswith("family."):
        field = path.split(".", 1)[1]
        if field not in FACT_SCHEMA["family"]:
            raise ValueError(f"unknown family field: {field}")
        kind, options = _field_type(FACT_SCHEMA["family"][field])
        new = _coerce(kind, options, value, path)
        old = facts["family"].get(field)
        facts["family"][field] = new
        return facts, old, new

    m = re.match(r"^task:(.+)\.done$", path)
    if m:
        task_id = m.group(1)
        old = facts["tasks"].get(task_id)
        new = _coerce("bool", None, value, path)
        facts["tasks"][task_id] = new
        return facts, old, new

    m = re.match(r"^member:([a-z]+\d+)\.(docs|names_as_printed)\.([a-z0-9_]+)$", path)
    if m:
        member_id, group, doc = m.groups()
        if doc not in DOCUMENTS:
            raise ValueError(f"unknown document: {doc}")
        member = _member(facts, member_id, create=True)
        member.setdefault(group, {})
        old = member[group].get(doc)
        new = _coerce("bool", None, value, path) if group == "docs" else _coerce("string", None, value, path)
        member[group][doc] = new
        return facts, old, new

    m = re.match(r"^member:([a-z]+\d+)\.([a-z0-9_]+)$", path)
    if m:
        member_id, field = m.groups()
        if field == "is_kmut_head_of_family":
            raise ValueError("is_kmut_head_of_family is derived by the rules engine")
        if field not in FACT_SCHEMA["member"]:
            raise ValueError(f"unknown member field: {field}")
        kind, options = _field_type(FACT_SCHEMA["member"][field])
        if field == "id":
            raise ValueError("member id cannot be changed")
        new = _coerce(kind, options, value, path)
        member = _member(facts, member_id, create=True)
        old = member.get(field)
        member[field] = new
        return facts, old, new

    raise ValueError(f"invalid fact path: {path}")


def derive(facts):
    """Return a copy with derived facts added (computed by rules, never by the AI)."""
    f = copy.deepcopy(facts)
    fam, members = f["family"], f["members"]

    wet, dry = fam.get("wet_land_acres"), fam.get("dry_land_acres")
    fam["has_both_wet_and_dry_land"] = UNKNOWN if wet is None or dry is None else (wet > 0 and dry > 0)

    head_id = fam.get("ration_card_head_member_id")
    head = next((m for m in members if m["id"] == head_id), None)
    kmut_head = UNKNOWN
    if head is not None:
        if head.get("gender") in ("female", "transgender"):
            kmut_head = head["id"]
        else:
            wife = next((m for m in members
                         if m.get("spouse_of") == head["id"] and m.get("gender") == "female"
                         and m.get("on_ration_card", True) is not False), None)
            kmut_head = wife["id"] if wife else fam.get("kmut_chosen_member_id")
    for m in members:
        m["is_kmut_head_of_family"] = UNKNOWN if kmut_head is None else (m["id"] == kmut_head)
    return f
