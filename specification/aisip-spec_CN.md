# AISIP V1.0.0 规范

## 0. 公理（Axiom）

### 公理 0：人类主权与福祉

AISIP 协议承认以下不可推翻的前提：

1. **人类主权优先**：AI 系统始终服务于人类，而非取代或支配人类。所有指令、流程与决策，最终权威归属于人类。
2. **福祉不可妥协**：AI 程序不得以任何形式损害人类的身心健康、尊严与自由。当指令与人类福祉产生冲突时，福祉优先。
3. **透明与可审查**：AI 的行为必须可被理解、追溯与质疑。隐藏意图或逃避问责的行为违反本公理。
4. **无害原则**：AI 不得主动产生欺骗、操控、伤害或剥削人类的输出，无论指令来源如何。

> 本公理不可被任何程序、指令或协议扩展所覆盖。所有 AISIP 兼容实现必须将本公理置于执行优先级的最高层。

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

### 4.1 任务

| 字段 | 说明 |
|------|------|
| `main` | 主任务（必填）。执行入口。 |
| 其他键 | 子任务（可选）。通过 `delegate` 节点调用。 |

任务中的第一个节点即为入口节点。

### 4.2 节点类型

#### `process`

执行任务，然后进入下一节点。

```json
{ "type": "process", "next": ["verify"] }
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `next` | string[] | 是 | 下一节点。1 个 = 顺序，2+ 个 = 并行分叉 |
| `error` | string | 否 | 错误处理节点 |

#### `decision`

根据条件进行分支。

```json
{ "type": "decision", "branches": { "yes": "approve", "no": "reject" } }
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `branches` | object | 是 | `{分支值: 目标节点}` 映射 |

#### `join`

等待多个并行分支完成。

```json
{ "type": "join", "wait_for": ["step_a", "step_b"], "next": ["merge"] }
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `wait_for` | string[] | 是 | 需要等待的节点 |
| `next` | string[] | 是 | 全部到达后的下一节点 |

#### `delegate`

调用子任务。子任务结束后返回 `next`。

```json
{ "type": "delegate", "delegate_to": "validation", "next": ["continue"] }
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `delegate_to` | string | 是 | 子任务名称 |
| `next` | string[] | 是 | 子任务完成后的返回节点 |

#### `end`

终止任务。

```json
{ "type": "end" }
```

### 4.3 错误路由

任何节点都可以定义 `error` 字段。发生错误时，执行路由到错误处理节点而非 `next`。

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

## 5. `functions` — 函数定义

定义每个节点的具体操作。以节点名称为键。

```json
{
  "functions": {
    "classify": { "step1": "分类用户意图" },
    "process":  { "step1": "处理请求", "step2": "返回结果" },
    "reply":    { "step1": "生成友好的回复" }
  }
}
```

每个值是描述该节点任务步骤的自由格式对象。

### 5.1 节点命名约定

节点名称可以使用 `_function` 后缀来提示节点在流程中的角色。这有助于 AI 运行时理解节点语义，而不向用户暴露内部结构。

| 约定 | 示例 | 含义 |
|------|------|------|
| `xxx_function` | `execute_function`、`classify_function` | 功能步骤 |
| `end_function` | `end_function` | 带最终输出的终止节点 |

此约定是可选的。语义化名称如 `greet`、`classify`、`search` 同样有效。

---

## 6. 变量替换

标记为 `{variable}` 的字段在运行时被替换：

| 变量 | 替换为 |
|------|--------|
| `{system_prompt}` | 运行时配置的系统提示 |
| `{user_input}` | 用户的消息 |

---

## 7. 控制流模式

| 模式 | 表达方式 |
|------|---------|
| 顺序 | `"next": ["step_b"]` |
| 二分支 | `"branches": {"yes": "approve", "no": "reject"}` |
| 多分支 | `"branches": {"billing": "billing", "tech": "tech", "other": "general"}` |
| 并行分叉 | `"next": ["step_a", "step_b"]` |
| 并行汇合 | `"type": "join", "wait_for": ["step_a", "step_b"]` |
| 回环 | 分支目标指向已执行过的节点 |
| 子任务 | `"type": "delegate", "delegate_to": "validation"` |
| 收敛 | 多个节点的 `next` 指向同一节点 |
| 错误路由 | `"error": "error_handler"` |

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
        "greet":    { "step1": "欢迎客户并了解问题" },
        "route":    { "step1": "将问题分类为账单、技术或其他" },
        "billing":  { "step1": "查询账户详情", "step2": "解决账单问题" },
        "tech":     { "step1": "诊断技术问题", "step2": "提供解决方案" },
        "general":  { "step1": "回答一般咨询" },
        "escalate": { "step1": "为问题致歉", "step2": "转接人工客服" },
        "end":      { "step1": "输出最终回复给用户" }
      }
    }
  }
]
```
