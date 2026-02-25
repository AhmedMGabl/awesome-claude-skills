---
name: git-hooks-automation
description: Git hooks and repository automation covering pre-commit hooks, commit message linting, Husky setup, lint-staged, conventional commits, branch protection, automated changelogs, semantic versioning, release automation, and developer experience tooling.
---

# Git Hooks & Automation

This skill should be used when setting up developer experience tooling for Git repositories. It covers hooks, commit conventions, automated releases, and repository automation.

## When to Use This Skill

Use this skill when you need to:

- Set up pre-commit hooks for linting and formatting
- Enforce commit message conventions
- Configure Husky and lint-staged
- Implement conventional commits
- Automate versioning and changelogs
- Build release automation pipelines

## Husky + lint-staged Setup

```bash
# Install
npm install -D husky lint-staged

# Initialize Husky
npx husky init
```

```json
// package.json
{
  "scripts": {
    "prepare": "husky"
  },
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix", "prettier --write"],
    "*.{css,scss}": ["prettier --write"],
    "*.{json,md,yml}": ["prettier --write"]
  }
}
```

```bash
# .husky/pre-commit
npx lint-staged

# .husky/commit-msg
npx commitlint --edit $1
```

## Conventional Commits

```bash
# Install commitlint
npm install -D @commitlint/cli @commitlint/config-conventional
```

```typescript
// commitlint.config.ts
export default {
  extends: ["@commitlint/config-conventional"],
  rules: {
    "type-enum": [2, "always", [
      "feat",     // New feature
      "fix",      // Bug fix
      "docs",     // Documentation
      "style",    // Formatting (no code change)
      "refactor", // Code change (no feature/fix)
      "perf",     // Performance improvement
      "test",     // Adding tests
      "build",    // Build system / dependencies
      "ci",       // CI configuration
      "chore",    // Other changes
      "revert",   // Revert previous commit
    ]],
    "subject-case": [2, "never", ["start-case", "pascal-case", "upper-case"]],
    "subject-max-length": [2, "always", 72],
    "body-max-line-length": [2, "always", 100],
  },
};
```

```
COMMIT MESSAGE FORMAT:
  <type>(<scope>): <description>

  [optional body]

  [optional footer(s)]

EXAMPLES:
  feat(auth): add OAuth2 login with Google
  fix(api): handle null response from payment gateway
  docs(readme): update installation instructions
  refactor(db): extract query builder into separate module

BREAKING CHANGES:
  feat(api)!: change response format for /users endpoint

  BREAKING CHANGE: The users endpoint now returns paginated results.
  Previously it returned a flat array.
```

## Changesets (Monorepo Versioning)

```bash
# Install
npm install -D @changesets/cli
npx changeset init
```

```json
// .changeset/config.json
{
  "$schema": "https://unpkg.com/@changesets/config@3.0.0/schema.json",
  "changelog": "@changesets/changelog-github",
  "commit": false,
  "fixed": [],
  "linked": [],
  "access": "public",
  "baseBranch": "main",
  "updateInternalDependencies": "patch"
}
```

```bash
# Create a changeset (interactive)
npx changeset

# Version packages (updates package.json + CHANGELOG.md)
npx changeset version

# Publish packages
npx changeset publish
```

## Semantic Release (Automated)

```bash
npm install -D semantic-release @semantic-release/changelog @semantic-release/git
```

```json
// .releaserc.json
{
  "branches": ["main"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    ["@semantic-release/changelog", { "changelogFile": "CHANGELOG.md" }],
    ["@semantic-release/npm", { "npmPublish": true }],
    ["@semantic-release/git", {
      "assets": ["CHANGELOG.md", "package.json"],
      "message": "chore(release): ${nextRelease.version}"
    }],
    "@semantic-release/github"
  ]
}
```

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    branches: [main]
jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      packages: write
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npx semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## Pre-commit Hooks (Python)

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-merge-conflict
      - id: detect-private-key

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.13.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

```bash
# Install
pip install pre-commit
pre-commit install
pre-commit run --all-files  # Test on entire repo
```

## Branch Protection Rules

```yaml
# GitHub branch protection (via API or UI)
protection:
  main:
    required_reviews: 1
    dismiss_stale_reviews: true
    require_code_owner_reviews: true
    required_status_checks:
      strict: true  # Branch must be up to date
      contexts:
        - "lint"
        - "test"
        - "build"
    enforce_admins: true
    restrictions: null  # No push restrictions
    allow_force_pushes: false
    allow_deletions: false
```

## Custom Git Hooks

```bash
# .husky/pre-push — Prevent pushing to main directly
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
  echo "Direct push to $BRANCH is not allowed. Use a pull request."
  exit 1
fi

# .husky/pre-commit — Check for debug statements
if git diff --cached --name-only | grep -E '\.(ts|tsx|js|jsx)$' | xargs grep -l 'console\.log\|debugger' 2>/dev/null; then
  echo "Found console.log or debugger statements. Remove before committing."
  exit 1
fi

# .husky/prepare-commit-msg — Add branch name to commit
BRANCH=$(git rev-parse --abbrev-ref HEAD)
TICKET=$(echo "$BRANCH" | grep -oE '[A-Z]+-[0-9]+' || true)
if [ -n "$TICKET" ]; then
  sed -i.bak "1s/$/ [$TICKET]/" "$1"
fi
```

## Additional Resources

- Conventional Commits: https://www.conventionalcommits.org/
- Husky: https://typicode.github.io/husky/
- Semantic Release: https://semantic-release.gitbook.io/
- Changesets: https://github.com/changesets/changesets
- Pre-commit: https://pre-commit.com/
