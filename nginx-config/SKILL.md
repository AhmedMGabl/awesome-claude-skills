---
name: nginx-config
description: Nginx configuration patterns covering reverse proxy, load balancing, SSL/TLS, caching, rate limiting, security headers, WebSocket proxying, and performance tuning.
---

# Nginx Configuration

This skill should be used when configuring Nginx as a web server or reverse proxy. It covers reverse proxy, load balancing, SSL, caching, rate limiting, and security.

## When to Use This Skill

Use this skill when you need to:

- Configure Nginx as a reverse proxy
- Set up SSL/TLS termination
- Implement load balancing
- Add caching, rate limiting, and security headers
- Proxy WebSocket connections

## Basic Reverse Proxy

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## SSL/TLS Configuration

```nginx
server {
    listen 80;
    server_name example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # HSTS
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Load Balancing

```nginx
upstream backend {
    least_conn;
    server 10.0.0.1:3000 weight=3;
    server 10.0.0.2:3000 weight=2;
    server 10.0.0.3:3000 backup;

    keepalive 32;
}

server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }
}
```

## Caching

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=app_cache:10m max_size=1g inactive=60m;

server {
    listen 80;
    server_name example.com;

    location /api/ {
        proxy_pass http://localhost:3000;
        proxy_cache app_cache;
        proxy_cache_valid 200 10m;
        proxy_cache_valid 404 1m;
        proxy_cache_key $scheme$request_method$host$request_uri;
        add_header X-Cache-Status $upstream_cache_status;
    }

    location /static/ {
        root /var/www;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
}
```

## Rate Limiting

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=login_limit:10m rate=1r/s;

server {
    listen 80;
    server_name example.com;

    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        proxy_pass http://localhost:3000;
    }

    location /api/auth/login {
        limit_req zone=login_limit burst=5;
        proxy_pass http://localhost:3000;
    }
}
```

## Security Headers

```nginx
server {
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self'" always;
    add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;

    # Hide server version
    server_tokens off;
}
```

## WebSocket Proxy

```nginx
location /ws/ {
    proxy_pass http://localhost:3000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_read_timeout 86400;
}
```

## Gzip Compression

```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_proxied any;
gzip_comp_level 6;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript image/svg+xml;
```

## Commands

```bash
nginx -t                  # test configuration
nginx -s reload           # reload config
nginx -s stop             # stop server
nginx -T                  # dump full config
```

## Additional Resources

- Nginx: https://nginx.org/en/docs/
- Reverse Proxy: https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/
- Security: https://docs.nginx.com/nginx/admin-guide/security-controls/
