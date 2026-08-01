---
description: Self review the current changes, then open the PR once the punch list is clear
argument-hint: "[paths to review]"
---

Gate my own changes before they become a PR: self review first, fix what must be fixed, then open the PR.

User input: $ARGUMENTS

1. Run the self review flow in `.claude/commands/self-review.md` in **one-shot mode** — this is a gate, not a teaching exercise, so run all five stages via the `self-reviewer` subagent and return the punch list in one pass.

2. Present the punch list grouped as FIX NOW / FIX BEFORE MERGE / CONSIDER.

3. **If there are FIX NOW items, stop.** List them and ask whether I want them applied. Do not open a PR over a FIX NOW finding, and do not apply fixes without my go-ahead.

4. If FIX NOW is empty (or I've confirmed the fixes are applied and the checks pass again), verify the Git workflow preconditions before proceeding:
   - Not on `main` — if I am, create a `feat|fix|chore|refactor|docs|test/<description>` branch from the latest `main` first
   - WIP commits squashed
   - Branch rebased on `main`

5. Then hand off to `.claude/commands/open-pr.md` to write and open the PR.

Do not force-push, and do not create commits I did not ask for.
