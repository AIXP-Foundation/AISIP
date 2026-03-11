# AISIP vs Mermaid: Control Flow Comparison

## Overview

| Control Structure | Mermaid | AISIP | Notes |
|-------------------|---------|-------|-------|
| Sequential | Yes | Yes | Equivalent |
| If/else (binary) | Yes | Yes | Equivalent |
| Switch (N-way) | Yes | Yes | Equivalent |
| Parallel fork | Yes | Yes | Equivalent |
| Parallel join | Yes | Yes | AISIP more explicit |
| Loop | Yes | Yes | Equivalent |
| Sub-flow (subgraph) | Yes | Yes | AISIP has delegate |
| Convergence (merge) | Yes | Yes | Equivalent |
| Error routing | No | Yes | **AISIP only** |

---

## Side-by-Side

### 1. Sequential

**Mermaid:**
```mermaid
graph TD
    greet[Greet] --> classify[Classify] --> reply[Reply] --> end_node((End))
```

**AISIP:**
```json
{
  "greet":    { "type": "process", "next": ["classify"] },
  "classify": { "type": "process", "next": ["reply"] },
  "reply":    { "type": "process", "next": ["end"] },
  "end":      { "type": "end" }
}
```

---

### 2. If/Else (Binary Branch)

**Mermaid:**
```mermaid
graph TD
    check{Check?} --yes--> approve[Approve]
    check --no--> reject[Reject]
```

**AISIP:**
```json
{
  "check": { "type": "decision", "branches": { "yes": "approve", "no": "reject" } }
}
```

---

### 3. Switch (N-way Branch)

**Mermaid:**
```mermaid
graph TD
    route{Route?} --billing--> billing[Billing]
    route --tech--> tech[Tech]
    route --other--> general[General]
```

**AISIP:**
```json
{
  "route": {
    "type": "decision",
    "branches": { "billing": "billing", "tech": "tech", "other": "general" }
  }
}
```

---

### 4. Parallel Fork

**Mermaid:**
```mermaid
graph TD
    prepare[Prepare] --> step_a[Step A]
    prepare --> step_b[Step B]
```

**AISIP:**
```json
{
  "prepare": { "type": "process", "next": ["step_a", "step_b"] }
}
```

---

### 5. Parallel Join

**Mermaid:**
```mermaid
graph TD
    step_a --> sync[Sync]
    step_b --> sync
    sync --> finish[Finish]
```

**AISIP:**
```json
{
  "step_a": { "type": "process", "next": ["sync"] },
  "step_b": { "type": "process", "next": ["sync"] },
  "sync":   { "type": "join", "wait_for": ["step_a", "step_b"], "next": ["finish"] }
}
```

AISIP advantage: `join` node explicitly declares which nodes to wait for. Mermaid arrows converging on a node are visual only — no waiting semantics.

---

### 6. Loop

**Mermaid:**
```mermaid
graph TD
    attempt[Attempt] --> check{Quality?}
    check --retry--> attempt
    check --pass--> done[Done]
```

**AISIP:**
```json
{
  "attempt": { "type": "process", "next": ["check"] },
  "check":   { "type": "decision", "branches": { "retry": "attempt", "pass": "done" } }
}
```

---

### 7. Sub-flow (Delegate)

**Mermaid:**
```mermaid
graph TD
    prepare --> call_sub[Call Sub]
    subgraph Sub Flow
        check_input --> verify --> sub_end((End))
    end
    call_sub --> sub_end --> continue_main[Continue]
```

**AISIP:**

Main task:
```json
{
  "prepare":  { "type": "process", "next": ["call_sub"] },
  "call_sub": { "type": "delegate", "delegate_to": "validation", "next": ["continue_main"] }
}
```

Sub-task (`validation`):
```json
{
  "check_input": { "type": "process", "next": ["verify"] },
  "verify":      { "type": "process", "next": ["done"] },
  "done":        { "type": "end" }
}
```

AISIP advantage: Sub-tasks are reusable — the same sub-task can be called from multiple delegate nodes. Mermaid subgraphs are visual grouping only.

---

### 8. Convergence (Merge)

**Mermaid:**
```mermaid
graph TD
    route{Route?} --a--> handle_a
    route --b--> handle_b
    route --c--> handle_c
    handle_a --> merge[Merge]
    handle_b --> merge
    handle_c --> merge
```

**AISIP:**
```json
{
  "route":    { "type": "decision", "branches": { "a": "handle_a", "b": "handle_b", "c": "handle_c" } },
  "handle_a": { "type": "process", "next": ["merge"] },
  "handle_b": { "type": "process", "next": ["merge"] },
  "handle_c": { "type": "process", "next": ["merge"] },
  "merge":    { "type": "process", "next": ["end"] }
}
```

---

### 9. Error Routing

**Mermaid:** No native support.

**AISIP:**
```json
{
  "risky_step": {
    "type": "process",
    "next": ["continue"],
    "error": "error_handler"
  },
  "error_handler": {
    "type": "process",
    "next": ["end"]
  }
}
```

AISIP only — equivalent to try/catch in programming languages.

---

## Summary

| Dimension | Mermaid | AISIP |
|-----------|---------|-------|
| Purpose | Flow visualization | Structured program definition |
| Machine-readable | Requires parser | Native JSON |
| Error handling | No | Yes (native) |
| Parallel join semantics | No (visual only) | Yes (explicit `wait_for`) |
| Sub-flow reuse | No (copy/paste) | Yes (delegate) |
| Visualization | Native rendering | Convertible to Mermaid |
| Structure/content separation | No | Yes (flow graph + functions) |

AISIP covers all Mermaid control flow capabilities (9/9) plus error routing. Mermaid's only advantage is native visualization — but AISIP JSON can be converted to Mermaid for display.
