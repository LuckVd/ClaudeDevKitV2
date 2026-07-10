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
