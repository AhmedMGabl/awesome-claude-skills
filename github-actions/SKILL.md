---
name: github-actions
description: GitHub Actions CI/CD covering workflow syntax, reusable workflows, composite actions, matrix strategies, caching, artifact management, environment deployments, secrets, and self-hosted runners.
---

# GitHub Actions

This skill should be used when setting up CI/CD pipelines with GitHub Actions. It covers workflow syntax, reusable workflows, matrix builds, caching, and deployment patterns.

## When to Use This Skill

Use this skill when you need to:

- Set up CI/CD pipelines for GitHub repositories
- Create reusable workflow components
- Configure matrix builds for multiple environments
- Implement deployment workflows with environments
- Optimize build performance with caching

## Basic CI Workflow

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: "npm"

      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm test -- --coverage

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: coverage
          path: coverage/
```

## Matrix Strategy

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        node-version: [18, 20, 22]
        exclude:
          - os: macos-latest
            node-version: 18
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm ci
      - run: npm test
```

## Caching Dependencies

```yaml
steps:
  # Node.js with npm
  - uses: actions/setup-node@v4
    with:
      node-version: 20
      cache: "npm"

  # Custom cache (e.g., Turborepo)
  - uses: actions/cache@v4
    with:
      path: .turbo
      key: turbo-${{ runner.os }}-${{ hashFiles('**/turbo.json') }}
      restore-keys: |
        turbo-${{ runner.os }}-

  # Docker layer caching
  - uses: docker/build-push-action@v5
    with:
      context: .
      cache-from: type=gha
      cache-to: type=gha,mode=max
```

## Reusable Workflow

```yaml
# .github/workflows/deploy-reusable.yml
name: Deploy

on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
      app-version:
        required: true
        type: string
    secrets:
      deploy-token:
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - uses: actions/checkout@v4
      - run: echo "Deploying ${{ inputs.app-version }} to ${{ inputs.environment }}"
```

```yaml
# .github/workflows/release.yml (caller)
name: Release

on:
  push:
    tags: ["v*"]

jobs:
  deploy-staging:
    uses: ./.github/workflows/deploy-reusable.yml
    with:
      environment: staging
      app-version: ${{ github.ref_name }}
    secrets:
      deploy-token: ${{ secrets.DEPLOY_TOKEN }}

  deploy-production:
    needs: deploy-staging
    uses: ./.github/workflows/deploy-reusable.yml
    with:
      environment: production
      app-version: ${{ github.ref_name }}
    secrets:
      deploy-token: ${{ secrets.DEPLOY_TOKEN }}
```

## Composite Action

```yaml
# .github/actions/setup-project/action.yml
name: Setup Project
description: Install dependencies and build

inputs:
  node-version:
    description: Node.js version
    default: "20"

runs:
  using: composite
  steps:
    - uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}
        cache: "npm"

    - run: npm ci
      shell: bash

    - run: npm run build
      shell: bash
```

## Deployment with Environments

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://myapp.com
    permissions:
      id-token: write # For OIDC
    steps:
      - uses: actions/checkout@v4

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: us-east-1

      - run: |
          aws s3 sync ./dist s3://${{ vars.S3_BUCKET }}
          aws cloudfront create-invalidation --distribution-id ${{ vars.CF_DIST_ID }} --paths "/*"
```

## Release Workflow

```yaml
on:
  push:
    tags: ["v*"]

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm run build

      - name: Create Release
        uses: softprops/action-gh-release@v2
        with:
          generate_release_notes: true
          files: dist/*
```

## Additional Resources

- GitHub Actions docs: https://docs.github.com/en/actions
- Workflow syntax: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions
- Marketplace: https://github.com/marketplace?type=actions
