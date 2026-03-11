# AISIP — AI Standard Instruction Protocol

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)

**An open protocol for defining structured AI programs in JSON.**

AISIP enables defining multi-step AI programs as structured JSON files — with control flow, branching, parallel execution, sub-tasks, and error handling — all in a single portable format.

## Why AISIP?

| Approach | Definition | Portable | Machine-readable |
|----------|-----------|----------|-----------------|
| Natural language prompts | Free text | Yes | No |
| Python / YAML workflows | Code / config | No | Partially |
| Visual builders (Dify, etc.) | Proprietary | No | No |
| **AISIP** | **JSON** | **Yes** | **Yes** |

AISIP files are plain JSON — readable by any language, editable in any editor, versionable in git.

## File Format

```json
[
  { "role": "system", "content": { "protocol": "AISIP V1.0.0", ... } },
  { "role": "user",   "content": { "instruction": "...", "aisip": { ... }, "functions": { ... } } }
]
```

| Element | Purpose |
|---------|---------|
| `system` | Program metadata (identity, version, description) |
| `user` | Instruction, flow graph, and function definitions |

## Quick Example

```json
[
  {
    "role": "system",
    "content": {
      "protocol": "AISIP V1.0.0",
      "id": "greeting_assistant",
      "name": "Greeting Assistant",
      "version": "1.0.0",
      "summary": "Classify user intent and respond"
    }
  },
  {
    "role": "user",
    "content": {
      "instruction": "RUN aisip.main",
      "user_input": "{user_input}",
      "aisip": {
        "main": {
          "greet":    { "type": "process",  "next": ["classify"] },
          "classify": { "type": "decision", "branches": { "question": "search", "chat": "reply" } },
          "search":   { "type": "process",  "next": ["end"] },
          "reply":    { "type": "process",  "next": ["end"] },
          "end":      { "type": "end" }
        }
      },
      "functions": {
        "greet":    { "step1": "Say hello to the user" },
        "classify": { "step1": "Classify user intent as 'question' or 'chat'" },
        "search":   { "step1": "Search for relevant info" },
        "reply":    { "step1": "Generate a friendly reply" },
        "end":      { "step1": "Output final response" }
      }
    }
  }
]
```

```
greet -> classify --(question)--> search -> end
                  \--(chat)-----> reply  -> end
```

## Key Features

- **9 Control Flow Types** — process, decision, join, delegate, end, error routing, parallel fork, loop, convergence
- **Three-Layer Separation** — metadata, flow graph, function definitions
- **Sub-task Support** — `main` + named sub-tasks with delegate nodes
- **Error Handling** — Any node can define an `error` route
- **Variable Substitution** — `{system_prompt}`, `{user_input}` replaced at runtime
- **Zero Dependencies** — Reference implementation uses Python stdlib only
- **AI-Agnostic** — Works with any AI runtime

## Node Types

| Type | Purpose | Syntax |
|------|---------|--------|
| `process` | Execute task, proceed to next | `"next": ["reply"]` |
| `decision` | Conditional branching | `"branches": {"yes": "approve", "no": "reject"}` |
| `join` | Wait for parallel branches | `"wait_for": ["step_a", "step_b"]` |
| `delegate` | Call sub-task | `"delegate_to": "validation"` |
| `end` | Terminate task | `{"type": "end"}` |

## Control Flow Patterns

| Pattern | How to Express |
|---------|----------------|
| Sequential | `"next": ["step_b"]` |
| If/else | `"branches": {"yes": "approve", "no": "reject"}` |
| Switch (N-way) | `"branches": {"billing": "billing", "tech": "tech", "other": "general"}` |
| Parallel fork | `"next": ["step_a", "step_b"]` |
| Parallel join | `"type": "join", "wait_for": ["step_a", "step_b"]` |
| Loop | Branch target points to an earlier node |
| Sub-task | `"type": "delegate", "delegate_to": "validation"` |
| Convergence | Multiple nodes' `next` point to the same node |
| Error routing | `"error": "error_handler"` |

## Getting Started

```bash
# Inspect a flow file
cd reference/python
python run.py example.aisip.json

# Run tests (no AI needed)
python test_all.py

# Build a prompt
python run.py example.aisip.json --prompt "hello"
```

## Project Structure

```
AISIP/
  specification/
    aisip-spec.md            # Protocol specification (V1.0.0)
    aisip-spec_CN.md          # Protocol specification — Chinese
  docs/
    comparison-mermaid.md     # AISIP vs Mermaid comparison
    performance-aisop-vs-aisip.md  # AISOP vs AISIP performance
  reference/
    python/
      flow_runtime.py         # Reference implementation (loader, validator, utilities)
      example.aisip.json      # Example flow definition
      test_all.py             # Test suite
      run.py                  # CLI tool
  LICENSE
  CONTRIBUTING.md
  CHANGELOG.md
```

## Related Protocols

| Protocol | Scope |
|----------|-------|
| [AISOP](https://aisop.dev) | AI Standard Operating Protocol |
| [AIAP](https://aiap.dev) | AI Application Protocol |
| [AISIP](https://aisip.dev) | AI Standard Instruction Protocol (this) |

## Axiom

AISIP is grounded in **Axiom 0: Human Sovereignty and Wellbeing** — AI systems exist to serve humanity, not replace or dominate it. All implementations must enforce this axiom at the highest execution priority. See [§0 of the specification](specification/aisip-spec.md) for the full text.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines / 见 [CONTRIBUTING_CN.md](CONTRIBUTING_CN.md) 了解贡献指南。

## License

[MIT](LICENSE) - Copyright (c) 2026 AIXP Foundation AIXP.dev | AISIP.dev
