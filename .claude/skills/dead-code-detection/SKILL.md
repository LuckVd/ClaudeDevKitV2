# dead-code-detection

Use this skill for `/ai-deadcode` or before `/ai-sync` when dead code may affect the result.

Detection policy:

- default to high-confidence findings only
- prioritize unreachable code
- then unused code with no incoming references
- then code obviously unrelated to the project's current goals

For each finding, report:

- path
- symbol or code block
- evidence
- confidence
- suggested disposition

Do not delete code automatically.
