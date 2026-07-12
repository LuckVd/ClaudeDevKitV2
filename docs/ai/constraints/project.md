# Project Constraints

- Record project-specific conventions here.
- Prefer extending existing modules over adding parallel abstractions.
- Add project-specific testing or release gates here when needed.

## 多实例并行协作红线

- 每个并行目标一个独立分支（`goal/<id>`）与 worktree（`.claude/worktrees/<id>/`），物理隔离避免冲突。
- 执行者（便宜模型）不得修改 `roadmap.md` 状态、不得自行合并到主线、不得 commit/push 到主线；完工只置 `stage: ready_for_review` + `merge_status: pending_review`。
- 合并与 roadmap 回写由编排者（贵模型）在主线完成，且必须经用户确认。
- `goals/INDEX.md` 是派生投影，由 `/ai-status`/编排者重渲染，不要手工长编辑。
- 提交纪律依赖三层：用户确认 gate（主闸）、执行者红线约定、hook 兜底破坏性 git 操作（见 `.claude/settings.json`）。
