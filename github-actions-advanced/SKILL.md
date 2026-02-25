---
name: github-actions-advanced
description: Advanced GitHub Actions patterns covering reusable workflows, composite actions, matrix strategies, concurrency control, caching (node_modules, Docker layers), environment deployments, OIDC authentication, artifact management, and workflow optimization.
---

# GitHub Actions Advanced

This skill should be used for advanced CI/CD patterns with GitHub Actions. It covers reusable workflows, matrix builds, caching, OIDC, deployments, and optimization.

## When to Use This Skill

Use this skill when you need to:

- Create reusable workflows and composite actions
- Optimize build times with caching and matrix
- Set up environment-based deployments
- Use OIDC for cloud authentication
- Handle complex CI/CD requirements

## Reusable Workflow

```yaml
# .github/workflows/deploy.yml (reusable)
name: Deploy
on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
      app-name:
        required: true
        type: string
    secrets:
      AWS_ROLE_ARN:
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v4

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: us-east-1

      - run: |
          aws deploy create-deployment \
            --application-name ${{ inputs.app-name }} \
            --deployment-group-name ${{ inputs.environment }}
```

```yaml
# .github/workflows/ci.yml (caller)
name: CI/CD
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: "pnpm" }
      - run: pnpm install --frozen-lockfile
      - run: pnpm test

  deploy-staging:
    needs: test
    uses: ./.github/workflows/deploy.yml
    with:
      environment: staging
      app-name: my-app
    secrets:
      AWS_ROLE_ARN: ${{ secrets.AWS_ROLE_ARN_STAGING }}

  deploy-production:
    needs: deploy-staging
    uses: ./.github/workflows/deploy.yml
    with:
      environment: production
      app-name: my-app
    secrets:
      AWS_ROLE_ARN: ${{ secrets.AWS_ROLE_ARN_PROD }}
```

## Matrix Strategy

```yaml
jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest]
        node: [20, 22]
        include:
          - os: ubuntu-latest
            node: 22
            coverage: true
        exclude:
          - os: macos-latest
            node: 20
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: ${{ matrix.node }} }
      - run: npm test
      - if: matrix.coverage
        run: npm run test:coverage
```

## Caching

```yaml
# Node modules cache
- uses: actions/setup-node@v4
  with:
    node-version: 22
    cache: "pnpm"

# Docker layer caching
- uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: my-app:latest
    cache-from: type=gha
    cache-to: type=gha,mode=max

# Custom cache
- uses: actions/cache@v4
  with:
    path: |
      ~/.cache/playwright
      .next/cache
    key: ${{ runner.os }}-cache-${{ hashFiles('**/pnpm-lock.yaml') }}
    restore-keys: ${{ runner.os }}-cache-
```

## Concurrency Control

```yaml
# Cancel in-progress runs on same branch
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

# Don't cancel production deploys
concurrency:
  group: deploy-${{ inputs.environment }}
  cancel-in-progress: ${{ inputs.environment != 'production' }}
```

## Composite Action

```yaml
# .github/actions/setup-project/action.yml
name: Setup Project
description: Install dependencies and build
inputs:
  node-version:
    default: "22"
runs:
  using: composite
  steps:
    - uses: pnpm/action-setup@v4
    - uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}
        cache: "pnpm"
    - run: pnpm install --frozen-lockfile
      shell: bash
    - run: pnpm build
      shell: bash
```

## Additional Resources

- GitHub Actions docs: https://docs.github.com/en/actions
- Reusable workflows: https://docs.github.com/en/actions/sharing-automations/reusing-workflows
- OIDC: https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect
