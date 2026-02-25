---
name: incident-response
description: Incident response and SRE patterns covering incident classification, triage workflows, runbook creation, postmortem templates, on-call procedures, service level objectives (SLOs), error budgets, chaos engineering, and production reliability practices.
---

# Incident Response & SRE

This skill should be used when managing production incidents or building site reliability engineering practices. It covers incident classification, triage, runbooks, postmortems, SLOs, and production reliability patterns.

## When to Use This Skill

Use this skill when you need to:

- Respond to and manage production incidents
- Create runbooks and playbooks for common failures
- Write postmortem documents
- Define SLOs, SLIs, and error budgets
- Set up on-call procedures
- Build reliability into system architecture
- Implement health checks and alerting

## Incident Classification

```
SEVERITY LEVELS:
┌──────────┬─────────────────────────────────────────────────┬──────────────┐
│ Severity │ Description                                     │ Response     │
├──────────┼─────────────────────────────────────────────────┼──────────────┤
│ SEV-1    │ Complete service outage, data loss risk,         │ Immediate    │
│          │ security breach affecting all users              │ all-hands    │
├──────────┼─────────────────────────────────────────────────┼──────────────┤
│ SEV-2    │ Major feature broken, significant degradation,   │ Immediate    │
│          │ affecting large percentage of users              │ on-call team │
├──────────┼─────────────────────────────────────────────────┼──────────────┤
│ SEV-3    │ Minor feature broken, workaround available,      │ Next         │
│          │ small subset of users affected                   │ business day │
├──────────┼─────────────────────────────────────────────────┼──────────────┤
│ SEV-4    │ Cosmetic issue, minor bug, no user impact        │ Backlog      │
└──────────┴─────────────────────────────────────────────────┴──────────────┘
```

## Incident Response Workflow

```
1. DETECT — Alert fires or user report received
   └─ Acknowledge alert within 5 minutes

2. TRIAGE — Assess severity and impact
   └─ Classify severity (SEV-1 through SEV-4)
   └─ Identify affected services and users
   └─ Assign Incident Commander (IC) for SEV-1/2

3. COMMUNICATE — Notify stakeholders
   └─ Post in incident channel (#incidents)
   └─ Update status page (for SEV-1/2)
   └─ Notify affected teams

4. MITIGATE — Stop the bleeding
   └─ Apply immediate fix (rollback, feature flag, scale up)
   └─ Focus on mitigation, not root cause
   └─ Verify mitigation is working

5. RESOLVE — Confirm service is restored
   └─ Validate metrics return to normal
   └─ Update status page
   └─ Close alert

6. FOLLOW UP — Learn from the incident
   └─ Schedule postmortem within 48 hours
   └─ Create action items
   └─ Update runbooks
```

## Runbook Template

```markdown
# Runbook: [Service Name] — [Failure Scenario]

## Overview
What this runbook addresses and when to use it.

## Symptoms
- Alert: `[alert name]` fires
- Users report: [specific user-visible behavior]
- Metrics: [which metrics are abnormal]

## Impact
- Affected services: [list]
- Affected users: [scope]
- Severity: [typical severity]

## Diagnosis Steps
1. Check service health: `curl https://api.example.com/health`
2. Check logs: `kubectl logs -l app=api-server --tail=100`
3. Check metrics: [link to dashboard]
4. Check recent deployments: `git log --oneline -5`
5. Check dependencies: [database, cache, external APIs]

## Mitigation Steps

### Option A: Rollback last deployment
```bash
kubectl rollout undo deployment/api-server
kubectl rollout status deployment/api-server
```

### Option B: Toggle feature flag
```bash
# Disable the problematic feature
curl -X POST https://admin.example.com/flags/feature-x -d '{"enabled": false}'
```

### Option C: Scale up
```bash
kubectl scale deployment/api-server --replicas=10
```

## Verification
1. Check health endpoint returns 200
2. Error rate drops below threshold
3. Latency returns to normal (p99 < 500ms)
4. User reports stop

## Escalation
If none of the above works within 30 minutes:
- Page: [team lead]
- Contact: [vendor support]
```

## Postmortem Template

```markdown
# Postmortem: [Incident Title]

**Date:** YYYY-MM-DD
**Duration:** [start time] — [end time] (X hours Y minutes)
**Severity:** SEV-[N]
**Authors:** [Names]

## Summary
[2-3 sentence summary of what happened and impact]

## Impact
- **Users affected:** [number or percentage]
- **Revenue impact:** [if applicable]
- **Duration of user-visible impact:** [time]

