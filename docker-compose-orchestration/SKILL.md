---
name: docker-compose-orchestration
description: This skill should be used when setting up multi-container Docker applications, development environments, service orchestration, or production deployments using Docker Compose.
---

# Docker Compose Orchestration

Complete guide for building multi-container applications with Docker Compose.

## When to Use This Skill

- Set up development environments with multiple services
- Orchestrate microservices locally
- Define service dependencies and startup order
- Configure networks and volumes
- Create production-ready compose files
- Build full-stack development stacks
- Deploy multi-container applications

## Installation

```bash
# Install Docker Desktop (includes Compose)
# https://docs.docker.com/get-docker/

# Verify installation
docker compose version
```

## Basic Structure

### Minimal docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
```

### Complete Example

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://db:5432/myapp
    volumes:
      - .:/app
      - /app/node_modules
    depends_on:
      - db
      - redis
    networks:
      - app-network

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    networks:
      - app-network

volumes:
  postgres-data:

networks:
  app-network:
    driver: bridge
```

## Common Commands

```bash
# Start services
docker compose up

# Start in background
docker compose up -d

# Build and start
docker compose up --build

# Stop services
docker compose down

# Stop and remove volumes
docker compose down -v

# View logs
docker compose logs

# Follow logs for specific service
docker compose logs -f app

# List running services
docker compose ps

# Execute command in service
docker compose exec app sh

# Scale service
docker compose up -d --scale worker=3

# Restart service
docker compose restart app
```

## Development Environments

### Node.js + MongoDB + Redis

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - MONGO_URL=mongodb://mongo:27017/myapp
      - REDIS_URL=redis://redis:6379
    volumes:
      - .:/app
      - /app/node_modules
    command: npm run dev
    depends_on:
      - mongo
      - redis

  mongo:
    image: mongo:6
    ports:
      - "27017:27017"
    volumes:
      - mongo-data:/data/db
    environment:
      - MONGO_INITDB_DATABASE=myapp

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

volumes:
  mongo-data:
  redis-data:
```

### Python FastAPI + PostgreSQL

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/myapi
    volumes:
      - .:/app
    command: uvicorn main:app --host 0.0.0.0 --reload
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=myapi
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres-data:
```

### React + Node.js + MySQL

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - REACT_APP_API_URL=http://localhost:4000

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    ports:
      - "4000:4000"
    environment:
      - DATABASE_HOST=mysql
      - DATABASE_PORT=3306
      - DATABASE_NAME=myapp
      - DATABASE_USER=root
      - DATABASE_PASSWORD=password
    volumes:
      - ./backend:/app
      - /app/node_modules
    depends_on:
      mysql:
        condition: service_healthy

  mysql:
    image: mysql:8
    environment:
      - MYSQL_ROOT_PASSWORD=password
      - MYSQL_DATABASE=myapp
    ports:
      - "3306:3306"
    volumes:
      - mysql-data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 5s
      timeout: 5s
      retries: 10

volumes:
  mysql-data:
```

## Service Dependencies

### depends_on with Conditions

```yaml
services:
  app:
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
      migration:
        condition: service_completed_successfully

  db:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready"]
      interval: 10s
      timeout: 5s
      retries: 5

  migration:
    command: npm run migrate
    restart: on-failure
```

### Wait-for Scripts

```yaml
services:
  app:
    command: sh -c "
      ./wait-for-it.sh db:5432 --timeout=60 --strict &&
      npm start"
    depends_on:
      - db
```

## Networks

### Custom Networks

```yaml
services:
  frontend:
    networks:
      - frontend-network

  backend:
    networks:
      - frontend-network
      - backend-network

  db:
    networks:
      - backend-network

networks:
  frontend-network:
    driver: bridge
  backend-network:
    driver: bridge
    internal: true  # No external access
```

### Network Aliases

```yaml
services:
  app:
    networks:
      app-network:
        aliases:
          - api
          - api.local

networks:
  app-network:
```

## Volumes

### Named Volumes

```yaml
services:
  db:
    volumes:
      - db-data:/var/lib/postgresql/data
      - db-logs:/var/log/postgresql

volumes:
  db-data:
    driver: local
  db-logs:
    driver: local
```

### Bind Mounts

```yaml
services:
  app:
    volumes:
      # Sync source code
      - ./src:/app/src:ro  # Read-only

      # Persist node_modules in container
      - /app/node_modules

      # Configuration files
      - ./config/app.yml:/app/config/app.yml:ro
```

### Volume Options

```yaml
volumes:
  db-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /mnt/data/postgres

  shared-data:
    driver: local
    driver_opts:
      type: nfs
      o: addr=192.168.1.100,rw
      device: ":/exports/shared"
```

## Environment Variables

### .env File

```env
# .env
NODE_ENV=development
API_PORT=4000
DATABASE_URL=postgresql://db:5432/myapp
REDIS_URL=redis://redis:6379
SECRET_KEY=your-secret-key
```

### Using in Compose

```yaml
services:
  app:
    environment:
      - NODE_ENV=${NODE_ENV}
      - API_PORT=${API_PORT}
      - DATABASE_URL=${DATABASE_URL}

  # Or load entire file
  app:
    env_file:
      - .env
      - .env.local
```

### Environment Substitution

```yaml
services:
  app:
    image: myapp:${TAG:-latest}
    ports:
      - "${API_PORT:-4000}:4000"
```

## Health Checks

```yaml
services:
  app:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  mysql:
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 5s
      timeout: 5s
      retries: 10
```

## Production Configurations

### Production docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    image: myapp:${TAG}
    restart: always
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=${DATABASE_URL}
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ssl-certs:/etc/ssl/certs:ro
    depends_on:
      - app

volumes:
  ssl-certs:
```

