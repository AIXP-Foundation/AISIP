# AISIP vs Mermaid：控制流对比

## 概览

| 控制结构 | Mermaid | AISIP | 备注 |
|---------|---------|-------|------|
| 顺序 | 支持 | 支持 | 等价 |
| 二分支 | 支持 | 支持 | 等价 |
| 多分支 | 支持 | 支持 | 等价 |
| 并行分叉 | 支持 | 支持 | 等价 |
| 并行汇合 | 支持 | 支持 | AISIP 更明确 |
| 回环 | 支持 | 支持 | 等价 |
| 子流程 | 支持 | 支持 | AISIP 有 delegate |
| 收敛 | 支持 | 支持 | 等价 |
| 错误路由 | 不支持 | 支持 | **AISIP 独有** |

---

## 逐项对比

### 1. 顺序

**Mermaid：**
```mermaid
graph TD
    greet[Greet] --> classify[Classify] --> reply[Reply] --> end_node((End))
```

**AISIP：**
```json
{
  "greet":    { "type": "process", "next": ["classify"] },
  "classify": { "type": "process", "next": ["reply"] },
  "reply":    { "type": "process", "next": ["end"] },
  "end":      { "type": "end" }
}
```

---

### 2. 二分支

**Mermaid：**
```mermaid
graph TD
    check{Check?} --yes--> approve[Approve]
    check --no--> reject[Reject]
```

**AISIP：**
```json
{
  "check": { "type": "decision", "branches": { "yes": "approve", "no": "reject" } }
}
```

---

### 3. 多分支

**Mermaid：**
```mermaid
graph TD
    route{Route?} --billing--> billing[Billing]
    route --tech--> tech[Tech]
    route --other--> general[General]
```

**AISIP：**
```json
{
  "route": {
    "type": "decision",
    "branches": { "billing": "billing", "tech": "tech", "other": "general" }
  }
}
```

---

### 4. 并行分叉

**Mermaid：**
```mermaid
graph TD
    prepare[Prepare] --> step_a[Step A]
    prepare --> step_b[Step B]
```

**AISIP：**
```json
{
  "prepare": { "type": "process", "next": ["step_a", "step_b"] }
}
```

---

### 5. 并行汇合

**Mermaid：**
```mermaid
graph TD
    step_a --> sync[Sync]
    step_b --> sync
    sync --> finish[Finish]
```

**AISIP：**
```json
{
  "step_a": { "type": "process", "next": ["sync"] },
  "step_b": { "type": "process", "next": ["sync"] },
  "sync":   { "type": "join", "wait_for": ["step_a", "step_b"], "next": ["finish"] }
}
```

AISIP 优势：`join` 节点明确声明需要等待的节点。Mermaid 中箭头汇聚到某节点仅是视觉效果 — 没有等待语义。

---

### 6. 回环

**Mermaid：**
```mermaid
graph TD
    attempt[Attempt] --> check{Quality?}
    check --retry--> attempt
    check --pass--> done[Done]
```

**AISIP：**
```json
{
  "attempt": { "type": "process", "next": ["check"] },
  "check":   { "type": "decision", "branches": { "retry": "attempt", "pass": "done" } }
}
```

---

### 7. 子流程（Delegate）

**Mermaid：**
```mermaid
graph TD
    prepare --> call_sub[Call Sub]
    subgraph Sub Flow
        check_input --> verify --> sub_end((End))
    end
    call_sub --> sub_end --> continue_main[Continue]
```

**AISIP：**

主任务：
```json
{
  "prepare":  { "type": "process", "next": ["call_sub"] },
  "call_sub": { "type": "delegate", "delegate_to": "validation", "next": ["continue_main"] }
}
```

子任务（`validation`）：
```json
{
  "check_input": { "type": "process", "next": ["verify"] },
  "verify":      { "type": "process", "next": ["done"] },
  "done":        { "type": "end" }
}
```

AISIP 优势：子任务可复用 — 同一子任务可以被多个 delegate 节点调用。Mermaid 的 subgraph 仅是视觉分组。

---

### 8. 收敛

**Mermaid：**
```mermaid
graph TD
    route{Route?} --a--> handle_a
    route --b--> handle_b
    route --c--> handle_c
    handle_a --> merge[Merge]
    handle_b --> merge
    handle_c --> merge
```

**AISIP：**
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

### 9. 错误路由

**Mermaid：** 无原生支持。

**AISIP：**
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

AISIP 独有 — 等同于编程语言中的 try/catch。

---

## 总结

| 维度 | Mermaid | AISIP |
|------|---------|-------|
| 用途 | 流程可视化 | 结构化程序定义 |
| 机器可读 | 需要解析器 | 原生 JSON |
| 错误处理 | 不支持 | 支持（原生） |
| 并行汇合语义 | 不支持（仅视觉） | 支持（明确的 `wait_for`） |
| 子流程复用 | 不支持（复制粘贴） | 支持（delegate） |
| 可视化 | 原生渲染 | 可转换为 Mermaid 显示 |
| 结构/内容分离 | 不支持 | 支持（流程图 + 函数） |

AISIP 覆盖了 Mermaid 的所有控制流能力（9/9），并额外支持错误路由。Mermaid 的唯一优势是原生可视化 — 但 AISIP JSON 可以转换为 Mermaid 进行展示。
