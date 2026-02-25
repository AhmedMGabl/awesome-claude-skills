---
name: docker-development
description: Docker development covering Dockerfile best practices, multi-stage builds, layer caching optimization, Docker Compose for development, volume mounts, networking, health checks, security hardening, debugging containers, and production image patterns.
---

# Docker Development

This skill should be used when building Docker images, writing Dockerfiles, or containerizing applications. It covers multi-stage builds, caching, security, debugging, and production patterns.

## When to Use This Skill

Use this skill when you need to:

- Write optimized Dockerfiles
- Set up Docker Compose for development
- Debug container issues
- Implement multi-stage builds
- Harden containers for production

## Multi-Stage Dockerfile (Node.js)

```dockerfile
# Stage 1: Dependencies
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts

# Stage 2: Build
FROM node:22-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Stage 3: Production
FROM node:22-alpine AS production
WORKDIR /app
ENV NODE_ENV=production

# Non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup
USER appuser

COPY --from=build --chown=appuser:appgroup /app/dist ./dist
COPY --from=deps --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=build --chown=appuser:appgroup /app/package.json ./

EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

CMD ["node", "dist/server.js"]
```

## Multi-Stage Dockerfile (Python)

```dockerfile
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

FROM base AS deps
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

FROM base AS production
WORKDIR /app

RUN groupadd -r appgroup && useradd -r -g appgroup appuser
USER appuser

COPY --from=deps /app/.venv /app/.venv
COPY . .

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Docker Compose for Development

```yaml
# docker-compose.yml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: deps  # Use deps stage for dev
    volumes:
      - .:/app
      - /app/node_modules  # Preserve container node_modules
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/myapp
      - REDIS_URL=redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    command: npm run dev

  db:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: myapp
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  pgdata:
```

## .dockerignore

```
node_modules
.git
.env*
dist
coverage
.next
*.md
.vscode
.idea
Dockerfile*
docker-compose*
```

## Layer Caching Tips

```dockerfile
# BAD — busts cache on any file change
COPY . .
RUN npm ci && npm run build

# GOOD — only re-install when deps change
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# GOOD — use cache mounts for package managers
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# GOOD — use bind mounts to avoid COPY
RUN --mount=type=bind,source=package.json,target=package.json \
    --mount=type=bind,source=package-lock.json,target=package-lock.json \
    --mount=type=cache,target=/root/.npm \
    npm ci
```

## Debugging Containers

```bash
# Shell into a running container
docker compose exec app sh

# View logs
docker compose logs -f app

# Inspect a container
docker inspect <container_id>

# Check resource usage
docker stats

# Build with no cache (force rebuild)
docker compose build --no-cache app

# Run one-off command
docker compose run --rm app npm test
```

## Security Checklist

```
DOCKERFILE SECURITY:
  [ ] Use specific image tags, not :latest
  [ ] Run as non-root user (USER directive)
  [ ] Use --no-cache-dir for pip install
  [ ] Don't store secrets in image layers (use build secrets)
  [ ] Scan images: docker scout cves <image>
  [ ] Use HEALTHCHECK for orchestrator awareness
  [ ] Minimize installed packages (use -slim or -alpine)
  [ ] Set read-only root filesystem where possible

BUILD SECRETS (don't bake into layers):
  docker build --secret id=npmrc,src=.npmrc .
  # In Dockerfile:
  RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci
```

## Additional Resources

- Dockerfile reference: https://docs.docker.com/reference/dockerfile/
- Docker Compose: https://docs.docker.com/compose/
- Best practices: https://docs.docker.com/build/building/best-practices/
- Docker Scout: https://docs.docker.com/scout/
