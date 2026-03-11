"""
AISIP V1 — Test suite for flow_runtime utilities.

Offline, no AI needed.

Usage: python test_all.py

Covers:
  1. Load & validate .aisip.json files
  2. Metadata extraction
  3. Task and function listing
  4. Flow rendering
  5. Prompt building
  6. Validation error detection
  7. Multiple tasks (main + sub-tasks)
  8. All node types
"""

import json
import os
import tempfile
from flow_runtime import (
    load, validate, get_metadata, get_tasks, get_functions,
    list_nodes, render_flow, build_prompt,
)


# ── Test fixtures ───────────────────────────────────────────

SIMPLE_FLOW = [
    {
        "role": "system",
        "content": {
            "protocol": "AISIP V1.0.0",
            "id": "test_simple",
            "name": "Simple Test",
            "version": "1.0.0",
            "summary": "A simple test flow",
            "tools": [],
            "params": { "language": "en", "tone": "friendly" },
            "system_prompt": "{system_prompt}"
        }
    },
    {
        "role": "user",
        "content": {
            "instruction": "RUN aisip.main",
            "user_input": "{user_input}",
            "aisip": {
                "main": {
                    "greet":    {"type": "process",  "next": ["classify"]},
                    "classify": {"type": "decision", "branches": {"question": "search", "chat": "reply"}},
                    "search":   {"type": "process",  "next": ["end"]},
                    "reply":    {"type": "process",  "next": ["end"]},
                    "end":      {"type": "end"}
                }
            },
            "functions": {
                "greet":    {"step1": "Say hello"},
                "classify": {"step1": "Classify intent"},
                "search":   {"step1": "Search info"},
                "reply":    {"step1": "Chat reply"},
                "end":      {"step1": "Final output"}
            }
        }
    }
]

MULTI_TASK_FLOW = [
    {
        "role": "system",
        "content": {
            "protocol": "AISIP V1.0.0",
            "id": "test_multi",
            "name": "Multi Task Test",
            "version": "1.0.0",
            "system_prompt": "{system_prompt}"
        }
    },
    {
        "role": "user",
        "content": {
            "instruction": "RUN aisip.main",
            "user_input": "{user_input}",
            "aisip": {
                "main": {
                    "start":    {"type": "process",  "next": ["delegate_step"]},
                    "delegate_step": {"type": "delegate", "delegate_to": "validation", "next": ["finish"]},
                    "finish":   {"type": "process",  "next": ["end"]},
                    "end":      {"type": "end"}
                },
                "validation": {
                    "check":  {"type": "process", "next": ["verify"]},
                    "verify": {"type": "process", "next": ["done"]},
                    "done":   {"type": "end"}
                }
            },
            "functions": {
                "start":    {"step1": "Begin"},
                "delegate_step": {"step1": "Call validation"},
                "finish":   {"step1": "Wrap up"},
                "check":    {"step1": "Check input"},
                "verify":   {"step1": "Verify result"}
            }
        }
    }
]

PARALLEL_FLOW = [
    {
        "role": "system",
        "content": {
            "protocol": "AISIP V1.0.0",
            "id": "test_parallel",
            "name": "Parallel Test",
            "version": "1.0.0",
            "system_prompt": "{system_prompt}"
        }
    },
    {
        "role": "user",
        "content": {
            "instruction": "RUN aisip.main",
            "user_input": "{user_input}",
            "aisip": {
                "main": {
                    "prepare": {"type": "process", "next": ["step_a", "step_b"]},
                    "step_a":  {"type": "process", "next": ["sync"]},
                    "step_b":  {"type": "process", "next": ["sync"]},
                    "sync":    {"type": "join", "wait_for": ["step_a", "step_b"], "next": ["finish"]},
                    "finish":  {"type": "process", "next": ["end"]},
                    "end":     {"type": "end"}
                }
            },
            "functions": {
                "prepare": {"step1": "Prepare data"},
                "step_a":  {"step1": "Process A"},
                "step_b":  {"step1": "Process B"},
                "finish":  {"step1": "Merge results"}
            }
        }
    }
]

