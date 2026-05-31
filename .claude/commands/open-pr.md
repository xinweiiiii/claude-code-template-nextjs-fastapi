Open a pull request for the current branch. Follow these steps exactly:

## Step 1 — Understand the changes

Run:
```
git log main..HEAD --oneline
git diff main...HEAD
```

Read the changed files. Understand intent, not just mechanics.

## Step 2 — Write the PR description

Use this structure. Do NOT summarise what the code does — explain context and rationale.

### Problem
What is broken, missing, or limiting? The reviewer should understand the problem without reading any code. Include as much context as possible — link to issues or incidents if available.

### Solution
Why this approach over alternatives? What trade-offs were considered? What was ruled out and why? Do not describe code changes — explain why you made the decisions you did.

### Deployment
Dependencies that must go first, migration order, backwards compatibility, rollback notes. If none apply, state: "No deployment dependencies. Can be merged and deployed independently."

### Testing
Be specific. List unit tests added, integration/E2E coverage, load test results if relevant. For manual testing include screenshots or curl commands. Vague statements like "tested locally" are not acceptable.

## Step 3 — Open the PR

```bash
gh pr create \
  --title "<concise title under 70 characters>" \
  --base main \
  --body "$(cat <<'EOF'
## Problem
...

## Solution
...

## Deployment
...

## Testing
...

🤖 Generated with [Claude Code](https://claude.ai/code)
EOF
)"
```

Return the PR URL when done.
