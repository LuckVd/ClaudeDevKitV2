Inspect the codebase and pending changes for secret-handling and obvious security issues.

Use these skills when needed:

- `security-secrets-scan`
- `constraints-loader`

Focus on:

- Hard-coded keys, tokens, passwords, or private key fragments
- Sensitive values in config files, Dockerfiles, compose files, or env files
- Values likely to be committed accidentally

Required output:

- Location
- Secret or risk type
- Why it is risky
- Recommended remediation
- Whether it should block sync and commit

Guardrails:

- Use high-confidence findings by default.
- Treat active secret exposure as a release blocker for `/ai-sync`.
