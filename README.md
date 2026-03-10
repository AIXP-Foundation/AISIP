# AISIP — AI Standard Instruction Protocol

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**An open protocol for defining structured AI programs in JSON.**

## File Format

AISIP files use the `.aisip.json` extension. A valid file is a JSON array with two elements:

```json
[
  { "role": "system", "content": { ... } },
  { "role": "user",   "content": { ... } }
]
```

| Element | Purpose |
|---------|---------|
| `system` | Program metadata (identity, version, description, system prompt) |
| `user` | Instruction, user input, flow graph, and function definitions |

## Specification

See [specification.md](specification.md) for the complete format definition.

## Example

```json
[
  {
    "role": "system",
    "content": {
      "protocol": "AISIP V2.0.0",
      "id": "greeting_assistant",
      "name": "Greeting Assistant",
      "version": "1.0.0",
      "summary": "Classify user intent and respond",
      "tools": [],
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
          "classify": { "type": "decision", "branches": { "question": "search", "chat": "reply" } },
          "search":   { "type": "process",  "next": ["end"] },
          "reply":    { "type": "process",  "next": ["end"] },
          "end":      { "type": "end" }
        }
      },
      "functions": {
        "classify": { "step1": "Classify user intent as 'question' or 'chat'" },
        "search":   { "step1": "Search for relevant information and answer" },
        "reply":    { "step1": "Generate a friendly conversational reply" },
        "end":      { "step1": "Output final response to user" }
      }
    }
  }
]
```

## Related Protocols

| Protocol | Scope |
|----------|-------|
| [AISOP](https://aisop.dev) | AI Standard Operating Protocol |
| [AIAP](https://aiap.dev) | AI Application Protocol |
| [AISIP](https://aisip.dev) | AI Standard Instruction Protocol (this) |

## License

[MIT](LICENSE) - Copyright (c) 2026 AIXP Foundation AIXP.dev | AISIP.dev
