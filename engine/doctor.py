"""Rejection Doctor: walks the yes/no decision trees in data/doctor_tree.json."""
from engine.data import DOCTOR_FILE

TREES = DOCTOR_FILE["trees"]
ENTRY_TREE = {e["id"]: e["tree"] for e in DOCTOR_FILE["entry_points"]}


def entry_points():
    return [{"id": e["id"], "en": e["en"], "ta": e["ta"], "tree": e["tree"]} for e in DOCTOR_FILE["entry_points"]]


def _step(tree, node_id, path, check_first=False):
    node = TREES[tree]["nodes"][node_id]
    if node["type"] == "question":
        return {"kind": "question", "tree": tree, "node_id": node_id, "en": node["en"], "ta": node["ta"], "path": path}
    fix_en, fix_ta = list(node["fix_en"]), list(node["fix_ta"])
    if check_first:  # "don't know" answers: verify first, as the tree's dont_know_rule says
        fix_en.insert(0, f"First check: {node['verify_en']}")
        fix_ta.insert(0, f"முதலில் சரிபார்க்கவும்: {node['verify_ta']}")
    return {"kind": "outcome", "tree": tree, "node_id": node_id,
            "cause_en": node["cause_en"], "cause_ta": node["cause_ta"],
            "verify_en": node["verify_en"], "verify_ta": node["verify_ta"],
            "fix_en": fix_en, "fix_ta": fix_ta, "office": node["office"],
            "draft_letter": node.get("draft_letter"), "escalate_to_helper": node.get("escalate_to_helper", False),
            "needs_helper_approval": node.get("needs_helper_approval", False), "source": node.get("source"),
            "path": path}


def start(entry_id):
    tree = ENTRY_TREE[entry_id]
    first = TREES[tree]["start"]
    return _step(tree, first, [first])


def answer(tree, path, reply, unsure=False):
    """Follow 'yes' or 'no' ('dont_know' follows 'no' and adds a check-first step)."""
    node = TREES[tree]["nodes"][path[-1]]
    if node["type"] != "question":
        return _step(tree, path[-1], path, unsure)
    unsure = unsure or reply == "dont_know"
    nxt = node["yes"] if reply == "yes" else node["no"]
    return _step(tree, nxt, path + [nxt], unsure)
