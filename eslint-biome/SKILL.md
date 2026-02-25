---
name: eslint-biome
description: Code linting and formatting covering ESLint flat config, Biome unified tooling, Prettier integration, custom rule development, TypeScript-aware linting, framework-specific plugins for React and Next.js, auto-fix strategies, and CI enforcement.
---

# ESLint & Biome

This skill should be used when configuring code linting and formatting tools. It covers ESLint flat config, Biome, Prettier, custom rules, and CI enforcement.

## When to Use This Skill

Use this skill when you need to:

- Configure ESLint with flat config (v9+)
- Set up Biome as an all-in-one linter/formatter
- Integrate Prettier with ESLint
- Write custom ESLint rules
- Enforce code quality in CI pipelines

## ESLint Flat Config (v9+)

```typescript
// eslint.config.ts
import eslint from "@eslint/js";
import tseslint from "typescript-eslint";
import react from "eslint-plugin-react";
import reactHooks from "eslint-plugin-react-hooks";
import importPlugin from "eslint-plugin-import";

export default tseslint.config(
  eslint.configs.recommended,
  ...tseslint.configs.strictTypeChecked,
  {
    languageOptions: {
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
  },
  {
    files: ["**/*.{ts,tsx}"],
    plugins: {
      react,
      "react-hooks": reactHooks,
      import: importPlugin,
    },
    rules: {
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "warn",
      "import/order": ["error", {
        groups: ["builtin", "external", "internal", "parent", "sibling"],
        "newlines-between": "always",
        alphabetize: { order: "asc" },
      }],
      "@typescript-eslint/no-unused-vars": ["error", {
        argsIgnorePattern: "^_",
        varsIgnorePattern: "^_",
      }],
      "@typescript-eslint/consistent-type-imports": "error",
    },
  },
  {
    ignores: ["dist/", "node_modules/", ".next/", "coverage/"],
  },
);
```

## Biome Configuration

```json
// biome.json
{
  "$schema": "https://biomejs.dev/schemas/1.9.0/schema.json",
  "organizeImports": { "enabled": true },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "complexity": {
        "noBannedTypes": "error",
        "noExtraBooleanCast": "error"
      },
      "correctness": {
        "noUnusedVariables": "warn",
        "useExhaustiveDependencies": "warn"
      },
      "style": {
        "noNonNullAssertion": "warn",
        "useConst": "error"
      },
      "suspicious": {
        "noExplicitAny": "warn"
      }
    }
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100
  },
  "javascript": {
    "formatter": {
      "quoteStyle": "double",
      "trailingCommas": "all",
      "semicolons": "always"
    }
  },
  "files": {
    "ignore": ["dist", "node_modules", ".next", "coverage"]
  }
}
```

## Prettier + ESLint Integration

```typescript
// eslint.config.ts — disable ESLint formatting, let Prettier handle it
import eslintConfigPrettier from "eslint-config-prettier";

export default tseslint.config(
  // ... other configs
  eslintConfigPrettier,  // Must be last to override formatting rules
);
```

```json
// .prettierrc
{
  "semi": true,
  "singleQuote": false,
  "trailingComma": "all",
  "printWidth": 100,
  "tabWidth": 2,
  "plugins": ["prettier-plugin-tailwindcss"]
}
```

## lint-staged + Husky

```json
// package.json
{
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix", "prettier --write"],
    "*.{json,md,yml}": ["prettier --write"]
  }
}
```

```bash
npx husky init
echo "npx lint-staged" > .husky/pre-commit
```

## CLI Commands

```bash
# ESLint
npx eslint .                    # Lint all files
npx eslint --fix .              # Auto-fix
npx eslint --inspect-config     # Debug config

# Biome
npx @biomejs/biome check .      # Lint + format check
npx @biomejs/biome check --write . # Auto-fix
npx @biomejs/biome format .     # Format only
npx @biomejs/biome lint .       # Lint only

# Prettier
npx prettier --write .          # Format all files
npx prettier --check .          # Check formatting
```

## ESLint vs Biome

```
FEATURE              ESLINT              BIOME
──────────────────────────────────────────────────────
Speed                Moderate            10-100x faster
Config               JavaScript          JSON
Plugins              Huge ecosystem      Built-in rules
Formatting           Via Prettier        Built-in
Custom rules         Full support        Limited
TypeScript           Via plugin          Native
Import sorting       Via plugin          Built-in
```

## Additional Resources

- ESLint flat config: https://eslint.org/docs/latest/use/configure/configuration-files
- Biome: https://biomejs.dev/
- typescript-eslint: https://typescript-eslint.io/
