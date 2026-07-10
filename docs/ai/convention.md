# 工作约定

本框架只保留强 LLM 和原生平台都替代不了的东西：

- **外部记忆**：跨会话的路线图与当前目标
- **约束一致性**：硬约束的统一加载与检查
- **进度回写**：把实现结果同步回路线图与变更记录
- **人类确认 gate**：方案、提交、推送前的确认

其余能力一律交给 Claude Code 原生机制，不要自己造。

## 原生能力对照表

| 需求 | 用这个，不要自己实现 |
|---|---|
| 实现前确认方案 | `plan mode` / `ExitPlanMode` |
| 方案评审 | `design-reviewer` subagent |
| 影响面分析 | `impact-mapper` subagent |
| 代码审查 / 死代码 / 可简化点 | 原生 `/code-review`、`/simplify` |
| 密钥与安全扫描 | 原生 `/security-review` |
| 实现后端到端验证 | 原生 `/verify` |
| 不自动提交的纪律 | `.claude/settings.json` hooks |
| 跨会话记忆 | 本框架的 `roadmap.md` + `current-goal.md` |

## 原则

- 状态只读写 `roadmap.md` / `current-goal.md` / `current-goal.state.yaml` / `change-log.md`。
- 让模型自己读代码，不维护项目结构摘要。
- 关键节点（方案确认、提交、推送）必须停下问用户。
- 发现文档与代码不一致，先问用户，不要擅自改。
- bug 修复、特性开发、TDD 这些流程本身交给正常对话，不再由命令强制驱动。