### Resource Limits

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### Restart Policies

```yaml
services:
  app:
    restart: always  # Always restart

  worker:
    restart: on-failure  # Only restart on failure

  migration:
    restart: no  # Never restart
```

## Complete Stacks

### MERN Stack

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:4000
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
    ports:
      - "4000:4000"
    environment:
      - MONGO_URL=mongodb://mongo:27017/myapp
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      mongo:
        condition: service_healthy
      redis:
        condition: service_started

  mongo:
    image: mongo:6
    ports:
      - "27017:27017"
    volumes:
      - mongo-data:/data/db
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

volumes:
  mongo-data:
  redis-data:
```

### WordPress + MySQL

```yaml
version: '3.8'

services:
  wordpress:
    image: wordpress:latest
    ports:
      - "8080:80"
    environment:
      - WORDPRESS_DB_HOST=mysql
      - WORDPRESS_DB_USER=wordpress
      - WORDPRESS_DB_PASSWORD=password
      - WORDPRESS_DB_NAME=wordpress
    volumes:
      - wordpress-data:/var/www/html
    depends_on:
      mysql:
        condition: service_healthy

  mysql:
    image: mysql:8
    environment:
      - MYSQL_DATABASE=wordpress
      - MYSQL_USER=wordpress
      - MYSQL_PASSWORD=password
      - MYSQL_ROOT_PASSWORD=rootpassword
    volumes:
      - mysql-data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 5s
      timeout: 5s
      retries: 10

volumes:
  wordpress-data:
  mysql-data:
```

### Microservices Architecture

```yaml
version: '3.8'

services:
  api-gateway:
    build: ./api-gateway
    ports:
      - "80:80"
    depends_on:
      - auth-service
      - user-service
      - order-service
    networks:
      - frontend
      - backend

  auth-service:
    build: ./services/auth
    environment:
      - JWT_SECRET=${JWT_SECRET}
      - DATABASE_URL=postgresql://postgres:password@auth-db:5432/auth
    depends_on:
      auth-db:
        condition: service_healthy
    networks:
      - backend

  user-service:
    build: ./services/users
    environment:
      - DATABASE_URL=postgresql://postgres:password@user-db:5432/users
    depends_on:
      user-db:
        condition: service_healthy
    networks:
      - backend

  order-service:
    build: ./services/orders
    environment:
      - DATABASE_URL=postgresql://postgres:password@order-db:5432/orders
      - REDIS_URL=redis://redis:6379
    depends_on:
      order-db:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - backend

  auth-db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=auth
      - POSTGRES_PASSWORD=password
    volumes:
      - auth-db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - backend

  user-db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=users
      - POSTGRES_PASSWORD=password
    volumes:
      - user-db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - backend

  order-db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=orders
      - POSTGRES_PASSWORD=password
    volumes:
      - order-db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - backend

  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
    networks:
      - backend

volumes:
  auth-db-data:
  user-db-data:
  order-db-data:
  redis-data:

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true
```

## Override Files

### docker-compose.override.yml (Auto-loaded)

```yaml
# Automatically merges with docker-compose.yml in development
version: '3.8'

services:
  app:
    volumes:
      - .:/app
    environment:
      - DEBUG=true
```

### docker-compose.prod.yml

```yaml
version: '3.8'

services:
  app:
    image: myapp:${TAG}
    restart: always
    deploy:
      replicas: 3

# Use with:
# docker compose -f docker-compose.yml -f docker-compose.prod.yml up
```

## Secrets Management

```yaml
version: '3.8'

services:
  app:
    image: myapp
    secrets:
      - db_password
      - api_key

secrets:
  db_password:
    file: ./secrets/db_password.txt
  api_key:
    file: ./secrets/api_key.txt
```

## Logging

```yaml
services:
  app:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  api:
    logging:
      driver: "syslog"
      options:
        syslog-address: "tcp://192.168.1.100:514"

  worker:
    logging:
      driver: "fluentd"
      options:
        fluentd-address: localhost:24224
        tag: "worker"
```

## Best Practices

### Development

✅ Use bind mounts for source code
✅ Enable hot reload
✅ Expose debugging ports
✅ Use lightweight images (alpine)
✅ Keep node_modules in container
✅ Use .dockerignore

### Production

✅ Use specific image tags (not :latest)
✅ Set resource limits
✅ Configure restart policies
✅ Use health checks
✅ Implement logging
✅ Use secrets for sensitive data
✅ Enable TLS/SSL
✅ Use multi-stage builds
✅ Run as non-root user

### Performance

✅ Use build cache effectively
✅ Minimize layer count
✅ Order layers by change frequency
✅ Use .dockerignore
✅ Multi-stage builds
✅ Alpine images where possible

## Troubleshooting

```bash
# View logs
docker compose logs
docker compose logs -f service-name

# Inspect service
docker compose exec service-name sh

# Check configuration
docker compose config

# Validate compose file
docker compose config --quiet

# Remove everything
docker compose down -v --remove-orphans

# Rebuild from scratch
docker compose build --no-cache
docker compose up --force-recreate
```

## Common Issues

**Port already in use**:
```bash
# Change port in compose file or find process
lsof -i :3000
kill -9 PID
```

**Volume permissions**:
```yaml
services:
  app:
    user: "${UID}:${GID}"
    volumes:
      - .:/app
```

**Service won't start**:
```bash
# Check logs
docker compose logs service-name

# Check if healthy
docker compose ps
```

## Resources

- Docker Compose Docs: https://docs.docker.com/compose/
- Compose File Reference: https://docs.docker.com/compose/compose-file/
- Docker Hub: https://hub.docker.com/
