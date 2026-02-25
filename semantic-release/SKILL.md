---
name: semantic-release
description: Automated release management and semantic versioning covering semantic-release configuration, conventional commits enforcement with commitlint and Husky, changesets for monorepo versioning, GitHub Actions release workflows, npm publishing automation, changelog generation, pre-release channels (alpha, beta, next), and release branching strategies. This skill should be used when setting up or troubleshooting automated version management, release pipelines, or commit convention enforcement in JavaScript/TypeScript projects.
---

# Semantic Release & Automated Versioning

This skill provides production-ready configurations for fully automated release management. It covers the entire release pipeline from enforcing commit conventions through Husky and commitlint, to automated version bumps, changelog generation, npm publishing, and GitHub release creation using semantic-release and changesets.

---

## 1. Semantic Versioning Fundamentals

Semantic versioning (SemVer) uses the format `MAJOR.MINOR.PATCH`:

| Increment | Trigger | Example |
|-----------|---------|---------|
| MAJOR | Breaking API changes | `1.2.3` -> `2.0.0` |
| MINOR | New backward-compatible features | `1.2.3` -> `1.3.0` |
| PATCH | Backward-compatible bug fixes | `1.2.3` -> `1.2.4` |

Pre-release identifiers append to the version: `2.0.0-alpha.1`, `2.0.0-beta.3`, `2.0.0-rc.1`.

Build metadata appends after `+`: `1.0.0+build.123` (ignored in version precedence).

### Version Precedence

```
1.0.0-alpha < 1.0.0-alpha.1 < 1.0.0-beta < 1.0.0-beta.2 < 1.0.0-rc.1 < 1.0.0
```

---

## 2. Conventional Commits Format

Every commit message must follow this structure:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Commit Types and Their SemVer Impact

| Type | Description | SemVer Impact |
|------|-------------|---------------|
| `feat` | New feature | MINOR bump |
| `fix` | Bug fix | PATCH bump |
| `docs` | Documentation only | No release |
| `style` | Formatting, whitespace (no logic change) | No release |
| `refactor` | Code restructuring (no feature/fix) | No release |
| `perf` | Performance improvement | PATCH bump |
| `test` | Adding or correcting tests | No release |
| `build` | Build system or external dependencies | No release |
| `ci` | CI configuration changes | No release |
| `chore` | Maintenance tasks | No release |
| `revert` | Revert a previous commit | PATCH bump |

### Breaking Changes (MAJOR bump)

Breaking changes are indicated in two ways:

```
feat(api)!: remove deprecated /users/list endpoint

BREAKING CHANGE: The /users/list endpoint has been removed.
Use /users with pagination parameters instead.
```

The `!` after the type/scope and/or the `BREAKING CHANGE:` footer both trigger a MAJOR version bump.

### Commit Message Examples

```
feat(auth): add OAuth2 login with Google provider
fix(parser): handle null bytes in CSV input
perf(query): add database index for user lookup
docs(readme): update installation instructions for v3
refactor(middleware): extract rate limiter into separate module
build(deps): upgrade webpack from v4 to v5

feat(api)!: change pagination response format

BREAKING CHANGE: The `data` field is now wrapped in a `results` object.
Migration: Replace `response.data` with `response.results.data`.

fix(auth): resolve token refresh race condition

When multiple API calls triggered concurrent token refreshes,
the refresh token could be invalidated before all calls completed.

Closes #1234
```

---

## 3. Commitlint Setup

### Installation

```bash
npm install -D @commitlint/cli @commitlint/config-conventional
```

### Configuration

```typescript
// commitlint.config.ts
import type { UserConfig } from "@commitlint/types";

const config: UserConfig = {
  extends: ["@commitlint/config-conventional"],
  rules: {
    // Type must be one of these values
    "type-enum": [
      2,
      "always",
      [
        "feat",
        "fix",
        "docs",
        "style",
        "refactor",
        "perf",
        "test",
        "build",
        "ci",
        "chore",
        "revert",
      ],
    ],
    // Type must be lowercase
    "type-case": [2, "always", "lower-case"],
    // Type is required
    "type-empty": [2, "never"],
    // Scope must be lowercase
    "scope-case": [2, "always", "lower-case"],
    // Subject is required
    "subject-empty": [2, "never"],
    // Subject must not start with uppercase
    "subject-case": [
      2,
      "never",
      ["start-case", "pascal-case", "upper-case"],
    ],
    // Subject must not end with period
    "subject-full-stop": [2, "never", "."],
    // Subject max length
    "subject-max-length": [2, "always", 72],
    // Header max length (type + scope + subject)
    "header-max-length": [2, "always", 100],
    // Body lines max length
    "body-max-line-length": [2, "always", 100],
    // Footer lines max length
    "footer-max-line-length": [2, "always", 100],
  },
};

export default config;
```