ERROR_FLOW = [
    {
        "role": "system",
        "content": {
            "protocol": "AISIP V1.0.0",
            "id": "test_error",
            "name": "Error Test",
            "version": "1.0.0",
            "system_prompt": "{system_prompt}"
        }
    },
    {
        "role": "user",
        "content": {
            "instruction": "RUN aisip.main",
            "user_input": "{user_input}",
            "aisip": {
                "main": {
                    "risky":         {"type": "process", "next": ["finish"], "error": "error_handler"},
                    "error_handler": {"type": "process", "next": ["finish"]},
                    "finish":        {"type": "process", "next": ["end"]},
                    "end":           {"type": "end"}
                }
            },
            "functions": {
                "risky":         {"step1": "Risky operation"},
                "error_handler": {"step1": "Handle error"},
                "finish":        {"step1": "Done"}
            }
        }
    }
]


# ── Tests ───────────────────────────────────────────────────

def test_validate_valid():
    """Valid AISIP data should pass validation."""
    validate(SIMPLE_FLOW)
    validate(MULTI_TASK_FLOW)
    validate(PARALLEL_FLOW)
    validate(ERROR_FLOW)
    print("  [PASS] validate: all valid flows pass")


def test_validate_invalid():
    """Invalid data should raise ValueError."""
    errors = 0

    # Not a list
    try:
        validate({"bad": True})
    except ValueError:
        errors += 1

    # Wrong length
    try:
        validate([{"role": "system", "content": {}}])
    except ValueError:
        errors += 1

    # Missing role
    try:
        validate([
            {"role": "wrong", "content": {"protocol": "AISIP V1.0.0", "id": "x", "name": "x", "version": "1"}},
            {"role": "user", "content": {"aisip": {"main": {}}}}
        ])
    except ValueError:
        errors += 1

    # Missing required metadata
    try:
        validate([
            {"role": "system", "content": {"protocol": "AISIP V1.0.0"}},
            {"role": "user", "content": {"aisip": {"main": {}}}}
        ])
    except ValueError:
        errors += 1

    # Missing main task
    try:
        validate([
            {"role": "system", "content": {"protocol": "AISIP V1.0.0", "id": "x", "name": "x", "version": "1"}},
            {"role": "user", "content": {"aisip": {"other": {}}}}
        ])
    except ValueError:
        errors += 1

    assert errors == 5, f"Expected 5 validation errors, got {errors}"
    print("  [PASS] validate: all invalid inputs rejected")


def test_get_metadata():
    """Extract metadata correctly."""
    meta = get_metadata(SIMPLE_FLOW)
    assert meta["protocol"] == "AISIP V1.0.0"
    assert meta["id"] == "test_simple"
    assert meta["name"] == "Simple Test"
    assert meta["version"] == "1.0.0"
    assert meta.get("params") == {"language": "en", "tone": "friendly"}
    print("  [PASS] get_metadata: correct extraction")


def test_get_tasks():
    """Extract task definitions."""
    tasks = get_tasks(SIMPLE_FLOW)
    assert "main" in tasks
    assert "greet" in tasks["main"]
    assert "classify" in tasks["main"]

    tasks2 = get_tasks(MULTI_TASK_FLOW)
    assert "main" in tasks2
    assert "validation" in tasks2
    print("  [PASS] get_tasks: main and sub-tasks found")


def test_get_functions():
    """Extract function definitions."""
    funcs = get_functions(SIMPLE_FLOW)
    assert "greet" in funcs
    assert funcs["greet"]["step1"] == "Say hello"
    assert "classify" in funcs
    print("  [PASS] get_functions: correct extraction")


def test_list_nodes():
    """List nodes with type and connections."""
    nodes = list_nodes(SIMPLE_FLOW)
    names = [n["name"] for n in nodes]
    assert "greet" in names
    assert "classify" in names
    assert "end" in names

    # Check decision node has branches
    classify = [n for n in nodes if n["name"] == "classify"][0]
    assert "branches" in classify
    assert classify["branches"]["question"] == "search"
    print("  [PASS] list_nodes: correct node listing")


