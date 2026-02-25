---
name: tinybird-analytics
description: Tinybird real-time analytics covering data sources, pipes, API endpoints, materialized views, SQL transformations, ingestion patterns, and integration with Next.js and event tracking.
---

# Tinybird Analytics

This skill should be used when building real-time analytics with Tinybird. It covers data ingestion, SQL transformations, API endpoints, and dashboard integration.

## When to Use This Skill

Use this skill when you need to:

- Build real-time analytics dashboards
- Create API endpoints backed by SQL queries
- Ingest high-volume event data
- Transform and aggregate data with SQL
- Build product analytics and metrics

## Data Source

```sql
-- datasources/events.datasource
SCHEMA >
    `event_id` String,
    `user_id` String,
    `event_type` String,
    `properties` String,
    `timestamp` DateTime

ENGINE "MergeTree"
ENGINE_PARTITION_KEY "toYYYYMM(timestamp)"
ENGINE_SORTING_KEY "event_type, user_id, timestamp"
```

## Ingest Events

```typescript
// Ingest via HTTP API
async function trackEvent(event: {
  eventId: string;
  userId: string;
  eventType: string;
  properties: Record<string, unknown>;
}) {
  await fetch(`https://api.tinybird.co/v0/events?name=events`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${process.env.TINYBIRD_TOKEN}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      event_id: event.eventId,
      user_id: event.userId,
      event_type: event.eventType,
      properties: JSON.stringify(event.properties),
      timestamp: new Date().toISOString(),
    }),
  });
}

// Batch ingest (NDJSON)
async function batchIngest(events: any[]) {
  const ndjson = events.map((e) => JSON.stringify(e)).join("\n");
  await fetch("https://api.tinybird.co/v0/events?name=events", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${process.env.TINYBIRD_TOKEN}`,
      "Content-Type": "application/x-ndjson",
    },
    body: ndjson,
  });
}
```

## Pipe (SQL Transformation)

```sql
-- pipes/daily_active_users.pipe
NODE daily_counts
SQL >
    SELECT
        toDate(timestamp) AS date,
        uniqExact(user_id) AS active_users,
        count() AS total_events
    FROM events
    WHERE timestamp >= now() - INTERVAL 30 DAY
    GROUP BY date
    ORDER BY date DESC

NODE endpoint
SQL >
    SELECT * FROM daily_counts
    WHERE date >= {{Date(start_date, '2024-01-01')}}
      AND date <= {{Date(end_date, today())}}
```

## Query API Endpoints

```typescript
async function getDailyActiveUsers(startDate: string, endDate: string) {
  const url = new URL("https://api.tinybird.co/v0/pipes/daily_active_users.json");
  url.searchParams.set("start_date", startDate);
  url.searchParams.set("end_date", endDate);

  const response = await fetch(url.toString(), {
    headers: { Authorization: `Bearer ${process.env.TINYBIRD_READ_TOKEN}` },
  });

  const { data } = await response.json();
  return data as { date: string; active_users: number; total_events: number }[];
}
```

## Materialized View

```sql
-- pipes/event_counts_mv.pipe
NODE aggregate
SQL >
    SELECT
        event_type,
        toStartOfHour(timestamp) AS hour,
        count() AS event_count,
        uniqExact(user_id) AS unique_users
    FROM events
    GROUP BY event_type, hour

TYPE materialized
DATASOURCE event_counts_hourly
```

## React Dashboard

```tsx
function AnalyticsDashboard() {
  const [data, setData] = useState<DailyStats[]>([]);

  useEffect(() => {
    getDailyActiveUsers("2024-01-01", "2024-12-31").then(setData);
  }, []);

  return (
    <div>
      <h2>Daily Active Users</h2>
      <LineChart data={data} xKey="date" yKey="active_users" />
    </div>
  );
}
```

## Additional Resources

- Tinybird docs: https://www.tinybird.co/docs
- SQL reference: https://www.tinybird.co/docs/sql-reference
- API endpoints: https://www.tinybird.co/docs/publish/api-endpoints
