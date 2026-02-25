---
name: pagerduty-incidents
description: PagerDuty incident management patterns covering service configuration, escalation policies, event rules, API integration, incident workflows, and on-call scheduling.
---

# PagerDuty Incidents

This skill should be used when implementing incident management with PagerDuty. It covers services, escalation policies, event rules, API integration, workflows, and on-call scheduling.

## When to Use This Skill

Use this skill when you need to:

- Configure PagerDuty services and escalation policies
- Send events and trigger incidents via API
- Set up event orchestration rules
- Manage on-call schedules and rotations
- Automate incident response workflows

## Event Submission (Events API v2)

```typescript
interface PagerDutyEvent {
  routing_key: string;
  event_action: "trigger" | "acknowledge" | "resolve";
  dedup_key?: string;
  payload: {
    summary: string;
    source: string;
    severity: "critical" | "error" | "warning" | "info";
    component?: string;
    group?: string;
    class?: string;
    custom_details?: Record<string, unknown>;
  };
  links?: Array<{ href: string; text: string }>;
  images?: Array<{ src: string; href?: string; alt?: string }>;
}

async function triggerIncident(event: PagerDutyEvent): Promise<string> {
  const response = await fetch("https://events.pagerduty.com/v2/enqueue", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(event),
  });

  const data = await response.json();
  return data.dedup_key;
}

// Trigger alert
const dedupKey = await triggerIncident({
  routing_key: process.env.PD_ROUTING_KEY!,
  event_action: "trigger",
  dedup_key: `db-connection-${Date.now()}`,
  payload: {
    summary: "Database connection pool exhausted",
    source: "api-server-01",
    severity: "critical",
    component: "database",
    group: "production",
    custom_details: {
      active_connections: 100,
      max_connections: 100,
      waiting_queries: 45,
    },
  },
  links: [
    { href: "https://grafana.example.com/d/db-pool", text: "Grafana Dashboard" },
  ],
});

// Resolve alert
await triggerIncident({
  routing_key: process.env.PD_ROUTING_KEY!,
  event_action: "resolve",
  dedup_key: dedupKey,
  payload: {
    summary: "Database connection pool recovered",
    source: "api-server-01",
    severity: "info",
  },
});
```

## REST API Usage

```typescript
const PD_API = "https://api.pagerduty.com";
const headers = {
  Authorization: `Token token=${process.env.PD_API_TOKEN}`,
  "Content-Type": "application/json",
};

// List incidents
async function listIncidents(status: string = "triggered,acknowledged") {
  const response = await fetch(
    `${PD_API}/incidents?statuses[]=${status}&sort_by=created_at:desc`,
    { headers }
  );
  return response.json();
}

// Get on-call users
async function getOnCall(scheduleId: string) {
  const now = new Date().toISOString();
  const response = await fetch(
    `${PD_API}/schedules/${scheduleId}/users?since=${now}&until=${now}`,
    { headers }
  );
  return response.json();
}

// Create incident note
async function addNote(incidentId: string, content: string) {
  const response = await fetch(`${PD_API}/incidents/${incidentId}/notes`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      note: { content },
    }),
  });
  return response.json();
}
```

## Terraform Configuration

```hcl
resource "pagerduty_service" "api" {
  name              = "API Service"
  description       = "Production API service"
  escalation_policy = pagerduty_escalation_policy.engineering.id
  alert_creation    = "create_alerts_and_incidents"

  auto_resolve_timeout    = 14400  # 4 hours
  acknowledgement_timeout = 1800   # 30 minutes

  incident_urgency_rule {
    type    = "use_support_hours"
    during_support_hours {
      type    = "constant"
      urgency = "high"
    }
    outside_support_hours {
      type    = "constant"
      urgency = "low"
    }
  }

  support_hours {
    type         = "fixed_time_per_day"
    time_zone    = "America/New_York"
    start_time   = "09:00:00"
    end_time     = "17:00:00"
    days_of_week = [1, 2, 3, 4, 5]
  }
}

resource "pagerduty_escalation_policy" "engineering" {
  name      = "Engineering Escalation"
  num_loops = 2

  rule {
    escalation_delay_in_minutes = 15
    target {
      type = "schedule_reference"
      id   = pagerduty_schedule.primary.id
    }
  }

  rule {
    escalation_delay_in_minutes = 30
    target {
      type = "user_reference"
      id   = pagerduty_user.engineering_manager.id
    }
  }
}

resource "pagerduty_schedule" "primary" {
  name      = "Primary On-Call"
  time_zone = "America/New_York"

  layer {
    name                         = "Weekly Rotation"
    start                        = "2025-01-01T00:00:00-05:00"
    rotation_virtual_start       = "2025-01-01T00:00:00-05:00"
    rotation_turn_length_seconds = 604800  # 1 week

    users = [
      pagerduty_user.engineer1.id,
      pagerduty_user.engineer2.id,
      pagerduty_user.engineer3.id,
    ]
  }
}
```

## Additional Resources

- PagerDuty Docs: https://developer.pagerduty.com/docs/
- Events API v2: https://developer.pagerduty.com/docs/events-api-v2/overview/
- REST API: https://developer.pagerduty.com/api-reference/
