---
name: istio-mesh
description: Istio service mesh patterns covering traffic management, virtual services, destination rules, mTLS, authorization policies, observability, and canary deployments.
---

# Istio Service Mesh

This skill should be used when implementing service mesh with Istio. It covers traffic management, virtual services, destination rules, security, observability, and canary deployments.

## When to Use This Skill

Use this skill when you need to:

- Manage traffic between microservices
- Implement canary and blue-green deployments
- Enforce mTLS and authorization policies
- Collect distributed tracing and metrics
- Configure fault injection for resilience testing

## Virtual Service (Traffic Routing)

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
    - reviews
  http:
    # Route by header
    - match:
        - headers:
            end-user:
              exact: "tester"
      route:
        - destination:
            host: reviews
            subset: v3
    # Canary: 90/10 split
    - route:
        - destination:
            host: reviews
            subset: v1
          weight: 90
        - destination:
            host: reviews
            subset: v2
          weight: 10
      timeout: 10s
      retries:
        attempts: 3
        perTryTimeout: 3s
        retryOn: "5xx,connect-failure"
```

## Destination Rule

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: reviews
spec:
  host: reviews
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        h2UpgradePolicy: DEFAULT
        http1MaxPendingRequests: 50
        http2MaxRequests: 100
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 10s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
    loadBalancer:
      simple: ROUND_ROBIN
  subsets:
    - name: v1
      labels:
        version: v1
    - name: v2
      labels:
        version: v2
    - name: v3
      labels:
        version: v3
```

## Gateway (Ingress)

```yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: app-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
    - port:
        number: 443
        name: https
        protocol: HTTPS
      tls:
        mode: SIMPLE
        credentialName: app-tls-cert
      hosts:
        - "app.example.com"
---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: app-routes
spec:
  hosts:
    - "app.example.com"
  gateways:
    - app-gateway
  http:
    - match:
        - uri:
            prefix: /api
      route:
        - destination:
            host: api-service
            port:
              number: 8080
    - match:
        - uri:
            prefix: /
      route:
        - destination:
            host: web-service
            port:
              number: 3000
```

## Security (mTLS and Authorization)

```yaml
# Enforce mTLS
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT
---
# Authorization policy
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: api-access
  namespace: production
spec:
  selector:
    matchLabels:
      app: api-service
  rules:
    - from:
        - source:
            principals:
              - "cluster.local/ns/production/sa/web-service"
      to:
        - operation:
            methods: ["GET", "POST"]
            paths: ["/api/*"]
    - from:
        - source:
            principals:
              - "cluster.local/ns/production/sa/admin-service"
      to:
        - operation:
            methods: ["*"]
```

## Fault Injection

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews-fault
spec:
  hosts:
    - reviews
  http:
    - fault:
        delay:
          percentage:
            value: 10
          fixedDelay: 5s
        abort:
          percentage:
            value: 5
          httpStatus: 503
      route:
        - destination:
            host: reviews
            subset: v1
```

## Installation

```bash
# Install Istio
istioctl install --set profile=demo

# Enable sidecar injection for namespace
kubectl label namespace default istio-injection=enabled

# Verify
istioctl analyze
```

## Additional Resources

- Istio: https://istio.io/latest/docs/
- Traffic Management: https://istio.io/latest/docs/concepts/traffic-management/
- Security: https://istio.io/latest/docs/concepts/security/
