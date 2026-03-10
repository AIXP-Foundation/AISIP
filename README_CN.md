# AISIP — AI Standard Instruction Protocol

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**用 JSON 定义结构化 AI 程序的开放协议。**

## 文件格式

AISIP 文件使用 `.aisip.json` 扩展名，由两个元素组成的 JSON 数组：

```json
[
  { "role": "system", "content": { ... } },
  { "role": "user",   "content": { ... } }
]
```

| 元素 | 用途 |
|------|------|
| `system` | 程序元数据（身份、版本、描述、系统提示） |
| `user` | 指令、用户输入、流程图、函数定义 |

## 规范

完整格式定义见 [specification.md](specification.md)。

## 示例

```json
[
  {
    "role": "system",
    "content": {
      "protocol": "AISIP V2.0.0",
      "id": "greeting_assistant",
      "name": "问候助手",
      "version": "1.0.0",
      "summary": "分类用户意图并回复",
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
        "classify": { "step1": "判断用户意图是 question 还是 chat" },
        "search":   { "step1": "搜索相关信息并回答" },
        "reply":    { "step1": "生成友好的对话回复" },
        "end":      { "step1": "输出最终回复给用户" }
      }
    }
  }
]
```

## 节点类型

| 类型 | 用途 | 写法 |
|------|------|------|
| `process` | 执行任务 | `"next": ["reply"]` |
| `decision` | 条件分支 | `"branches": {"yes": "approve", "no": "reject"}` |
| `join` | 并行汇合 | `"wait_for": ["step_a", "step_b"]` |
| `delegate` | 调用子流程 | `"delegate_to": "validation"` |
| `end` | 结束 | `{"type": "end"}` |

## 控制流模式

| 模式 | 表达方式 |
|------|---------|
| 顺序 | `"next": ["process"]` |
| 二分支 | `"branches": {"yes": "approve", "no": "reject"}` |
| 多分支 | `"branches": {"billing": "billing", "tech": "tech", "other": "general"}` |
| 并行分叉 | `"next": ["step_a", "step_b"]` |
| 并行汇合 | `"type": "join", "wait_for": ["step_a", "step_b"]` |
| 回环 | 分支目标指向已执行过的节点 |
| 子流程 | `"type": "delegate", "delegate_to": "validation"` |
| 收敛 | 多个节点的 `next` 指向同一节点 |
| 错误处理 | `"error": "error_handler"` |

## 相关协议

| 协议 | 范围 |
|------|------|
| [AISOP](https://aisop.dev) | AI Standard Operating Protocol |
| [AIAP](https://aiap.dev) | AI Application Protocol |
| [AISIP](https://aisip.dev) | AI Standard Instruction Protocol（本协议） |

## 许可证

[MIT](LICENSE) - Copyright (c) 2026 AIXP Foundation AIXP.dev | AISIP.dev
