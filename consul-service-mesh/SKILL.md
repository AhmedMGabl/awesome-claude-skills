---
name: consul-service-mesh
description: HashiCorp Consul patterns covering service discovery, health checks, KV store, service mesh, intentions, prepared queries, and multi-datacenter configuration.
---

# Consul Service Mesh

This skill should be used when implementing service discovery and mesh with HashiCorp Consul. It covers service registration, health checks, KV store, intentions, and multi-datacenter setups.

## When to Use This Skill

Use this skill when you need to:

- Register and discover services dynamically
- Implement service mesh with mTLS
- Use KV store for distributed configuration
- Define service-to-service access with intentions
- Set up multi-datacenter service discovery

## Service Registration

```hcl
# consul.d/web-service.hcl
service {
  name = "web"
  port = 8080
  tags = ["v1", "production"]

  meta {
    version = "1.2.0"
    environment = "production"
  }

  check {
    http     = "http://localhost:8080/health"
    interval = "10s"
    timeout  = "3s"
  }

  connect {
    sidecar_service {
      proxy {
        upstreams {
          destination_name = "api"
          local_bind_port  = 9091
        }
        upstreams {
          destination_name = "cache"
          local_bind_port  = 9092
        }
      }
    }
  }
}
```

## Service Discovery (API)

```typescript
import Consul from "consul";

const consul = new Consul({ host: "127.0.0.1", port: 8500 });

// Register service
await consul.agent.service.register({
  name: "api-server",
  port: 3000,
  tags: ["v2"],
  check: {
    http: "http://localhost:3000/health",
    interval: "10s",
  },
});

// Discover services
const services = await consul.health.service({ service: "api-server", passing: true });
for (const entry of services) {
  const { Address, Port } = entry.Service;
  console.log(`Found: ${Address}:${Port}`);
}

// Watch for changes
const watcher = consul.watch({
  method: consul.health.service,
  options: { service: "api-server", passing: true },
});

watcher.on("change", (data) => {
  console.log("Services changed:", data.length);
});
```

## KV Store

```typescript
// Write key
await consul.kv.set("config/database/host", "db.example.com");
await consul.kv.set("config/database/port", "5432");

// Read key
const result = await consul.kv.get("config/database/host");
console.log(Buffer.from(result.Value, "base64").toString());

// List keys by prefix
const keys = await consul.kv.keys("config/");

// Watch for changes
const kvWatcher = consul.watch({
  method: consul.kv.get,
  options: { key: "config/feature-flags" },
});

kvWatcher.on("change", (data) => {
  const flags = JSON.parse(Buffer.from(data.Value, "base64").toString());
  updateFeatureFlags(flags);
});
```

## Service Intentions

```hcl
# Allow web to call api
Kind = "service-intentions"
Name = "api"
Sources = [
  {
    Name   = "web"
    Action = "allow"
  },
  {
    Name   = "admin"
    Action = "allow"
  },
  {
    Name   = "*"
    Action = "deny"
  }
]
```

## Server Configuration

```hcl
# consul.d/server.hcl
datacenter = "dc1"
data_dir   = "/opt/consul/data"
server     = true

bootstrap_expect = 3

ui_config {
  enabled = true
}

connect {
  enabled = true
}

addresses {
  http = "0.0.0.0"
}

retry_join = ["consul-server-1", "consul-server-2", "consul-server-3"]
```

## Docker Compose

```yaml
services:
  consul:
    image: hashicorp/consul:1.18
    ports:
      - "8500:8500"
      - "8600:8600/udp"
    command: agent -server -bootstrap-expect=1 -ui -client=0.0.0.0
    volumes:
      - consul-data:/consul/data
      - ./consul.d:/consul/config

volumes:
  consul-data:
```

## Additional Resources

- Consul: https://developer.hashicorp.com/consul/docs
- Service Mesh: https://developer.hashicorp.com/consul/docs/connect
- API: https://developer.hashicorp.com/consul/api-docs
