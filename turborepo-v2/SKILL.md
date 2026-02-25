---
name: turborepo-v2
description: Turborepo v2 covering task configuration in turbo.json, watch mode, boundary enforcement, workspace dependencies, remote caching, environment variable passthrough, and migration from v1.
---

# Turborepo v2

This skill should be used when configuring Turborepo v2 for monorepo task orchestration. It covers new task configuration, watch mode, boundaries, and migration from v1.

## When to Use This Skill

Use this skill when you need to:

- Configure Turborepo v2 task pipelines
- Enable watch mode for development
- Enforce package boundaries
- Set up remote caching
- Migrate from Turborepo v1

## turbo.json v2

```jsonc
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**", "!.next/cache/**"],
      "env": ["NODE_ENV", "API_URL"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "test": {
      "dependsOn": ["build"],
      "env": ["CI"]
    },
    "lint": {},
    "typecheck": {
      "dependsOn": ["^build"]
    }
  }
}
```

## Watch Mode

```bash
# Run tasks in watch mode
turbo watch dev

# Watch specific packages
turbo watch dev --filter=@app/web --filter=@app/api
```

## Package-Level Task Config

```jsonc
// packages/ui/turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "extends": ["//"],
  "tasks": {
    "build": {
      "outputs": ["dist/**"],
      "inputs": ["src/**", "tsconfig.json"]
    }
  }
}
```

## Boundary Enforcement

```jsonc
// turbo.json — enforce package boundaries
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"]
    }
  },
  // Packages can only depend on packages in their dependency tree
  "boundaries": {
    "tags": {
      "apps/*": { "allow": ["packages/*"] },
      "packages/ui": { "allow": ["packages/utils"] },
      "packages/utils": { "allow": [] }
    }
  }
}
```

## CLI Commands

```bash
turbo build                    # Run build for all packages
turbo build --filter=@app/web  # Run for specific package
turbo build --filter=...[HEAD] # Run for changed packages
turbo build --dry              # Dry run showing what would execute
turbo build --graph            # Generate task graph
turbo run lint test --parallel # Run multiple tasks in parallel
turbo prune @app/web           # Create pruned monorepo for Docker
```

## Additional Resources

- Turborepo docs: https://turbo.build/repo/docs
- Task configuration: https://turbo.build/repo/docs/reference/configuration
