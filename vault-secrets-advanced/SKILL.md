---
name: vault-secrets-advanced
description: HashiCorp Vault advanced patterns covering dynamic secrets, PKI certificates, transit encryption, policies, auth methods, secret engines, and Kubernetes integration.
---

# Vault Secrets Advanced

This skill should be used when implementing advanced secrets management with HashiCorp Vault. It covers dynamic secrets, PKI, transit encryption, policies, and Kubernetes integration.

## When to Use This Skill

Use this skill when you need to:

- Generate dynamic database credentials
- Issue and manage PKI certificates
- Encrypt data with transit secret engine
- Define fine-grained access policies
- Integrate Vault with Kubernetes workloads

## Dynamic Database Secrets

```bash
# Enable database secrets engine
vault secrets enable database

# Configure PostgreSQL connection
vault write database/config/mydb \
  plugin_name=postgresql-database-plugin \
  connection_url="postgresql://{{username}}:{{password}}@db:5432/mydb" \
  allowed_roles="readonly,readwrite" \
  username="vault_admin" \
  password="vault_password"

# Create readonly role
vault write database/roles/readonly \
  db_name=mydb \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  default_ttl="1h" \
  max_ttl="24h"

# Generate credentials
vault read database/creds/readonly
```

## PKI Certificates

```bash
# Enable PKI
vault secrets enable pki
vault secrets tune -max-lease-ttl=87600h pki

# Generate root CA
vault write pki/root/generate/internal \
  common_name="Example Root CA" \
  ttl=87600h

# Enable intermediate PKI
vault secrets enable -path=pki_int pki
vault write pki_int/intermediate/generate/internal \
  common_name="Example Intermediate CA"

# Create role for issuing certs
vault write pki_int/roles/web-server \
  allowed_domains="example.com" \
  allow_subdomains=true \
  max_ttl="720h"

# Issue certificate
vault write pki_int/issue/web-server \
  common_name="api.example.com" \
  ttl="24h"
```

## Transit Encryption

```bash
# Enable transit
vault secrets enable transit

# Create encryption key
vault write -f transit/keys/my-app-key

# Encrypt data
vault write transit/encrypt/my-app-key \
  plaintext=$(echo -n "sensitive data" | base64)

# Decrypt data
vault write transit/decrypt/my-app-key \
  ciphertext="vault:v1:..."
```

```typescript
import Vault from "node-vault";

const vault = Vault({ endpoint: "http://127.0.0.1:8200", token: process.env.VAULT_TOKEN });

async function encrypt(plaintext: string): Promise<string> {
  const result = await vault.write("transit/encrypt/my-app-key", {
    plaintext: Buffer.from(plaintext).toString("base64"),
  });
  return result.data.ciphertext;
}

async function decrypt(ciphertext: string): Promise<string> {
  const result = await vault.write("transit/decrypt/my-app-key", { ciphertext });
  return Buffer.from(result.data.plaintext, "base64").toString();
}
```

## Policies

```hcl
# policies/app-policy.hcl
path "secret/data/myapp/*" {
  capabilities = ["read", "list"]
}

path "database/creds/readonly" {
  capabilities = ["read"]
}

path "transit/encrypt/my-app-key" {
  capabilities = ["update"]
}

path "transit/decrypt/my-app-key" {
  capabilities = ["update"]
}

path "pki_int/issue/web-server" {
  capabilities = ["create", "update"]
}
```

## Kubernetes Auth

```bash
# Enable Kubernetes auth
vault auth enable kubernetes

vault write auth/kubernetes/config \
  kubernetes_host="https://kubernetes.default.svc"

vault write auth/kubernetes/role/myapp \
  bound_service_account_names=myapp \
  bound_service_account_namespaces=default \
  policies=app-policy \
  ttl=1h
```

```yaml
# Vault Agent Injector annotations
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    metadata:
      annotations:
        vault.hashicorp.com/agent-inject: "true"
        vault.hashicorp.com/role: "myapp"
        vault.hashicorp.com/agent-inject-secret-db: "database/creds/readonly"
        vault.hashicorp.com/agent-inject-template-db: |
          {{- with secret "database/creds/readonly" -}}
          DATABASE_URL=postgresql://{{ .Data.username }}:{{ .Data.password }}@db:5432/mydb
          {{- end }}
    spec:
      serviceAccountName: myapp
      containers:
        - name: app
          image: myapp:latest
```

## Additional Resources

- Vault: https://developer.hashicorp.com/vault/docs
- Dynamic Secrets: https://developer.hashicorp.com/vault/docs/secrets/databases
- Transit: https://developer.hashicorp.com/vault/docs/secrets/transit
