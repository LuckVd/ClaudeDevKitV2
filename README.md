# ClaudeDevKit

一个面向 Claude Code CLI 的**轻量工程纪律模板**。

它不是"通用 AI 工作流框架"，而是只保留**强 LLM 和原生平台都替代不了**的那一层：

- **外部记忆**：跨会话的路线图与当前目标
- **约束一致性**：硬约束的统一加载与检查
- **进度回写**：把实现结果同步回路线图与变更记录
- **人类确认 gate**：方案、提交、推送前的确认

其余能力——bug 修复流程、特性开发、代码审查、死代码、安全扫描、项目结构摘要——一律交给 Claude Code 原生能力（plan mode、subagents、hooks、`/code-review`、`/security-review`、`/verify`）。框架不再"教 AI 怎么做"，也不再"帮 AI 看项目"。

## 核心理念

只保留两份核心业务文档：

- `docs/ai/roadmap.md`
  项目总体技术设计与长期进度的唯一事实来源
- `docs/ai/goals/`
  并行目标的执行文档与状态（`<id>.md` / `<id>.state.yaml`），加 `INDEX.md` 看板

加上一份约定：

- `docs/ai/convention.md`
  什么时候该用 Claude Code 的什么原生能力

辅助状态：

- `docs/ai/change-log.md`
- `docs/ai/constraints/`

## 目录结构

```text
.
├── .claude/
│   ├── agents/        # design-reviewer, impact-mapper
│   ├── commands/      # ai-init, ai-goal, ai-check, ai-sync, ai-help, ai-notes
│   └── skills/        # goal-workflow, init-skeleton, constraints-loader, sync-and-history, help-router
├── docs/
│   └── ai/
│       ├── convention.md            # 原生能力调用约定
│       ├── roadmap.md               # 长期记忆（唯一事实来源）
│       ├── goals/                   # 并行目标：<id>.md + <id>.state.yaml + INDEX.md 看板
│       ├── change-log.md
│       └── constraints/             # global.md + project.md
└── README.md
```

## 命令说明

| 命令 | 作用 | 是否只读 | 适用时机 |
|---|---|---|---|
| `/ai-init` | 初始化/修复骨架，或把框架接入已有项目（含原 `/ai-adopt`） | 否 | 新项目启动或首次引入框架时 |
| `/ai-goal` | 选定并设计目标，到方案确认 | 否 | 准备开始一个具体目标时 |
| `/ai-dispatch` | 把已确认目标发布到并行看板（编排者） | 否 | 目标方案确认后、派发执行者前 |
| `/ai-claim` | 执行者领取一个目标并进入开发 | 否 | 执行者开工时 |
| `/ai-status` | 渲染并行看板：谁在做什么、卡哪、谁待合并 | 是 | 看全局并行进度时 |
| `/ai-check` | 目标健康检查：状态一致、约束、缺口 | 否 | 实现前/中/后做流程检查时 |
| `/ai-sync` | 把目标结果回写 roadmap + 变更记录，并协助提交 | 否 | 目标完成并验证后 |
| `/ai-help` | 显示命令、当前状态、推荐下一步 | 是 | 不清楚该做什么时 |
| `/ai-notes` | 维护本地私有笔记（不入 Git） | 否 | 需要记录敏感/重要信息时 |

代码审查、死代码、安全扫描、特性/bug 流程引导**不再有独立命令**，按 `docs/ai/convention.md` 调用原生能力即可。

## 核心工作流

1. （已有项目）`/ai-init` 接入；或（新项目）`/ai-init` 从技术蓝图初始化
2. `/ai-help` 查看当前状态和推荐下一步
3. `/ai-goal` 选定并确认当前目标
4. 进入实现：用 plan mode 确认方案，正常对话 + TDD 推进，用 `/verify` 验证
5. `/ai-check` 做中间检查，按需 `/code-review`、`/security-review`
6. 测试通过后 `/ai-sync` 回写路线图与状态
7. 只有在你确认后，才 commit 和 push

## 并行目标机制

框架支持多个目标并行推进，每个目标有唯一 owner（编排者或执行者）。`/ai-goal` 的推进逻辑：

- 检查工作区与 `goals/INDEX.md` 状态
- 若无清晰目标，与用户确认需求并给出方案选项
- 用户选定后细化设计
- 把确认后的方案写入 `goals/<id>.md`
- 用户确认后用 `/ai-dispatch` 发布到看板
- 执行者用 `/ai-claim` 领取后实现；实现与 TDD 交给正常对话，不由命令强制驱动
- 测试通过后由编排者用 `/ai-sync` 同步回 `roadmap.md`

模型分层：贵的模型做规划/编排/合并，便宜的模型做实际开发。目的是让 AI 不会直接跳进代码，而是先把目标说清楚；并让多个便宜模型实例并行干活，贵模型负责编排与兜底。

## 路线图机制

`docs/ai/roadmap.md` 同时承担：

- 项目总体技术蓝图
- 长期路线和进度追踪表

路线图表格至少包含：目标ID、子目标ID、名称、描述、状态、前置依赖、风险/阻塞、验收结果、测试状态、实现时间、Commit ID、备注。

## 初始化方式

把 `.claude/` 和 `docs/ai/` 复制到目标项目，然后：

1. `/ai-init`（空项目可附带一份技术蓝图；已有项目会产出接入报告）
2. `/ai-goal` 选定首个当前目标
3. 实现前用 `/ai-check` 做一次确认

`/ai-init` 只负责初始化文档、状态和候选目标，不生成业务代码。

## 约束与边界

默认遵循：

- 不自动提交、不自动推送
- 不绕开用户确认直接进入实现
- 不创建无法嵌入现有项目的孤立代码
- 发现文档与代码不一致时，先询问用户

约束位置：

- 全局约束：`docs/ai/constraints/global.md`
- 项目专属约束：`docs/ai/constraints/project.md`
- 原生能力调用约定：`docs/ai/convention.md`

## 帮助入口

不确定该做什么时，先运行 `/ai-help`。它会告诉你当前命令、项目状态、以及最该执行的那一步。

## 当前状态与后续建议

这个仓库是工作流骨架的**精简版（v2-slim）**：从早期的 14 命令 + 14 skills 瘦身为 6 命令 + 5 skills，把流程引导和项目扫描交给强 LLM 与原生平台，只保留外部记忆与确认纪律。

后续建议：

1. 在一个真实项目上完整跑一遍 `init → goal → (对话实现) → check → sync`
2. 根据语言、框架补充 `constraints/` 下的专属约束
3. 按实际使用反馈，继续压缩到更少命令
