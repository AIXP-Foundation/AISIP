# Performance: AISOP vs AISIP

## Token Count Comparison

The same flow expressed in both protocols:

**AISOP (Mermaid) — ~40 tokens:**

```
graph TD
    N1{match} -->|matched| N2[execute_function]
    N1 -->|uncertain| N4[classify_function]
    N2 --> N3[end_function]
    N4 --> N2
```

**AISIP (JSON) — ~60 tokens:**

```json
"main": {
    "N1": {"branches": {"matched": "N2", "uncertain": "N4"}},
    "N2": {"next": ["N3"]},
    "N3": {},
    "N4": {"next": ["N2"]}
}
```

Mermaid uses roughly **half the tokens** for the same flow definition. Fewer tokens = faster input processing + lower cost. Note: AISIP's type-free format reduces token count compared to the older type-based format.

## LLM Comprehension

- Mermaid is a visual language with extensive presence in LLM training data. Branch relationships are immediately apparent.
- JSON flow requires layer-by-layer parsing of `next`/`branches` fields to trace the execution path.

## When AISOP Wins

- **Simple routing flows** — fewer tokens, more intuitive for LLMs
- **Speed-sensitive scenarios** — lower latency due to compact representation
- **Cost optimization** — fewer input tokens = lower API cost

## When AISIP Wins

- **Complex flows** (join, parallel, delegate, error routing) — JSON semantics are more precise; Mermaid cannot express wait/join behavior
- **Programmatic processing** — JSON can be directly parsed and validated by code; Mermaid requires string parsing
- **Sub-tasks** — AISIP's multi-task structure with `delegate_to` and `RUN aisip.sub` is clearer than Mermaid subgraphs
- **Strict validation** — JSON schema can enforce structure at the protocol level

## Conclusion

| Scenario | Recommended | Reason |
|----------|-------------|--------|
| Simple routing / intent matching | AISOP | Fewer tokens, faster, intuitive |
| Complex multi-step workflows | AISIP | Precise semantics, no ambiguity |
| Cost-sensitive deployments | AISOP | ~50% fewer flow tokens |
| Programmatic flow generation | AISIP | Native JSON, easy to build/validate |

Both protocols share the same function definitions and metadata format. The choice depends on flow complexity and deployment priorities.

---

# 性能对比：AISOP vs AISIP

## Token 数量对比

同样的流程，两种协议的表达：

**AISOP (Mermaid) — 约 40 tokens：**

```
graph TD
    N1{match} -->|matched| N2[execute_function]
    N1 -->|uncertain| N4[classify_function]
    N2 --> N3[end_function]
    N4 --> N2
```

**AISIP (JSON) — 约 60 tokens：**

```json
"main": {
    "N1": {"branches": {"matched": "N2", "uncertain": "N4"}},
    "N2": {"next": ["N3"]},
    "N3": {},
    "N4": {"next": ["N2"]}
}
```

Mermaid 的 token 数量大约是 JSON 的 **一半**。Token 越少 = 输入处理越快 + 费用越低。注意：AISIP 的无 type 格式比旧的 type 格式减少了 token 数量。

## LLM 理解度

- Mermaid 是视觉化语言，LLM 训练数据中大量存在，分支关系一目了然。
- JSON flow 需要逐层解析 `next`/`branches` 字段才能理清执行路径。

## AISOP 更优的场景

- **简单路由流程** — token 少，LLM 理解更直观
- **对速度敏感的场景** — 紧凑表达带来更低延迟
- **成本优化** — 更少的输入 token = 更低的 API 费用

## AISIP 更优的场景

- **复杂流程**（join、parallel、delegate、error routing）— JSON 语义更精确，Mermaid 无法表达等待/汇合行为
- **程序化处理** — JSON 可以直接被代码解析验证，Mermaid 需要字符串解析
- **子任务** — AISIP 的 `delegate_to` 和 `RUN aisip.sub` 多任务结构比 Mermaid subgraph 更清晰
- **严格校验** — JSON schema 可以在协议层面强制执行结构约束

## 结论

| 场景 | 推荐 | 原因 |
|------|------|------|
| 简单路由 / 意图匹配 | AISOP | token 少，速度快，直观 |
| 复杂多步骤工作流 | AISIP | 语义精确，无歧义 |
| 成本敏感部署 | AISOP | 流程 token 减少约 50% |
| 程序化生成流程 | AISIP | 原生 JSON，易于构建和验证 |

两种协议共享相同的函数定义和元数据格式。选择取决于流程复杂度和部署优先级。
