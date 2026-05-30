Write tests for the current changes using the `test-writer` subagent.

1. Identify the files changed in the last commit.

2. Use the `test-writer` subagent on those files. Ask it to:
   - Identify all untested or undertested behavior
   - Write tests covering happy paths, error cases, validation, auth/authorization, and edge cases
   - Follow the project's testing conventions (pytest for FastAPI, Playwright/Vitest for Next.js)
   - Use realistic test data and explicit assertions

3. Report what tests were written and what coverage gaps remain.
