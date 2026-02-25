---
name: biome-config
description: Biome advanced configuration patterns covering rule customization, per-file overrides, import sorting, formatter options, linter groups, ignore patterns, CI integration, and migration from ESLint and Prettier.
---

# Biome Config

This skill should be used when configuring Biome for linting, formatting, and import sorting beyond the defaults. It covers rule customization, overrides, CI integration, and migration.

## When to Use This Skill

Use this skill when you need to:

- Customize Biome linting rules and severity levels
- Configure per-file and per-directory overrides
- Set up import sorting with custom groups
- Integrate Biome into CI pipelines
- Migrate from ESLint and Prettier to Biome

## Full Configuration

```json
// biome.json
{
  "$schema": "https://biomejs.dev/schemas/1.9.0/schema.json",
  "vcs": {
    "enabled": true,
    "clientKind": "git",
    "useIgnoreFile": true
  },
  "organizeImports": {
    "enabled": true
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100,
    "lineEnding": "lf",
    "formatWithErrors": false,
    "ignore": ["dist/**", "node_modules/**", "*.min.js"]
  },
  "javascript": {
    "formatter": {
      "quoteStyle": "double",
      "jsxQuoteStyle": "double",
      "trailingCommas": "all",
      "semicolons": "always",
      "arrowParentheses": "always",
      "bracketSpacing": true,
      "bracketSameLine": false
    }
  },
  "json": {
    "formatter": {
      "trailingCommas": "none"
    }
  },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "complexity": {
        "noExcessiveCognitiveComplexity": {
          "level": "warn",
          "options": { "maxAllowedComplexity": 15 }
        },
        "noUselessFragments": "error",
        "noForEach": "warn"
      },
      "correctness": {
        "noUnusedVariables": "error",
        "noUnusedImports": "error",
        "useExhaustiveDependencies": "warn",
        "useHookAtTopLevel": "error"
      },
      "performance": {
        "noAccumulatingSpread": "error",
        "noDelete": "warn"
      },
      "security": {
        "noDangerouslySetInnerHtml": "error"
      },
      "style": {
        "noNonNullAssertion": "warn",
        "useConst": "error",
        "useTemplate": "error",
        "useImportType": "error",
        "noParameterAssign": "error"
      },
      "suspicious": {
        "noExplicitAny": "warn",
        "noConsoleLog": "warn",
        "noDebugger": "error"
      },
      "nursery": {
        "useSortedClasses": {
          "level": "warn",
          "options": {
            "attributes": ["class", "className"],
            "functions": ["clsx", "cn", "cva"]
          }
        }
      }
    }
  }
}
```

## Per-File Overrides

```json
{
  "overrides": [
    {
      "include": ["**/*.test.ts", "**/*.test.tsx", "**/*.spec.ts"],
      "linter": {
        "rules": {
          "suspicious": {
            "noExplicitAny": "off"
          },
          "correctness": {
            "noUnusedVariables": "off"
          }
        }
      }
    },
    {
      "include": ["scripts/**"],
      "linter": {
        "rules": {
          "suspicious": {
            "noConsoleLog": "off"
          }
        }
      }
    },
    {
      "include": ["**/*.d.ts"],
      "linter": {
        "enabled": false
      }
    }
  ]
}
```

## CI Integration

```yaml
# .github/workflows/lint.yml
name: Lint
on: [push, pull_request]

jobs:
  biome:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: biomejs/setup-biome@v2
      - run: biome ci .
```

```bash
# CI commands
biome ci .                    # Lint + format check (no writes, exits non-zero on issues)
biome check .                 # Lint + format check
biome check --write .         # Auto-fix everything possible
biome format --write .        # Format only
biome lint --write .          # Lint fix only

# Check specific files
biome check src/
biome check --changed         # Only changed files (git)
biome check --staged          # Only staged files
```

## Pre-commit Hook

```json
// package.json
{
  "scripts": {
    "check": "biome check .",
    "fix": "biome check --write .",
    "format": "biome format --write ."
  },
  "lint-staged": {
    "*.{js,ts,tsx,json,css}": ["biome check --write --no-errors-on-unmatched"]
  }
}
```

## Migration from ESLint/Prettier

```bash
# Auto-migrate from ESLint config
biome migrate eslint --write

# Auto-migrate from Prettier config
biome migrate prettier --write

# Check what would change
biome migrate eslint --dry-run
```

## Additional Resources

- Biome docs: https://biomejs.dev/
- Configuration: https://biomejs.dev/reference/configuration/
- Rules: https://biomejs.dev/linter/rules/
