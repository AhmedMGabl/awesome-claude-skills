---
name: pnpm-workspaces
description: pnpm workspace management covering workspace protocol, shared dependencies, filtering commands, catalogs for version alignment, peer dependency handling, .npmrc configuration, publishing packages, and migration from npm or yarn.
---

# pnpm Workspaces

This skill should be used when managing monorepo dependencies with pnpm workspaces. It covers workspace setup, dependency management, filtering, catalogs, and publishing.

## When to Use This Skill

Use this skill when you need to:

- Set up a pnpm monorepo workspace
- Manage shared and per-package dependencies
- Run commands across specific workspaces
- Align dependency versions with catalogs
- Publish packages from a monorepo

## Workspace Configuration

```yaml
# pnpm-workspace.yaml
packages:
  - "apps/*"
  - "packages/*"
  - "tools/*"
```

```ini
# .npmrc
auto-install-peers=true
strict-peer-dependencies=false
shamefully-hoist=false
link-workspace-packages=true
```

## Workspace Protocol

```json
// packages/ui/package.json
{
  "name": "@repo/ui",
  "version": "1.0.0",
  "dependencies": {
    "@repo/utils": "workspace:*",
    "@repo/tsconfig": "workspace:^"
  }
}
```

```
workspace:*    → resolves to any version (most common)
workspace:^    → resolves to ^1.0.0 when published
workspace:~    → resolves to ~1.0.0 when published
```

## Catalogs (Version Alignment)

```yaml
# pnpm-workspace.yaml
packages:
  - "apps/*"
  - "packages/*"

catalog:
  react: ^19.0.0
  react-dom: ^19.0.0
  typescript: ^5.7.0
  zod: ^3.24.0

catalogs:
  testing:
    vitest: ^2.1.0
    "@testing-library/react": ^16.0.0
```

```json
// apps/web/package.json
{
  "dependencies": {
    "react": "catalog:",
    "react-dom": "catalog:",
    "zod": "catalog:"
  },
  "devDependencies": {
    "vitest": "catalog:testing"
  }
}
```

## Filtering Commands

```bash
# Run in specific workspace
pnpm --filter @repo/web dev
pnpm --filter @repo/web build

# Run in workspace and its dependencies
pnpm --filter @repo/web... build

# Run in all packages that depend on @repo/ui
pnpm --filter ...@repo/ui test

# Run in all apps
pnpm --filter "./apps/*" build

# Run in changed packages (since main)
pnpm --filter "...[origin/main]" test

# Add dependency to specific workspace
pnpm --filter @repo/web add react-router
pnpm --filter @repo/web add -D vitest

# Add shared dev dependency to root
pnpm add -Dw turbo typescript
```

## Root package.json

```json
{
  "name": "monorepo",
  "private": true,
  "scripts": {
    "build": "turbo run build",
    "dev": "turbo run dev",
    "lint": "turbo run lint",
    "test": "turbo run test",
    "clean": "pnpm -r exec rm -rf node_modules dist .next .turbo",
    "format": "prettier --write ."
  },
  "devDependencies": {
    "turbo": "^2.0.0",
    "prettier": "^3.0.0",
    "typescript": "^5.7.0"
  },
  "packageManager": "pnpm@9.15.0"
}
```

## CLI Commands

```bash
pnpm install                         # Install all workspaces
pnpm -r build                        # Run build in all packages
pnpm -r --parallel dev               # Run dev in all (parallel)
pnpm list -r --depth 0               # List all workspace deps
pnpm why react                       # Why is react installed
pnpm outdated -r                     # Check outdated across all
pnpm dedupe                          # Deduplicate dependencies
```

## Additional Resources

- pnpm workspaces: https://pnpm.io/workspaces
- pnpm catalogs: https://pnpm.io/catalogs
- pnpm filtering: https://pnpm.io/filtering
