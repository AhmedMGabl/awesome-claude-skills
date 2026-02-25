---
name: coolify-selfhost
description: Coolify self-hosted PaaS covering server setup, application deployment from GitHub, database provisioning, environment variables, custom domains, SSL certificates, Docker Compose projects, and backup configuration.
---

# Coolify Self-Hosted PaaS

This skill should be used when deploying applications with Coolify, a self-hosted alternative to Vercel/Heroku. It covers server setup, app deployment, databases, and domain configuration.

## When to Use This Skill

Use this skill when you need to:

- Self-host applications on your own servers
- Deploy from GitHub repositories automatically
- Provision databases without managed services
- Configure custom domains and SSL
- Run Docker Compose projects

## Server Setup

```bash
# Install Coolify on a fresh VPS (Ubuntu/Debian)
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash

# Access dashboard at http://your-server-ip:8000
# Complete initial setup wizard
```

## Application Deployment

1. Connect GitHub repository in Coolify dashboard
2. Select branch and build pack (Nixpacks, Dockerfile, Docker Compose)
3. Configure build and start commands
4. Set environment variables
5. Deploy

## Nixpacks Configuration

```toml
# nixpacks.toml
[phases.setup]
nixPkgs = ["nodejs_20", "python3"]

[phases.install]
cmds = ["npm ci"]

[phases.build]
cmds = ["npm run build"]

[start]
cmd = "npm start"
```

## Docker Compose Deployment

```yaml
# docker-compose.yml
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - db

  db:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: myapp
      POSTGRES_PASSWORD: ${DB_PASSWORD}

volumes:
  pgdata:
```

## Database Provisioning

Coolify supports provisioning:
- PostgreSQL
- MySQL/MariaDB
- MongoDB
- Redis
- ClickHouse

Each database gets automatic backups when configured.

## Environment Variables

```
# Set in Coolify dashboard or via API
NODE_ENV=production
DATABASE_URL=postgresql://user:pass@db:5432/myapp
REDIS_URL=redis://redis:6379
SECRET_KEY=your-secret-key
```

## Custom Domain

1. Add domain in Coolify dashboard
2. Point DNS A record to your server IP
3. Coolify automatically provisions Let's Encrypt SSL
4. Supports wildcard domains with DNS challenge

## Backup Configuration

```yaml
# Coolify supports automated backups for databases
# Configure in dashboard:
# - Backup frequency (cron)
# - Retention period
# - S3-compatible storage destination
```

## API Access

```bash
# Coolify exposes a REST API
curl -H "Authorization: Bearer $COOLIFY_TOKEN" \
  https://coolify.example.com/api/v1/applications
```

## Additional Resources

- Coolify docs: https://coolify.io/docs
- Coolify GitHub: https://github.com/coollabsio/coolify
