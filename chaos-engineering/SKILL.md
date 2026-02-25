---
name: chaos-engineering
description: This skill should be used when designing chaos experiments, implementing fault injection, building resilience tests, planning gamedays, or hardening distributed systems against failure using tools like LitmusChaos, Toxiproxy, and circuit breaker patterns.
---

# Chaos Engineering & Resilience Testing

Guide for proactively injecting failures into distributed systems to validate steady-state hypotheses and build confidence in resilience.

## When to Use This Skill

- Design and run chaos experiments
- Inject network faults with Toxiproxy
- Create Kubernetes chaos experiments with LitmusChaos
- Implement circuit breakers and prevent retry storms
- Plan and execute gameday exercises
- Control blast radius during fault injection

## Core Concepts

```
CHAOS ENGINEERING CYCLE:
1. STEADY STATE    Define normal behavior (metrics, SLOs)
2. HYPOTHESIZE     "System continues serving when X fails"
3. INJECT FAULT    Introduce a controlled failure
4. OBSERVE         Compare behavior against hypothesis
5. LEARN           Document findings, fix weaknesses, repeat
```

| Fault Pattern       | Target             | Tools                    |
|---------------------|--------------------|--------------------------|
| Network latency     | Service-to-service | Toxiproxy, tc, Istio     |
| Service unavailable | Downstream deps    | Toxiproxy, LitmusChaos   |
| Pod termination     | Kubernetes pods    | LitmusChaos, Chaos Mesh  |
| CPU/memory stress   | Node resources     | stress-ng, LitmusChaos   |

## Toxiproxy Setup (Go)

```go
package main

import (
    "log"
    toxiproxy "github.com/Shopify/toxiproxy/v2/client"
)

func main() {
    client := toxiproxy.NewClient("localhost:8474")
    proxy, err := client.CreateProxy("payment-service", "localhost:6300", "payment-api:8080")
    if err != nil { log.Fatalf("failed to create proxy: %v", err) }
    _, err = proxy.AddToxic("latency_down", "latency", "downstream", 1.0, toxiproxy.Attributes{
        "latency": 500, "jitter": 100,
    })
    if err != nil { log.Fatalf("failed to add toxic: %v", err) }
    proxy.Disable() // Simulate complete outage
    proxy.Enable()  // Restore connectivity
}
```

## Toxiproxy Setup (Node.js)

```javascript
const Toxiproxy = require("toxiproxy-node-client");

async function setupChaos() {
  const toxiproxy = new Toxiproxy("http://localhost:8474");
  const proxy = await toxiproxy.createProxy({
    name: "order-service", listen: "localhost:6301", upstream: "order-api:8080",
  });
  await proxy.addToxic({
    name: "slow_bandwidth", type: "bandwidth",
    stream: "downstream", toxicity: 1.0, attributes: { rate: 1 },
  });
  await proxy.addToxic({
    name: "partial_reset", type: "reset_peer",
    stream: "downstream", toxicity: 0.3, attributes: { timeout: 200 },
  });
  return proxy;
}
```

## Resilience Testing with Jest

```javascript
const { createProxyClient } = require("./test-helpers");

describe("Order Service Resilience", () => {
  let proxy;
  beforeAll(async () => {
    proxy = await createProxyClient("payment-service", 6300, "payment:8080");
  });
  afterEach(async () => { await proxy.removeAllToxics(); await proxy.enable(); });

  test("returns cached result under high latency", async () => {
    await proxy.addToxic({
      name: "high_latency", type: "latency",
      stream: "downstream", attributes: { latency: 3000 },
    });
    const start = Date.now();
    const response = await fetch("http://localhost:3000/api/orders/123");
    expect(response.status).toBe(200);
    expect(Date.now() - start).toBeLessThan(1000);
  });

  test("returns 503 when downstream is down", async () => {
    await proxy.disable();
    const response = await fetch("http://localhost:3000/api/orders/123");
    expect(response.status).toBe(503);
  });

  test("circuit breaker opens after repeated failures", async () => {
    await proxy.addToxic({
      name: "reset", type: "reset_peer",
      stream: "downstream", toxicity: 1.0, attributes: { timeout: 0 },
    });
    for (let i = 0; i < 5; i++) await fetch("http://localhost:3000/api/orders/123");
    const response = await fetch("http://localhost:3000/api/orders/123");
    expect(response.status).toBe(503);
    expect((await response.json()).circuit).toBe("open");
  });
});
```