For JavaScript projects, use `commitlint.config.js` instead:

```javascript
// commitlint.config.js
module.exports = {
  extends: ["@commitlint/config-conventional"],
  rules: {
    "type-enum": [
      2,
      "always",
      [
        "feat", "fix", "docs", "style", "refactor",
        "perf", "test", "build", "ci", "chore", "revert",
      ],
    ],
    "subject-max-length": [2, "always", 72],
    "header-max-length": [2, "always", 100],
    "body-max-line-length": [2, "always", 100],
  },
};
```

### Custom Scopes (Optional)

To restrict valid scopes to known module names:

```javascript
// commitlint.config.js
module.exports = {
  extends: ["@commitlint/config-conventional"],
  rules: {
    "scope-enum": [
      2,
      "always",
      ["api", "auth", "cli", "config", "core", "db", "docs", "ui"],
    ],
  },
};
```

---

## 4. Husky + Commitlint Integration

### Installation and Setup

```bash
# Install Husky and commitlint
npm install -D husky @commitlint/cli @commitlint/config-conventional

# Initialize Husky
npx husky init
```

### Git Hook Configuration

```bash
# .husky/commit-msg
npx --no -- commitlint --edit $1
```

```bash
# .husky/pre-commit
npx lint-staged
```

### package.json Configuration

```json
{
  "scripts": {
    "prepare": "husky",
    "commitlint": "commitlint --from HEAD~1 --to HEAD --verbose"
  },
  "lint-staged": {
    "*.{ts,tsx,js,jsx}": ["eslint --fix", "prettier --write"],
    "*.{css,scss,less}": ["prettier --write"],
    "*.{json,md,yml,yaml}": ["prettier --write"]
  }
}
```

### Interactive Commit Helper (Optional)

To provide a guided commit message prompt:

```bash
npm install -D @commitlint/prompt-cli
# or use commitizen
npm install -D commitizen cz-conventional-changelog
```

```json
{
  "scripts": {
    "commit": "cz"
  },
  "config": {
    "commitizen": {
      "path": "cz-conventional-changelog"
    }
  }
}
```

Then commit interactively with `npm run commit` instead of `git commit`.

---

## 5. Semantic-Release Configuration

### Installation

```bash
npm install -D semantic-release \
  @semantic-release/changelog \
  @semantic-release/git \
  @semantic-release/github \
  @semantic-release/npm \
  conventional-changelog-conventionalcommits
```

### Basic Configuration (.releaserc.json)

```json
{
  "branches": ["main"],
  "plugins": [
    [
      "@semantic-release/commit-analyzer",
      {
        "preset": "conventionalcommits",
        "releaseRules": [
          { "type": "feat", "release": "minor" },
          { "type": "fix", "release": "patch" },
          { "type": "perf", "release": "patch" },
          { "type": "revert", "release": "patch" },
          { "type": "docs", "scope": "README", "release": "patch" },
          { "breaking": true, "release": "major" }
        ]
      }
    ],
    [
      "@semantic-release/release-notes-generator",
      {
        "preset": "conventionalcommits",
        "presetConfig": {
          "types": [
            { "type": "feat", "section": "Features" },
            { "type": "fix", "section": "Bug Fixes" },
            { "type": "perf", "section": "Performance Improvements" },
            { "type": "revert", "section": "Reverts" },
            { "type": "docs", "section": "Documentation", "hidden": false },
            { "type": "style", "section": "Styles", "hidden": true },
            { "type": "chore", "section": "Miscellaneous", "hidden": true },
            { "type": "refactor", "section": "Code Refactoring", "hidden": true },
            { "type": "test", "section": "Tests", "hidden": true },
            { "type": "build", "section": "Build System", "hidden": true },
            { "type": "ci", "section": "CI/CD", "hidden": true }
          ]
        }
      }
    ],
    [
      "@semantic-release/changelog",
      {
        "changelogFile": "CHANGELOG.md",
        "changelogTitle": "# Changelog"
      }
    ],
    [
      "@semantic-release/npm",
      {
        "npmPublish": true
      }
    ],
    [
      "@semantic-release/git",
      {
        "assets": ["CHANGELOG.md", "package.json", "package-lock.json"],
        "message": "chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}"
      }
    ],
    "@semantic-release/github"
  ]
}
```

