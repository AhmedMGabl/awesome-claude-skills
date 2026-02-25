---
name: vault-secrets
description: HashiCorp Vault patterns covering secret engines, dynamic secrets, authentication methods, policies, transit encryption, PKI certificates, and Kubernetes integration.
---

# HashiCorp Vault Secrets

This skill should be used when managing secrets with HashiCorp Vault. It covers secret engines, dynamic secrets, authentication, policies, transit encryption, and Kubernetes integration.

## When to Use This Skill

Use this skill when you need to:

- Store and retrieve secrets securely
- Generate dynamic database credentials
- Encrypt data with the transit engine
- Manage PKI certificates
- Integrate Vault with Kubernetes

## KV Secrets Engine

```bash
# Enable KV v2
vault secrets enable -path=secret kv-v2

# Write secrets
vault kv put secret/myapp/config \
    db_host=postgres.example.com \
    db_user=myapp \
    db_password=supersecret \
    api_key=abc123

# Read secrets
vault kv get secret/myapp/config
vault kv get -field=db_password secret/myapp/config
vault kv get -format=json secret/myapp/config

# List secrets
vault kv list secret/myapp/

# Delete
vault kv delete secret/myapp/config

# Version history
vault kv get -version=2 secret/myapp/config
vault kv rollback -version=1 secret/myapp/config
```

## Dynamic Database Secrets

```bash
# Enable database engine
vault secrets enable database

# Configure PostgreSQL connection
vault write database/config/mydb \
    plugin_name=postgresql-database-plugin \
    allowed_roles="readonly,readwrite" \
    connection_url="postgresql://{{username}}:{{password}}@postgres:5432/mydb?sslmode=disable" \
    username="vault_admin" \
    password="admin_password"

# Create readonly role
vault write database/roles/readonly \
    db_name=mydb \
    creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
    default_ttl="1h" \
    max_ttl="24h"

# Generate credentials
vault read database/creds/readonly
# Returns: username, password (auto-expires)
```

## Authentication Methods

```bash
# AppRole (for applications)
vault auth enable approle

vault write auth/approle/role/myapp \
    secret_id_ttl=10m \
    token_ttl=20m \
    token_max_ttl=30m \
    policies="myapp-policy"

ROLE_ID=$(vault read -field=role_id auth/approle/role/myapp/role-id)
SECRET_ID=$(vault write -f -field=secret_id auth/approle/role/myapp/secret-id)

vault write auth/approle/login role_id=$ROLE_ID secret_id=$SECRET_ID

# Kubernetes auth
vault auth enable kubernetes

vault write auth/kubernetes/config \
    kubernetes_host="https://kubernetes.default.svc"

vault write auth/kubernetes/role/myapp \
    bound_service_account_names=myapp \
    bound_service_account_namespaces=default \
    policies=myapp-policy \
    ttl=1h
```

## Policies

```hcl
# myapp-policy.hcl
path "secret/data/myapp/*" {
  capabilities = ["read", "list"]
}

path "database/creds/readonly" {
  capabilities = ["read"]
}

path "transit/encrypt/myapp" {
  capabilities = ["update"]
}

path "transit/decrypt/myapp" {
  capabilities = ["update"]
}
```

```bash
vault policy write myapp-policy myapp-policy.hcl
```

## Transit Encryption

```bash
# Enable transit engine
vault secrets enable transit

# Create encryption key
vault write -f transit/keys/myapp

# Encrypt data
vault write transit/encrypt/myapp \
    plaintext=$(echo -n "sensitive data" | base64)
# Returns: ciphertext

# Decrypt data
vault write transit/decrypt/myapp \
    ciphertext="vault:v1:..."
# Returns: plaintext (base64 encoded)

# Key rotation
vault write -f transit/keys/myapp/rotate
```

## Kubernetes Injection

```yaml
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
        vault.hashicorp.com/agent-inject-secret-config: "secret/data/myapp/config"
        vault.hashicorp.com/agent-inject-template-config: |
          {{- with secret "secret/data/myapp/config" -}}
          DB_HOST={{ .Data.data.db_host }}
          DB_USER={{ .Data.data.db_user }}
          DB_PASSWORD={{ .Data.data.db_password }}
          {{- end }}
    spec:
      serviceAccountName: myapp
      containers:
        - name: myapp
          image: myapp:latest
          volumeMounts:
            - name: vault-secrets
              mountPath: /vault/secrets
              readOnly: true
```

## Application Integration (Go)

```go
import vault "github.com/hashicorp/vault/api"

func getSecret(path string) (map[string]interface{}, error) {
    config := vault.DefaultConfig()
    client, err := vault.NewClient(config)
    if err != nil {
        return nil, err
    }

    secret, err := client.KVv2("secret").Get(context.Background(), path)
    if err != nil {
        return nil, err
    }

    return secret.Data, nil
}
```

## Additional Resources

- Vault: https://developer.hashicorp.com/vault/docs
- Tutorials: https://developer.hashicorp.com/vault/tutorials
- API: https://developer.hashicorp.com/vault/api-docs
