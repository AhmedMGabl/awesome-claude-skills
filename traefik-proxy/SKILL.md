---
name: traefik-proxy
description: Traefik proxy patterns covering Docker/Kubernetes integration, automatic service discovery, Let's Encrypt TLS, middleware chains, load balancing, and dashboard configuration.
---

# Traefik Proxy

This skill should be used when configuring Traefik as a reverse proxy and load balancer. It covers Docker/Kubernetes integration, service discovery, TLS, middleware, and dashboard.

## When to Use This Skill

Use this skill when you need to:

- Set up a reverse proxy with automatic service discovery
- Integrate with Docker or Kubernetes
- Configure automatic TLS with Let's Encrypt
- Add middleware for auth, rate limiting, and headers
- Monitor routing with the Traefik dashboard

## Static Configuration

```yaml
# traefik.yml
api:
  dashboard: true
  insecure: true  # disable in production

entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
  websecure:
    address: ":443"

certificatesResolvers:
  letsencrypt:
    acme:
      email: admin@example.com
      storage: /letsencrypt/acme.json
      httpChallenge:
        entryPoint: web

providers:
  docker:
    exposedByDefault: false
  file:
    directory: /etc/traefik/dynamic
    watch: true
```

## Docker Compose Integration

```yaml
# docker-compose.yml
services:
  traefik:
    image: traefik:v3.0
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik.yml:/etc/traefik/traefik.yml
      - letsencrypt:/letsencrypt

  webapp:
    image: myapp:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.webapp.rule=Host(`example.com`)"
      - "traefik.http.routers.webapp.entrypoints=websecure"
      - "traefik.http.routers.webapp.tls.certresolver=letsencrypt"
      - "traefik.http.services.webapp.loadbalancer.server.port=3000"

  api:
    image: myapi:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=Host(`api.example.com`)"
      - "traefik.http.routers.api.entrypoints=websecure"
      - "traefik.http.routers.api.tls.certresolver=letsencrypt"
      - "traefik.http.services.api.loadbalancer.server.port=4000"

volumes:
  letsencrypt:
```

## Middleware

```yaml
# dynamic/middleware.yml
http:
  middlewares:
    security-headers:
      headers:
        browserXssFilter: true
        contentTypeNosniff: true
        frameDeny: true
        stsIncludeSubdomains: true
        stsSeconds: 63072000

    rate-limit:
      rateLimit:
        average: 100
        burst: 50
        period: 1m

    basic-auth:
      basicAuth:
        users:
          - "admin:$apr1$hashed_password"

    compress:
      compress: {}

    redirect-www:
      redirectRegex:
        regex: "^https://www\\.(.*)"
        replacement: "https://${1}"
        permanent: true
```

## Docker Labels with Middleware

```yaml
services:
  webapp:
    image: myapp:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.webapp.rule=Host(`example.com`)"
      - "traefik.http.routers.webapp.entrypoints=websecure"
      - "traefik.http.routers.webapp.tls.certresolver=letsencrypt"
      - "traefik.http.routers.webapp.middlewares=security-headers@file,compress@file,rate-limit@file"
      - "traefik.http.services.webapp.loadbalancer.server.port=3000"
```

## Kubernetes IngressRoute

```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: myapp
  namespace: default
spec:
  entryPoints:
    - websecure
  routes:
    - match: Host(`example.com`)
      kind: Rule
      services:
        - name: myapp-service
          port: 80
      middlewares:
        - name: security-headers
  tls:
    certResolver: letsencrypt
---
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: security-headers
spec:
  headers:
    browserXssFilter: true
    contentTypeNosniff: true
    frameDeny: true
```

## File-Based Routing

```yaml
# dynamic/routes.yml
http:
  routers:
    webapp:
      rule: "Host(`example.com`)"
      entryPoints:
        - websecure
      service: webapp
      tls:
        certResolver: letsencrypt

    api:
      rule: "Host(`example.com`) && PathPrefix(`/api`)"
      entryPoints:
        - websecure
      service: api
      middlewares:
        - rate-limit
      tls:
        certResolver: letsencrypt

  services:
    webapp:
      loadBalancer:
        servers:
          - url: "http://10.0.0.1:3000"
          - url: "http://10.0.0.2:3000"
        healthCheck:
          path: /health
          interval: 10s

    api:
      loadBalancer:
        servers:
          - url: "http://10.0.0.3:4000"
```

## Additional Resources

- Traefik: https://doc.traefik.io/traefik/
- Docker: https://doc.traefik.io/traefik/providers/docker/
- Kubernetes: https://doc.traefik.io/traefik/providers/kubernetes-ingress/