## Circuit Breakers & Retry Storm Prevention

```
CLOSED ──(failure threshold)──> OPEN ──(timeout)──> HALF-OPEN ──(success)──> CLOSED
```

Prevent retry storms with: **exponential backoff with jitter**, **circuit breakers**, **retry budgets** (cap at 10% of total requests), and **client-side rate limiting**.

```javascript
function calculateBackoff(attempt, baseDelayMs, maxDelayMs) {
  const exponentialDelay = baseDelayMs * Math.pow(2, attempt);
  return Math.random() * Math.min(exponentialDelay, maxDelayMs);
}
```

## LitmusChaos Kubernetes Experiment

Install: `kubectl apply -f https://litmuschaos.github.io/litmus/litmus-operator-v3.0.0.yaml`

```yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: order-service-chaos
  namespace: production
spec:
  appinfo:
    appns: production
    applabel: app=order-service
    appkind: deployment
  chaosServiceAccount: litmus-admin
  experiments:
    - name: pod-delete
      spec:
        components:
          env:
            - name: TOTAL_CHAOS_DURATION
              value: "60"
            - name: CHAOS_INTERVAL
              value: "15"
            - name: PODS_AFFECTED_PERC
              value: "50"
        probe:
          - name: steady-state-check
            type: httpProbe
            mode: Continuous
            httpProbe/inputs:
              url: http://order-service.production.svc:8080/health
              method:
                get:
                  criteria: ==
                  responseCode: "200"
            runProperties:
              probeTimeout: 5s
              interval: 10s
```

## Steady-State Hypothesis

Define "normal" before injecting faults so deviations are measurable.

```yaml
steady_state_hypothesis:
  title: "Order processing remains functional"
  probes:
    - name: api-responds-200
      type: http
      provider: { url: "http://order-service:8080/health", expected_status: 200 }
    - name: error-rate-below-threshold
      type: prometheus
      provider:
        query: "rate(http_requests_total{status=~'5..', service='order'}[5m])"
        expected_max: 0.01
    - name: p99-latency-acceptable
      type: prometheus
      provider:
        query: "histogram_quantile(0.99, rate(http_duration_seconds_bucket{service='order'}[5m]))"
        expected_max: 2.0
```

## Blast Radius Control

- Target non-production environments first
- Limit to a single AZ or replica subset
- Set maximum duration with automatic rollback
- Define abort conditions (error rate > 5%, latency > 10s)
- Notify on-call team and have a one-command rollback ready
- Start with read-only paths, then expand to writes
- Never target stateful services without backups

## Gameday Runbook Template

```markdown
# Gameday: [Scenario Title]
**Date:** YYYY-MM-DD  **Facilitator:** [Name]  **Environment:** [staging / canary]

## Objective
[Resilience property being validated]

## Steady-State: success rate > 99.5%, p99 < 500ms, throughput > 100 req/min

## Steps
1. Confirm steady-state metrics, announce in #incidents
2. Inject fault: [describe], observe dashboards for 5 minutes
3. Record deviations, remove fault, verify recovery within 2 minutes

## Abort: error rate > 10%, p99 > 10s, data loss, customer impact

## Findings
| Metric          | Expected | Actual | Status |
|-----------------|----------|--------|--------|
| Success rate    |          |        |        |
| p99 latency     |          |        |        |
| Recovery time   |          |        |        |

## Action Items
| Action | Owner | Priority | Due Date |
|--------|-------|----------|----------|
```

## Additional Resources

- Principles of Chaos Engineering: https://principlesofchaos.org/
- LitmusChaos: https://litmuschaos.io/
- Toxiproxy: https://github.com/Shopify/toxiproxy
- Chaos Mesh: https://chaos-mesh.org/
