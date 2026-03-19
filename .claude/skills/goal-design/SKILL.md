# goal-design

Use this skill after the user has selected a direction for the current goal.

Requirements:

- Fill in scope, out-of-scope, acceptance criteria, test plan, and implementation steps.
- Expand the plan into explicit steps and tasks in `docs/ai/current-goal.md`.
- Surface every ambiguity that could materially change the implementation.
- Make the design fit the existing project instead of creating a separate subsystem.
- Prefer small, reviewable steps.

Before allowing implementation:

1. Confirm all critical assumptions.
2. Write the design into `docs/ai/current-goal.md`.
3. Set `stage: confirm_plan` in `docs/ai/current-goal.state.yaml`.
