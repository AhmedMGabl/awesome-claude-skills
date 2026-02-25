---
name: biome-linting
description: Biome toolchain covering linting, formatting, import sorting, configuration, rule customization, IDE integration, migration from ESLint and Prettier, CI setup, and monorepo support.
---

# Biome Toolchain

This skill should be used when using Biome as an all-in-one linter, formatter, and import sorter. It covers configuration, rule customization, migration, and CI integration.

## When to Use This Skill

Use this skill when you need to:

- Replace ESLint + Prettier with a single tool
- Configure linting rules for TypeScript/JavaScript
- Set up formatting with consistent style
- Organize imports automatically
- Integrate with CI pipelines

## Setup

```bash
npm install --save-dev --save-exact @biomejs/biome
npx @biomejs/biome init
```

## Configuration

```jsonc
// biome.json
{
  "$schema": "https://biomejs.dev/schemas/1.9.0/schema.json",
  "organizeImports": {
    "enabled": true
  },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "complexity": {
        "noBannedTypes": "error",
        "noUselessTypeConstraint": "error"
      },
      "correctness": {
        "noUnusedImports": "error",
        "noUnusedVariables": "warn",
        "useExhaustiveDependencies": "warn"
      },
      "suspicious": {
        "noExplicitAny": "warn",
        "noConsoleLog": "warn"
      },
      "style": {
        "noNonNullAssertion": "warn",
        "useConst": "error",
        "useImportType": "error"
      },
      "nursery": {
        "useSortedClasses": "warn"
      }
    }
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100,
    "lineEnding": "lf"
  },
  "javascript": {
    "formatter": {
      "quoteStyle": "double",
      "semicolons": "always",
      "trailingCommas": "all",
      "arrowParentheses": "always"
    }
  },
  "files": {
    "ignore": ["node_modules", "dist", ".next", "coverage"]
  }
}
```

## Override Rules Per Path

```jsonc
{
  "overrides": [
    {
      "include": ["**/*.test.ts", "**/*.spec.ts"],
      "linter": {
        "rules": {
          "suspicious": { "noExplicitAny": "off" }
        }
      }
    },
    {
      "include": ["scripts/**"],
      "linter": {
        "rules": {
          "suspicious": { "noConsoleLog": "off" }
        }
      }
    }
  ]
}
```

## CLI Commands

```bash
npx biome check .               # Lint + format check
npx biome check --write .       # Lint + format + fix
npx biome lint .                # Lint only
npx biome format .              # Format check only
npx biome format --write .      # Format and write
npx biome ci .                  # CI mode (errors only, no writes)
npx biome migrate eslint        # Migrate from ESLint config
npx biome migrate prettier      # Migrate from Prettier config
```

## Package.json Scripts

```json
{
  "scripts": {
    "lint": "biome check .",
    "lint:fix": "biome check --write .",
    "format": "biome format --write .",
    "ci": "biome ci ."
  }
}
```

## Git Hooks (with lint-staged)

```json
{
  "lint-staged": {
    "*.{js,ts,jsx,tsx,json,css}": ["biome check --write --no-errors-on-unmatched"]
  }
}
```

## CI Integration

```yaml
# .github/workflows/lint.yml
name: Lint
on: [pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: biomejs/setup-biome@v2
      - run: biome ci .
```

## Additional Resources

- Biome docs: https://biomejs.dev/
- Biome rules: https://biomejs.dev/linter/rules/
- Migration guide: https://biomejs.dev/guides/migrate-eslint-prettier/
