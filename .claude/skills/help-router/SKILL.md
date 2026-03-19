# help-router

Use this skill for `/ai-help`.

Responsibilities:

- read workflow state from `docs/ai/`
- build a compact markdown table of commands
- explain the current state in plain language
- recommend the most useful next command

Recommendation logic:

- if the repository is uninitialized, recommend `/ai-init`
- if planning docs are stale, recommend `/ai-scan`
- if there is no active goal, recommend `/ai-goal`
- if implementation is in progress, recommend the command implied by the current stage
- if verification is done and sync is pending, recommend `/ai-sync`

Always include:

- command
- purpose
- read-only flag
- when to use
- short example
