---
name: snyk-security
description: Snyk security patterns covering dependency scanning, container scanning, IaC testing, code analysis, license compliance, fix PRs, and CI/CD pipeline integration.
---

# Snyk Security

This skill should be used when securing applications with Snyk. It covers dependency scanning, container scanning, IaC testing, code analysis, license compliance, and CI/CD integration.

## When to Use This Skill

Use this skill when you need to:

- Scan dependencies for known vulnerabilities
- Test container images for security issues
- Analyze Infrastructure as Code for misconfigurations
- Enforce license compliance policies
- Automate security fixes with pull requests

## CLI Usage

```bash
# Install
npm install -g snyk

# Authenticate
snyk auth

# Test project dependencies
snyk test

# Test with severity threshold
snyk test --severity-threshold=high

# Monitor project (continuous scanning)
snyk monitor

# Test a specific package
snyk test express@4.18.0

# Test container image
snyk container test node:20-alpine

# Test IaC files
snyk iac test ./terraform/

# Code analysis
snyk code test
```

## Dependency Scanning

```bash
# Test and get JSON output
snyk test --json > snyk-results.json

# Test with specific package manager
snyk test --file=package-lock.json
snyk test --file=requirements.txt
snyk test --file=go.sum

# Ignore specific vulnerabilities
snyk ignore --id=SNYK-JS-EXAMPLE-123456 --expiry=2025-12-31 --reason="Not exploitable"

# Test all projects in monorepo
snyk test --all-projects
```

## Container Scanning

```bash
# Scan container image
snyk container test myapp:latest

# Scan with Dockerfile for better remediation
snyk container test myapp:latest --file=Dockerfile

# Get base image recommendations
snyk container test myapp:latest --file=Dockerfile --exclude-base-image-vulns

# Monitor container for new vulnerabilities
snyk container monitor myapp:latest --file=Dockerfile
```

## IaC Testing

```bash
# Test Terraform
snyk iac test ./terraform/main.tf

# Test Kubernetes manifests
snyk iac test ./k8s/deployment.yaml

# Test with custom rules
snyk iac test --rules=./custom-rules/

# Generate report
snyk iac test --json > iac-results.json
```

## CI/CD Integration

```yaml
# GitHub Actions
name: Snyk Security
on: [push, pull_request]

jobs:
  snyk:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Snyk to check for vulnerabilities
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high

      - name: Run Snyk container scan
        uses: snyk/actions/docker@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          image: myapp:${{ github.sha }}
          args: --severity-threshold=high

      - name: Run Snyk IaC test
        uses: snyk/actions/iac@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

## .snyk Policy File

```yaml
# .snyk
version: v1.25.0
ignore:
  SNYK-JS-EXAMPLE-123456:
    - '*':
        reason: 'Not exploitable in our context'
        expires: 2025-12-31T00:00:00.000Z
        created: 2025-01-01T00:00:00.000Z
patch: {}
```

## Additional Resources

- Snyk Docs: https://docs.snyk.io/
- Snyk CLI: https://docs.snyk.io/snyk-cli
- Vulnerability DB: https://security.snyk.io/
