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
      "classify": { "branches": { "yes": "approve", "no": "reject" } },
      "approve":  { "next": ["end"] },
      "reject":   { "next": ["end"] },
      "end":      {}
    },
    "validation": {
      "check_input": { "next": ["verify"] },
      "verify":      { "next": ["done"] },
      "done":        {}
    }
  }
}
```

### 4.1 Tasks

| Field | Description |
|-------|-------------|
| `main` | Primary task (required). Execution entry point. |
| Other keys | Sub-tasks (optional). Called via node `delegate_to` field (see §4.2) or step-level `RUN aisip.<sub>` (see §5.2.1). |

The first node in a task is the entry node.

### 4.2 Node Structure

A node is a step in the flow graph. Each node defines only its connections (topology). The execution behavior is defined in `functions` (see §5).

All node fields are topology information — everything Mermaid can draw:

| Field | Type | Description | Mermaid equivalent |
|-------|------|-------------|--------------------|
| `next` | string[] | Next node(s). 1 = sequential, 2+ = parallel fork | `-->` solid edge |
| `branches` | object | Conditional branching: `{label: target_node}` | `-->|label|` labeled edge |
| `error` | string | Error handler node (error edge) | `-.->` dashed edge |
| `delegate_to` | string | Call a sub-task by name | `Node[aisip.sub]` node text |
| `wait_for` | string[] | Wait for these nodes before proceeding (join) | Multiple edges converging |

All fields are optional. An empty object `{}` represents an end node.

Node behavior is inferred from structure (by priority, highest first):

| Priority | Structure | Inferred behavior |
|----------|-----------|-------------------|
| 1 | Empty object `{}` | End — terminate the task |
| 2 | Has `branches` | Decision — route based on condition |
| 3 | Has `delegate_to` | Delegate — call sub-task, then continue to `next` |
| 4 | Has `wait_for` | Join — wait for all listed nodes, then continue to `next` |
| 5 | Has `next` (2+ targets) | Parallel fork — execute targets concurrently |
| 6 | Has `next` (1 target) | Process — execute then proceed |

A node may have multiple fields (e.g. `delegate_to` + `next` + `error`). The highest-priority field determines the primary behavior.

**Example (basic flow):**

```json
{
  "aisip": {
    "main": {
      "classify": { "branches": { "yes": "approve", "no": "reject" } },
      "approve":  { "next": ["end"] },
      "reject":   { "next": ["end"] },
      "end":      {}
    }
  }
}
```

**Example (delegate + join):**

```json
{
  "aisip": {
    "main": {
      "start":    { "next": ["gen"] },
      "gen":      { "delegate_to": "generate_sub", "next": ["fork"] },
      "fork":     { "next": ["branch_a", "branch_b"] },
      "branch_a": { "next": ["merge"] },
      "branch_b": { "next": ["merge"] },
      "merge":    { "wait_for": ["branch_a", "branch_b"], "next": ["end"] },
      "end":      {}
    },
    "generate_sub": {
      "scaffold": { "next": ["content"] },
      "content":  { "next": ["done"] },
      "done":     {}
    }
  }
}
```

### 4.3 Error Routing

Any node can define an `error` field. When an error occurs, execution routes to the error handler node instead of `next`. The `error` field is a topology-level error edge (equivalent to Mermaid dashed edge `-.->`). For fine-grained error routing by error type, see `on_error` in §5.2.

```json
{
  "risky_step": {
    "next": ["continue"],
    "error": "error_handler"
  }
}
```

---

## 5. `functions` — Function Definitions

Defines what each node does and how it behaves at runtime. Keyed by node name. Each value contains execution steps and optional runtime behavior configuration.

```json
{
  "functions": {
    "classify": { "step1": "Classify user intent" },
    "process":  { "step1": "Process the request", "step2": "Return result" },
    "reply":    { "step1": "Generate a friendly reply" }
  }
}
```

### 5.1 Node Naming Convention

Node names can use a `_function` suffix to hint at the node's role within the flow. This helps the AI runtime understand node semantics without exposing internal structure to the user.

| Convention | Example | Meaning |
|------------|---------|---------|
| `xxx_function` | `execute_function`, `classify_function` | Functional step |
| `end_function` | `end_function` | Termination with final output |

This convention is optional. Semantic names like `greet`, `classify`, `search` are equally valid.

### 5.2 Reserved Keys

Keys in a function body fall into two categories:

- **Execution steps**: `step1`, `step2`, ... `stepN` — executed sequentially at runtime
- **Reserved keys** (`RESERVED_KEYS`): recognized as behavior configuration, not executed as steps

| Key | Type | Description |
|-----|------|-------------|
| `join` | object | Join runtime config (merge_strategy, timeout) |
| `map` | object | Iterate over a collection in parallel |
| `on_error` | object | Route errors by type to handler nodes |
| `retry_policy` | object | Auto-retry on failure with backoff |
| `context_filter` | object | Restrict input context for this node |
| `output_mapping` | string | Store output under a specific key |
| `constraints` | array | Constraint declarations (not executed) |

> **Note:**
> - `delegate_to` and `wait_for` are topology information — defined in nodes (see §4.2), not in functions.
> - `join` in functions contains only runtime config (`merge_strategy`, `timeout_seconds`). The `wait_for` list is defined in the node.

**Runtime parsing rule:**
- Keys NOT in `RESERVED_KEYS` → execution steps
- Keys IN `RESERVED_KEYS` → behavior configuration

#### 5.2.1 Sub-task Invocation

Sub-tasks can be invoked in two ways. Neither is a `RESERVED_KEY`:

**(a) Node-level `delegate_to` (topology, see §4.2):**

`delegate_to` is topology information (Mermaid can draw it). Defined in nodes, not in functions.

```json
"gen": { "delegate_to": "generate_sub", "next": ["validate"] }
```

If a delegate node needs additional runtime configuration, add steps in functions:

```json
"gen": { "step1": "Prepare context before calling sub-task" }
```

**(b) Step-level `RUN aisip.<sub>` (behavior, inside function):**

Function steps can invoke sub-tasks mid-execution. Syntax: use `RUN aisip.<sub_name>` in step text, consistent with the `instruction` field syntax.

| Level | Location | Syntax | Scenario |
|-------|----------|--------|----------|
| Node-level | §4.2 node field | `"delegate_to": "sub"` | Entire node delegates to sub-task |
| Step-level | §5 function step | `RUN aisip.sub` in step text | Mid-step invocation of sub-task |

Node-level = Mermaid can draw it (topology).
Step-level = Mermaid cannot draw it (behavior, hidden inside function).

```json
"function_one": {
  "step1": "Do something",
  "step2": "Fetch info from web, RUN aisip.extract_keywords",
  "step3": "Continue with extracted keywords"
}
```

Execution: step1 → step2 (enters extract_keywords sub-task, returns after completion) → step3

#### 5.2.2 `join`

`wait_for` is topology information (Mermaid can draw it: multiple edges converging), defined in nodes. The `join` key in functions contains only runtime configuration: how to merge, how long to wait.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `merge_strategy` | string | no | `"merge"` / `"array"` / `"first"`. Default: `"merge"` |
| `timeout_seconds` | number | no | Timeout in seconds. Default: none |

`merge_strategy` options:
- `merge`: Merge into a single object
- `array`: Collect as an array
- `first`: Take only the first completed result
- On timeout, the branch gets `{error: "timeout"}`

**Node (§4) — topology (who to wait for):**

```json
"merge_results": { "wait_for": ["branch_a", "branch_b"], "next": ["end"] }
```

**Function (§5) — behavior (how to merge):**

```json
"merge_results": {
  "step1": "Combine results from all branches",
  "join": {
    "merge_strategy": "array",
    "timeout_seconds": 120
  }
}
```

#### 5.2.3 `map`

Iterate over a collection, executing a specified function for each element. When a function body contains `map`, it replaces step execution.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `items_path` | string | yes | Path to the collection (e.g. `"state.items"`) |
| `iterator` | string | yes | Function name to execute for each item |
| `concurrency` | number | no | Max parallel executions. Default: 1, Max: 10 |
| `max_items` | number | no | Maximum items to process |
| `on_item_error` | string | no | `"skip"` / `"fail"` / `"collect"`. Default: `"fail"` |

```json
"batch_search": {
  "step1": "Search each keyword in the list",
  "map": {
    "items_path": "state.keywords",
    "iterator": "search_one",
    "concurrency": 3,
    "on_item_error": "collect"
  }
}
```

#### 5.2.4 `on_error`

Route errors by type to different handler nodes. More fine-grained than the node's `error` field: `error` is a topology-level default error edge, while `on_error` provides type-based dispatch.

Matching order: exact type → category match → `default` → node `error` edge.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| (key) | string | — | Error type (e.g. `"timeout"`, `"tool_error"`) |
| `default` | string | no | Fallback handler if no type matches |

```json
"fetch_data": {
  "step1": "Call the external API",
  "on_error": {
    "timeout": "timeout_handler",
    "tool_error": "tool_error_handler",
    "default": "global_error"
  }
}
```

#### 5.2.5 `retry_policy`

Auto-retry on node execution failure.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `max_attempts` | number | yes | Total attempts including initial (3 = initial + 2 retries) |
| `correction_prompt` | string | no | Prompt appended on retry |
| `backoff_factor` | number | no | Exponential backoff: wait = factor^attempt seconds |
| `jitter` | boolean | no | Add random 0–50% extra wait time. Default: `false` |

```json
"call_llm": {
  "step1": "Generate JSON output from LLM",
  "retry_policy": {
    "max_attempts": 3,
    "correction_prompt": "Previous output was not valid JSON. Please regenerate.",
    "backoff_factor": 2.0,
    "jitter": true
  }
}
```

#### 5.2.6 `context_filter`

Restrict the input context accessible to this node.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `include` | string[] | no | Allowlist — only these fields are passed |
| `exclude` | string[] | no | Blocklist — these fields are excluded |

`include` and `exclude` are mutually exclusive.

```json
"analyze_item": {
  "step1": "Analyze the current data item",
  "context_filter": { "include": ["current_item", "config"] }
}
```

#### 5.2.7 `output_mapping`

Store node output under a specific key instead of merging into the global context.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `output_mapping` | string | yes | Key name to store output under |

Often used with `context_filter`: filter controls input, mapping controls output.

```json
"process_item": {
  "step1": "Process and return structured result",
  "context_filter": { "include": ["current_item"] },
  "output_mapping": "processed_results"
}
```

### 5.3 Execution Order

The runtime processes each node in the following order:

1. `context_filter` — Filter input context
2. `retry_policy` — Wrap execution with retry logic
3. **Execute steps** — `step1`, `step2`, ... (or replaced by substitute execution)
4. `on_error` — Route errors by type
5. `output_mapping` — Store output

**Substitute execution** (triggered by node fields):
- If node has `delegate_to` → replaces steps, calls sub-task
- If node has `wait_for` → replaces steps, waits and merges (using `join` config in functions)
- If function body has `map` → replaces steps, iterates over collection
- `delegate_to` / `wait_for` / `map` are mutually exclusive — a node may have at most one

**Step-level sub-task invocation:**
- If a step text contains `RUN aisip.<sub_name>`, the runtime pauses the current step, executes the specified sub-task, and resumes the next step after completion
- This does not replace steps — it is a nested invocation within step execution

---

## 6. Variable Substitution

Fields marked with `{variable}` are replaced at runtime:

| Variable | Replaced With |
|----------|---------------|
| `{system_prompt}` | System prompt configured by the runtime |
| `{user_input}` | User's message |

---

## 7. Control Flow Patterns

| Pattern | Flow Graph node (§4) | Functions (§5) |
|---------|----------------------|----------------|
| Sequential | `"next": ["step_b"]` | — |
| If/else | `"branches": {"yes": "approve", "no": "reject"}` | — |
| Switch (N-way) | `"branches": {"billing": "b", "tech": "t", ...}` | — |
| Parallel fork | `"next": ["step_a", "step_b"]` | — |
| Parallel join | `"wait_for": ["step_a", "step_b"], "next": ["end"]` | `"join": {"merge_strategy": "array"}` |
| Loop | Branch target points to an earlier node | — |
| Sub-task | `"delegate_to": "sub_name", "next": ["continue"]` | — |
| Convergence | Multiple nodes' `next` point to the same node | — |
| Error routing | `"error": "error_handler"` | `"on_error": {"timeout": "t", "default": "d"}` |
| Batch iterate | `"next": ["merge"]` | `"map": {"items_path": "...", "iterator": ".."}` |
| Retry | — | `"retry_policy": {"max_attempts": 3}` |
| Data isolation | — | `"context_filter": {"include": [...]}` |
| Step-level sub | — | step text: `RUN aisip.sub` |

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
          "greet":        { "next": ["route"] },
          "route":        { "branches": { "billing": "billing", "technical": "tech", "other": "general" } },
          "billing":      { "next": ["end"], "error": "escalate" },
          "tech":         { "delegate_to": "tech_diagnose", "next": ["fork_check"], "error": "escalate" },
          "fork_check":   { "next": ["check_logs", "check_config"] },
          "check_logs":   { "next": ["merge_results"] },
          "check_config": { "next": ["merge_results"] },
          "merge_results":{ "wait_for": ["check_logs", "check_config"], "next": ["end"] },
          "general":      { "next": ["end"] },
          "escalate":     { "next": ["end"] },
          "end":          {}
        },
        "tech_diagnose": {
          "gather_info":   { "next": ["analyze"] },
          "analyze":       { "next": ["diagnose_done"] },
          "diagnose_done": {}
        },
        "extract_keywords": {
          "parse":        { "next": ["filter"] },
          "filter":       { "next": ["extract_done"] },
          "extract_done": {}
        }
      },
      "functions": {
        "greet":    { "step1": "Welcome the customer and identify their issue" },
        "route":    { "step1": "Classify the issue as billing, technical, or other" },
        "billing":  {
          "step1": "Look up account details",
          "step2": "Resolve billing issue",
          "retry_policy": { "max_attempts": 2, "correction_prompt": "Account lookup failed, please retry" },
          "on_error": { "timeout": "escalate", "default": "escalate" }
        },
        "tech":          { "step1": "Prepare technical diagnosis context" },
        "gather_info":   {
          "step1": "Collect system information from user description, RUN aisip.extract_keywords",
          "step2": "Use extracted keywords to search knowledge base"
        },
        "analyze":       {
          "step1": "Analyze gathered info and provide diagnosis",
          "context_filter": { "include": ["gather_info_result", "user_input"] },
          "output_mapping": "diagnosis_result"
        },
        "fork_check":    { "step1": "Prepare parallel check tasks" },
        "check_logs":    { "step1": "Check system logs for errors" },
        "check_config":  { "step1": "Verify configuration settings" },
        "merge_results": {
          "step1": "Combine all check results into final report",
          "join": { "merge_strategy": "array", "timeout_seconds": 60 }
        },
        "parse":     { "step1": "Parse text and extract candidate keywords" },
        "filter":    { "step1": "Filter and rank keywords by relevance" },
        "general":   { "step1": "Answer general inquiry" },
        "escalate":  { "step1": "Apologize for the issue", "step2": "Transfer to human agent" },
        "end":       { "step1": "Output final response to user" }
      }
    }
  }
]
```
