# Change Log

## 2026-03-19

- Goal ID: bootstrap
- Summary: Initialized the Claude Code workflow skeleton.
- Impact: `docs/ai`, `.claude/commands`, `.claude/skills`, `.claude/agents`
- Tests: structure verification pending
- Dead Code: not run
- Security: not run
- Commit Status: not committed

## 2026-07-11

- Goal ID: framework-slim (refactor)
- Summary: 把工作流从 14 命令 + 14 skills 瘦身为 6 命令 + 5 skills。移除流程引导与项目扫描类机制；代码审查 / 安全 / 验证改走原生能力（见 `convention.md`）。`/ai-adopt` 并入 `/ai-init`；goal-discovery + goal-design 合并为 `goal-workflow`；init-from-proposal + project-adoption 合并为 `init-skeleton`。被移除资产归档到 `_archive/`。
- Impact: `.claude/{commands,skills,agents}`、`docs/ai/{README.md,convention.md}`；删除 `docs/ai/{project-tree,project-summary}.md`
- Tests: 结构一致性已自检
- Native review: 未运行（需要时用 `/code-review`、`/security-review`）
- Commit Status: not committed

## 2026-07-11

- Goal ID: parallel-mode
- Summary: 把「单一当前目标」状态模型升级为「多目标并行看板」，支持多 AI 实例协作（贵模型编排 + 便宜模型执行）。
- Impact: 新增 `goals/`（`INDEX.md` + `_TEMPLATE.*`），废弃 `current-goal.*` 单例；新增命令 `/ai-dispatch`、`/ai-claim`、`/ai-status` 与 skill `claim-workflow`；`convention.md` 加「模型分工」「并行编排」「提交纪律」三节；新建 `.claude/settings.json` + hook 兜底破坏性 git；`.gitignore` 忽略 `.claude/worktrees/`；现有命令/skill/README 引用从单例迁到 `goals/`。
- Tests: 结构一致性已自检（grep 验证 `current-goal` 仅 `_archive/` 残留）
- Native review: 未运行（需要时用 `/code-review`、`/security-review`）
- Commit Status: not committed
