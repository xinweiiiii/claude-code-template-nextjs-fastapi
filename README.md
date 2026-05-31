# Claude Code Setup — Next.js + FastAPI Template

A Claude Code configuration template for full-stack projects using Next.js and FastAPI. Drop this into your project and Claude gets safety rails, domain skills, quality-gate commands, and structured PR workflows out of the box.

---

## How it works

Claude Code loads three layers of configuration automatically at the start of every session:

1. **`CLAUDE.md`** — tells Claude your stack, dev commands, coding standards, and git workflow. Fill this in for your project.
2. **`.claude/agents/`** — specialised sub-agents Claude can spawn for focused tasks (code review, security audit, test writing, PR creation).
3. **`.claude/skills/`** — domain knowledge Claude loads on demand to follow project-specific patterns (FastAPI, Next.js App Router, Pydantic, Tailwind, PostgreSQL, Redis, Docker).

Hooks in `.claude/settings.json` run automatically on every tool call — blocking dangerous commands, linting and formatting files on save, and logging sessions.

---

## Slash commands

Run these from any Claude Code session:

| Command | What it does |
|---|---|
| `/project-setup` | Scaffold a new Next.js 15 + Tailwind frontend and FastAPI backend from scratch |
| `/open-pr` | Write a structured PR description and open a pull request |
| `/review` | Run a code review on the current changes |
| `/security-audit` | Audit the current changes for auth gaps, injection risks, and secrets exposure |
| `/write-tests` | Write tests covering happy paths, error cases, and edge cases |
| `/test-and-review` | Full quality gate — tests + security audit + code review in sequence |

---

## Agents

Sub-agents in `.claude/agents/` are spawned automatically by the commands above, or you can invoke them directly:

| Agent | Purpose |
|---|---|
| `code-reviewer` | Reviews for correctness, architecture, FastAPI/Next.js best practices, and production readiness |
| `security-auditor` | Checks auth, authorisation, injection vectors, secrets exposure, and unsafe data handling |
| `test-writer` | Writes pytest and Playwright tests with explicit assertions and realistic test data |
| `pr-writer` | Produces four-section PR descriptions: Problem, Solution, Deployment, Testing |

---

## Skills

Skills in `.claude/skills/` are reference knowledge Claude uses when working in each domain:

| Skill | When it applies |
|---|---|
| `fastapi-architecture` | REST response conventions, status codes, error schemas |
| `pydantic-patterns` | Pydantic v2 models, validators, serialization, settings |
| `rest-response-standard` | Pagination, filtering, sorting, response envelope |
| `postgres-patterns` | Query optimisation, indexing, schema design |
| `redis` | Data structure selection, key naming conventions |
| `python-testing` | pytest patterns, fixtures, mocking, parametrization |
| `deployment-patterns` | CI/CD, Docker, health checks, rollback strategies |
| `docker-publish` | Build and push frontend/backend images to ECR or Docker Hub |
| `project-setup` | Full scaffold: Next.js 15 + FastAPI + PostgreSQL + Redis + Docker Compose |
| `nextjs-app-router-fundamental` | Server Actions, Route Handlers, Suspense streaming, error boundaries |
| `nextjs-advanced-routing` | Parallel Routes, Intercepting Routes, Server Component architecture |
| `nextjs-anti-patterns` | Common App Router mistakes to avoid |
| `nextjs-client-cookie-pattern` | Client component → server action cookie pattern |
| `tailwind-css` | Tailwind v4 utility patterns, dark mode, responsive design |

---

## Hooks

Hooks in `.claude/settings.json` run automatically — no manual invocation needed:

| Hook | Trigger | What it does |
|---|---|---|
| `lint-and-format` | After every file write or edit | Runs ESLint + Prettier for `.ts`/`.tsx`, ruff for `.py` |
| `block_dangerous.py` | Before every bash command | Blocks destructive operations (force push, `rm -rf /`, `DROP TABLE`, curl-to-shell, etc.) |
| `session_summary.py` | On session stop | Appends session metadata to `.claude/session-logs/YYYY-MM-DD.log` |

---

## Getting started

1. Clone this repo into your project root
2. Fill in `CLAUDE.md` with your stack, commands, and conventions
3. Fill in `docs/architecture.md` and `docs/design-docs.md` with system context
4. Start a Claude Code session — configuration loads automatically
