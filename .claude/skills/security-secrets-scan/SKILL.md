# security-secrets-scan

Use this skill for `/ai-security`, `/ai-check`, and `/ai-sync`.

Focus areas:

- source files
- config files
- Dockerfiles and compose files
- env files and examples
- staged or modified content when available

High-confidence blockers include:

- API keys
- access tokens
- private keys
- passwords in plaintext

For each issue, report:

- location
- issue type
- confidence
- remediation
- whether commit or push should be blocked
