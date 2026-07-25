---
description: Run a code review on the current changes, optionally against a ticket, spec, or issue for context
argument-hint: "[jira link | issue # | spec path | free-text requirements]"
---

Run a code review on the current changes using the `code-reviewer` subagent.

Context reference provided by the user: $ARGUMENTS

## 1. Resolve the context reference

A review without stated requirements can only find syntax problems — it cannot tell you whether the code does the right thing. Resolve intent **before** reviewing.

If `$ARGUMENTS` is non-empty, treat it as the source of truth for intended behaviour and resolve it by type:

| Input | How to fetch |
|---|---|
| Jira URL or key (`PROJ-123`, `https://<site>.atlassian.net/browse/PROJ-123`) | See "Fetching Jira" below |
| GitHub issue URL or `#123` | `gh issue view <n> --json title,body,labels,comments` |
| GitHub PR URL or number | `gh pr view <n> --json title,body,comments` |
| Local file path | Read it directly (e.g. `specs/<feature>/spec.md`, `docs/design-docs.md`) |
| Anything else | Treat as free-text requirements and use verbatim |

If `$ARGUMENTS` is empty, look for context in this order and state which you used:

1. A spec-kit spec for the current branch — check `specs/` for a directory matching the branch name, then read its `spec.md` and `tasks.md`
2. An issue or ticket key in the branch name or commit messages (`feat/PROJ-123-...`) — fetch it as above
3. An open PR for this branch — `gh pr view --json title,body`
4. Commit messages on the branch — weakest signal; say so

If you find nothing, say plainly: "No requirements source found — reviewing for defects and quality only, not for requirement satisfaction." Do not invent the intent.

### Fetching Jira

Jira Cloud is behind authentication, so `WebFetch` will hit a login wall and return the SPA shell rather than the ticket. Try in order:

1. If a Jira MCP server is connected, use its issue-read tool.
2. If `JIRA_BASE_URL`, `JIRA_EMAIL`, and `JIRA_API_TOKEN` are set in the environment:
   ```bash
   curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
     -H "Accept: application/json" \
     "$JIRA_BASE_URL/rest/api/3/issue/PROJ-123?fields=summary,description,status,issuetype,labels" \
     | jq '.fields'
   ```
   Never echo the token, and never write it into a file or PR body.
3. Otherwise **ask the user to paste the ticket summary and acceptance criteria.** Do not guess at requirements from the ticket key alone, and do not report a fetch failure as though there were no requirements.

Extract from whatever you fetch: the problem statement, the acceptance criteria, and any explicit non-goals or out-of-scope notes.

## 2. Determine the review scope

Prefer the full branch diff over a single commit — reviewing one commit misses interactions with the rest of the branch:

```bash
git log main..HEAD --oneline
git diff main...HEAD --stat
```

If the branch is `main` or has no commits ahead of it, fall back to uncommitted changes (`git diff HEAD`), then to the last commit.

Report the diff size alongside the scope. Flag changes over ~1000 changed lines as too large to review properly and recommend a split, unless the bulk is file deletions or mechanical refactoring.

## 3. Run the review

Use the `code-reviewer` subagent on the changed files.

**The subagent has no web access — it cannot open a URL.** Pass the resolved context down as text in its prompt: the problem statement, the acceptance criteria as an explicit list, the declared non-goals, and the ticket or spec identifier for attribution. A bare link in the prompt is useless to it.

Ask it to follow its own review process (intent → tests first → implementation → verify the verification) and to evaluate correctness, edge cases, security, performance, architecture, refactoring quality, dependency changes, FastAPI/Next.js best practices, test coverage, and production readiness.

## 4. Report

Open with the context you used — ticket or spec identifier, and its acceptance criteria — so the reader knows what the code was judged against.

Then include a **requirements traceability** table, one row per acceptance criterion:

| Criterion | Status | Evidence |
|---|---|---|
| <criterion from the ticket> | Met / Not met / Partially met / Untested | `file_path:line` or the test that covers it |

Mark a criterion **Untested** when the code appears to implement it but no test proves it. Flag anything in the diff that satisfies no criterion and was not asked for — unrequested scope is a finding, not a bonus.

Then report findings grouped by MUST FIX, SHOULD FIX, CONSIDER — ordered by leverage within each group, correctness and security first. Do not bury a structural problem under cosmetic nits.

Include the verification story: which of `pytest`, `npm test`, `npm run typecheck && mypy .`, `npm run lint && ruff check .` were actually run, and their results. State plainly anything that was not run.

End with an APPROVAL STATUS: APPROVED, APPROVED WITH MINOR ISSUES, or CHANGES REQUESTED, with a rationale. Approve when the change definitely improves overall code health — do not request changes over preferences. An unmet acceptance criterion is CHANGES REQUESTED regardless of code quality.