### Alternative Configuration Formats

Configuration can be placed in any of these files:

- `.releaserc` (JSON or YAML)
- `.releaserc.json`
- `.releaserc.yaml` / `.releaserc.yml`
- `.releaserc.js` / `.releaserc.cjs` / `.releaserc.mjs`
- `release.config.js` / `release.config.cjs` / `release.config.mjs`
- `"release"` key in `package.json`

JavaScript configuration for advanced logic:

```javascript
// release.config.js
module.exports = {
  branches: ["main"],
  plugins: [
    ["@semantic-release/commit-analyzer", {
      preset: "conventionalcommits",
    }],
    ["@semantic-release/release-notes-generator", {
      preset: "conventionalcommits",
    }],
    ["@semantic-release/changelog", {
      changelogFile: "CHANGELOG.md",
    }],
    ["@semantic-release/npm", {
      npmPublish: !!process.env.NPM_TOKEN,
    }],
    ["@semantic-release/git", {
      assets: ["CHANGELOG.md", "package.json", "package-lock.json"],
      message: "chore(release): ${nextRelease.version} [skip ci]",
    }],
    "@semantic-release/github",
  ],
};
```

### Configuration Without npm Publishing

For projects that do not publish to npm (e.g., applications, services):

```json
{
  "branches": ["main"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    ["@semantic-release/changelog", { "changelogFile": "CHANGELOG.md" }],
    ["@semantic-release/npm", { "npmPublish": false }],
    ["@semantic-release/git", {
      "assets": ["CHANGELOG.md", "package.json"],
      "message": "chore(release): ${nextRelease.version} [skip ci]"
    }],
    "@semantic-release/github"
  ]
}
```

### Plugin Execution Order

Plugins execute in the order listed. The recommended order:

1. `@semantic-release/commit-analyzer` -- Determine the release type
2. `@semantic-release/release-notes-generator` -- Generate release notes
3. `@semantic-release/changelog` -- Update CHANGELOG.md
4. `@semantic-release/npm` -- Update package.json version and publish
5. `@semantic-release/git` -- Commit changed files back to repository
6. `@semantic-release/github` -- Create GitHub release and comment on issues/PRs

---

## 6. Pre-Release Channels

### Branch-Based Pre-Release Configuration

```json
{
  "branches": [
    "main",
    { "name": "next", "prerelease": true },
    { "name": "beta", "prerelease": true },
    { "name": "alpha", "prerelease": true }
  ],
  "plugins": [
    ["@semantic-release/commit-analyzer", {
      "preset": "conventionalcommits"
    }],
    "@semantic-release/release-notes-generator",
    ["@semantic-release/changelog", { "changelogFile": "CHANGELOG.md" }],
    ["@semantic-release/npm", { "npmPublish": true }],
    ["@semantic-release/git", {
      "assets": ["CHANGELOG.md", "package.json", "package-lock.json"],
      "message": "chore(release): ${nextRelease.version} [skip ci]"
    }],
    "@semantic-release/github"
  ]
}
```

### How Pre-Release Channels Work

| Branch | Channel | npm Tag | Example Version |
|--------|---------|---------|-----------------|
| `main` | default | `latest` | `1.2.3` |
| `next` | next | `next` | `1.3.0-next.1` |
| `beta` | beta | `beta` | `1.3.0-beta.1` |
| `alpha` | alpha | `alpha` | `1.3.0-alpha.1` |

Users install specific channels with:

```bash
npm install my-package               # latest stable
npm install my-package@next          # next pre-release
npm install my-package@beta          # beta pre-release
npm install my-package@alpha         # alpha pre-release
```

### Maintenance Branches

To support multiple major version lines simultaneously:

