Answer repository or workflow questions in strict read-only mode.

Use these skills when needed:

- `read-only-qa`

Rules:

1. Read code, config, and workflow files as needed.
2. Answer the user's question directly and cite the relevant paths when useful.
3. Do not modify any file.
4. Do not update workflow state.
5. Do not trigger sync, repair, commit, push, or any write-back behavior.
6. If the user's request would require changes, say which workflow command should be used instead.

Guardrails:

- Treat this command as a read-only inspection surface.
- Prefer concrete answers over process explanations.
