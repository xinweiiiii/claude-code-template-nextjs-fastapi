Run a code review on the current changes using the `code-reviewer` subagent.

1. Identify the files changed in the last commit.

2. Use the `code-reviewer` subagent on those files. Ask it to evaluate correctness, edge cases, security, performance, architecture, FastAPI/Next.js best practices, test coverage, and production readiness.

3. Report findings grouped by: MUST FIX, SHOULD FIX, CONSIDER.

4. End with an APPROVAL STATUS: APPROVED, APPROVED WITH MINOR ISSUES, or CHANGES REQUESTED, with a rationale.
