---
name: docker-publish
displayName: Docker Build & Publish
description: Build Docker images for the Next.js frontend and FastAPI backend, run them with docker-compose, and push to AWS ECR or Docker Hub. Use when containerizing or deploying the full-stack app.
version: 1.0.0
---

# Docker Build & Publish

Build production images for the frontend and backend, validate them locally with docker-compose, then push to a registry.

---

## Dockerfiles

### Frontend — `frontend/Dockerfile`

```dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
ENV PORT=3000
CMD ["node", "server.js"]
```

> Requires `output: "standalone"` in `next.config.ts`:
> ```ts
> const nextConfig = { output: "standalone" };
> export default nextConfig;
> ```

### Backend — `backend/Dockerfile`

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

FROM python:3.12-slim AS runner
WORKDIR /app
RUN useradd -r -u 1001 appuser
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
USER appuser
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

---

## docker-compose.yml (full stack)

```yaml
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      backend:
        condition: service_healthy

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 5s
      retries: 3

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
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### Run locally

```bash
# Build and start all services
docker compose up --build

# Run in background
docker compose up --build -d

# Tail logs
docker compose logs -f frontend backend

# Tear down
docker compose down
```

---

## Push to AWS ECR

### One-time setup

```bash
# Create repositories (run once per environment)
aws ecr create-repository --repository-name myapp/frontend --region ap-southeast-1
aws ecr create-repository --repository-name myapp/backend  --region ap-southeast-1
```

### Build and push script

Set these variables first:

```bash
export AWS_ACCOUNT_ID=123456789012
export AWS_REGION=ap-southeast-1
export IMAGE_TAG=$(git rev-parse --short HEAD)   # e.g. a1b2c3d
```

```bash
# Authenticate Docker to ECR
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin \
  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build
docker build -t myapp/frontend ./frontend
docker build -t myapp/backend  ./backend

# Tag
docker tag myapp/frontend $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/myapp/frontend:$IMAGE_TAG
docker tag myapp/backend  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/myapp/backend:$IMAGE_TAG

# Also tag :latest
docker tag myapp/frontend $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/myapp/frontend:latest
docker tag myapp/backend  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/myapp/backend:latest

# Push
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/myapp/frontend:$IMAGE_TAG
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/myapp/frontend:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/myapp/backend:$IMAGE_TAG
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/myapp/backend:latest
```

---

## Push to Docker Hub

### One-time setup

```bash
docker login   # prompts for Docker Hub username and password/token
```

### Build and push script

```bash
export DOCKER_HUB_USERNAME=myusername
export IMAGE_TAG=$(git rev-parse --short HEAD)

# Build
docker build -t $DOCKER_HUB_USERNAME/myapp-frontend ./frontend
docker build -t $DOCKER_HUB_USERNAME/myapp-backend  ./backend

# Tag
docker tag $DOCKER_HUB_USERNAME/myapp-frontend $DOCKER_HUB_USERNAME/myapp-frontend:$IMAGE_TAG
docker tag $DOCKER_HUB_USERNAME/myapp-backend  $DOCKER_HUB_USERNAME/myapp-backend:$IMAGE_TAG

# Push
docker push $DOCKER_HUB_USERNAME/myapp-frontend:$IMAGE_TAG
docker push $DOCKER_HUB_USERNAME/myapp-frontend:latest
docker push $DOCKER_HUB_USERNAME/myapp-backend:$IMAGE_TAG
docker push $DOCKER_HUB_USERNAME/myapp-backend:latest
```

---

## GitHub Actions — build and push on merge to main

```yaml
# .github/workflows/docker-publish.yml
name: Docker Build & Publish

on:
  push:
    branches: [main]

env:
  AWS_REGION: ap-southeast-1
  ECR_FRONTEND: myapp/frontend
  ECR_BACKEND: myapp/backend

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      id-token: write   # required for OIDC
      contents: read

    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/github-actions-ecr
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build, tag, and push frontend
        env:
          REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $REGISTRY/$ECR_FRONTEND:$IMAGE_TAG ./frontend
          docker tag  $REGISTRY/$ECR_FRONTEND:$IMAGE_TAG $REGISTRY/$ECR_FRONTEND:latest
          docker push $REGISTRY/$ECR_FRONTEND:$IMAGE_TAG
          docker push $REGISTRY/$ECR_FRONTEND:latest

      - name: Build, tag, and push backend
        env:
          REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $REGISTRY/$ECR_BACKEND:$IMAGE_TAG ./backend
          docker tag  $REGISTRY/$ECR_BACKEND:$IMAGE_TAG $REGISTRY/$ECR_BACKEND:latest
          docker push $REGISTRY/$ECR_BACKEND:$IMAGE_TAG
          docker push $REGISTRY/$ECR_BACKEND:latest
```

> Use OIDC (keyless auth) instead of long-lived `AWS_ACCESS_KEY_ID` secrets. Set up the IAM role with the GitHub OIDC trust policy and attach `AmazonEC2ContainerRegistryPowerUser`.

---

## Checklist

- [ ] `frontend/Dockerfile` exists with multi-stage build
- [ ] `backend/Dockerfile` exists with multi-stage build
- [ ] `next.config.ts` has `output: "standalone"`
- [ ] `docker compose up --build` starts all 4 services cleanly
- [ ] Backend health check passes (`/health` returns 200)
- [ ] ECR repositories created (or Docker Hub repo exists)
- [ ] Images tagged with git SHA and `latest`
- [ ] No secrets baked into images — use env vars or secrets manager
- [ ] `.dockerignore` excludes `node_modules`, `.next`, `__pycache__`, `.venv`, `.env`
