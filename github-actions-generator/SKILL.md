---
name: github-actions-generator
description: This skill should be used when users need to create, modify, or optimize GitHub Actions workflows for CI/CD, testing, deployment, or automation. Generates production-ready YAML workflows following GitHub Actions best practices.
---

# GitHub Actions Workflow Generator

Generate production-ready GitHub Actions workflows for CI/CD, testing, deployment, and automation tasks.

## When to Use This Skill

Use this skill when:
- User wants to create a new GitHub Actions workflow
- User mentions "CI/CD", "GitHub Actions", "workflow", or "automation"
- User asks to set up testing, deployment, or release automation
- User wants to optimize existing workflows
- User needs to add secrets, caching, or matrix strategies
- User mentions "continuous integration" or "continuous deployment"

## Key Features

### 1. Workflow Generation
- Creates properly formatted GitHub Actions YAML files
- Follows best practices and conventions
- Includes comprehensive comments
- Supports all major GitHub Actions features

### 2. Common Workflow Types
- **CI/CD Pipelines** - Test and deploy code
- **Testing Workflows** - Run unit, integration, E2E tests
- **Release Automation** - Create releases, changelogs, tags
- **Code Quality** - Linting, formatting, type checking
- **Security Scanning** - Dependency scanning, SAST, secrets detection
- **Documentation** - Generate and deploy docs
- **Scheduled Jobs** - Cron-based automation

### 3. Advanced Features
- Matrix strategies for multi-version testing
- Caching for faster builds
- Secrets and environment variables
- Conditional execution
- Reusable workflows
- Composite actions

## Workflow Templates

### Basic CI Workflow (Node.js)

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [18.x, 20.x, 22.x]

    steps:
    - uses: actions/checkout@v4

    - name: Setup Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Run linter
      run: npm run lint

    - name: Run tests
      run: npm test

    - name: Build
      run: npm run build
```

### Basic CI Workflow (Python)

```yaml
name: Python CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
        cache: 'pip'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run tests
      run: pytest --cov=. --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v4
      with:
        file: ./coverage.xml
```

### Docker Build and Push

```yaml
name: Docker Build

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
    - uses: actions/checkout@v4

    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}

    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: .
        push: ${{ github.event_name != 'pull_request' }}
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
```

### Release Automation

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Generate changelog
      id: changelog
      run: |
        # Generate changelog from git commits
        echo "CHANGELOG<<EOF" >> $GITHUB_OUTPUT
        git log $(git describe --tags --abbrev=0 HEAD^)..HEAD --pretty=format:"- %s (%h)" >> $GITHUB_OUTPUT
        echo "EOF" >> $GITHUB_OUTPUT

    - name: Create Release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ github.ref_name }}
        release_name: Release ${{ github.ref_name }}
        body: ${{ steps.changelog.outputs.CHANGELOG }}
        draft: false
        prerelease: false
```

### Security Scanning

```yaml
name: Security Scan

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write

    steps:
    - uses: actions/checkout@v4

    - name: Run Dependency Check
      uses: dependency-check/Dependency-Check_Action@main
      with:
        project: 'my-project'
        path: '.'
        format: 'SARIF'

    - name: Upload results
      uses: github/codeql-action/upload-sarif@v3
      with:
        sarif_file: dependency-check-report.sarif

  secret-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Gitleaks scan
      uses: gitleaks/gitleaks-action@v2
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Best Practices

### 1. Workflow Organization
- Place workflows in `.github/workflows/` directory
- Use descriptive names (ci.yml, deploy.yml, release.yml)
- Add clear comments explaining each step
- Group related jobs together

### 2. Performance Optimization
- Use caching for dependencies (npm, pip, cargo)
- Run jobs in parallel when possible
- Use matrix strategies for multi-version testing
- Cache Docker layers for faster builds

### 3. Security
- Never hardcode secrets in workflows
- Use `${{ secrets.SECRET_NAME }}` for sensitive data
- Limit permissions with `permissions:` key
- Pin action versions using commit SHA or specific tag

### 4. Debugging
- Add `ACTIONS_STEP_DEBUG: true` to secrets for debug logs
- Use `actions/upload-artifact@v4` to save build artifacts
- Add status badges to README

### 5. Reusability
- Create reusable workflows for common tasks
- Use composite actions for repeated step sequences
- Define environment variables at workflow level

## Common Patterns

### Conditional Execution

```yaml
steps:
  - name: Deploy to production
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    run: npm run deploy
```

### Using Secrets

```yaml
steps:
  - name: Deploy
    env:
      API_KEY: ${{ secrets.API_KEY }}
      DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
    run: ./deploy.sh
