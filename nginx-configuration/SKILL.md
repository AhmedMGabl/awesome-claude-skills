---
name: nginx-configuration
description: Nginx web server configuration covering reverse proxy setup, SSL/TLS with Let's Encrypt, load balancing algorithms, caching, gzip compression, security headers, rate limiting, WebSocket proxying, static file serving, and Docker-based deployment patterns.
---

# Nginx Configuration

This skill should be used when configuring Nginx as a reverse proxy, load balancer, or web server. It covers SSL, caching, security headers, and production deployment patterns.

## When to Use This Skill

Use this skill when you need to:

- Set up Nginx as a reverse proxy
- Configure SSL/TLS with Let's Encrypt
- Implement load balancing
- Add caching and compression
- Configure security headers
- Proxy WebSocket connections

## Reverse Proxy

```nginx
# /etc/nginx/sites-available/app.conf
upstream app_backend {
    server 127.0.0.1:3000;
    server 127.0.0.1:3001;
    keepalive 32;
}

server {
    listen 80;
    server_name app.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name app.example.com;

    # SSL
    ssl_certificate /etc/letsencrypt/live/app.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;

    # Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml;
    gzip_min_length 1000;
    gzip_comp_level 6;

    # Proxy to backend
    location / {
        proxy_pass http://app_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
        proxy_connect_timeout 5s;
        proxy_read_timeout 60s;
    }

    # WebSocket proxy
    location /ws {
        proxy_pass http://app_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 3600s;
    }

    # Static files with caching
    location /static/ {
        alias /var/www/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # API rate limiting
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://app_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Load Balancing

```nginx
# Round-robin (default)
upstream backend {
    server 10.0.0.1:3000;
    server 10.0.0.2:3000;
    server 10.0.0.3:3000;
}

# Least connections
upstream backend_lc {
    least_conn;
    server 10.0.0.1:3000;
    server 10.0.0.2:3000;
}

# IP hash (sticky sessions)
upstream backend_sticky {
    ip_hash;
    server 10.0.0.1:3000;
    server 10.0.0.2:3000;
}

# Weighted distribution
upstream backend_weighted {
    server 10.0.0.1:3000 weight=5;  # Gets 5x traffic
    server 10.0.0.2:3000 weight=1;
}

# Health checks
upstream backend_health {
    server 10.0.0.1:3000 max_fails=3 fail_timeout=30s;
    server 10.0.0.2:3000 max_fails=3 fail_timeout=30s;
    server 10.0.0.3:3000 backup;  # Only used when others fail
}
```

## Caching

```nginx
# Proxy cache configuration
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=app_cache:10m
    max_size=1g inactive=60m use_temp_path=off;

server {
    location /api/ {
        proxy_cache app_cache;
        proxy_cache_valid 200 10m;
        proxy_cache_valid 404 1m;
        proxy_cache_key "$scheme$request_method$host$request_uri";
        proxy_cache_use_stale error timeout updating http_500 http_502;
        add_header X-Cache-Status $upstream_cache_status;

        # Skip cache for authenticated requests
        proxy_cache_bypass $http_authorization;
        proxy_no_cache $http_authorization;

        proxy_pass http://app_backend;
    }
}
```

## Rate Limiting

```nginx
# Define rate limit zones (in http block)
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=api:10m rate=30r/s;
limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

# Connection limits
limit_conn_zone $binary_remote_addr zone=addr:10m;

server {
    # General pages
    location / {
        limit_req zone=general burst=20 nodelay;
        limit_conn addr 10;
    }

    # API endpoints
    location /api/ {
        limit_req zone=api burst=50 nodelay;
        limit_req_status 429;
    }

    # Login — strict
    location /api/auth/login {
        limit_req zone=login burst=3;
        limit_req_status 429;
    }
}
```

## Let's Encrypt with Certbot

```bash
# Install certbot
apt install certbot python3-certbot-nginx

# Obtain certificate
certbot --nginx -d app.example.com -d www.app.example.com

# Auto-renewal (crontab)
# 0 3 * * * certbot renew --quiet --post-hook "systemctl reload nginx"

# Test configuration
nginx -t && systemctl reload nginx
```

## Docker Compose with Nginx

```yaml
# docker-compose.yml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - static_files:/var/www/static:ro
    depends_on:
      - app
    restart: unless-stopped

  app:
    build: .
    expose:
      - "3000"
    environment:
      - NODE_ENV=production
    restart: unless-stopped
```

## Additional Resources

- Nginx docs: https://nginx.org/en/docs/
- Mozilla SSL Config Generator: https://ssl-config.mozilla.org/
- Certbot: https://certbot.eff.org/
- Nginx Amplify (monitoring): https://amplify.nginx.com/
