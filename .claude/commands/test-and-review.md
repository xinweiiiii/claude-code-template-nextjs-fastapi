Run a full quality gate on the current changes: write tests, audit security, then review code.

1. Use the `test-writer` subagent on the files changed in the last commit. Ask it to identify missing test coverage and write tests for happy paths, error cases, and edge cases.

2. Use the `security-auditor` subagent on the same changes. Ask it to check for auth gaps, authorization flaws, injection risks, secrets exposure, and unsafe data handling.

3. Use the `code-reviewer` subagent on the same changes. Ask it to review for correctness, architecture violations, FastAPI/Next.js best practices, and maintainability.

4. Summarize all findings across the three agents grouped by severity: MUST FIX, SHOULD FIX, CONSIDER.

5. If any MUST FIX issues remain unresolved, stop and list them clearly. Do not proceed until they are addressed.
