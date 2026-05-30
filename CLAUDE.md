---
1. Keep it concise (< 200 lines)
2. WHAT: Tell claude about your stack 
3. WHY: Give Claude the purpose behind decisions
4. HOW: How to work on the project

Refer to the sample below
---

# Project: [Name]

## Stack
- Frontend: Next.js 15, React 19, TypeScript 5.4
- Backend: FastAPI (Python 3.12+)
- Database: PostgreSQL
- Cache: Redis Cloud
- Testing: Jest, Supertest
- Infrastructure: Docker, GitHub Actions
- Code Quality: ESLint, Prettier

See @package.json for all dependencies.
See @docs/architecture.md for system design.
See @docs/design-docs.md for system context.

## How to work on this project
- Frontend dev: `npm run dev`
- Backend dev: `uvicorn app.main:app --reload`
- Run tests: `pytest && npm test`
- Run single backend test: `pytest tests/test_auth.py`
- Typecheck: `npm run typecheck && mypy .`
- Lint: `npm run lint && ruff check .`
- Format: `ruff format .`
- Run migrations: `alembic upgrade head`
- Create migration: `alembic revision --autogenerate -m "description"`
- Build frontend: `npm run build`
- Start local services: `docker compose up -d`


## Things to get right
- Validate all input with Pydantic; never trust raw request data
- Use separate schemas for create, update, read, and list views
- Keep routes thin; put business logic in services and persistence outside routes
- Return consistent errors and correct HTTP status codes
- Paginate, filter, sort, and search list endpoints where needed
- Enforce auth and ownership checks on every protected action
- Handle loading, empty, and error states on the frontend
- Disable duplicate submits and keep mutations idempotent where possible
- Invalidate or refresh cached data after CRUD mutations
- Use transactions for multi-step writes
- Add tests for success, validation, permission, and not-found cases

## Git Workflow
- Never commit directly to `main`
- Create a feature branch from the latest `main`
- Branch naming:
  - `feat/<description>`
  - `fix/<description>`
  - `chore/<description>`
  - `refactor/<description>`
  - `docs/<description>`
  - `test/<description>`
- Keep branches focused on a single feature, bug fix, or task
- Rebase regularly against `main` to minimize merge conflicts
- Prefer a clean, linear commit history
- Squash WIP commits before opening a PR
- Do not create commits unless explicitly requested
- Do not force-push without approval
- Show proposed file changes before performing large refactors
- Prefer multiple small commits over one large commit during development

