---
name: monorepo-management
description: This skill should be used when setting up, configuring, or managing TypeScript/JavaScript monorepos using Turborepo, Nx, or pnpm workspaces, including task pipelines, remote caching, shared packages, code generation, versioning with changesets, CI optimization, and shared configurations.
---

# Monorepo Management

Guide for building production-grade TypeScript/JavaScript monorepos. To use this skill, describe the monorepo tool (Turborepo, Nx, or pnpm workspaces), the workspace structure, and the problem to solve.

## When to Use This Skill

- Initialize a monorepo with Turborepo, Nx, or pnpm workspaces
- Architect shared packages and internal library patterns
- Configure task pipelines, remote caching, and build orchestration
- Run affected/changed-only commands in CI
- Manage versioning and changelogs with changesets
- Create shared configs for ESLint, TypeScript, and Prettier

---

## 1. Workspace Setup with pnpm

```yaml
# pnpm-workspace.yaml
packages:
  - "apps/*"
  - "packages/*"
```

```jsonc
// package.json (root)
{
  "private": true,
  "packageManager": "pnpm@9.15.0",
  "scripts": {
    "build": "turbo run build",
    "dev": "turbo run dev",
    "lint": "turbo run lint",
    "test": "turbo run test",
    "format": "prettier --write \"**/*.{ts,tsx,js,jsx,json,md}\"",
    "release": "turbo run build --filter='./packages/*' && changeset publish"
  },
  "devDependencies": {
    "@changesets/cli": "^2.27.0",
    "prettier": "^3.4.0",
    "turbo": "^2.3.0"
  }
}
```

### Directory Structure

```
my-monorepo/
├── apps/           # web/, api/, docs/ (deployable applications)
├── packages/       # ui/, utils/, db/, tsconfig/, eslint-config/, prettier-config/
├── turbo.json
├── pnpm-workspace.yaml
├── package.json
└── .changeset/config.json
```

---

## 2. Turborepo Configuration (Primary)

```jsonc
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "globalEnv": ["NODE_ENV"],
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**", "!.next/cache/**"],
      "env": ["NEXT_PUBLIC_API_URL"]
    },
    "dev": { "cache": false, "persistent": true },
    "lint": { "dependsOn": ["^build"] },
    "test": { "dependsOn": ["build"], "outputs": ["coverage/**"], "env": ["CI"] },
    "typecheck": { "dependsOn": ["^build"] },
    "clean": { "cache": false }
  }
}
```

**Key concepts:** `^build` in `dependsOn` means "build dependency packages first." `outputs` defines cached artifacts. `persistent: true` marks long-running dev servers. `env` lists variables affecting the task hash.

### Common Commands

```bash
turbo run build                          # All packages
turbo run dev --filter=web               # Single app dev server
turbo run test --filter='...[HEAD~1]'    # Changed packages + dependents
turbo run build --filter=web...          # Package + its dependencies
turbo run build --graph                  # Visualize task graph
```

---

## 3. Nx Configuration (Alternative)

```jsonc
// nx.json
{
  "targetDefaults": {
    "build": { "dependsOn": ["^build"], "outputs": ["{projectRoot}/dist"], "cache": true },
    "lint": { "cache": true },
    "test": { "cache": true, "outputs": ["{projectRoot}/coverage"] }
  },
  "defaultBase": "main",
  "namedInputs": {
    "default": ["{projectRoot}/**/*", "sharedGlobals"],
    "sharedGlobals": ["{workspaceRoot}/tsconfig.base.json"]
  }
}
// Commands: nx affected -t build | nx run web:build | nx graph | nx g @nx/js:library utils
```

---

## 4. Internal Packages Pattern

```jsonc
// packages/ui/package.json
{
  "name": "@repo/ui",
  "version": "0.0.0",
  "private": true,
  "exports": {
    ".": { "types": "./src/index.ts", "default": "./dist/index.js" },
    "./button": { "types": "./src/button.ts", "default": "./dist/button.js" }
  },
  "scripts": {
    "build": "tsup src/index.ts --format esm,cjs --dts",
    "dev": "tsup src/index.ts --format esm,cjs --dts --watch"
  },
  "devDependencies": { "@repo/tsconfig": "workspace:*", "tsup": "^8.3.0", "typescript": "^5.7.0" }
}
```

Consume via `workspace:*` references in apps:

```jsonc
// apps/web/package.json  ->  { "dependencies": { "@repo/ui": "workspace:*" } }
```

```typescript
import { Button } from "@repo/ui";  // apps/web/src/page.tsx
```

---

## 5. Shared Configurations

### TypeScript

```jsonc
// packages/tsconfig/base.json
{
  "compilerOptions": {
    "strict": true, "esModuleInterop": true, "skipLibCheck": true,
    "moduleResolution": "bundler", "module": "ESNext", "target": "ES2022",
    "resolveJsonModule": true, "isolatedModules": true,
    "declaration": true, "declarationMap": true, "sourceMap": true
  },
  "exclude": ["node_modules", "dist"]
}
// packages/tsconfig/react.json  ->  extends base, adds "jsx": "react-jsx", "lib": ["ES2022","DOM","DOM.Iterable"]
// apps/web/tsconfig.json        ->  { "extends": "@repo/tsconfig/react.json", "include": ["src"] }
```

### ESLint (Flat Config)

