# Claude Code Setup — Next.js + FastAPI Template

A Claude Code configuration template for full-stack projects using Next.js and FastAPI.

## What's included

- `CLAUDE.md` — project instructions for Claude: stack, dev commands, coding standards, and git workflow
- `.claude/agents/` — custom sub-agents (code reviewer, security auditor, test writer)
- `.claude/skills/` — reusable skill prompts (FastAPI architecture, Pydantic patterns, REST standards, PostgreSQL, Redis, deployment, Python testing)
- `.claude/settings.json` — Claude Code settings
- `docs/` — architecture and design doc templates

## How to use

1. Clone this repo into your project
2. Fill in `CLAUDE.md` with your project's stack, commands, and conventions
3. Fill in `docs/architecture.md` and `docs/design-docs.md` with your system context
4. Start a Claude Code session — Claude will pick up the instructions automatically
