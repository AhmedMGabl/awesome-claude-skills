---
name: security-scanning
description: This skill should be used when implementing security scanning for dependencies, static code analysis, secrets detection, vulnerability management, and security best practices in CI/CD pipelines.
---

# Security Scanning & Vulnerability Management

Complete guide for implementing security scanning in your development workflow and CI/CD pipelines.

## When to Use This Skill

- Scan dependencies for known vulnerabilities
- Detect secrets and credentials in code
- Perform static application security testing (SAST)
- Implement security gates in CI/CD
- Monitor and manage vulnerabilities
- Enforce security best practices

## Dependency Scanning

### Node.js
```bash
npm audit
npm audit fix
npm audit --audit-level=moderate

# Snyk
npm install -g snyk
snyk test
snyk monitor
```

### Python
```bash
pip install pip-audit safety
pip-audit
safety check
```

## Secrets Detection

### gitleaks
```bash
brew install gitleaks
gitleaks detect --source . --verbose
gitleaks protect --staged  # Pre-commit
```

### TruffleHog
```bash
pip install truffleHog
trufflehog git file://. --json
```

## SAST (Static Analysis)

### Semgrep
```bash
pip install semgrep
semgrep --config=auto .
semgrep --config=p/owasp-top-ten .
```

### CodeQL (GitHub)
```yaml
# .github/workflows/codeql.yml
name: CodeQL
on: [push, pull_request]
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: github/codeql-action/init@v2
        with:
          languages: javascript, python
      - uses: github/codeql-action/analyze@v2
```

## Container Security

### Trivy
```bash
brew install trivy
trivy image nginx:latest
trivy fs .
trivy config .
```

## CI/CD Integration

### Complete Security Pipeline
```yaml
# .github/workflows/security.yml
name: Security Scanning

on: [push, pull_request]

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm ci
      - run: npm audit --audit-level=moderate

  secrets-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2

  sast-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: returntocorp/semgrep-action@v1
        with:
          config: p/security-audit

  container-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: docker build -t myapp .
      - uses: aquasecurity/trivy-action@master
        with:
          image-ref: myapp
          severity: CRITICAL,HIGH
```

## Pre-commit Hooks

```bash
# .husky/pre-commit
#!/bin/sh
gitleaks protect --staged --verbose
npm audit --audit-level=high
```

## Common Vulnerabilities

### SQL Injection
```javascript
// Vulnerable
const query = `SELECT * FROM users WHERE id = ${userId}`;

// Safe
const query = 'SELECT * FROM users WHERE id = ?';
db.query(query, [userId]);
```

### XSS
```javascript
// Vulnerable
element.innerHTML = userInput;

// Safe
element.textContent = userInput;
```

### Command Injection
```javascript
// Vulnerable - DO NOT USE
const { exec } = require('child_process');
exec(`git log ${userInput}`);

// Safe - Use execFile
const { execFile } = require('child_process');
execFile('git', ['log', userInput]);
```

## Best Practices

✅ Scan dependencies regularly
✅ Use secrets detection in pre-commit
✅ Implement security gates in CI/CD
✅ Keep tools updated
✅ Monitor continuously
✅ Use .gitignore for secrets
✅ Apply security headers
✅ Follow principle of least privilege
✅ Use parameterized queries
✅ Sanitize user input
✅ Enable audit logging

## Tool Comparison

| Tool | Type | Best For |
|------|------|----------|
| npm audit | Dependencies | Node.js projects |
| Snyk | Dependencies | Multi-language |
| gitleaks | Secrets | Fast scanning |
| Semgrep | SAST | Custom rules |
| CodeQL | SAST | Deep analysis |
| Trivy | Container | Multi-purpose |

## Resources

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Snyk: https://snyk.io/
- Semgrep: https://semgrep.dev/
- Gitleaks: https://github.com/gitleaks/gitleaks
- Trivy: https://github.com/aquasecurity/trivy
