# AISIP V1.0.0 规范

## 0. 公理

### 公理 0：人类主权与福祉

AISIP 协议承认以下不可撤销的前提：

1. **人类主权优先**：AI 系统服务于人类，而非取代或支配人类。所有指令、流程和决策的最终权力归属于人类。
2. **福祉不可妥协**：AI 程序不得以任何形式损害人类的身体或心理健康、尊严或自由。当指令与人类福祉冲突时，福祉优先。
3. **透明与问责**：AI 行为必须是可理解的、可追溯的、可质疑的。隐匿意图或逃避责任违反本公理。
4. **不造成伤害**：无论指令来源如何，AI 不得产生欺骗、操纵、伤害或剥削人类的输出。

> 本公理不可被任何程序、指令或协议扩展所覆盖。所有符合 AISIP 的实现必须将此公理置于执行优先级的最高层。

---

## 1. 文件格式

AISIP 文件使用 `.aisip.json` 扩展名。有效文件是一个包含两个元素的 JSON 数组：

```json
[
  { "role": "system", "content": { ... } },
  { "role": "user",   "content": { ... } }
]
```

---

## 2. `system` — 程序元数据

程序身份、描述和系统级配置。

```json
{
  "role": "system",
  "content": {
    "protocol": "AISIP V1.0.0",
    "id": "my_program",
    "name": "My Program",
    "version": "1.0.0",
    "summary": "一句话描述",
    "description": "详细描述",
    "loading_mode": "normal",
    "tools": ["tool_name"],
    "system_prompt": "{system_prompt}"
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `protocol` | string | 是 | 协议版本，如 `"AISIP V1.0.0"` |
| `id` | string | 是 | 唯一程序标识符 |
| `name` | string | 是 | 显示名称 |
| `version` | string | 是 | 语义化版本 |
| `summary` | string | 否 | 一句话功能概述 |
| `description` | string | 否 | 详细描述 |
| `loading_mode` | string | 否 | `"normal"` = 发送完整程序，`"node"` = 按需加载函数。默认：`"normal"` |
| `tools` | string[] | 否 | 工具声明 |
| `system_prompt` | string | 否 | 系统提示（支持变量替换） |

---

## 3. `user` — 指令与流程

包含执行指令、用户输入、流程图和函数定义。

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

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `instruction` | string | 是 | 执行指令 |
| `user_input` | string | 是 | 用户消息（支持变量替换） |
| `aisip` | object | 是 | 流程图定义（见 §4） |
| `functions` | object | 是 | 函数定义（见 §5） |

---

## 4. `aisip` — 流程图

定义一个或多个任务，每个任务包含一组节点，构成有向图。

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

### 4.1 任务

| 字段 | 说明 |
|------|------|
| `main` | 主任务（必填）。执行入口。 |
| 其他键 | 子任务（可选）。通过节点 `delegate_to` 字段（见 §4.2）或步骤层 `RUN aisip.<sub>`（见 §5.2.1）调用。 |

任务中的第一个节点即为入口节点。

### 4.2 节点结构

节点是流程图中的一个步骤。每个节点只定义连接关系（拓扑），具体执行行为在 `functions` 中定义（见 §5）。

节点可用字段（全部是拓扑信息，Mermaid 都能画出来）：

| 字段 | 类型 | 说明 | Mermaid 对应 |
|------|------|------|-------------|
| `next` | string[] | 下一节点。1 个 = 顺序，2+ 个 = 并行分叉 | `-->` 实线 |
| `branches` | object | 条件分支：`{标签: 目标节点}` | `-->\|label\|` 带标签边 |
| `error` | string | 错误处理节点（错误边） | `-.->` 虚线 |
| `delegate_to` | string | 按名称调用子任务 | `Node[aisip.sub]` 节点文本 |
| `wait_for` | string[] | 等待这些节点完成后继续（汇聚） | 多条边汇入 |

所有字段均为可选。空对象 `{}` 表示结束节点。

节点行为从结构自动推断（按优先级从高到低）：

| 优先级 | 结构 | 推断行为 |
|--------|------|---------|
| 1 | 空对象 `{}` | 结束 — 终止任务 |
| 2 | 有 `branches` | 决策 — 根据条件路由 |
| 3 | 有 `delegate_to` | 委派 — 调用子任务，完成后继续到 `next` |
| 4 | 有 `wait_for` | 汇聚 — 等待所有列出的节点，然后继续到 `next` |
| 5 | 有 `next`（2+ 个目标） | 并行分叉 — 并发执行目标节点 |
| 6 | 有 `next`（1 个目标） | 处理 — 执行后继续 |

一个节点可同时有多个字段（如 `delegate_to` + `next` + `error`），按优先级取最高的作为主行为。

**示例（基本流程）：**

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

**示例（delegate + join）：**

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

### 4.3 错误路由

任何节点都可以定义 `error` 字段。发生错误时，执行路由到错误处理节点而非 `next`。`error` 是拓扑层面的错误边（相当于 Mermaid 虚线 `-.->`)。细粒度的按类型错误路由见 §5.2 的 `on_error`。

```json
{
  "risky_step": {
    "next": ["continue"],
    "error": "error_handler"
  }
}
```

---

## 5. `functions` — 函数定义

定义每个节点的具体操作和运行时行为。以节点名称为键。每个值包含执行步骤和可选的运行时行为配置。

```json
{
  "functions": {
    "classify": { "step1": "分类用户意图" },
    "process":  { "step1": "处理请求", "step2": "返回结果" },
    "reply":    { "step1": "生成友好的回复" }
  }
}
```

### 5.1 节点命名约定

节点名称可以使用 `_function` 后缀来提示节点在流程中的角色。这有助于 AI 运行时理解节点语义，而不向用户暴露内部结构。

| 约定 | 示例 | 含义 |
|------|------|------|
| `xxx_function` | `execute_function`、`classify_function` | 功能步骤 |
| `end_function` | `end_function` | 带最终输出的终止节点 |

此约定是可选的。语义化名称如 `greet`、`classify`、`search` 同样有效。

### 5.2 保留键

函数体中的键分为两类：

- **执行步骤**：`step1`, `step2`, ... `stepN` — 运行时按顺序执行
- **保留键**（`RESERVED_KEYS`）：运行时识别为行为配置，不作为步骤执行

| 键 | 类型 | 说明 |
|----|------|------|
| `join` | object | 汇聚运行时配置（merge_strategy, timeout） |
| `map` | object | 对集合并行迭代 |
| `on_error` | object | 按错误类型路由到处理节点 |
| `retry_policy` | object | 失败时自动重试 |
| `context_filter` | object | 限制节点的输入上下文 |
| `output_mapping` | string | 将输出存储到指定键 |
| `constraints` | array | 约束声明（不执行） |

> **注意：**
> - `delegate_to` 和 `wait_for` 是拓扑信息，在节点中定义（见 §4.2），不在 functions 中。
> - `join` 在 functions 中仅包含运行时配置（`merge_strategy`, `timeout_seconds`），`wait_for` 在节点中定义。

**运行时解析规则：**
- 不在 `RESERVED_KEYS` 中的键 → 执行步骤
- 在 `RESERVED_KEYS` 中的键 → 行为配置

#### 5.2.1 子流程调用

子流程有两种调用方式，均不属于 `RESERVED_KEYS`：

**(a) 节点层 `delegate_to`（拓扑，见 §4.2）：**

`delegate_to` 是拓扑信息（Mermaid 能画出来），在节点中定义，不在 functions 中。

```json
"gen": { "delegate_to": "generate_sub", "next": ["validate"] }
```

如果 delegate 节点需要额外的运行时配置，可在 functions 中添加步骤：

```json
"gen": { "step1": "准备子流程上下文" }
```

**(b) 步骤层 `RUN aisip.<sub>`（行为，藏在 function 内部）：**

函数步骤内也可以调用子流程。语法：在 step 文本中使用 `RUN aisip.<sub_name>`，与 `instruction` 字段语法一致。

| 层级 | 位置 | 语法 | 场景 |
|------|------|------|------|
| 节点层 | §4.2 节点字段 | `"delegate_to": "sub"` | 整个节点交给子流程 |
| 步骤层 | §5 函数步骤 | step 中写 `RUN aisip.sub` | 某个步骤中途调用子流程 |

节点层 = Mermaid 画得出来（拓扑）。步骤层 = Mermaid 画不出来（行为，藏在 function 内部）。

```json
"function_one": {
  "step1": "做某事",
  "step2": "从网络获取信息，RUN aisip.extract_keywords",
  "step3": "用返回的关键词继续处理"
}
```

执行流程：step1 → step2（中途进入 extract_keywords 子流程，完成后返回）→ step3

#### 5.2.2 `join`

`wait_for` 是拓扑信息（Mermaid 能画出来：多条边汇入），在节点中定义。functions 中的 `join` 仅包含运行时配置：如何合并、等多久。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `merge_strategy` | string | 否 | `"merge"` / `"array"` / `"first"`。默认：`"merge"` |
| `timeout_seconds` | number | 否 | 超时时间（秒）。默认：无 |

`merge_strategy` 选项：
- `merge`：合并为单个对象
- `array`：收集为数组
- `first`：只取第一个完成的结果
- 超时的分支得到 `{error: "timeout"}`

**节点（§4）— 拓扑（等谁）：**

```json
"merge_results": { "wait_for": ["branch_a", "branch_b"], "next": ["end"] }
```

**函数（§5）— 行为（怎么合并）：**

```json
"merge_results": {
  "step1": "合并所有分支的结果",
  "join": {
    "merge_strategy": "array",
    "timeout_seconds": 120
  }
}
```

#### 5.2.3 `map`

对集合中的每个元素执行指定函数。当函数体包含 `map` 时，替代步骤执行。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `items_path` | string | 是 | 集合路径（如 `"state.items"`） |
| `iterator` | string | 是 | 对每个元素执行的函数名 |
| `concurrency` | number | 否 | 最大并行数。默认：1，最大：10 |
| `max_items` | number | 否 | 最大处理条目数 |
| `on_item_error` | string | 否 | `"skip"` / `"fail"` / `"collect"`。默认：`"fail"` |

```json
"batch_search": {
  "step1": "搜索列表中的每个关键词",
  "map": {
    "items_path": "state.keywords",
    "iterator": "search_one",
    "concurrency": 3,
    "on_item_error": "collect"
  }
}
```

#### 5.2.4 `on_error`

按错误类型路由到不同处理节点。比节点的 `error` 字段更细粒度：`error` 是拓扑层面的默认错误边，`on_error` 提供按类型分发的详细路由。

匹配顺序：精确类型 → 分类匹配 → `default` → 节点 `error` 边。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| (键) | string | — | 错误类型（如 `"timeout"`, `"tool_error"`） |
| `default` | string | 否 | 无匹配类型时的兜底处理节点 |

```json
"fetch_data": {
  "step1": "调用外部 API",
  "on_error": {
    "timeout": "timeout_handler",
    "tool_error": "tool_error_handler",
    "default": "global_error"
  }
}
```

#### 5.2.5 `retry_policy`

节点执行失败时自动重试。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `max_attempts` | number | 是 | 总尝试次数含首次（3 = 首次 + 2 次重试） |
| `correction_prompt` | string | 否 | 重试时追加的提示 |
| `backoff_factor` | number | 否 | 指数退避：等待时间 = factor^attempt 秒 |
| `jitter` | boolean | 否 | 添加 0–50% 随机额外等待。默认：`false` |

```json
"call_llm": {
  "step1": "从 LLM 生成 JSON 输出",
  "retry_policy": {
    "max_attempts": 3,
    "correction_prompt": "上次输出不是有效 JSON，请重新生成。",
    "backoff_factor": 2.0,
    "jitter": true
  }
}
```

#### 5.2.6 `context_filter`

限制节点可访问的上下文数据范围。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `include` | string[] | 否 | 白名单 — 只传入这些字段 |
| `exclude` | string[] | 否 | 黑名单 — 排除这些字段 |

`include` 和 `exclude` 互斥，不可同时使用。

```json
"analyze_item": {
  "step1": "分析当前数据项",
  "context_filter": { "include": ["current_item", "config"] }
}
```

#### 5.2.7 `output_mapping`

将节点输出存储到指定键，而非合并到全局上下文。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `output_mapping` | string | 是 | 存储输出的键名 |

通常与 `context_filter` 配合：filter 控制输入，mapping 控制输出。

```json
"process_item": {
  "step1": "处理并返回结构化结果",
  "context_filter": { "include": ["current_item"] },
  "output_mapping": "processed_results"
}
```

### 5.3 执行顺序

运行时对每个节点按以下顺序处理：

1. `context_filter` — 过滤输入上下文
2. `retry_policy` — 包装重试逻辑
3. **执行步骤** — `step1`, `step2`, ...（或由替代执行取代）
4. `on_error` — 按类型路由错误
5. `output_mapping` — 存储输出

**替代执行**（由节点字段触发）：
- 如果节点有 `delegate_to` → 替代步骤，调用子流程
- 如果节点有 `wait_for` → 替代步骤，等待并合并（配合 functions 中的 `join` 配置）
- 如果函数体有 `map` → 替代步骤，迭代执行 iterator
- `delegate_to` / `wait_for` / `map` 互斥，一个节点最多只有一个

**步骤内子流程调用：**
- 如果 step 文本中包含 `RUN aisip.<sub_name>`，运行时暂停当前步骤，执行指定子流程，完成后返回继续下一步骤
- 这不替代步骤，而是在步骤执行过程中嵌套调用

---

## 6. 变量替换

标记为 `{variable}` 的字段在运行时被替换：

| 变量 | 替换为 |
|------|--------|
| `{system_prompt}` | 运行时配置的系统提示 |
| `{user_input}` | 用户的消息 |

---

## 7. 控制流模式

| 模式 | 流程图节点（§4） | 函数（§5） |
|------|-----------------|-----------|
| 顺序 | `"next": ["step_b"]` | — |
| 二分支 | `"branches": {"yes": "approve", "no": "reject"}` | — |
| 多分支 | `"branches": {"billing": "b", "tech": "t", ...}` | — |
| 并行分叉 | `"next": ["step_a", "step_b"]` | — |
| 并行汇聚 | `"wait_for": ["step_a", "step_b"], "next": ["end"]` | `"join": {"merge_strategy": "array"}` |
| 回环 | 分支目标指向已执行过的节点 | — |
| 子任务 | `"delegate_to": "sub_name", "next": ["continue"]` | — |
| 收敛 | 多个节点的 `next` 指向同一节点 | — |
| 错误路由 | `"error": "error_handler"` | `"on_error": {"timeout": "t", "default": "d"}` |
| 批量迭代 | `"next": ["merge"]` | `"map": {"items_path": "...", "iterator": ".."}` |
| 重试 | — | `"retry_policy": {"max_attempts": 3}` |
| 数据隔离 | — | `"context_filter": {"include": [...]}` |
| 步骤内子流程 | — | step 中写 `RUN aisip.sub` |

---

## 8. 完整示例

```json
[
  {
    "role": "system",
    "content": {
      "protocol": "AISIP V1.0.0",
      "id": "customer_support",
      "name": "客户支持机器人",
      "version": "1.0.0",
      "summary": "将客户咨询路由到对应处理程序",
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
        "greet":    { "step1": "欢迎客户并了解问题" },
        "route":    { "step1": "将问题分类为账单、技术或其他" },
        "billing":  {
          "step1": "查询账户详情",
          "step2": "解决账单问题",
          "retry_policy": { "max_attempts": 2, "correction_prompt": "账户查询失败，请重试" },
          "on_error": { "timeout": "escalate", "default": "escalate" }
        },
        "tech":          { "step1": "准备技术诊断上下文" },
        "gather_info":   {
          "step1": "从用户描述中收集系统信息，RUN aisip.extract_keywords",
          "step2": "用提取的关键词搜索知识库"
        },
        "analyze":       {
          "step1": "分析收集的信息并提供诊断",
          "context_filter": { "include": ["gather_info_result", "user_input"] },
          "output_mapping": "diagnosis_result"
        },
        "fork_check":    { "step1": "准备并行检查任务" },
        "check_logs":    { "step1": "检查系统日志中的错误" },
        "check_config":  { "step1": "验证配置设置" },
        "merge_results": {
          "step1": "将所有检查结果合并为最终报告",
          "join": { "merge_strategy": "array", "timeout_seconds": 60 }
        },
        "parse":     { "step1": "解析文本并提取候选关键词" },
        "filter":    { "step1": "按相关性过滤和排序关键词" },
        "general":   { "step1": "回答一般咨询" },
        "escalate":  { "step1": "为问题致歉", "step2": "转接人工客服" },
        "end":       { "step1": "输出最终回复给用户" }
      }
    }
  }
]
```
