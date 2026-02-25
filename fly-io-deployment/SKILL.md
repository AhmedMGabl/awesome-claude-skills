---
name: fly-io-deployment
description: Fly.io deployment covering fly launch, multi-region deployment, Postgres clusters, Redis, volume storage, autoscaling, health checks, secrets management, and CI/CD with GitHub Actions.
---

# Fly.io Deployment

This skill should be used when deploying applications on Fly.io. It covers app configuration, multi-region deployment, databases, volumes, autoscaling, and CI/CD.

## When to Use This Skill

Use this skill when you need to:

- Deploy containerized apps globally on Fly.io
- Set up multi-region Postgres and Redis
- Configure volume storage for persistent data
- Implement autoscaling and health checks
- Automate deployments with GitHub Actions

## Getting Started

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Launch a new app
fly launch

# Deploy
fly deploy
```

## fly.toml Configuration

```toml
# fly.toml
app = "my-app"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[env]
  NODE_ENV = "production"
  PORT = "8080"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = "stop"
  auto_start_machines = true
  min_machines_running = 1

  [http_service.concurrency]
    type = "requests"
    hard_limit = 250
    soft_limit = 200

[[http_service.checks]]
  grace_period = "10s"
  interval = "30s"
  method = "GET"
  path = "/health"
  timeout = "5s"

[[vm]]
  size = "shared-cpu-1x"
  memory = "512mb"
  cpu_kind = "shared"
  cpus = 1
```

## Multi-Region Deployment

```bash
# Add regions
fly regions add lhr sin syd

# Scale to multiple regions
fly scale count 3 --region iad,lhr,sin

# Check regions
fly regions list

# Primary region for writes, replicas for reads
fly postgres create --region iad --name my-db
fly postgres attach my-db
```

## Postgres

```bash
# Create cluster
fly postgres create \
  --name my-db \
  --region iad \
  --vm-size shared-cpu-1x \
  --initial-cluster-size 2

# Attach to app
fly postgres attach my-db

# Connect
fly postgres connect -a my-db

# Add read replicas
fly machine clone <machine-id> --region lhr -a my-db
```

## Redis (Upstash)

```bash
# Create managed Redis
fly redis create \
  --name my-redis \
  --region iad \
  --enable-eviction

# Get connection URL
fly redis status my-redis
```

## Volumes

```bash
# Create volume
fly volumes create data --region iad --size 10

# Mount in fly.toml
# [mounts]
#   source = "data"
#   destination = "/data"
```

```toml
[mounts]
  source = "data"
  destination = "/data"
```

## Secrets Management

```bash
# Set secrets
fly secrets set DATABASE_URL="postgres://..." SESSION_SECRET="..."

# List secrets
fly secrets list

# Unset
fly secrets unset OLD_SECRET
```

## Autoscaling

```toml
# In fly.toml
[http_service]
  auto_stop_machines = "stop"
  auto_start_machines = true
  min_machines_running = 1

[[vm]]
  size = "shared-cpu-1x"
  memory = "512mb"
```

```bash
# Manual scaling
fly scale count 3
fly scale vm shared-cpu-2x
fly scale memory 1024
```

## GitHub Actions CI/CD

```yaml
# .github/workflows/deploy.yml
name: Deploy to Fly.io
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

## Useful Commands

```bash
fly status              # App status
fly logs                # Stream logs
fly ssh console         # SSH into machine
fly dashboard           # Open web dashboard
fly monitor             # Real-time metrics
fly releases            # Deployment history
fly machine list        # List machines
fly machine restart     # Restart machines
```

## Additional Resources

- Fly.io docs: https://fly.io/docs/
- Fly.io Postgres: https://fly.io/docs/postgres/
- flyctl reference: https://fly.io/docs/flyctl/
