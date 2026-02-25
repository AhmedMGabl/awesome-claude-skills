---
name: turborepo
description: Turborepo monorepo patterns covering turbo.json pipeline configuration, caching, remote cache, task dependencies, filtering, workspace packages, pruning, and CI/CD optimization for large-scale TypeScript projects.
---

# Turborepo

This skill should be used when managing monorepos with Turborepo. It covers pipeline configuration, caching, workspace management, task filtering, and CI/CD optimization.

## When to Use This Skill

Use this skill when you need to:

- Set up and manage a monorepo with Turborepo
- Configure task pipelines with dependencies
- Optimize builds with local and remote caching
- Filter and run tasks for specific packages
- Set up CI/CD for monorepo workflows

## Project Structure

```
my-monorepo/
├── turbo.json
├── package.json
├── apps/
│   ├── web/
│   │   ├── package.json
│   │   └── src/
│   └── api/
│       ├── package.json
│       └── src/
└── packages/
    ├── ui/
    │   ├── package.json
    │   └── src/
    ├── config-eslint/
    │   └── package.json
    ├── config-typescript/
    │   └── tsconfig.json
    └── shared/
        ├── package.json
        └── src/
```

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
      "outputs": ["dist/**", ".next/**", "!.next/cache/**"],
      "env": ["DATABASE_URL", "API_KEY"]
    },
    "lint": {
      "dependsOn": ["^build"]
    },
    "test": {
      "dependsOn": ["build"],
      "inputs": ["src/**", "test/**"],
      "outputs": ["coverage/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "type-check": {
      "dependsOn": ["^build"]
    },
    "db:generate": {
      "cache": false
    }
  }
}
```

## Root package.json

```json
{
  "name": "my-monorepo",
  "private": true,
  "workspaces": ["apps/*", "packages/*"],
  "scripts": {
    "build": "turbo build",
    "dev": "turbo dev",
    "lint": "turbo lint",
    "test": "turbo test",
    "type-check": "turbo type-check",
    "clean": "turbo clean && rm -rf node_modules"
  },
  "devDependencies": {
    "turbo": "^2.0.0"
  }
}
```

## Package Configuration

```json
// packages/ui/package.json
{
  "name": "@repo/ui",
  "version": "0.0.0",
  "private": true,
  "exports": {
    "./button": "./src/button.tsx",
    "./card": "./src/card.tsx",
    "./styles.css": "./src/styles.css"
  },
  "scripts": {
    "build": "tsup src/index.ts --format esm,cjs --dts",
    "lint": "eslint src/",
    "type-check": "tsc --noEmit"
  }
}

// apps/web/package.json
{
  "name": "web",
  "version": "0.0.0",
  "private": true,
  "dependencies": {
    "@repo/ui": "workspace:*",
    "@repo/shared": "workspace:*"
  }
}
```

## Filtering Tasks

```bash
# Run for specific package
turbo build --filter=web

# Run for package and its dependencies
turbo build --filter=web...

# Run for all dependents of a package
turbo build --filter=...@repo/ui

# Run for changed packages since main
turbo build --filter=[main]

# Combine filters
turbo build --filter=web --filter=api

# Exclude packages
turbo build --filter=!@repo/config-*

# Run only for packages in apps/
turbo build --filter=./apps/*
```

## Remote Caching

```bash
# Login to Vercel Remote Cache
npx turbo login

# Link to remote cache
npx turbo link

# Or use environment variables
TURBO_TOKEN=<token>
TURBO_TEAM=<team>

# Self-hosted remote cache
TURBO_API=https://my-cache-server.com
TURBO_TOKEN=<token>
TURBO_TEAM=my-team
```

## Per-Package turbo.json

```json
// apps/web/turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "extends": ["//"],
  "tasks": {
    "build": {
      "outputs": [".next/**", "!.next/cache/**"],
      "env": ["NEXT_PUBLIC_API_URL"]
    },
    "dev": {
      "env": ["NEXT_PUBLIC_API_URL"]
    }
  }
}
```

## CI/CD Integration

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci

      - run: npx turbo build lint test --filter=[HEAD^1]
        env:
          TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
          TURBO_TEAM: ${{ vars.TURBO_TEAM }}
```

## Pruning for Docker

```dockerfile
FROM node:20-alpine AS base

# Prune workspace for specific app
FROM base AS pruner
WORKDIR /app
COPY . .
RUN npx turbo prune web --docker

# Install dependencies
FROM base AS installer
WORKDIR /app
COPY --from=pruner /app/out/json/ .
RUN npm ci

# Build
COPY --from=pruner /app/out/full/ .
RUN npx turbo build --filter=web

# Run
FROM base AS runner
WORKDIR /app
COPY --from=installer /app/apps/web/.next/standalone ./
CMD ["node", "apps/web/server.js"]
```

## Additional Resources

- Turborepo: https://turbo.build/repo
- Task configuration: https://turbo.build/repo/docs/crafting-your-repository/configuring-tasks
- Filtering: https://turbo.build/repo/docs/crafting-your-repository/running-tasks
