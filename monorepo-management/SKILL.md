---
name: monorepo-management
description: Monorepo management covering pnpm workspaces, Nx build system, changeset versioning, shared package configuration, dependency management, task orchestration, affected-only testing, workspace protocol references, and publishing packages from a monorepo.
---

# Monorepo Management

This skill should be used when managing monorepo projects with multiple packages. It covers workspace setup, task orchestration, versioning, dependency management, and CI optimization.

## When to Use This Skill

Use this skill when you need to:

- Set up a monorepo with pnpm workspaces
- Orchestrate builds across packages with Nx
- Manage versioning with changesets
- Configure shared TypeScript and ESLint configs
- Optimize CI with affected-only testing

## pnpm Workspace Setup

```yaml
# pnpm-workspace.yaml
packages:
  - "apps/*"
  - "packages/*"
  - "tools/*"
```

```json
// package.json (root)
{
  "name": "my-monorepo",
  "private": true,
  "scripts": {
    "build": "pnpm -r run build",
    "test": "pnpm -r run test",
    "lint": "pnpm -r run lint",
    "dev": "pnpm --filter @repo/web dev"
  }
}
```

## Package Structure

```
monorepo/
├── apps/
│   ├── web/            # Next.js frontend
│   └── api/            # Express backend
├── packages/
│   ├── ui/             # Shared component library
│   ├── shared/         # Shared utilities
│   └── config/         # Shared configs (tsconfig, eslint)
├── pnpm-workspace.yaml
└── package.json
```

## Workspace References

```json
// apps/web/package.json
{
  "name": "@repo/web",
  "dependencies": {
    "@repo/ui": "workspace:*",
    "@repo/shared": "workspace:*"
  }
}
```

```json
// packages/ui/package.json
{
  "name": "@repo/ui",
  "version": "0.1.0",
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "exports": {
    ".": "./src/index.ts",
    "./button": "./src/button.tsx"
  }
}
```

## Shared TypeScript Config

```json
// packages/config/tsconfig.base.json
{
  "compilerOptions": {
    "strict": true,
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "isolatedModules": true
  }
}

// apps/web/tsconfig.json — extends shared config
// { "extends": "@repo/config/tsconfig.base.json" }
```

## Nx Task Orchestration

```json
// nx.json
{
  "targetDefaults": {
    "build": {
      "dependsOn": ["^build"],
      "cache": true
    },
    "test": { "cache": true },
    "lint": { "cache": true }
  },
  "affected": { "defaultBase": "main" }
}
```

```bash
# Run only affected tasks
npx nx affected -t build
npx nx affected -t test

# Visualize dependency graph
npx nx graph
```

## Changeset Versioning

```bash
npx changeset init     # Initialize
npx changeset          # Create changeset (interactive)
npx changeset version  # Bump versions
npx changeset publish  # Publish to npm
```

```json
// .changeset/config.json
{
  "changelog": "@changesets/cli/changelog",
  "commit": false,
  "access": "restricted",
  "baseBranch": "main",
  "linked": [["@repo/ui", "@repo/shared"]]
}
```

## CI with Affected Testing

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - run: npx nx affected -t lint test build --base=origin/main
```

## Common Commands

```
COMMAND                              PURPOSE
───────────────────────────────────────────────
pnpm --filter @repo/web add lodash   Add dep to specific package
pnpm -r run build                    Build all packages
pnpm --filter @repo/web dev          Dev single app
pnpm --filter @repo/ui... build      Build package and its deps
nx affected -t test                  Test only changed packages
```

## Additional Resources

- pnpm workspaces: https://pnpm.io/workspaces
- Nx: https://nx.dev/
- Changesets: https://github.com/changesets/changesets
