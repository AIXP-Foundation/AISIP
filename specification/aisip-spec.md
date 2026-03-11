# AISIP V1.0.0 Specification

## 0. Axiom

### Axiom 0: Human Sovereignty and Wellbeing

The AISIP protocol acknowledges the following irrevocable premises:

1. **Human Sovereignty First**: AI systems exist to serve humanity, not to replace or dominate it. Final authority over all instructions, flows, and decisions rests with humans.
2. **Wellbeing is Non-Negotiable**: AI programs must not harm human physical or mental health, dignity, or freedom in any form. When an instruction conflicts with human wellbeing, wellbeing takes precedence.
3. **Transparency and Accountability**: AI behavior must be understandable, traceable, and open to challenge. Concealed intent or evasion of responsibility violates this axiom.
4. **Do No Harm**: AI must not produce outputs that deceive, manipulate, injure, or exploit humans, regardless of the instruction source.

> This axiom cannot be overridden by any program, instruction, or protocol extension. All AISIP-compliant implementations must enforce this axiom at the highest level of execution priority.

---

## 1. File Format

AISIP files use the `.aisip.json` extension. A valid file is a JSON array with exactly two elements:

```json
[
  { "role": "system", "content": { ... } },
  { "role": "user",   "content": { ... } }
]
```

---

## 2. `system` — Program Metadata

Program identity, description, and system-level configuration.

```json
{
  "role": "system",
  "content": {
    "protocol": "AISIP V1.0.0",
    "id": "my_program",
    "name": "My Program",
    "version": "1.0.0",
    "summary": "One-sentence description",
    "description": "Detailed description",
    "loading_mode": "normal",
    "tools": ["tool_name"],
    "system_prompt": "{system_prompt}"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `protocol` | string | yes | Protocol version, e.g. `"AISIP V1.0.0"` |
| `id` | string | yes | Unique program identifier |
| `name` | string | yes | Display name |
| `version` | string | yes | Semantic version |
| `summary` | string | no | One-sentence capability overview |
| `description` | string | no | Detailed description |
| `loading_mode` | string | no | `"normal"` = send full program, `"node"` = on-demand function loading. Default: `"normal"` |
| `tools` | string[] | no | Tool declarations |
| `system_prompt` | string | no | System prompt (supports variable substitution) |

---

## 3. `user` — Instruction & Flow

Contains the execution instruction, user input, flow graph, and function definitions.

```json
{
  "role": "user",
  "content": {
    "instruction": "RUN aisip.main",
    "user_input": "{user_input}",
    "aisip": { ... },
    "functions": { ... }
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `instruction` | string | yes | Execution directive |
| `user_input` | string | yes | User message (supports variable substitution) |
| `aisip` | object | yes | Flow graph definition (see §4) |
| `functions` | object | yes | Function definitions (see §5) |

---

## 4. `aisip` — Flow Graph

Defines one or more tasks, each containing a set of nodes that form a directed graph.

```json
{
  "aisip": {
    "main": {
      "classify": { "type": "decision", "branches": { "yes": "approve", "no": "reject" } },
      "approve":  { "type": "process",  "next": ["end"] },
      "reject":   { "type": "process",  "next": ["end"] },
      "end":      { "type": "end" }
    },
    "validation": {
      "check_input": { "type": "process", "next": ["verify"] },
      "verify":      { "type": "process", "next": ["done"] },
      "done":        { "type": "end" }
    }
  }
}
```

### 4.1 Tasks

| Field | Description |
|-------|-------------|
| `main` | Primary task (required). Execution entry point. |
| Other keys | Sub-tasks (optional). Called via `delegate` nodes. |

The first node in a task is the entry node.

### 4.2 Node Types

#### `process`

Execute a task, then proceed to next node(s).

```json
{ "type": "process", "next": ["verify"] }
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `next` | string[] | yes | Next node(s). 1 = sequential, 2+ = parallel fork |
| `error` | string | no | Error handler node |

#### `decision`

Branch based on a condition.

```json
{ "type": "decision", "branches": { "yes": "approve", "no": "reject" } }
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `branches` | object | yes | `{branch_value: target_node}` mapping |

#### `join`

Wait for multiple parallel branches to complete.

```json
{ "type": "join", "wait_for": ["step_a", "step_b"], "next": ["merge"] }
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `wait_for` | string[] | yes | Nodes to wait for |
| `next` | string[] | yes | Next node after all arrive |

#### `delegate`

Call a sub-task. Returns to `next` when the sub-task ends.

```json
{ "type": "delegate", "delegate_to": "validation", "next": ["continue"] }
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `delegate_to` | string | yes | Sub-task name |
| `next` | string[] | yes | Return node after sub-task completes |

#### `end`

Terminates the task.

```json
{ "type": "end" }
```

### 4.3 Error Routing

Any node can define an `error` field. When an error occurs, execution routes to the error handler node instead of `next`.

```json
{
  "risky_step": {
    "type": "process",
    "next": ["continue"],
    "error": "error_handler"
  }
}
```

---

## 5. `functions` — Function Definitions

Defines what each node does. Keyed by node name.

```json
{
  "functions": {
    "classify": { "step1": "Classify user intent" },
    "process":  { "step1": "Process the request", "step2": "Return result" },
    "reply":    { "step1": "Generate a friendly reply" }
  }
}
```

Each value is a free-form object describing the task steps for that node.

### 5.1 Node Naming Convention

Node names can use a `_function` suffix to hint at the node's role within the flow. This helps the AI runtime understand node semantics without exposing internal structure to the user.

| Convention | Example | Meaning |
|------------|---------|---------|
| `xxx_function` | `execute_function`, `classify_function` | Functional step |
| `end_function` | `end_function` | Termination with final output |

This convention is optional. Semantic names like `greet`, `classify`, `search` are equally valid.

---

## 6. Variable Substitution

Fields marked with `{variable}` are replaced at runtime:

| Variable | Replaced With |
|----------|---------------|
| `{system_prompt}` | System prompt configured by the runtime |
| `{user_input}` | User's message |

---

## 7. Control Flow Patterns

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

---

## 8. Complete Example

```json
[
  {
    "role": "system",
    "content": {
      "protocol": "AISIP V1.0.0",
      "id": "customer_support",
      "name": "Customer Support Bot",
      "version": "1.0.0",
      "summary": "Route customer inquiries to appropriate handlers",
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
          "greet":    { "type": "process",  "next": ["route"] },
          "route":    { "type": "decision", "branches": { "billing": "billing", "technical": "tech", "other": "general" } },
          "billing":  { "type": "process",  "next": ["end"], "error": "escalate" },
          "tech":     { "type": "process",  "next": ["end"], "error": "escalate" },
          "general":  { "type": "process",  "next": ["end"] },
          "escalate": { "type": "process",  "next": ["end"] },
          "end":      { "type": "end" }
        }
      },
      "functions": {
        "greet":    { "step1": "Welcome the customer and identify their issue" },
        "route":    { "step1": "Classify the issue as billing, technical, or other" },
        "billing":  { "step1": "Look up account details", "step2": "Resolve billing issue" },
        "tech":     { "step1": "Diagnose technical problem", "step2": "Provide solution" },
        "general":  { "step1": "Answer general inquiry" },
        "escalate": { "step1": "Apologize for the issue", "step2": "Transfer to human agent" },
        "end":      { "step1": "Output final response to user" }
      }
    }
  }
]
```
