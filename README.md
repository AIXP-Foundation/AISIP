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
          "greet":    { "next": ["classify"] },
          "classify": { "branches": { "question": "search", "chat": "reply" } },
          "search":   { "next": ["end"] },
          "reply":    { "next": ["end"] },
          "end":      {}
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

- **13 Control Flow Patterns** — sequential, decision, parallel fork/join, delegate, loop, convergence, error routing, batch iterate, retry, data isolation, step-level sub-task
- **Type-free Nodes** — no `type` field needed, behavior inferred from structure
- **Three-Layer Separation** — metadata, flow graph, function definitions
- **Topology / Behavior Split** — nodes define connections (what Mermaid can draw), functions define runtime behavior
- **Sub-task Support** — `main` + named sub-tasks via `delegate_to` or step-level `RUN aisip.<sub>`
- **Reserved Keys** — 7 runtime behavior keys in functions (join, map, on_error, retry_policy, context_filter, output_mapping, constraints)
- **Error Handling** — node-level `error` edge + function-level `on_error` type routing
- **Variable Substitution** — `{system_prompt}`, `{user_input}` replaced at runtime
- **Zero Dependencies** — Reference implementation uses Python stdlib only
- **AI-Agnostic** — Works with any AI runtime

## Node Structure

Nodes define only topology (connections). Behavior is inferred from structure:

| Structure | Inferred behavior | Syntax |
|-----------|-------------------|--------|
| Has `next` (1 target) | Process — execute then proceed | `"next": ["reply"]` |
| Has `branches` | Decision — conditional branching | `"branches": {"yes": "a", "no": "b"}` |
| Has `wait_for` | Join — wait for parallel branches | `"wait_for": ["a", "b"], "next": ["c"]` |
| Has `delegate_to` | Delegate — call sub-task | `"delegate_to": "sub", "next": ["c"]` |
| Empty `{}` | End — terminate task | `{}` |

## Control Flow Patterns

| Pattern | Flow Graph node (§4) | Functions (§5) |
|---------|----------------------|----------------|
| Sequential | `"next": ["step_b"]` | — |
| If/else | `"branches": {"yes": "approve", "no": "reject"}` | — |
| Switch (N-way) | `"branches": {"billing": "b", "tech": "t", ...}` | — |
| Parallel fork | `"next": ["step_a", "step_b"]` | — |
| Parallel join | `"wait_for": ["a", "b"], "next": ["end"]` | `"join": {"merge_strategy": "array"}` |
| Loop | Branch target points to an earlier node | — |
| Sub-task | `"delegate_to": "sub", "next": ["continue"]` | — |
| Convergence | Multiple nodes' `next` point to same node | — |
| Error routing | `"error": "handler"` | `"on_error": {"timeout": "t"}` |
| Batch iterate | `"next": ["merge"]` | `"map": {"items_path": "..."}` |
| Retry | — | `"retry_policy": {"max_attempts": 3}` |
| Data isolation | — | `"context_filter": {"include": [...]}` |
| Step-level sub | — | step text: `RUN aisip.sub` |

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
