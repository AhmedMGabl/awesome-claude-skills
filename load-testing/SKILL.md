---
name: load-testing
description: Load testing and performance benchmarking covering k6 scripts, Autocannon for HTTP benchmarking, Artillery scenarios, stress and spike testing, threshold-based pass/fail, CI integration, metrics analysis (p95/p99 latency, throughput), and capacity planning.
---

# Load Testing

This skill should be used when load testing APIs and web applications. It covers k6, Autocannon, Artillery, stress testing, and CI integration.

## When to Use This Skill

Use this skill when you need to:

- Benchmark API endpoint performance
- Run stress and spike tests
- Set SLO-based pass/fail thresholds
- Integrate load tests into CI pipelines
- Plan capacity and identify bottlenecks

## k6 Load Test

```javascript
// load-test.js — run with: k6 run load-test.js
import http from "k6/http";
import { check, sleep } from "k6";
import { Rate, Trend } from "k6/metrics";

const errorRate = new Rate("errors");
const apiDuration = new Trend("api_duration");

export const options = {
  stages: [
    { duration: "1m", target: 50 },   // Ramp up to 50 users
    { duration: "3m", target: 50 },   // Stay at 50 users
    { duration: "1m", target: 100 },  // Ramp to 100
    { duration: "3m", target: 100 },  // Stay at 100
    { duration: "1m", target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ["p(95)<500", "p(99)<1000"],
    errors: ["rate<0.01"],  // Less than 1% errors
    http_req_failed: ["rate<0.01"],
  },
};

export default function () {
  // GET request
  const listRes = http.get("http://localhost:3000/api/users");
  check(listRes, {
    "status is 200": (r) => r.status === 200,
    "response time < 500ms": (r) => r.timings.duration < 500,
  });
  errorRate.add(listRes.status !== 200);
  apiDuration.add(listRes.timings.duration);

  sleep(1);

  // POST request
  const createRes = http.post(
    "http://localhost:3000/api/users",
    JSON.stringify({ name: "Test User", email: `user${__VU}@test.com` }),
    { headers: { "Content-Type": "application/json" } },
  );
  check(createRes, { "created successfully": (r) => r.status === 201 });

  sleep(1);
}
```

## k6 Test Types

```javascript
// Smoke test — verify system works under minimal load
export const options = {
  vus: 1,
  duration: "1m",
};

// Load test — normal expected traffic
export const options = {
  stages: [
    { duration: "5m", target: 100 },
    { duration: "10m", target: 100 },
    { duration: "5m", target: 0 },
  ],
};

// Stress test — find breaking point
export const options = {
  stages: [
    { duration: "2m", target: 100 },
    { duration: "2m", target: 200 },
    { duration: "2m", target: 400 },
    { duration: "2m", target: 800 },
    { duration: "5m", target: 0 },
  ],
};

// Spike test — sudden traffic burst
export const options = {
  stages: [
    { duration: "1m", target: 10 },
    { duration: "10s", target: 1000 },
    { duration: "3m", target: 1000 },
    { duration: "10s", target: 10 },
    { duration: "1m", target: 0 },
  ],
};
```

## Autocannon (Node.js)

```typescript
import autocannon from "autocannon";

const result = await autocannon({
  url: "http://localhost:3000/api/users",
  connections: 100,
  duration: 30,
  headers: { Authorization: "Bearer token" },
});

console.log(`
  Requests/sec: ${result.requests.average}
  Latency p50:  ${result.latency.p50}ms
  Latency p99:  ${result.latency.p99}ms
  Throughput:   ${(result.throughput.average / 1024 / 1024).toFixed(2)} MB/s
  Errors:       ${result.errors}
`);
```

## CI Integration

```yaml
# .github/workflows/load-test.yml
name: Load Test
on:
  pull_request:
    branches: [main]
jobs:
  k6:
    runs-on: ubuntu-latest
    services:
      app:
        image: myapp:latest
        ports: ["3000:3000"]
    steps:
      - uses: actions/checkout@v4
      - uses: grafana/k6-action@v0.3.1
        with:
          filename: tests/load-test.js
          flags: --out json=results.json
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: k6-results
          path: results.json
```

## Metrics Reference

```
METRIC             MEANING                    GOOD TARGET
─────────────────────────────────────────────────────────
p50 latency        Median response time       < 100ms
p95 latency        95th percentile            < 500ms
p99 latency        99th percentile            < 1000ms
Requests/sec       Throughput                 Depends on SLO
Error rate         % failed requests          < 0.1%
TTFB               Time to first byte         < 200ms
```

## Additional Resources

- k6 docs: https://grafana.com/docs/k6/latest/
- Autocannon: https://github.com/mcollina/autocannon
- Artillery: https://www.artillery.io/
