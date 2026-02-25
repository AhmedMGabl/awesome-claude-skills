---
name: trivy-scanning
description: Trivy security scanning patterns covering container image scanning, filesystem scanning, IaC misconfiguration detection, SBOM generation, and CI/CD integration.
---

# Trivy Security Scanning

This skill should be used when scanning for vulnerabilities with Trivy. It covers container images, filesystem scanning, IaC misconfigurations, SBOM generation, and CI/CD integration.

## When to Use This Skill

Use this skill when you need to:

- Scan container images for vulnerabilities
- Detect misconfigurations in IaC (Terraform, K8s)
- Generate Software Bill of Materials (SBOM)
- Scan filesystem dependencies for CVEs
- Integrate security scanning into CI/CD

## Container Image Scanning

```bash
# Scan a container image
trivy image nginx:latest

# Scan with severity filter
trivy image --severity CRITICAL,HIGH node:20-alpine

# Scan with specific output format
trivy image --format json --output results.json myapp:latest

# Scan with exit code for CI/CD (fail on HIGH+)
trivy image --exit-code 1 --severity HIGH,CRITICAL myapp:latest

# Scan private registry image
trivy image --username user --password pass registry.example.com/myapp:latest

# Ignore unfixed vulnerabilities
trivy image --ignore-unfixed nginx:latest
```

## Filesystem Scanning

```bash
# Scan project dependencies
trivy fs .

# Scan specific directory
trivy fs --scanners vuln,secret,misconfig ./src

# Scan for secrets in code
trivy fs --scanners secret .

# Skip specific directories
trivy fs --skip-dirs node_modules,vendor .
```

## IaC Scanning

```bash
# Scan Terraform files
trivy config ./terraform/

# Scan Kubernetes manifests
trivy config ./k8s/

# Scan Dockerfile
trivy config ./Dockerfile

# Scan Helm charts
trivy config ./helm/mychart/

# Custom severity threshold
trivy config --severity CRITICAL,HIGH ./terraform/
```

## SBOM Generation

```bash
# Generate CycloneDX SBOM
trivy image --format cyclonedx --output sbom.json myapp:latest

# Generate SPDX SBOM
trivy image --format spdx-json --output sbom.spdx.json myapp:latest

# Scan an existing SBOM
trivy sbom sbom.json
```

## CI/CD Integration

```yaml
# GitHub Actions
name: Security Scan
on: [push, pull_request]

jobs:
  trivy-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build image
        run: docker build -t myapp:${{ github.sha }} .

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: myapp:${{ github.sha }}
          format: sarif
          output: trivy-results.sarif
          severity: CRITICAL,HIGH

      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: trivy-results.sarif
```

```yaml
# GitLab CI
trivy-scan:
  stage: security
  image:
    name: aquasec/trivy:latest
    entrypoint: [""]
  script:
    - trivy image --exit-code 1 --severity CRITICAL $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  allow_failure: true
```

## Configuration File

```yaml
# trivy.yaml
severity:
  - CRITICAL
  - HIGH
  - MEDIUM

scan:
  security-checks:
    - vuln
    - misconfig
    - secret

vulnerability:
  type:
    - os
    - library
  ignore-unfixed: true

misconfig:
  severity:
    - CRITICAL
    - HIGH

db:
  skip-update: false
  java-db-update: true

cache:
  dir: /tmp/trivy-cache
```

## Ignore Rules

```yaml
# .trivyignore.yaml
vulnerabilities:
  - id: CVE-2023-12345
    statement: "Not exploitable in our configuration"
    expires: 2025-12-31

  - id: CVE-2023-67890
    paths:
      - "usr/lib/libexample.so"
    statement: "False positive, library not used"

misconfigurations:
  - id: AVD-DS-0002
    statement: "Running as root is required for this service"
```

## Additional Resources

- Trivy Docs: https://aquasecurity.github.io/trivy/
- Trivy GitHub: https://github.com/aquasecurity/trivy
- Trivy Operator: https://aquasecurity.github.io/trivy-operator/
