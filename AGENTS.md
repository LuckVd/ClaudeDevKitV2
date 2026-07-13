# AGENTS.md

本项目使用 **ClaudeDevKit** 轻量工程工作流。本文件面向**不原生识别 `.claude/` 的 AI 编码工具**(如 OpenCode、Cursor 等),告诉它如何参与这套工作流。

## 这是什么

一个「贵模型规划编排 + 便宜模型并行开发」的轻量纪律模板。核心:用 `docs/ai/` 下的文件做跨会话共享状态,用 git worktree 做物理隔离,用人类确认 gate 兜底关键决策。

## 关键文件(先读)

- `docs/ai/convention.md` —— **角色边界、并行编排、提交纪律**。最重要,先读。
- `docs/ai/roadmap.md` —— 项目技术蓝图与长期进度(唯一事实来源)。
- `docs/ai/goals/INDEX.md` —— 并行目标看板(派生投影)。
- `docs/ai/goals/<id>.md` / `<id>.state.yaml` —— 每个目标的设计文档与状态。
- `docs/ai/constraints/` —— 全局与项目硬约束。
- `docs/ai/change-log.md` —— 变更记录。

## 命令(OpenCode 原生 slash)

本项目已适配 OpenCode 原生命令(`.opencode/commands/`,通过 `@file` 复用 `.claude/commands/` 内容,零重复维护)。直接输入 `/` + 命令名:

| 命令 | 作用 | 默认 agent |
|---|---|---|
| `/ai-init` | 初始化 / 修复骨架 | 默认 |
| `/ai-goal` | 选定并设计目标 | orchestrator |
| `/ai-dispatch` | 发布目标到看板 | orchestrator |
| `/ai-claim` | 执行者领取目标 | **executor(红线强制)** |
| `/ai-status` | 渲染并行看板 | 默认 |
| `/ai-check` | 健康检查 | 默认 |
| `/ai-sync` | 回写 + 协助提交 | orchestrator |
| `/ai-help` | 状态 + 推荐下一步 | 默认 |
| `/ai-notes` | 本地笔记(不入库) | 默认 |

**两个角色 agent**(Tab 切换;定义在 `opencode.json`):

- `executor`(执行者·便宜模型):`permission` 原生拦截 `git push`/`merge`/`rebase`/`reset --hard`/切主线——红线由工具强制,不靠自觉。
- `orchestrator`(编排者·贵模型):git 写操作(`push`/`merge`/`commit`)需确认。

命令的真实逻辑在 `.claude/commands/`(被 `.opencode/commands/` 复用);命令里引用的 skill 在 `.claude/skills/<name>/SKILL.md`,已被对应 `.opencode` 命令一并 `@file` 加载。

## 两个角色

- **编排者(贵模型)**:规划、设计、发布(`/ai-dispatch`)、评审、合并、回写(`/ai-sync`)。同一时刻建议只有一个编排者管主线合并。
- **执行者(便宜模型,可多个)**:`/ai-claim` 领取 → 在专属 worktree 写代码 → 完工 parking(`ready_for_review`)。

## 硬纪律(无 hook 兜底,全靠你自觉遵守)

你所在工具可能没有 Claude Code 的 hook,以下纪律**必须自觉遵守**:

- **不自动 commit / push**;任何 `git add`/`commit`/`push` 前必须停下问用户。
- **执行者红线**:不改 `roadmap.md` 状态、不自行合并、不向主线 commit/push;完工只置 `ready_for_review` + `pending_review`。
- **合并与主线提交只由编排者做**,且必须经用户确认。
- **领取伪原子**:`/ai-claim` 守卫 `owner` 为空 → 写 → **写后回读校验** owner 是自己;被覆盖则退出。
- **破坏性 git**(`push --force` / `push --delete` / `reset --hard` 到远端)绝不做;需要时让用户在自己终端执行。
- 文档与代码不一致,先问用户,不要擅自改。

## worktree 约定

每个并行目标一个分支 + worktree:

```
git worktree add .claude/worktrees/<id-小写kebab> -b goal/<id-小写kebab> main
```

`.claude/worktrees/` 已被 gitignore,不入库。

## 快速开始

1. 先读 `docs/ai/convention.md` 和 `docs/ai/goals/INDEX.md` 了解现状。
2. 若是执行者:读 `.claude/commands/ai-claim.md`,从 INDEX 找 `ready_to_claim` 目标领取。
3. 若是编排者:读 `.claude/commands/ai-dispatch.md`(发布)或 `ai-sync.md`(回写合并)推进目标生命周期。
4. 不确定做什么:读 `.claude/commands/ai-help.md` + `.claude/skills/help-router/SKILL.md`,按状态推荐下一步。
