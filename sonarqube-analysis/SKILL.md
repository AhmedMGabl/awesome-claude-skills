---
name: sonarqube-analysis
description: SonarQube code analysis patterns covering quality gates, code smells, security hotspots, coverage reporting, custom rules, branch analysis, and CI/CD integration.
---

# SonarQube Analysis

This skill should be used when implementing code quality analysis with SonarQube. It covers quality gates, code smells, security hotspots, coverage, custom rules, and CI/CD integration.

## When to Use This Skill

Use this skill when you need to:

- Analyze code for bugs, vulnerabilities, and code smells
- Configure quality gates for merge requirements
- Review security hotspots and fix recommendations
- Track code coverage and duplication metrics
- Integrate analysis into CI/CD pipelines

## Project Configuration

```properties
# sonar-project.properties
sonar.projectKey=my-project
sonar.projectName=My Project
sonar.projectVersion=1.0

sonar.sources=src
sonar.tests=tests
sonar.sourceEncoding=UTF-8

# Language-specific settings
sonar.javascript.lcov.reportPaths=coverage/lcov.info
sonar.typescript.lcov.reportPaths=coverage/lcov.info
sonar.python.coverage.reportPaths=coverage.xml

# Exclusions
sonar.exclusions=**/*.test.ts,**/*.spec.ts,**/node_modules/**,**/dist/**
sonar.test.exclusions=**/node_modules/**
sonar.coverage.exclusions=**/*.test.ts,**/*.config.ts
```

## Scanner Usage

```bash
# Install scanner
npm install -g sonarqube-scanner

# Run analysis
sonar-scanner \
  -Dsonar.host.url=https://sonar.example.com \
  -Dsonar.token=$SONAR_TOKEN

# Docker scanner
docker run --rm \
  -e SONAR_HOST_URL="https://sonar.example.com" \
  -e SONAR_TOKEN="$SONAR_TOKEN" \
  -v "$(pwd):/usr/src" \
  sonarsource/sonar-scanner-cli

# With Gradle
./gradlew sonar \
  -Dsonar.host.url=https://sonar.example.com \
  -Dsonar.token=$SONAR_TOKEN

# With Maven
mvn sonar:sonar \
  -Dsonar.host.url=https://sonar.example.com \
  -Dsonar.token=$SONAR_TOKEN
```

## Quality Gate Configuration

```json
{
  "name": "Strict Quality Gate",
  "conditions": [
    { "metric": "new_reliability_rating", "op": "GT", "error": "1" },
    { "metric": "new_security_rating", "op": "GT", "error": "1" },
    { "metric": "new_maintainability_rating", "op": "GT", "error": "1" },
    { "metric": "new_coverage", "op": "LT", "error": "80" },
    { "metric": "new_duplicated_lines_density", "op": "GT", "error": "3" },
    { "metric": "new_security_hotspots_reviewed", "op": "LT", "error": "100" }
  ]
}
```

## CI/CD Integration

```yaml
# GitHub Actions
name: SonarQube Analysis
on: [push, pull_request]

jobs:
  sonarqube:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for blame

      - name: Install dependencies and test
        run: |
          npm ci
          npm test -- --coverage

      - name: SonarQube Scan
        uses: SonarSource/sonarqube-scan-action@master
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}

      - name: Quality Gate check
        uses: SonarSource/sonarqube-quality-gate-action@master
        timeout-minutes: 5
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

## Branch and PR Analysis

```properties
# Branch analysis
sonar.branch.name=${BRANCH_NAME}

# Pull request analysis
sonar.pullrequest.key=${PR_NUMBER}
sonar.pullrequest.branch=${PR_BRANCH}
sonar.pullrequest.base=${TARGET_BRANCH}
sonar.pullrequest.provider=GitHub
sonar.pullrequest.github.repository=owner/repo
```

## Additional Resources

- SonarQube Docs: https://docs.sonarsource.com/sonarqube/latest/
- SonarCloud: https://sonarcloud.io/
- Rules Explorer: https://rules.sonarsource.com/
