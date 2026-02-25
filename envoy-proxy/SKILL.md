---
name: envoy-proxy
description: Envoy proxy patterns covering listeners, clusters, routes, filters, rate limiting, circuit breaking, load balancing, and service mesh data plane configuration.
---

# Envoy Proxy

This skill should be used when configuring Envoy as an edge or service proxy. It covers listeners, clusters, routes, filters, rate limiting, circuit breaking, and load balancing.

## When to Use This Skill

Use this skill when you need to:

- Configure Envoy as a reverse proxy or API gateway
- Implement circuit breaking and rate limiting
- Set up load balancing strategies
- Use HTTP filters for routing and transformation
- Deploy Envoy as a service mesh sidecar

## Basic Configuration

```yaml
# envoy.yaml
static_resources:
  listeners:
    - name: main
      address:
        socket_address:
          address: 0.0.0.0
          port_value: 8080
      filter_chains:
        - filters:
            - name: envoy.filters.network.http_connection_manager
              typed_config:
                "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
                stat_prefix: ingress_http
                route_config:
                  name: local_route
                  virtual_hosts:
                    - name: backend
                      domains: ["*"]
                      routes:
                        - match:
                            prefix: "/api/v1"
                          route:
                            cluster: api_v1
                            timeout: 30s
                        - match:
                            prefix: "/api/v2"
                          route:
                            cluster: api_v2
                            timeout: 30s
                http_filters:
                  - name: envoy.filters.http.router
                    typed_config:
                      "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router

  clusters:
    - name: api_v1
      connect_timeout: 5s
      type: STRICT_DNS
      lb_policy: ROUND_ROBIN
      load_assignment:
        cluster_name: api_v1
        endpoints:
          - lb_endpoints:
              - endpoint:
                  address:
                    socket_address:
                      address: api-v1
                      port_value: 3000
    - name: api_v2
      connect_timeout: 5s
      type: STRICT_DNS
      lb_policy: ROUND_ROBIN
      load_assignment:
        cluster_name: api_v2
        endpoints:
          - lb_endpoints:
              - endpoint:
                  address:
                    socket_address:
                      address: api-v2
                      port_value: 3000
```

## Circuit Breaking

```yaml
clusters:
  - name: api_v1
    circuit_breakers:
      thresholds:
        - priority: DEFAULT
          max_connections: 100
          max_pending_requests: 50
          max_requests: 200
          max_retries: 3
          retry_budget:
            budget_percent:
              value: 20.0
            min_retry_concurrency: 3
    outlier_detection:
      consecutive_5xx: 5
      interval: 10s
      base_ejection_time: 30s
      max_ejection_percent: 50
```

## Rate Limiting

```yaml
http_filters:
  - name: envoy.filters.http.local_ratelimit
    typed_config:
      "@type": type.googleapis.com/envoy.extensions.filters.http.local_ratelimit.v3.LocalRateLimit
      stat_prefix: http_local_rate_limiter
      token_bucket:
        max_tokens: 100
        tokens_per_fill: 100
        fill_interval: 60s
      filter_enabled:
        runtime_key: local_rate_limit_enabled
        default_value:
          numerator: 100
          denominator: HUNDRED
```

## Header-Based Routing

```yaml
routes:
  - match:
      prefix: "/api"
      headers:
        - name: "x-api-version"
          string_match:
            exact: "v2"
    route:
      cluster: api_v2
  - match:
      prefix: "/api"
    route:
      cluster: api_v1
      retry_policy:
        retry_on: "5xx,connect-failure"
        num_retries: 3
        per_try_timeout: 5s
```

## TLS Termination

```yaml
listeners:
  - name: https
    address:
      socket_address:
        address: 0.0.0.0
        port_value: 443
    filter_chains:
      - transport_socket:
          name: envoy.transport_sockets.tls
          typed_config:
            "@type": type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.DownstreamTlsContext
            common_tls_context:
              tls_certificates:
                - certificate_chain:
                    filename: /etc/envoy/certs/server.crt
                  private_key:
                    filename: /etc/envoy/certs/server.key
        filters:
          - name: envoy.filters.network.http_connection_manager
            # ... same as above
```

## Docker Compose

```yaml
services:
  envoy:
    image: envoyproxy/envoy:v1.29-latest
    ports:
      - "8080:8080"
      - "9901:9901"
    volumes:
      - ./envoy.yaml:/etc/envoy/envoy.yaml
    command: -c /etc/envoy/envoy.yaml --service-cluster front-proxy
```

## Additional Resources

- Envoy: https://www.envoyproxy.io/docs/envoy/latest/
- Configuration: https://www.envoyproxy.io/docs/envoy/latest/configuration/
- xDS API: https://www.envoyproxy.io/docs/envoy/latest/api-docs/xds_protocol
