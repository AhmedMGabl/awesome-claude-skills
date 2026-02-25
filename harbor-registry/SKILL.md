---
name: harbor-registry
description: Harbor container registry patterns covering project management, vulnerability scanning, replication, robot accounts, RBAC, garbage collection, and CI/CD integration.
---

# Harbor Registry

This skill should be used when managing container images with Harbor. It covers projects, scanning, replication, robot accounts, RBAC, and CI/CD integration.

## When to Use This Skill

Use this skill when you need to:

- Host a private container registry
- Scan images for vulnerabilities
- Replicate images across registries
- Manage access with robot accounts and RBAC
- Integrate Harbor with CI/CD pipelines

## Docker Login

```bash
# Login to Harbor
docker login harbor.example.com -u admin -p Harbor12345

# Tag and push image
docker tag myapp:latest harbor.example.com/myproject/myapp:v1.0.0
docker push harbor.example.com/myproject/myapp:v1.0.0

# Pull image
docker pull harbor.example.com/myproject/myapp:v1.0.0
```

## Harbor API

```typescript
const HARBOR_URL = "https://harbor.example.com/api/v2.0";
const headers = {
  Authorization: `Basic ${Buffer.from("admin:Harbor12345").toString("base64")}`,
  "Content-Type": "application/json",
};

// Create project
await fetch(`${HARBOR_URL}/projects`, {
  method: "POST",
  headers,
  body: JSON.stringify({
    project_name: "myproject",
    metadata: {
      public: "false",
      auto_scan: "true",
    },
    storage_limit: 10 * 1024 * 1024 * 1024, // 10GB
  }),
});

// List repositories
const repos = await fetch(
  `${HARBOR_URL}/projects/myproject/repositories`,
  { headers }
).then((r) => r.json());

// List artifacts (tags)
const artifacts = await fetch(
  `${HARBOR_URL}/projects/myproject/repositories/myapp/artifacts`,
  { headers }
).then((r) => r.json());

// Get vulnerability report
const vulns = await fetch(
  `${HARBOR_URL}/projects/myproject/repositories/myapp/artifacts/v1.0.0/additions/vulnerabilities`,
  { headers }
).then((r) => r.json());
```

## Robot Accounts

```typescript
// Create robot account for CI/CD
await fetch(`${HARBOR_URL}/robots`, {
  method: "POST",
  headers,
  body: JSON.stringify({
    name: "ci-robot",
    duration: -1, // never expires
    level: "project",
    permissions: [
      {
        namespace: "myproject",
        kind: "project",
        access: [
          { resource: "repository", action: "push" },
          { resource: "repository", action: "pull" },
          { resource: "artifact", action: "read" },
        ],
      },
    ],
  }),
});
```

## Replication Rules

```typescript
// Create replication rule (push to remote)
await fetch(`${HARBOR_URL}/replication/policies`, {
  method: "POST",
  headers,
  body: JSON.stringify({
    name: "push-to-dr",
    src_registry: null, // local Harbor
    dest_registry: { id: 1 }, // pre-configured remote
    dest_namespace: "myproject",
    trigger: { type: "event_based" },
    filters: [
      { type: "name", value: "myproject/**" },
      { type: "tag", value: "v*" },
    ],
    enabled: true,
  }),
});
```

## CI/CD Integration (GitHub Actions)

```yaml
jobs:
  build-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Login to Harbor
        uses: docker/login-action@v3
        with:
          registry: harbor.example.com
          username: ${{ secrets.HARBOR_USER }}
          password: ${{ secrets.HARBOR_PASSWORD }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: harbor.example.com/myproject/myapp:${{ github.sha }}

      - name: Check vulnerability scan
        run: |
          sleep 30  # wait for scan
          VULNS=$(curl -s -H "Authorization: Basic ${{ secrets.HARBOR_AUTH }}" \
            "https://harbor.example.com/api/v2.0/projects/myproject/repositories/myapp/artifacts/${{ github.sha }}/additions/vulnerabilities")
          echo "$VULNS" | jq '.[]?.vulnerabilities | length'
```

## Docker Compose (Development)

```yaml
services:
  harbor:
    image: goharbor/harbor-core:v2.10
    # Note: For production, use the Harbor installer
    # https://goharbor.io/docs/latest/install-config/
```

## Additional Resources

- Harbor: https://goharbor.io/docs/
- API: https://editor.swagger.io/?url=https://raw.githubusercontent.com/goharbor/harbor/main/api/v2.0/swagger.yaml
- Installation: https://goharbor.io/docs/latest/install-config/
