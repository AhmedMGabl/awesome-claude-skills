---
name: turborepo-pipelines
description: Turborepo monorepo build orchestration covering task pipelines, remote caching, workspace dependencies, turbo.json configuration, environment variables, pruned Docker builds, GitHub Actions integration, and migration from Lerna or Nx.
---

# Turborepo Pipelines

This skill should be used when configuring Turborepo for monorepo build orchestration. It covers pipelines, remote caching, workspace management, and CI optimization.

## When to Use This Skill

Use this skill when you need to:

- Configure Turborepo task pipelines
- Set up remote caching for faster builds
- Manage workspace dependencies
- Optimize CI build times
- Build Docker images from monorepo apps

## turbo.json Configuration

```json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "globalEnv": ["NODE_ENV"],
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "inputs": ["$TURBO_DEFAULT$", ".env*"],
      "outputs": [".next/**", "dist/**"],
      "env": ["DATABASE_URL", "NEXT_PUBLIC_*"]
    },
    "lint": {
      "dependsOn": ["^build"]
    },
    "test": {
      "dependsOn": ["^build"],
      "inputs": ["src/**", "test/**"],
      "outputs": ["coverage/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "typecheck": {
      "dependsOn": ["^build"]
    }
  }
}
```

## Workspace Structure

```
monorepo/
├── turbo.json
├── package.json             # Root — workspaces config
├── apps/
│   ├── web/                 # Next.js app
│   │   └── package.json     # depends on @repo/ui, @repo/utils
│   └── api/                 # Express API
│       └── package.json     # depends on @repo/db, @repo/utils
├── packages/
│   ├── ui/                  # Shared React components
│   │   └── package.json     # @repo/ui
│   ├── db/                  # Prisma client
│   │   └── package.json     # @repo/db
│   ├── utils/               # Shared utilities
│   │   └── package.json     # @repo/utils
│   └── tsconfig/            # Shared TypeScript configs
│       └── package.json     # @repo/tsconfig
```

## Root package.json

```json
{
  "name": "monorepo",
  "private": true,
  "workspaces": ["apps/*", "packages/*"],
  "scripts": {
    "build": "turbo run build",
    "dev": "turbo run dev",
    "lint": "turbo run lint",
    "test": "turbo run test",
    "typecheck": "turbo run typecheck"
  },
  "devDependencies": {
    "turbo": "^2.0.0"
  }
}
```

## Remote Caching

```bash
# Login to Vercel (free remote cache)
npx turbo login

# Link to Vercel team
npx turbo link

# Or use custom remote cache
# Set TURBO_TOKEN and TURBO_TEAM environment variables
```

## Pruned Docker Build

```dockerfile
FROM node:20-alpine AS base
RUN corepack enable

# Prune workspace for this app only
FROM base AS pruner
WORKDIR /app
COPY . .
RUN npx turbo prune --scope=@repo/web --docker

# Install dependencies
FROM base AS installer
WORKDIR /app
COPY --from=pruner /app/out/json/ .
RUN pnpm install --frozen-lockfile

# Build
COPY --from=pruner /app/out/full/ .
RUN pnpm turbo build --filter=@repo/web

# Production
FROM base AS runner
WORKDIR /app
COPY --from=installer /app/apps/web/.next/standalone ./
CMD ["node", "apps/web/server.js"]
```

## GitHub Actions CI

```yaml
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: "pnpm" }
      - run: pnpm install --frozen-lockfile
      - run: pnpm turbo build lint test
        env:
          TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
          TURBO_TEAM: ${{ vars.TURBO_TEAM }}
```

## CLI Commands

```bash
turbo run build                       # Build all
turbo run build --filter=@repo/web    # Build one app
turbo run build --filter=./apps/*     # Build all apps
turbo run dev --filter=@repo/web...   # Dev with deps
turbo run build --dry                 # Preview task graph
turbo run build --graph               # Visualize graph
```

## Additional Resources

- Turborepo docs: https://turbo.build/repo/docs
- Task pipelines: https://turbo.build/repo/docs/crafting-your-repository/configuring-tasks
- Remote caching: https://turbo.build/repo/docs/core-concepts/remote-caching
