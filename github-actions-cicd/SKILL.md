---
name: github-actions-cicd
description: GitHub Actions CI/CD workflows covering reusable workflows, composite actions, matrix strategies, caching, artifact management, environment deployments, OIDC authentication, monorepo change detection, and security best practices.
---

# GitHub Actions CI/CD

This skill should be used when building production CI/CD pipelines with GitHub Actions. It covers reusable workflows, deployment strategies, caching, and security patterns.

## When to Use This Skill

Use this skill when you need to:

- Build CI pipelines for testing and linting
- Deploy to production with environment gates
- Create reusable workflows and composite actions
- Optimize build times with caching
- Implement OIDC authentication for cloud deployments

## Full CI/CD Pipeline

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
  lint-and-typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: "pnpm"
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint
      - run: pnpm typecheck

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        shard: [1, 2, 3]
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: "pnpm" }
      - run: pnpm install --frozen-lockfile
      - run: pnpm vitest --shard=${{ matrix.shard }}/3
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: coverage-${{ matrix.shard }}
          path: coverage/

  deploy:
    needs: [lint-and-typecheck, test]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_ROLE_ARN }}
          aws-region: us-east-1
      - run: pnpm install --frozen-lockfile && pnpm build
      - run: aws s3 sync dist/ s3://${{ vars.S3_BUCKET }} --delete
      - run: aws cloudfront create-invalidation --distribution-id ${{ vars.CF_DIST_ID }} --paths "/*"
```

## Reusable Workflow

```yaml
# .github/workflows/deploy-app.yml
name: Deploy App
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
      DEPLOY_TOKEN:
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - uses: actions/checkout@v4
      - run: echo "Deploying ${{ inputs.app-name }} to ${{ inputs.environment }}"
      - run: ./deploy.sh ${{ inputs.app-name }}
        env:
          DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
```

```yaml
# .github/workflows/release.yml — caller
jobs:
  staging:
    uses: ./.github/workflows/deploy-app.yml
    with:
      environment: staging
      app-name: web
    secrets:
      DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}

  production:
    needs: staging
    uses: ./.github/workflows/deploy-app.yml
    with:
      environment: production
      app-name: web
    secrets:
      DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
```

## Composite Action

```yaml
# .github/actions/setup-node-pnpm/action.yml
name: Setup Node + pnpm
description: Install Node.js and pnpm with caching

inputs:
  node-version:
    description: Node.js version
    default: "20"

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
```

## Change Detection for Monorepo

```yaml
jobs:
  changes:
    runs-on: ubuntu-latest
    outputs:
      web: ${{ steps.filter.outputs.web }}
      api: ${{ steps.filter.outputs.api }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            web:
              - 'apps/web/**'
              - 'packages/ui/**'
            api:
              - 'apps/api/**'
              - 'packages/db/**'

  deploy-web:
    needs: changes
    if: needs.changes.outputs.web == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying web app"

  deploy-api:
    needs: changes
    if: needs.changes.outputs.api == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying API"
```

## Security Best Practices

```
RULE                                    WHY
──────────────────────────────────────────────────────
Pin action versions with SHA            Prevent supply chain attacks
Use OIDC instead of long-lived keys     No secrets to rotate
Limit permissions to minimum            Principle of least privilege
Use environments with approvals         Gate production deploys
Never echo secrets                      Prevent log exposure
Use concurrency groups                  Prevent duplicate runs
```

## Additional Resources

- GitHub Actions docs: https://docs.github.com/en/actions
- Reusable workflows: https://docs.github.com/en/actions/using-workflows/reusing-workflows
- OIDC: https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect
