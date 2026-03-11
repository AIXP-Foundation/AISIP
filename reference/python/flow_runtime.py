"""
AISIP Runtime — AI Standard Instruction Protocol V2

Loads .aisip.json files, validates structure, and provides utilities
for working with AISIP flow definitions.

Zero dependencies beyond Python stdlib.
"""

import json
from pathlib import Path


# ── Load & Validate ─────────────────────────────────────────

def load(path: str) -> list:
    """Load an .aisip.json file and return parsed JSON."""
    with open(path, encoding="utf-8-sig") as f:
        data = json.load(f)
    validate(data)
    return data


def validate(data: list) -> None:
    """Validate AISIP V2 structure. Raises ValueError on invalid input."""
    if not isinstance(data, list) or len(data) != 2:
        raise ValueError("AISIP file must be a JSON array with exactly 2 elements")

    system, user = data
    if system.get("role") != "system":
        raise ValueError("First element must have role='system'")
    if user.get("role") != "user":
        raise ValueError("Second element must have role='user'")

    sc = system.get("content", {})
    for field in ("protocol", "id", "name", "version"):
        if field not in sc:
            raise ValueError(f"system.content missing required field: {field}")

    uc = user.get("content", {})
    if "aisip" not in uc:
        raise ValueError("user.content missing required field: aisip")
    if "main" not in uc["aisip"]:
        raise ValueError("aisip must contain a 'main' task")

    # Validate nodes
    for task_name, task_body in uc["aisip"].items():
        if not isinstance(task_body, dict):
            continue
        for node_name, node in task_body.items():
            if not isinstance(node, dict):
                continue
            ntype = node.get("type")
            if ntype not in ("process", "decision", "join", "delegate", "end"):
                raise ValueError(f"Unknown node type '{ntype}' in {task_name}.{node_name}")


# ── Metadata ────────────────────────────────────────────────

def get_metadata(data: list) -> dict:
    """Extract program metadata from AISIP data."""
    return data[0]["content"]


def get_tasks(data: list) -> dict:
    """Extract all tasks (flow graphs) from AISIP data."""
    return data[1]["content"].get("aisip", {})


def get_functions(data: list) -> dict:
    """Extract all function definitions from AISIP data."""
    return data[1]["content"].get("functions", {})


# ── Flow Analysis ───────────────────────────────────────────

def list_nodes(data: list, task: str = "main") -> list[dict]:
    """List all nodes in a task with their type and connections."""
    tasks = get_tasks(data)
    task_body = tasks.get(task, {})
    nodes = []
    for name, node in task_body.items():
        if not isinstance(node, dict):
            continue
        info = {"name": name, "type": node.get("type", "unknown")}
        if "next" in node:
            info["next"] = node["next"]
        if "branches" in node:
            info["branches"] = node["branches"]
        if "wait_for" in node:
            info["wait_for"] = node["wait_for"]
        if "delegate_to" in node:
            info["delegate_to"] = node["delegate_to"]
        if "error" in node:
            info["error"] = node["error"]
        nodes.append(info)
    return nodes


def render_flow(data: list, task: str = "main") -> str:
    """Render a simple text flow diagram for a task."""
    nodes = list_nodes(data, task)
    if not nodes:
        return "(empty)"

    lines = []
    for node in nodes:
        name = node["name"]
        ntype = node["type"]

        if ntype == "end":
            lines.append(f"  ({name})")
        elif ntype == "decision":
            branches = node.get("branches", {})
            br_str = ", ".join(f"{k} -> {v}" for k, v in branches.items())
            lines.append(f"  {name} ? [{br_str}]")
        elif ntype == "join":
            wait = node.get("wait_for", [])
            nxt = node.get("next", [])
            lines.append(f"  {name} [wait: {', '.join(wait)}] -> {', '.join(nxt)}")
        elif ntype == "delegate":
            target = node.get("delegate_to", "?")
            nxt = node.get("next", [])
            lines.append(f"  {name} => {target} -> {', '.join(nxt)}")
        else:
            nxt = node.get("next", [])
            lines.append(f"  {name} -> {', '.join(nxt)}")

    return "\n".join(lines)


# ── Prompt Builder ──────────────────────────────────────────

def build_prompt(data: list, user_input: str, system_prompt: str = "") -> str:
    """Build a complete prompt string from AISIP data and user input.

    Replaces {system_prompt} and {user_input} variables.
    Returns the full JSON string ready for use.
    """
    import copy
    result = copy.deepcopy(data)

    if system_prompt:
        result[0]["content"]["system_prompt"] = system_prompt
    result[1]["content"]["user_input"] = user_input

    return json.dumps(result, ensure_ascii=False, indent=2)


# ── CLI ─────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python flow_runtime.py <file.aisip.json> [task]")
        sys.exit(1)

    path = sys.argv[1]
    task = sys.argv[2] if len(sys.argv) > 2 else "main"

    data = load(path)
    meta = get_metadata(data)

    print(f"AISIP: {meta.get('name')} v{meta.get('version')}")
    print(f"Protocol: {meta.get('protocol')}")
    print(f"Summary: {meta.get('summary', '-')}")
    print()
    print(f"Flow ({task}):")
    print(render_flow(data, task))
    print()
    print(f"Functions: {', '.join(get_functions(data).keys())}")
