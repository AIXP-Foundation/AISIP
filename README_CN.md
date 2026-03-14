# AISIP — AI Standard Instruction Protocol

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)

**用 JSON 定义结构化 AI 程序的开放协议。**

AISIP 将多步骤 AI 程序定义为结构化 JSON 文件 — 支持控制流、分支、并行执行、子任务和错误处理 — 全部在一个可移植的格式中。

## 为什么选择 AISIP？

| 方案 | 定义方式 | 可移植 | 机器可读 |
|------|---------|--------|---------|
| 自然语言提示 | 自由文本 | 是 | 否 |
| Python / YAML 工作流 | 代码 / 配置 | 否 | 部分 |
| 可视化构建器 (Dify 等) | 专有格式 | 否 | 否 |
| **AISIP** | **JSON** | **是** | **是** |

AISIP 文件是纯 JSON — 任何语言可读、任何编辑器可编辑、可用 git 版本管理。

## 文件格式

AISIP 文件使用 `.aisip.json` 扩展名，由两个元素组成的 JSON 数组：

```json
[
  { "role": "system", "content": { "protocol": "AISIP V1.0.0", ... } },
  { "role": "user",   "content": { "instruction": "...", "aisip": { ... }, "functions": { ... } } }
]
```

| 元素 | 用途 |
|------|------|
| `system` | 程序元数据（身份、版本、描述、系统提示） |
| `user` | 指令、用户输入、流程图、函数定义 |

## 快速示例

```json
[
  {
    "role": "system",
    "content": {
      "protocol": "AISIP V1.0.0",
      "id": "greeting_assistant",
      "name": "问候助手",
      "version": "1.0.0",
      "summary": "分类用户意图并回复"
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
        "greet":    { "step1": "向用户问好并了解需求" },
        "classify": { "step1": "判断用户意图是 question 还是 chat" },
        "search":   { "step1": "搜索相关信息并回答" },
        "reply":    { "step1": "生成友好的对话回复" },
        "end":      { "step1": "输出最终回复给用户" }
      }
    }
  }
]
```

```
greet -> classify --(question)--> search -> end
                  \--(chat)-----> reply  -> end
```

## 核心特性

- **13 种控制流模式** — 顺序、决策、并行分叉/汇聚、委派、回环、收敛、错误路由、批量迭代、重试、数据隔离、步骤内子流程
- **无 type 节点** — 无需 `type` 字段，行为从结构自动推断
- **三层分离** — 元数据、流程图、函数定义
- **拓扑/行为分离** — 节点定义连接（Mermaid 能画出来的），函数定义运行时行为
- **子任务支持** — `main` + 命名子任务，通过 `delegate_to` 或步骤层 `RUN aisip.<sub>` 调用
- **保留键** — 函数中 7 个运行时行为键（join, map, on_error, retry_policy, context_filter, output_mapping, constraints）
- **错误处理** — 节点层 `error` 边 + 函数层 `on_error` 类型路由
- **变量替换** — `{system_prompt}`、`{user_input}` 在运行时替换
- **零依赖** — 参考实现仅使用 Python 标准库
- **AI 无关** — 可与任何 AI 运行时配合使用

## 节点结构

节点只定义拓扑（连接关系），行为从结构自动推断：

| 结构 | 推断行为 | 写法 |
|------|---------|------|
| 有 `next`（1 个目标） | 处理 — 执行后继续 | `"next": ["reply"]` |
| 有 `branches` | 决策 — 条件分支 | `"branches": {"yes": "a", "no": "b"}` |
| 有 `wait_for` | 汇聚 — 等待并行分支 | `"wait_for": ["a", "b"], "next": ["c"]` |
| 有 `delegate_to` | 委派 — 调用子任务 | `"delegate_to": "sub", "next": ["c"]` |
| 空 `{}` | 结束 — 终止任务 | `{}` |

## 控制流模式

| 模式 | 流程图节点（§4） | 函数（§5） |
|------|-----------------|-----------|
| 顺序 | `"next": ["step_b"]` | — |
| 二分支 | `"branches": {"yes": "approve", "no": "reject"}` | — |
| 多分支 | `"branches": {"billing": "b", "tech": "t", ...}` | — |
| 并行分叉 | `"next": ["step_a", "step_b"]` | — |
| 并行汇聚 | `"wait_for": ["a", "b"], "next": ["end"]` | `"join": {"merge_strategy": "array"}` |
| 回环 | 分支目标指向已执行过的节点 | — |
| 子任务 | `"delegate_to": "sub", "next": ["continue"]` | — |
| 收敛 | 多个节点的 `next` 指向同一节点 | — |
| 错误路由 | `"error": "handler"` | `"on_error": {"timeout": "t"}` |
| 批量迭代 | `"next": ["merge"]` | `"map": {"items_path": "..."}` |
| 重试 | — | `"retry_policy": {"max_attempts": 3}` |
| 数据隔离 | — | `"context_filter": {"include": [...]}` |
| 步骤内子流程 | — | step 中写 `RUN aisip.sub` |

## 快速开始

```bash
# 检查流程文件
cd reference/python
python run.py example.aisip.json

# 运行测试（无需 AI）
python test_all.py

# 构建提示词
python run.py example.aisip.json --prompt "你好"
```

## 项目结构

```
AISIP/
  specification/
    aisip-spec.md            # 协议规范 (V1.0.0)
    aisip-spec_CN.md          # 协议规范 — 中文版
  docs/
    comparison-mermaid.md     # AISIP vs Mermaid 对比
    performance-aisop-vs-aisip.md  # AISOP vs AISIP 性能对比
  reference/
    python/
      flow_runtime.py         # 参考实现（加载器、验证器、工具集）
      example.aisip.json      # 示例流程定义
      test_all.py             # 测试套件
      run.py                  # 命令行工具
  LICENSE
  CONTRIBUTING.md
  CHANGELOG.md
```

## 相关协议

| 协议 | 范围 |
|------|------|
| [AISOP](https://aisop.dev) | AI Standard Operating Protocol |
| [AIAP](https://aiap.dev) | AI Application Protocol |
| [AISIP](https://aisip.dev) | AI Standard Instruction Protocol（本协议） |

## 公理

AISIP 以**公理 0：人类主权与福祉**为基础 — AI 系统服务于人类，而非取代或支配人类。所有实现必须将此公理置于执行优先级的最高层。完整内容见[规范 §0](specification/aisip-spec_CN.md)。

## 贡献

见 [CONTRIBUTING_CN.md](CONTRIBUTING_CN.md) 了解贡献指南 / See [CONTRIBUTING.md](CONTRIBUTING.md) for English guidelines.

## 许可证

[MIT](LICENSE) - Copyright (c) 2026 AIXP Foundation AIXP.dev | AISIP.dev
