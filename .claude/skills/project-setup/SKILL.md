---
name: project-setup
displayName: Project Setup
description: Scaffold a new Next.js 15 + Tailwind CSS frontend and FastAPI backend from scratch. Use when initializing a new full-stack project.
version: 1.0.0
---

# Project Setup: Next.js + FastAPI

Scaffold a full-stack project with a Next.js 15 frontend (Tailwind CSS) and a FastAPI backend.

## Step 1 — Scaffold the Next.js frontend

Run the official `create-next-app` CLI with the recommended flags for this stack:

```bash
npx create-next-app@latest frontend \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --src-dir \
  --import-alias "@/*" \
  --no-turbopack
```

This produces:
- App Router under `frontend/src/app/`
- Tailwind CSS v4 pre-configured
- TypeScript and ESLint configured
- Path alias `@/*` → `src/*`

After scaffolding, verify Tailwind is wired into `src/app/globals.css`:

```css
@import "tailwindcss";
```

## Step 2 — Scaffold the FastAPI backend

Create the backend directory and a Python virtual environment:

```bash
mkdir backend && cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

Install core dependencies:

```bash
pip install fastapi uvicorn[standard] pydantic python-dotenv
pip install sqlalchemy alembic asyncpg
pip install redis
pip install pytest httpx pytest-asyncio
```

Freeze dependencies:

```bash
pip freeze > requirements.txt
```

Create the project layout:

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       └── __init__.py
│   ├── models/
│   │   └── __init__.py
│   ├── schemas/
│   │   └── __init__.py
│   └── services/
│       └── __init__.py
├── tests/
│   └── __init__.py
├── alembic/
├── alembic.ini
├── requirements.txt
└── .env
```

Minimal `app/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
```

Minimal `app/core/config.py`:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "app"
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"

settings = Settings()
```

Minimal `.env`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/app
REDIS_URL=redis://localhost:6379
```

## Step 3 — Docker Compose for local services

Create `docker-compose.yml` at the project root:

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: app
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

Start services:

```bash
docker compose up -d
```

## Step 4 — Verify everything runs

```bash
# Frontend
cd frontend && npm run dev       # http://localhost:3000

# Backend
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload    # http://localhost:8000
```

Check:
- `http://localhost:3000` — Next.js default page
- `http://localhost:8000/health` → `{"status": "ok"}`
- `http://localhost:8000/docs` — FastAPI Swagger UI

## Step 5 — Initialise Alembic

```bash
cd backend
alembic init alembic
```

Update `alembic.ini`:

```ini
sqlalchemy.url = postgresql+asyncpg://postgres:postgres@localhost:5432/app
```

Update `alembic/env.py` to import your `Base` metadata when models are ready.

---

## Checklist

- [ ] `frontend/` scaffolded with `create-next-app` (TypeScript, Tailwind, App Router)
- [ ] `backend/` with virtual env, FastAPI, and dependencies installed
- [ ] `requirements.txt` generated
- [ ] `docker-compose.yml` with PostgreSQL and Redis
- [ ] `.env` created (never committed)
- [ ] Health endpoint returns `{"status": "ok"}`
- [ ] Alembic initialised
- [ ] Both dev servers start without errors