```json
{
  "branches": [
    "+([0-9])?(.{+([0-9]),x}).x",
    "main",
    { "name": "next", "prerelease": true },
    { "name": "beta", "prerelease": true }
  ]
}
```

This allows branches like `1.x`, `2.x`, or `1.5.x` to receive patch releases independently. Example:

- `main` -> `3.0.0`, `3.1.0`, etc.
- `2.x` -> `2.7.1`, `2.7.2`, etc. (maintenance patches)
- `1.x` -> `1.15.3`, `1.15.4`, etc. (long-term support)

---

## 7. GitHub Actions Release Workflow

### Complete Automated Release Pipeline

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    branches:
      - main
      - next
      - beta
      - alpha
      - "+([0-9])?(.{+([0-9]),x}).x"

permissions:
  contents: write
  issues: write
  pull-requests: write
  packages: write
  id-token: write

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npm test -- --coverage

  release:
    name: Release
    needs: test
    runs-on: ubuntu-latest
    outputs:
      published: ${{ steps.semantic.outputs.new_release_published }}
      version: ${{ steps.semantic.outputs.new_release_version }}
      major: ${{ steps.semantic.outputs.new_release_major_version }}
      minor: ${{ steps.semantic.outputs.new_release_minor_version }}
      patch: ${{ steps.semantic.outputs.new_release_patch_version }}
      channel: ${{ steps.semantic.outputs.new_release_channel }}
      git-tag: ${{ steps.semantic.outputs.new_release_git_tag }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          persist-credentials: false
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - name: Semantic Release
        id: semantic
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
        run: npx semantic-release

  post-release:
    name: Post-Release
    needs: release
    if: needs.release.outputs.published == 'true'
    runs-on: ubuntu-latest
    steps:
      - name: Release summary
        run: |
          echo "## Release Published" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "- **Version:** ${{ needs.release.outputs.version }}" >> $GITHUB_STEP_SUMMARY
          echo "- **Tag:** ${{ needs.release.outputs.git-tag }}" >> $GITHUB_STEP_SUMMARY
          echo "- **Channel:** ${{ needs.release.outputs.channel || 'latest' }}" >> $GITHUB_STEP_SUMMARY
```

### Pull Request Validation Workflow

Enforce conventional commits on all pull requests:

```yaml
# .github/workflows/commitlint.yml
name: Commitlint

on:
  pull_request:
    branches: [main, next, beta, alpha]

jobs:
  commitlint:
    name: Lint Commit Messages
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - name: Validate PR commits
        run: npx commitlint --from ${{ github.event.pull_request.base.sha }} --to ${{ github.event.pull_request.head.sha }} --verbose
```

### Dry Run Workflow for Testing

Preview what a release would look like without actually publishing:

```yaml
# .github/workflows/release-dry-run.yml
name: Release Dry Run

on:
  pull_request:
    branches: [main]

jobs:
  dry-run:
    name: Preview Release
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - name: Semantic Release (dry run)
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: npx semantic-release --dry-run
```

---

## 8. npm Publishing Automation

### npm Token Configuration

```bash
# Generate a granular access token at https://www.npmjs.com/settings/~/tokens
# Add it as a repository secret named NPM_TOKEN
```

### .npmrc for CI Publishing

```ini
# .npmrc (committed to repository)
//registry.npmjs.org/:_authToken=${NPM_TOKEN}
access=public
```

Alternatively, configure in the workflow without committing `.npmrc`:

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: 20
    registry-url: https://registry.npmjs.org/
- run: npx semantic-release
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

### Scoped Package Publishing

```json
{
  "name": "@myorg/my-package",
  "publishConfig": {
    "access": "public",
    "registry": "https://registry.npmjs.org/"
  }
}
```

### GitHub Packages Publishing

To publish to GitHub Packages instead of or alongside npm:

```json
{
  "publishConfig": {
    "registry": "https://npm.pkg.github.com/"
  }
}
```

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: 20
    registry-url: https://npm.pkg.github.com/
- run: npx semantic-release
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    NODE_AUTH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Dual Publishing (npm + GitHub Packages)

```javascript
// release.config.js
module.exports = {
  branches: ["main"],
  plugins: [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    ["@semantic-release/changelog", { changelogFile: "CHANGELOG.md" }],
    // Publish to npm
    ["@semantic-release/npm", { npmPublish: true }],
    // Publish to GitHub Packages via exec plugin
    ["@semantic-release/exec", {
      publishCmd: [
        "npm config set //npm.pkg.github.com/:_authToken=${GITHUB_TOKEN}",
        "npm publish --registry https://npm.pkg.github.com/",
      ].join(" && "),
    }],
    ["@semantic-release/git", {
      assets: ["CHANGELOG.md", "package.json", "package-lock.json"],
      message: "chore(release): ${nextRelease.version} [skip ci]",
    }],
    "@semantic-release/github",
  ],
};
```

### npm Provenance (Supply Chain Security)

Enable npm provenance statements for builds on GitHub Actions:

```json
{
  "publishConfig": {
    "provenance": true
  }
}
```

```yaml
permissions:
  id-token: write  # Required for npm provenance
```

---

## 9. Changelog Generation

### Automatic Changelog via semantic-release

The `@semantic-release/changelog` plugin generates and updates `CHANGELOG.md` automatically. Configure the output format through `@semantic-release/release-notes-generator`:

```json
[
  "@semantic-release/release-notes-generator",
  {
    "preset": "conventionalcommits",
    "presetConfig": {
      "types": [
        { "type": "feat", "section": "Features", "hidden": false },
        { "type": "fix", "section": "Bug Fixes", "hidden": false },
        { "type": "perf", "section": "Performance", "hidden": false },
        { "type": "revert", "section": "Reverts", "hidden": false },
        { "type": "docs", "section": "Documentation", "hidden": false },
        { "type": "refactor", "section": "Refactoring", "hidden": false },
        { "type": "test", "section": "Tests", "hidden": true },
        { "type": "build", "section": "Build", "hidden": true },
        { "type": "ci", "section": "CI", "hidden": true },
        { "type": "chore", "section": "Chores", "hidden": true },
        { "type": "style", "section": "Styles", "hidden": true }
      ]
    },
    "writerOpts": {
      "commitsSort": ["scope", "subject"]
    }
  }
]
```

### Generated Changelog Format

The generated `CHANGELOG.md` follows this structure:

```markdown
# Changelog

## [2.1.0](https://github.com/org/repo/compare/v2.0.0...v2.1.0) (2026-02-25)

### Features

* **auth:** add SAML SSO integration ([#142](https://github.com/org/repo/issues/142)) ([abc1234](https://github.com/org/repo/commit/abc1234))
* **api:** add batch endpoint for bulk operations ([def5678](https://github.com/org/repo/commit/def5678))

### Bug Fixes

* **parser:** handle edge case with empty arrays ([ghi9012](https://github.com/org/repo/commit/ghi9012))

### Performance

* **query:** optimize N+1 query in user listing ([jkl3456](https://github.com/org/repo/commit/jkl3456))

## [2.0.0](https://github.com/org/repo/compare/v1.5.0...v2.0.0) (2026-01-15)

### BREAKING CHANGES

* **api:** response envelope format changed from `{ data }` to `{ results: { data } }`
```

---

## 10. Changesets for Monorepo Versioning

### Installation and Initialization

```bash
npm install -D @changesets/cli @changesets/changelog-github
npx changeset init
```

### Configuration

```json
// .changeset/config.json
{
  "$schema": "https://unpkg.com/@changesets/config@3.1.0/schema.json",
  "changelog": [
    "@changesets/changelog-github",
    { "repo": "org/monorepo" }
  ],
  "commit": false,
  "fixed": [],
  "linked": [
    ["@myorg/core", "@myorg/utils"]
  ],
  "access": "public",
  "baseBranch": "main",
  "updateInternalDependencies": "patch",
  "ignore": [],
  "___experimentalUnsafeOptions_WILL_CHANGE_IN_PATCH": {
    "onlyUpdatePeerDependentsWhenOutOfRange": true
  }
}
```

### Configuration Options Explained

| Option | Purpose |
|--------|---------|
| `changelog` | Changelog generator plugin (use `@changesets/changelog-github` for PR/commit links) |
| `commit` | Whether to auto-commit the changeset file |
| `fixed` | Groups of packages that always release together with the same version |
| `linked` | Groups of packages whose versions are linked (bump together) |
| `access` | npm access level (`public` or `restricted`) |
| `baseBranch` | Branch against which to compare for changes |
| `updateInternalDependencies` | Minimum bump for internal dependency updates (`patch`, `minor`, `major`) |
| `ignore` | Packages to exclude from versioning |

### Workflow: Creating a Changeset

```bash
# Interactive: select packages and describe changes
npx changeset

# This creates a file like .changeset/brave-dogs-fly.md:
```

```markdown
---
"@myorg/core": minor
"@myorg/utils": patch
---

Add new validation helpers to core package and update utils to use them.
```

### Workflow: Versioning and Publishing

```bash
# Apply all pending changesets (bumps versions, updates changelogs)
npx changeset version

# Publish all changed packages
npx changeset publish

# Tag published packages
git push --follow-tags
```

### GitHub Actions with Changesets

```yaml
# .github/workflows/release.yml
name: Release (Changesets)

on:
  push:
    branches: [main]

concurrency: ${{ github.workflow }}-${{ github.ref }}

jobs:
  release:
    name: Release
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
      packages: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci

      - name: Create Release Pull Request or Publish
        id: changesets
        uses: changesets/action@v1
        with:
          title: "chore: version packages"
          commit: "chore: version packages"
          publish: npx changeset publish
          version: npx changeset version
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}

      - name: Tag published packages
        if: steps.changesets.outputs.published == 'true'
        run: git push --follow-tags
```

### Changeset Pre-Release Mode

```bash
# Enter pre-release mode (creates .changeset/pre.json)
npx changeset pre enter beta

# Create changesets as normal
npx changeset

# Version packages (generates beta versions like 1.2.0-beta.0)
npx changeset version

# Publish beta versions
npx changeset publish

# Exit pre-release mode when ready for stable
npx changeset pre exit
npx changeset version
npx changeset publish
```

### Semantic-Release vs. Changesets

| Feature | semantic-release | Changesets |
|---------|-----------------|------------|
| Versioning trigger | Commit messages | Explicit changeset files |
| Monorepo support | Limited (multi-semantic-release) | Native |
| Developer intent | Implicit (from commits) | Explicit (per changeset) |
| Release grouping | Automatic per push | Batched via PR |
| Pre-releases | Branch-based channels | Pre-release mode |
| Human review | Optional dry run | Release PR with changelog preview |
| Best for | Single packages, libraries | Monorepos, multi-package projects |

---

## 11. Release Branching Strategies

### Strategy 1: Trunk-Based with Pre-Release Branches

```
main (stable releases: 1.0.0, 1.1.0, 2.0.0)
  |
  +-- next (next pre-releases: 2.1.0-next.1, 2.1.0-next.2)
  |
  +-- beta (beta pre-releases: 2.0.0-beta.1, 2.0.0-beta.2)
  |
  +-- alpha (alpha pre-releases: 3.0.0-alpha.1)
```

```json
{
  "branches": [
    "main",
    { "name": "next", "prerelease": true },
    { "name": "beta", "prerelease": true },
    { "name": "alpha", "prerelease": true }
  ]
}
```

Flow:

1. Develop features on topic branches
2. Merge to `alpha` for early testing -> publishes `x.y.z-alpha.N`
3. Promote to `beta` when feature-complete -> publishes `x.y.z-beta.N`
4. Promote to `next` for release candidate testing -> publishes `x.y.z-next.N`
5. Merge to `main` for stable release -> publishes `x.y.z`

### Strategy 2: Maintenance Branches (Multi-Version Support)

```
main (current major: 3.x)
  |
  +-- 2.x (maintenance: 2.8.1, 2.8.2)
  |
  +-- 1.x (LTS: 1.20.5, 1.20.6)
```

```json
{
  "branches": [
    "+([0-9])?(.{+([0-9]),x}).x",
    "main",
    { "name": "next", "prerelease": true }
  ]
}
```

Creating a maintenance branch:

```bash
# After releasing 3.0.0 on main, create a 2.x branch
git checkout -b 2.x v2.7.0
git push -u origin 2.x

# Cherry-pick fixes from main to 2.x
git checkout 2.x
git cherry-pick <commit-hash>
git push
# semantic-release creates 2.7.1 on the 2.x branch
```

### Strategy 3: Release Branches (Scheduled Releases)

```
main (development)
  |
  +-- release/3.2 (frozen for QA, receives only fixes)
  |
  +-- release/3.1 (previous release, hotfixes only)
```

```json
{
  "branches": [
    { "name": "release/+([0-9]).+([0-9])", "channel": "${name.replace(/^release\\//g, '')}" },
    "main",
    { "name": "next", "prerelease": true }
  ]
}
```

### Branch Protection for Release Branches

```yaml
# Recommended branch protection rules

main:
  require_pull_request_reviews: true
  required_approving_review_count: 2
  dismiss_stale_reviews: true
  require_status_checks_to_pass: true
  required_status_checks:
    - "test"
    - "lint"
    - "commitlint"
  enforce_admins: true
  allow_force_pushes: false

next:
  require_pull_request_reviews: true
  required_approving_review_count: 1
  require_status_checks_to_pass: true
  required_status_checks:
    - "test"

beta:
  require_status_checks_to_pass: true
  required_status_checks:
    - "test"
```

---

## 12. Complete Project Setup

### Step-by-Step Bootstrap

```bash
# 1. Initialize project
npm init -y

# 2. Install dependencies
npm install -D \
  semantic-release \
  @semantic-release/changelog \
  @semantic-release/git \
  @semantic-release/github \
  @semantic-release/npm \
  conventional-changelog-conventionalcommits \
  @commitlint/cli \
  @commitlint/config-conventional \
  husky \
  lint-staged

# 3. Initialize Husky
npx husky init

# 4. Create commit-msg hook
echo 'npx --no -- commitlint --edit $1' > .husky/commit-msg

# 5. Create pre-commit hook
echo 'npx lint-staged' > .husky/pre-commit
```

### Required Repository Secrets (GitHub)

| Secret | Source | Purpose |
|--------|--------|---------|
| `GITHUB_TOKEN` | Automatic | GitHub releases, comments, status checks |
| `NPM_TOKEN` | npmjs.com account settings | npm package publishing |

The `GITHUB_TOKEN` is provided automatically by GitHub Actions. Only `NPM_TOKEN` needs manual configuration.

### Minimum File Set

```
project/
  .github/
    workflows/
      release.yml          # Automated release pipeline
      commitlint.yml       # PR commit validation
  .husky/
    commit-msg             # commitlint hook
    pre-commit             # lint-staged hook
  .releaserc.json          # semantic-release configuration
  commitlint.config.js     # commitlint rules
  package.json             # scripts and lint-staged config
  CHANGELOG.md             # Auto-generated (empty initially)
```

---

## 13. Troubleshooting

### Common Issues

**semantic-release skips release ("no release published")**:
- Verify commits follow conventional commit format
- Check that commit types are configured in `releaseRules` (e.g., `chore` does not trigger a release by default)
- Ensure `fetch-depth: 0` in the checkout step (required for git history analysis)
- Run `npx semantic-release --dry-run` to debug

**GITHUB_TOKEN insufficient permissions**:
- Add explicit permissions block in the workflow
- For protected branches, use a personal access token or GitHub App token instead of `GITHUB_TOKEN`

**npm publish fails with 403**:
- Verify `NPM_TOKEN` is set and has publish permissions
- For scoped packages, ensure `"access": "public"` in `publishConfig`
- Check that the package name is not already taken

**commitlint rejects valid commits**:
- Run `echo "your commit message" | npx commitlint` locally to test
- Check that `commitlint.config.js` is in the repository root
- Verify the commit-msg hook has correct syntax: `npx --no -- commitlint --edit $1`

**Duplicate releases or tags**:
- Ensure the `[skip ci]` tag is in the release commit message
- Add `persist-credentials: false` to the checkout step
- Verify only one workflow triggers releases on the same branch

### Dry Run Commands

```bash
# Preview semantic-release behavior without publishing
npx semantic-release --dry-run

# Test commitlint against a message
echo "feat(api): add new endpoint" | npx commitlint

# Validate all commits on a branch
npx commitlint --from main --to HEAD --verbose

# Preview changeset version bumps (changesets)
npx changeset status --verbose
```

---

## Additional Resources

- Semantic Versioning Specification: https://semver.org/
- Conventional Commits: https://www.conventionalcommits.org/
- semantic-release: https://semantic-release.gitbook.io/
- Changesets: https://github.com/changesets/changesets
- commitlint: https://commitlint.js.org/
- Husky: https://typicode.github.io/husky/
