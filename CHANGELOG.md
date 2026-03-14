# Changelog

## 2026-03-14 — Node Structure Alignment & Functions Extension

### Changed
- **§4.2 Node Structure**: Removed `type` field from all nodes. Node behavior is now inferred from structure (has `branches` → decision, has `delegate_to` → delegate, has `wait_for` → join, has `next` → process, `{}` → end). Priority-based inference with 6 levels.
- **§4.1 Tasks**: Sub-tasks now callable via node `delegate_to` field or step-level `RUN aisip.<sub>`.
- **§4.3 Error Routing**: Removed `type` from example, added reference to `on_error` in §5.2.
- **§7 Control Flow Patterns**: Expanded from 9 to 13 patterns with two-column table (Flow Graph + Functions).
- **§8 Complete Example**: Rewritten to demonstrate delegate_to, wait_for/join, RUN aisip.sub, retry_policy, on_error, context_filter, and output_mapping.

### Added
- **§5.2 Reserved Keys**: 7 RESERVED_KEYS (join, map, on_error, retry_policy, context_filter, output_mapping, constraints) with runtime parsing rules.
- **§5.2.1 Sub-task Invocation**: Two-level sub-task invocation — node-level `delegate_to` (topology) and step-level `RUN aisip.<sub>` (behavior).
- **§5.2.2 join**: Runtime config (merge_strategy, timeout_seconds) separate from node-level `wait_for`.
- **§5.2.3 map**: Collection iteration with concurrency control.
- **§5.2.4 on_error**: Type-based error routing with fallback chain.
- **§5.2.5 retry_policy**: Auto-retry with backoff and correction prompt.
- **§5.2.6 context_filter**: Input context restriction (include/exclude).
- **§5.2.7 output_mapping**: Named output storage.
- **§5.3 Execution Order**: 5-step processing order + substitute execution rules + step-level sub-task invocation.

### Removed
- `type` field from all node definitions and examples.
- Separate `process`, `decision`, `join`, `delegate`, `end` subsections in §4.2 (consolidated into Node Structure table).

### Design Principle
- **Topology vs Behavior**: Mermaid can draw it = topology = node fields (`next`, `branches`, `error`, `delegate_to`, `wait_for`). Mermaid cannot draw it = runtime behavior = functions RESERVED_KEYS.
- Protocol version remains AISIP V1.0.0. Backward compatible — runtime can recognize nodes with or without `type` field.