## Timeline (all times UTC)
| Time  | Event |
|-------|-------|
| 14:00 | Deployment of v2.3.1 begins |
| 14:05 | Error rate increases 5x |
| 14:08 | PagerDuty alert fires |
| 14:10 | On-call engineer acknowledges |
| 14:15 | Incident Commander assigned |
| 14:20 | Root cause identified: database migration timeout |
| 14:25 | Rollback initiated |
| 14:30 | Service restored |
| 14:35 | Monitoring confirms resolution |

## Root Cause
[Detailed technical explanation of what went wrong and why]

## What Went Well
- Alert fired quickly (within 3 minutes)
- Rollback procedure worked as documented
- Team response time was within SLA

## What Went Wrong
- Migration was not tested against production-sized data
- No rollback plan was documented for this specific migration
- Status page was not updated for 15 minutes

## Action Items
| Action | Owner | Priority | Due Date |
|--------|-------|----------|----------|
| Add migration testing against prod data copy | @engineer | P1 | YYYY-MM-DD |
| Automate status page updates on SEV-1 | @sre-team | P2 | YYYY-MM-DD |
| Add deployment canary for database migrations | @platform | P2 | YYYY-MM-DD |

## Lessons Learned
[What should the organization learn from this incident?]
```

## Service Level Objectives (SLOs)

```yaml
# SLO definition
service: api-server
slos:
  - name: Availability
    description: "API returns successful responses"
    sli: "successful_requests / total_requests"
    target: 99.9%  # 43.8 minutes downtime/month
    window: 30d

  - name: Latency
    description: "API responds within acceptable time"
    sli: "requests_under_500ms / total_requests"
    target: 99.0%  # p99 latency < 500ms
    window: 30d

  - name: Freshness
    description: "Data is updated within expected time"
    sli: "data_age < 5_minutes"
    target: 99.5%
    window: 30d
```

```
ERROR BUDGET CALCULATION:
  Target: 99.9% availability
  Budget: 0.1% = 43.2 minutes/month
  Current month: 15 minutes of downtime used
  Remaining: 28.2 minutes

  If error budget is nearly exhausted:
  - Freeze non-critical deployments
  - Focus engineering effort on reliability
  - Review and fix top error contributors
```

## Health Checks

```typescript
// Comprehensive health check endpoint
app.get("/health", async (req, res) => {
  const checks = {
    status: "healthy",
    timestamp: new Date().toISOString(),
    version: process.env.APP_VERSION,
    uptime: process.uptime(),
    checks: {} as Record<string, { status: string; latency?: number; error?: string }>,
  };

  // Database check
  const dbStart = Date.now();
  try {
    await db.$queryRaw`SELECT 1`;
    checks.checks.database = { status: "healthy", latency: Date.now() - dbStart };
  } catch (err) {
    checks.checks.database = { status: "unhealthy", error: (err as Error).message };
    checks.status = "degraded";
  }

  // Redis check
  const redisStart = Date.now();
  try {
    await redis.ping();
    checks.checks.redis = { status: "healthy", latency: Date.now() - redisStart };
  } catch (err) {
    checks.checks.redis = { status: "unhealthy", error: (err as Error).message };
    checks.status = "degraded";
  }

  // Memory check
  const memUsage = process.memoryUsage();
  const memPercent = memUsage.heapUsed / memUsage.heapTotal;
  checks.checks.memory = {
    status: memPercent > 0.9 ? "warning" : "healthy",
    latency: Math.round(memPercent * 100),
  };

  const statusCode = checks.status === "healthy" ? 200 : 503;
  res.status(statusCode).json(checks);
});

// Separate liveness and readiness probes (Kubernetes)
app.get("/health/live", (_, res) => res.status(200).json({ status: "alive" }));

app.get("/health/ready", async (_, res) => {
  try {
    await db.$queryRaw`SELECT 1`;
    res.status(200).json({ status: "ready" });
  } catch {
    res.status(503).json({ status: "not ready" });
  }
});
```

## Alerting Best Practices

```yaml
# Good alert: symptom-based, actionable
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.01
  for: 5m  # Avoid flapping
  labels:
    severity: critical
  annotations:
    summary: "Error rate above 1% for 5 minutes"
    runbook: "https://wiki.example.com/runbooks/high-error-rate"
    dashboard: "https://grafana.example.com/d/api-errors"

# Alert fatigue prevention:
# - Only alert on symptoms, not causes
# - Set appropriate thresholds (not too sensitive)
# - Use "for" duration to avoid flapping
# - Every alert must have a runbook
# - Review and retire stale alerts quarterly
```

## Additional Resources

- Google SRE Book: https://sre.google/sre-book/table-of-contents/
- PagerDuty Incident Response: https://response.pagerduty.com/
- Atlassian Incident Management: https://www.atlassian.com/incident-management
