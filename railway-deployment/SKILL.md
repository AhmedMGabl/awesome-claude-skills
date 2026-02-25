---
name: railway-deployment
description: Railway deployment covering project setup, service configuration, Postgres and Redis provisioning, environment variables, custom domains, Nixpacks builds, health checks, cron jobs, and GitHub integration.
---

# Railway Deployment

This skill should be used when deploying applications on Railway. It covers project setup, databases, environment variables, custom domains, and CI/CD.

## When to Use This Skill

Use this skill when you need to:

- Deploy web apps and APIs on Railway
- Provision Postgres, Redis, or MySQL databases
- Configure custom domains and SSL
- Set up cron jobs and background workers
- Automate deployments from GitHub

## Project Setup

```bash
# Install CLI
npm install -g @railway/cli

# Login and initialize
railway login
railway init
railway link
```

## railway.toml Configuration

```toml
[build]
builder = "nixpacks"
buildCommand = "npm ci && npm run build"

[deploy]
startCommand = "npm start"
healthcheckPath = "/health"
healthcheckTimeout = 300
numReplicas = 1
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3

[deploy.cron]
# Optional cron service
schedule = "0 */6 * * *"
```

## Environment Variables

```bash
# Set variables
railway variables set NODE_ENV=production
railway variables set DATABASE_URL=${{Postgres.DATABASE_URL}}
railway variables set REDIS_URL=${{Redis.REDIS_URL}}

# Reference other services with template syntax
# ${{ServiceName.VARIABLE_NAME}}
```

## Database Provisioning

```bash
# Add Postgres
railway add --plugin postgresql

# Add Redis
railway add --plugin redis

# Connect to database locally
railway connect postgresql
```

## Custom Domains

```bash
# Add custom domain
railway domain

# The CLI provides CNAME record to configure in your DNS
```

## Dockerfile Deploy

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./
EXPOSE 8080
CMD ["node", "dist/index.js"]
```

## CLI Commands

```bash
railway up              # Deploy current directory
railway logs            # View logs
railway status          # Check deployment status
railway run <command>   # Run command with Railway env vars
railway shell           # Open shell with env vars
railway open            # Open project dashboard
```

## Additional Resources

- Railway docs: https://docs.railway.app/
- Railway templates: https://railway.app/templates
- Nixpacks: https://nixpacks.com/