```javascript
// packages/eslint-config/base.js
import js from "@eslint/js";
import tseslint from "typescript-eslint";
import prettierConfig from "eslint-config-prettier";

export default tseslint.config(
  js.configs.recommended, ...tseslint.configs.recommended, prettierConfig,
  { rules: { "@typescript-eslint/no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
             "@typescript-eslint/consistent-type-imports": "error" } },
  { ignores: ["dist/", "node_modules/", ".next/", "coverage/"] }
);
```

### Prettier

```jsonc
// packages/prettier-config/index.json
{ "semi": true, "singleQuote": false, "trailingComma": "all", "tabWidth": 2, "printWidth": 100 }
// Root package.json:  { "prettier": "@repo/prettier-config" }
```

---

## 6. Remote Caching

**Turborepo (Vercel):** Run `npx turbo login && npx turbo link` for interactive setup, or set `TURBO_TOKEN` + `TURBO_TEAM` env vars in CI. Add `"remoteCache": { "signature": true }` to turbo.json for signed artifacts.

**Self-hosted:** Set `TURBO_API`, `TURBO_TOKEN`, and `TURBO_TEAM` to point at a custom cache server.

**Nx Cloud:** Set `nxCloudAccessToken` in nx.json or export `NX_CLOUD_ACCESS_TOKEN` in CI.

---

## 7. Versioning with Changesets

```jsonc
// .changeset/config.json
{
  "changelog": "@changesets/cli/changelog",
  "commit": false,
  "linked": [["@repo/ui", "@repo/utils"]],
  "access": "restricted",
  "baseBranch": "main",
  "updateInternalDependencies": "patch",
  "ignore": ["web", "api", "docs"]
}
```

```bash
pnpm changeset              # Create a changeset (interactive)
pnpm changeset version      # Consume changesets, bump versions, update changelogs
pnpm changeset publish      # Publish to npm
```

### Automated Release PR

Use `changesets/action@v1` in GitHub Actions. On push to main, it either opens a "Version Packages" PR (if changesets exist) or publishes (if the PR was merged):

```yaml
# .github/workflows/release.yml
name: Release
on: { push: { branches: [main] } }
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - uses: changesets/action@v1
        with: { version: "pnpm changeset version", publish: "pnpm release" }
        env: { GITHUB_TOKEN: "${{ secrets.GITHUB_TOKEN }}", NPM_TOKEN: "${{ secrets.NPM_TOKEN }}" }
```

---

## 8. CI Optimization

### GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI
on:
  push: { branches: [main] }
  pull_request: { branches: [main] }
concurrency: { group: "${{ github.workflow }}-${{ github.ref }}", cancel-in-progress: true }
env:
  TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
  TURBO_TEAM: ${{ vars.TURBO_TEAM }}
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 2 }
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - run: turbo run build lint test --filter='...[HEAD~1]'
```

### Affected Filter Syntax

| Filter | Meaning |
|---|---|
| `--filter='...[HEAD~1]'` | Changed since last commit |
| `--filter='...[main]'` | Changed vs main branch |
| `--filter='...[origin/main]'` | Changed in current PR |
| `--filter='...@repo/ui'` | Package + all dependents |

### Docker Build with turbo prune

`turbo prune <app> --docker` creates a sparse monorepo with only the target and its dependencies. Use a multi-stage Dockerfile:

```dockerfile
FROM node:20-alpine AS base
RUN corepack enable && corepack prepare pnpm@9.15.0 --activate

FROM base AS pruner
WORKDIR /app
COPY . .
RUN npx turbo prune web --docker

FROM base AS installer
WORKDIR /app
COPY --from=pruner /app/out/json/ .
RUN pnpm install --frozen-lockfile
COPY --from=pruner /app/out/full/ .
RUN turbo run build --filter=web

FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=installer /app/apps/web/.next/standalone ./
COPY --from=installer /app/apps/web/.next/static ./apps/web/.next/static
EXPOSE 3000
CMD ["node", "apps/web/server.js"]
```

---

## 9. Code Generation

Define generators in `turbo/generators/config.ts` using Plop templates:

```typescript
// turbo/generators/config.ts
import type { PlopTypes } from "@turbo/gen";
export default function generator(plop: PlopTypes.NodePlopAPI): void {
  plop.setGenerator("package", {
    description: "Create a new internal package",
    prompts: [{ type: "input", name: "name", message: "Package name:" }],
    actions: [
      { type: "add", path: "packages/{{name}}/package.json",
        templateFile: "templates/package/package.json.hbs" },
      { type: "add", path: "packages/{{name}}/src/index.ts",
        template: 'export const {{name}} = () => "Hello from @repo/{{name}}";' },
    ],
  });
}
// Run: turbo gen package
```

---

## 10. Best Practices

**Package architecture:** Keep apps in `apps/` and libraries in `packages/`. Prefix internal packages with a scope (e.g., `@repo/`). Use `workspace:*` for internal dependency versions. Mark internal packages as `"private": true`.

**Task pipelines:** Always declare `dependsOn: ["^build"]` for build tasks. Cache everything except dev servers and clean tasks. List all environment variables affecting output in `env`. Declare `outputs` for every cacheable task.

**CI performance:** Enable remote caching in all CI environments. Use `--filter='...[base-ref]'` to run only affected tasks. Use `turbo prune` for Docker builds. Cache `node_modules` and the pnpm store between runs.

**Dependency management:** Pin `packageManager` in root `package.json`. Use `linked` in changeset config for packages that version together. Set `updateInternalDependencies` to keep internal versions in sync. Run `pnpm dedupe` periodically.
