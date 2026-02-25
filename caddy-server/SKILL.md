---
name: caddy-server
description: Caddy server patterns covering automatic HTTPS, reverse proxy, file serving, load balancing, Caddyfile syntax, API configuration, and production deployment.
---

# Caddy Server

This skill should be used when configuring Caddy as a web server or reverse proxy. It covers automatic HTTPS, reverse proxy, file serving, load balancing, and Caddyfile syntax.

## When to Use This Skill

Use this skill when you need to:

- Set up a web server with automatic HTTPS
- Configure reverse proxy with Caddy
- Serve static files and SPAs
- Implement load balancing
- Use Caddyfile or JSON API configuration

## Basic Caddyfile

```caddyfile
example.com {
    reverse_proxy localhost:3000
}
```

Caddy automatically provisions and renews TLS certificates from Let's Encrypt.

## Reverse Proxy

```caddyfile
example.com {
    reverse_proxy localhost:3000 {
        header_up Host {host}
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
    }
}

# Multiple backends with load balancing
api.example.com {
    reverse_proxy {
        to localhost:3001 localhost:3002 localhost:3003
        lb_policy round_robin
        health_uri /health
        health_interval 10s
    }
}
```

## Static File Serving

```caddyfile
example.com {
    root * /var/www/html
    file_server

    # Enable compression
    encode gzip zstd

    # SPA fallback
    try_files {path} /index.html
}
```

## Path-Based Routing

```caddyfile
example.com {
    # API reverse proxy
    handle /api/* {
        reverse_proxy localhost:3000
    }

    # WebSocket
    handle /ws/* {
        reverse_proxy localhost:3000
    }

    # Static files
    handle {
        root * /var/www/html
        try_files {path} /index.html
        file_server
    }
}
```

## Headers and Security

```caddyfile
example.com {
    header {
        X-Frame-Options "SAMEORIGIN"
        X-Content-Type-Options "nosniff"
        X-XSS-Protection "1; mode=block"
        Referrer-Policy "strict-origin-when-cross-origin"
        -Server
    }

    reverse_proxy localhost:3000
}
```

## Rate Limiting

```caddyfile
example.com {
    rate_limit {
        zone api {
            key {remote_host}
            events 100
            window 1m
        }
    }

    reverse_proxy localhost:3000
}
```

## Redirects and Rewrites

```caddyfile
# HTTP to HTTPS (automatic, but explicit)
http://example.com {
    redir https://example.com{uri} permanent
}

# www redirect
www.example.com {
    redir https://example.com{uri} permanent
}

# Path redirect
example.com {
    redir /old-page /new-page permanent
    redir /blog/* /articles/{uri} permanent

    reverse_proxy localhost:3000
}
```

## Multiple Sites

```caddyfile
example.com {
    reverse_proxy localhost:3000
}

api.example.com {
    reverse_proxy localhost:4000
}

admin.example.com {
    basicauth {
        admin $2a$14$hashed_password
    }
    reverse_proxy localhost:5000
}
```

## Logging

```caddyfile
example.com {
    log {
        output file /var/log/caddy/access.log {
            roll_size 100mb
            roll_keep 5
        }
        format json
        level INFO
    }

    reverse_proxy localhost:3000
}
```

## Local Development

```caddyfile
:8080 {
    reverse_proxy localhost:3000
}

# With local HTTPS
localhost {
    reverse_proxy localhost:3000
}
```

## Commands

```bash
caddy run                      # start with Caddyfile
caddy run --config caddy.json  # start with JSON
caddy reload                   # reload config
caddy fmt --overwrite          # format Caddyfile
caddy validate                 # validate config
caddy adapt                    # convert Caddyfile to JSON
```

## Additional Resources

- Caddy: https://caddyserver.com/docs/
- Caddyfile: https://caddyserver.com/docs/caddyfile
- Modules: https://caddyserver.com/docs/modules/