```

### Caching Dependencies

```yaml
# NPM
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'

# Pip
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: 'pip'

# Custom cache
- uses: actions/cache@v4
  with:
    path: ~/.cache/my-tool
    key: ${{ runner.os }}-my-tool-${{ hashFiles('**/lock-file') }}
```

### Manual Workflow Triggers

```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy to'
        required: true
        type: choice
        options:
          - staging
          - production
      version:
        description: 'Version to deploy'
        required: true
        type: string
```

## Troubleshooting

### Common Issues

**Workflow not triggering**:
- Check branch filters in `on:` section
- Verify workflow file is in `.github/workflows/`
- Ensure YAML syntax is valid

**Permission denied**:
- Add appropriate `permissions:` to job
- Check if workflow needs write access to packages/contents

**Cache not working**:
- Verify cache key is correct
- Check if cache size exceeds limit (10GB)
- Ensure restore-keys pattern matches

**Secrets not available**:
- Verify secret is defined in repository settings
- Check secret name matches exactly (case-sensitive)
- Ensure workflow has access to environment secrets

## Example Workflows by Use Case

### Continuous Integration
- Run tests on every push
- Lint code for style issues
- Check test coverage
- Build application

### Continuous Deployment
- Deploy to staging on develop branch
- Deploy to production on main branch
- Create releases on tags
- Update documentation

### Scheduled Tasks
- Generate weekly reports
- Clean up old artifacts
- Update dependencies
- Run security scans

### Pull Request Automation
- Run tests on PR
- Check for breaking changes
- Auto-assign reviewers
- Label PRs by type

## Integration with Other Tools

### Codecov
```yaml
- uses: codecov/codecov-action@v4
  with:
    token: ${{ secrets.CODECOV_TOKEN }}
    files: ./coverage.xml
```

### Slack Notifications
```yaml
- uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Deployment completed'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Terraform
```yaml
- uses: hashicorp/setup-terraform@v3
  with:
    terraform_version: 1.6.0
```

## References

- GitHub Actions Documentation: https://docs.github.com/en/actions
- Workflow Syntax: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions
- GitHub Actions Marketplace: https://github.com/marketplace?type=actions
- Security Hardening: https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions

---

## Usage Examples

**Example 1: Create Node.js CI Workflow**
```
User: "Create a GitHub Actions workflow for my Node.js project"

Claude will:
1. Ask about Node versions to test
2. Ask about package manager (npm/yarn/pnpm)
3. Ask if deployment is needed
4. Generate workflow with tests, linting, building
5. Save to .github/workflows/ci.yml
```

**Example 2: Add Docker Build**
```
User: "Add Docker build to my GitHub Actions"

Claude will:
1. Ask about registry (Docker Hub, GHCR, ECR)
2. Ask about image naming
3. Generate workflow with build and push
4. Set up proper authentication
```

**Example 3: Release Automation**
```
User: "Automate releases when I create tags"

Claude will:
1. Generate release workflow
2. Add changelog generation
3. Set up artifact uploading
4. Configure GitHub releases
```

---

**Created for**: awesome-claude-skills repository
**Version**: 1.0.0
**Last Updated**: January 25, 2026
