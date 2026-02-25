---
name: docker-kubernetes
description: Docker and Kubernetes production deployment covering multi-stage Dockerfiles, Docker Compose services, Kubernetes Deployments, Services, Ingress, ConfigMaps, Secrets, Helm charts, horizontal pod autoscaling, health checks, and CI/CD deployment pipelines.
---

# Docker & Kubernetes Production

This skill should be used when deploying containerized applications to production. It covers Docker best practices, Kubernetes resources, Helm charts, and deployment strategies.

## When to Use This Skill

Use this skill when you need to:

- Build production-ready Docker images
- Deploy applications to Kubernetes
- Set up Helm charts for templated deployments
- Configure autoscaling and health checks
- Implement rolling updates and blue-green deployments

## Multi-Stage Dockerfile

```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

# Production stage
FROM node:20-alpine AS runner
WORKDIR /app
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
USER nextjs
EXPOSE 3000
ENV PORT=3000 HOSTNAME="0.0.0.0"
CMD ["node", "server.js"]
```

## Docker Compose

```yaml
# docker-compose.yml
services:
  app:
    build: .
    ports: ["3000:3000"]
    environment:
      DATABASE_URL: postgres://user:pass@db:5432/app
      REDIS_URL: redis://cache:6379
    depends_on:
      db: { condition: service_healthy }
      cache: { condition: service_started }
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 5s
      retries: 3

  db:
    image: postgres:16-alpine
    volumes: ["pgdata:/var/lib/postgresql/data"]
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d app"]
      interval: 10s
      timeout: 5s
      retries: 5

  cache:
    image: redis:7-alpine
    volumes: ["redisdata:/data"]

volumes:
  pgdata:
  redisdata:
```

## Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  labels:
    app: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: app
          image: registry.example.com/my-app:latest
          ports:
            - containerPort: 3000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: app-secrets
                  key: database-url
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
          readinessProbe:
            httpGet:
              path: /api/health
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /api/health
              port: 3000
            initialDelaySeconds: 15
            periodSeconds: 20
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

## Service + Ingress

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app
spec:
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 3000
  type: ClusterIP
---
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts: [app.example.com]
      secretName: app-tls
  rules:
    - host: app.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-app
                port:
                  number: 80
```

## HPA (Autoscaling)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

## Helm Chart Values

```yaml
# values.yaml
replicaCount: 3
image:
  repository: registry.example.com/my-app
  tag: "1.0.0"
  pullPolicy: IfNotPresent
service:
  type: ClusterIP
  port: 80
ingress:
  enabled: true
  hosts:
    - host: app.example.com
      paths: ["/"]
resources:
  requests: { cpu: 100m, memory: 128Mi }
  limits: { cpu: 500m, memory: 512Mi }
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
```

## Useful Commands

```bash
# Docker
docker build -t my-app .
docker compose up -d
docker compose logs -f app

# Kubernetes
kubectl apply -f k8s/
kubectl get pods -l app=my-app
kubectl rollout status deployment/my-app
kubectl rollout undo deployment/my-app
helm install my-app ./chart --values values.yaml
helm upgrade my-app ./chart --values values.yaml
```

## Additional Resources

- Kubernetes docs: https://kubernetes.io/docs/
- Helm docs: https://helm.sh/docs/
- Docker best practices: https://docs.docker.com/build/building/best-practices/