def test_list_nodes_subtask():
    """List nodes from a sub-task."""
    nodes = list_nodes(MULTI_TASK_FLOW, "validation")
    names = [n["name"] for n in nodes]
    assert "check" in names
    assert "verify" in names
    assert "done" in names
    print("  [PASS] list_nodes: sub-task listing works")


def test_parallel_nodes():
    """Parallel fork and join nodes listed correctly."""
    nodes = list_nodes(PARALLEL_FLOW)
    prepare = [n for n in nodes if n["name"] == "prepare"][0]
    assert prepare["next"] == ["step_a", "step_b"]

    sync = [n for n in nodes if n["name"] == "sync"][0]
    assert sync["type"] == "join"
    assert set(sync["wait_for"]) == {"step_a", "step_b"}
    print("  [PASS] list_nodes: parallel fork and join")


def test_error_routing_nodes():
    """Error routing node listed correctly."""
    nodes = list_nodes(ERROR_FLOW)
    risky = [n for n in nodes if n["name"] == "risky"][0]
    assert risky["error"] == "error_handler"
    print("  [PASS] list_nodes: error routing")


def test_delegate_nodes():
    """Delegate node listed correctly."""
    nodes = list_nodes(MULTI_TASK_FLOW)
    delegate = [n for n in nodes if n["name"] == "delegate_step"][0]
    assert delegate["type"] == "delegate"
    assert delegate["delegate_to"] == "validation"
    print("  [PASS] list_nodes: delegate node")


def test_render_flow():
    """Render text flow diagram."""
    output = render_flow(SIMPLE_FLOW)
    assert "greet" in output
    assert "classify" in output
    assert "question -> search" in output
    assert "(end)" in output
    print("  [PASS] render_flow: correct output")


def test_build_prompt():
    """Build prompt with variable substitution."""
    prompt = build_prompt(SIMPLE_FLOW, "hello", "You are a helpful assistant.")
    parsed = json.loads(prompt)
    assert parsed[0]["content"]["system_prompt"] == "You are a helpful assistant."
    assert parsed[1]["content"]["user_input"] == "hello"
    print("  [PASS] build_prompt: variable substitution works")


def test_load_file():
    """Load from actual file."""
    # Write temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".aisip.json", delete=False, encoding="utf-8") as f:
        json.dump(SIMPLE_FLOW, f, ensure_ascii=False)
        tmp_path = f.name

    try:
        data = load(tmp_path)
        assert get_metadata(data)["id"] == "test_simple"
        print("  [PASS] load: file loading works")
    finally:
        os.unlink(tmp_path)


def test_load_example():
    """Load the bundled example.aisip.json."""
    example_path = os.path.join(os.path.dirname(__file__), "example.aisip.json")
    if os.path.exists(example_path):
        data = load(example_path)
        meta = get_metadata(data)
        assert meta["protocol"] == "AISIP V1.0.0"
        assert "main" in get_tasks(data)
        print("  [PASS] load: example.aisip.json valid")
    else:
        print("  [SKIP] load: example.aisip.json not found")


def test_params():
    """params field in system.content is optional and preserved."""
    meta = get_metadata(SIMPLE_FLOW)
    assert "params" in meta
    assert meta["params"]["language"] == "en"
    assert meta["params"]["tone"] == "friendly"

    # Flow without params should also be valid
    validate(MULTI_TASK_FLOW)  # no params field
    meta2 = get_metadata(MULTI_TASK_FLOW)
    assert meta2.get("params") is None
    print("  [PASS] params: optional field correctly handled")



if __name__ == "__main__":
    print("AISIP V1 — Testing all utilities:\n")
    test_validate_valid()
    test_validate_invalid()
    test_get_metadata()
    test_params()
    test_get_tasks()
    test_get_functions()
    test_list_nodes()
    test_list_nodes_subtask()
    test_parallel_nodes()
    test_error_routing_nodes()
    test_delegate_nodes()
    test_render_flow()
    test_build_prompt()
    test_load_file()
    test_load_example()
    print(f"\nAll tests passed!")
