# AI Workflow

This repository uses a lightweight Claude Code workflow — an engineering-discipline template, not a full framework.

Shared state lives in this directory. Process behavior lives under `.claude/`.

Default read set:

- `roadmap.md`
- `current-goal.md`
- `current-goal.state.yaml`
- `change-log.md`
- `convention.md`

Rules:

- Do not auto-commit or auto-push.
- Do not create isolated code that does not fit the existing project.
- If workflow docs disagree with the codebase, ask the user whether to sync the docs.
- Only one active current goal is allowed at a time.
- Prefer Claude Code native capabilities over custom machinery; see `convention.md`.

Slash commands:

- `/ai-help`
- `/ai-init`
- `/ai-goal`
- `/ai-check`
- `/ai-sync`
- `/ai-notes`

Command intent:

- `/ai-init` initializes or repairs the skeleton, and safely adopts the workflow into an existing repository (formerly `/ai-adopt`).
- `/ai-goal` drives the current goal from selection through plan confirmation.
- `/ai-check` runs a health check on the active goal.
- `/ai-sync` writes results back to the roadmap and change log, and assists with commit/push on confirmation.
- `/ai-help` shows the current state and recommends the next command.
- `/ai-notes` maintains local private notes that are never committed.

Bug fixing, feature work, code review, dead-code and security scanning no longer have dedicated commands — use native plan mode, `/code-review`, `/security-review`, and `/verify` as described in `convention.md`.

Document roles:

- `roadmap.md` is the single source of truth for overall technical design and long-term progress.
- `current-goal.md` is the execution document for the active goal.
- `convention.md` maps common needs to the right Claude Code native capability.
- `change-log.md` records what each goal changed.

Human-editable constraints live in `constraints/`. Claude-native behavior lives in `.claude/skills` and `.claude/agents`.
