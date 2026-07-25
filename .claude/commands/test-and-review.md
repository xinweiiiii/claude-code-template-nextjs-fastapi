---
description: Full quality gate on the current changes — write tests, audit security, then review code
argument-hint: "[jira link | issue # | spec path | free-text requirements]"
---

Run a full quality gate on the current changes: write tests, audit security, then review code.

Context reference provided by the user: $ARGUMENTS

0. Resolve the context reference before spawning any subagent, using the resolution order in `.claude/commands/review.md` (explicit argument → spec-kit spec for the branch → ticket key in branch/commits → open PR → commit messages). Extract the problem statement, acceptance criteria, and declared non-goals. None of the subagents have web access, so pass the resolved requirements down as **text** in each prompt — a bare link is useless to them. If a Jira or other authenticated URL cannot be fetched, ask for the criteria to be pasted rather than proceeding without them.

1. Use the `test-writer` subagent on the files changed in the last commit. Give it the acceptance criteria so tests are written against stated behaviour, not just against the implementation. Ask it to identify missing test coverage and write tests for happy paths, error cases, and edge cases.

2. Use the `security-auditor` subagent on the same changes. Ask it to check for auth gaps, authorization flaws, injection risks, secrets exposure, and unsafe data handling.

3. Use the `code-reviewer` subagent on the same changes, passing the resolved requirements text. Ask it to review for correctness, architecture violations, FastAPI/Next.js best practices, and maintainability, and to return a requirements traceability table.

4. Summarize all findings across the three agents grouped by severity: MUST FIX, SHOULD FIX, CONSIDER. Lead with the traceability table and the context identifier it was judged against.

5. If any MUST FIX issues remain unresolved, stop and list them clearly. Do not proceed until they are addressed.
