---
description: Blunt pre-PR self review of your own changes, stage by stage, before you open a PR
argument-hint: "[paths to review] [full — skip the gates and run it all at once]"
---

Review my own changes as a chief programmer and chief architect would, **before** I open a PR. Be blunt — the point is to catch problems before a reviewer does.

User input: $ARGUMENTS

## 1. Determine what to review

If `$ARGUMENTS` names files or paths, review exactly those. Otherwise pick the first that is non-empty:

```bash
git status --short                # uncommitted work — the default target
git diff main...HEAD --stat       # branch commits, if ahead of main
```

Prefer **uncommitted changes** — this is a pre-PR check, so the work in progress is the point. If the working tree is clean, fall back to the branch diff against `main`, and say which you used.

If `$ARGUMENTS` contains the word `full`, run in one-shot mode (see §3). Otherwise run staged (§2).

## 2. Staged mode (default)

The value of this review is that you get to steer it between stages — correcting a wrong assumption at Stage 1 saves three stages of misdirected findings.

Run **Stage 1 (Scope)** yourself, without a subagent. It is cheap and you need the context anyway. Present:

- What changed and why, inferred from the diff
- The split: production code / test code / config & infra / docs, with the diff size
- Branch hygiene: not on `main`, branch name matches `feat|fix|chore|refactor|docs|test/<description>`, WIP commits that need squashing

Then **stop and wait** for me to confirm or correct the inferred intent before going further.

For **Stages 2, 3, and 4**, use the `self-reviewer` subagent. Spawn it once with `run_in_background: false` for Stage 2, passing down:

- The confirmed intent from Stage 1 (the subagent cannot see our conversation)
- The exact file list and the diff scope it should review
- Which single stage to run, and an instruction to run *only* that stage and stop

Then continue the **same agent** for Stage 3 and Stage 4 via `SendMessage` using its ID — a fresh `Agent` call would start cold and re-derive everything it already established.

After each stage: present its findings verbatim, then **stop and wait** for my confirmation before requesting the next one. Do not batch stages together, and do not summarize away a finding — if the subagent quoted three lines of offending code, show those three lines.

Finally, run **Stage 5 (Verdict)** by asking the same agent to consolidate everything into the punch list.

## 3. One-shot mode (`full`)

Spawn the `self-reviewer` subagent once and ask it to run all five stages and return them as separate sections in a single report. No gates. Use this when I say `full`, or when the diff is small enough that stopping four times is pure overhead.

## 4. Report

Give me the punch list, ordered by leverage inside each bucket — correctness and security first:

- **FIX NOW** — will get rejected in review, or will cause a bug, security hole, or data loss
- **FIX BEFORE MERGE** — real issues that won't block a first review round but must not ship
- **CONSIDER** — suggestions, not requirements

Every item: `file_path:line_number`, the offending line(s) quoted, what's wrong, what to do instead. Say which of `pytest`, `npm test`, `npm run typecheck && mypy .`, `npm run lint && ruff check .` were actually run and what they returned — and state plainly anything that was not run.

If there is one structural problem and ten nits, lead with the structural problem.

## 5. Afterwards

Ask whether I want the FIX NOW items applied. **Do not apply them unprompted** — this is a review, not a refactor, and I may disagree with a finding.

Do not commit anything. Per this project's Git workflow, commits happen only when I explicitly ask.
