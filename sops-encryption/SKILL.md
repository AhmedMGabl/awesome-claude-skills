---
name: sops-encryption
description: Mozilla SOPS patterns covering secret encryption, age/PGP/KMS key management, .sops.yaml configuration, CI/CD integration, Kubernetes secrets, and key rotation.
---

# SOPS Encryption

This skill should be used when managing encrypted secrets with Mozilla SOPS. It covers encryption, age/PGP/KMS keys, configuration, CI/CD integration, Kubernetes secrets, and key rotation.

## When to Use This Skill

Use this skill when you need to:

- Encrypt secrets in version control
- Manage encryption keys with age, PGP, or cloud KMS
- Configure per-path and per-environment encryption
- Integrate encrypted secrets into CI/CD pipelines
- Decrypt secrets for Kubernetes deployments

## Setup

```bash
# Install SOPS
brew install sops           # macOS
apt install sops            # Debian/Ubuntu

# Install age for key management
brew install age
age-keygen -o key.txt       # Generate key pair
```

## Basic Usage

```bash
# Encrypt a file
sops --encrypt --age age1... secrets.yaml > secrets.enc.yaml

# Decrypt a file
sops --decrypt secrets.enc.yaml > secrets.yaml

# Edit encrypted file in-place
sops secrets.enc.yaml       # Opens in $EDITOR, re-encrypts on save

# Encrypt specific keys only
sops --encrypt --encrypted-regex '^(password|api_key|secret)$' config.yaml > config.enc.yaml
```

## Configuration (.sops.yaml)

```yaml
# .sops.yaml
creation_rules:
  # Production uses AWS KMS
  - path_regex: environments/production/.*
    kms: arn:aws:kms:us-east-1:123456:key/abc-123
    encrypted_regex: "^(password|secret|key|token)$"

  # Staging uses age
  - path_regex: environments/staging/.*
    age: age1abc123...
    encrypted_regex: "^(password|secret|key|token)$"

  # Development uses local age key
  - path_regex: environments/dev/.*
    age: age1dev456...

  # Default rule
  - age: age1default789...
```

## Secrets File Structure

```yaml
# secrets.yaml (before encryption)
database:
  host: db.example.com        # Not encrypted (no match)
  password: super_secret_123   # Encrypted (matches regex)
  port: 5432                   # Not encrypted

api:
  key: sk_live_abc123          # Encrypted
  url: https://api.example.com # Not encrypted

jwt:
  secret: my_jwt_secret        # Encrypted
  expiry: 3600                 # Not encrypted
```

## Kubernetes Integration

```bash
# Decrypt and apply as Kubernetes secret
sops --decrypt secrets.enc.yaml | kubectl apply -f -

# Use with Helm
sops --decrypt values.enc.yaml > /tmp/values.yaml
helm upgrade --install myapp ./chart -f /tmp/values.yaml
rm /tmp/values.yaml

# Flux CD integration (built-in SOPS support)
# Place .sops.yaml in repo root
# Flux automatically decrypts on apply
```

```yaml
# Kubernetes secret template
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
stringData:
  DATABASE_PASSWORD: ENC[AES256_GCM,data:abc123...]
  API_KEY: ENC[AES256_GCM,data:def456...]
```

## CI/CD Integration

```yaml
# GitHub Actions
- name: Decrypt secrets
  env:
    SOPS_AGE_KEY: ${{ secrets.SOPS_AGE_KEY }}
  run: |
    sops --decrypt secrets.enc.yaml > secrets.yaml

# GitLab CI
decrypt:
  script:
    - export SOPS_AGE_KEY="$AGE_SECRET_KEY"
    - sops --decrypt secrets.enc.yaml > secrets.yaml
```

## Key Rotation

```bash
# Add new key to encrypted file
sops --rotate --add-age age1newkey... secrets.enc.yaml

# Remove old key
sops --rotate --rm-age age1oldkey... secrets.enc.yaml

# Rotate with multiple key types
sops --rotate \
  --add-kms arn:aws:kms:us-east-1:123:key/new-key \
  --rm-kms arn:aws:kms:us-east-1:123:key/old-key \
  secrets.enc.yaml
```

## Additional Resources

- SOPS GitHub: https://github.com/getsops/sops
- Age Encryption: https://github.com/FiloSottile/age
- SOPS + Flux: https://fluxcd.io/flux/guides/mozilla-sops/
