---
name: turborepo-monorepo
description: Turborepo monorepo management covering workspace setup, task pipelines, remote caching, shared packages, internal packages pattern, code generation, environment variables, CI optimization, and incremental builds for large TypeScript projects.
---

# Turborepo Monorepo

This skill should be used when setting up or managing monorepos with Turborepo. It covers workspace configuration, task pipelines, remote caching, shared packages, and CI optimization.

## When to Use This Skill

Use this skill when you need to:

- Set up a Turborepo monorepo
- Configure task pipelines and caching
- Share packages between applications
- Optimize CI builds with remote caching
- Manage workspace dependencies

## Project Structure

```
my-monorepo/
├── turbo.json
├── package.json
├── apps/
│   ├── web/          # Next.js app
│   │   └── package.json
│   ├── api/          # Express/Fastify server
│   │   └── package.json
│   └── docs/         # Documentation site
│       └── package.json
├── packages/
│   ├── ui/           # Shared React components
│   │   └── package.json
│   ├── db/           # Database client (Prisma)
│   │   └── package.json
│   ├── config-eslint/ # Shared ESLint config
│   │   └── package.json
│   └── config-typescript/ # Shared tsconfig
│       └── package.json
```

## Root Configuration

```json
// package.json (root)
{
  "private": true,
  "workspaces": ["apps/*", "packages/*"],
  "scripts": {
    "dev": "turbo dev",
    "build": "turbo build",
    "lint": "turbo lint",
    "test": "turbo test",
    "format": "prettier --write \"**/*.{ts,tsx,md}\""
  },
  "devDependencies": {
    "turbo": "^2",
    "prettier": "^3"
  }
}
```

```json
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "dist/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {
      "dependsOn": ["^build"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"]
    },
    "db:generate": {
      "cache": false
    }
  }
}
```

## Shared UI Package

```json
// packages/ui/package.json
{
  "name": "@repo/ui",
  "version": "0.0.0",
  "private": true,
  "exports": {
    "./button": "./src/button.tsx",
    "./card": "./src/card.tsx",
    "./input": "./src/input.tsx"
  },
  "peerDependencies": {
    "react": "^19",
    "react-dom": "^19"
  },
  "devDependencies": {
    "@repo/config-typescript": "workspace:*",
    "typescript": "^5"
  }
}
```

```tsx
// packages/ui/src/button.tsx
import type { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "destructive";
}

export function Button({ variant = "primary", className, ...props }: ButtonProps) {
  return <button data-variant={variant} className={className} {...props} />;
}
```

## Consuming Shared Packages

```json
// apps/web/package.json
{
  "name": "web",
  "dependencies": {
    "@repo/ui": "workspace:*",
    "@repo/db": "workspace:*"
  }
}
```

```tsx
// apps/web/app/page.tsx
import { Button } from "@repo/ui/button";
import { Card } from "@repo/ui/card";

export default function Home() {
  return (
    <Card>
      <h1>Welcome</h1>
      <Button variant="primary">Get Started</Button>
    </Card>
  );
}
```

## CI Configuration

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: "pnpm"
      - run: pnpm install --frozen-lockfile
      - run: pnpm turbo build lint test
        env:
          TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
          TURBO_TEAM: ${{ vars.TURBO_TEAM }}
```

## Additional Resources

- Turborepo docs: https://turbo.build/repo/docs
- Monorepo handbook: https://turbo.build/repo/docs/handbook
- pnpm workspaces: https://pnpm.io/workspaces
