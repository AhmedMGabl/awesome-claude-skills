---
name: clickhouse-analytics
description: ClickHouse analytics patterns covering table engines, MergeTree family, materialized views, aggregating functions, partitioning, and real-time analytics queries.
---

# ClickHouse Analytics

This skill should be used when building analytics systems with ClickHouse. It covers table engines, MergeTree, materialized views, aggregation, partitioning, and query optimization.

## When to Use This Skill

Use this skill when you need to:

- Build real-time analytics with ClickHouse
- Design schemas with MergeTree table engines
- Use materialized views for pre-aggregation
- Optimize queries for billion-row datasets
- Integrate ClickHouse with Node.js or Python

## Table Design

```sql
CREATE TABLE events (
    event_id UUID DEFAULT generateUUIDv4(),
    event_type LowCardinality(String),
    user_id UInt64,
    session_id String,
    page_url String,
    referrer String,
    country LowCardinality(String),
    device LowCardinality(String),
    properties String,  -- JSON string
    created_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_at)
ORDER BY (event_type, user_id, created_at)
TTL created_at + INTERVAL 1 YEAR
SETTINGS index_granularity = 8192;
```

## ReplacingMergeTree (Deduplication)

```sql
CREATE TABLE users (
    user_id UInt64,
    name String,
    email String,
    plan LowCardinality(String),
    updated_at DateTime
)
ENGINE = ReplacingMergeTree(updated_at)
ORDER BY user_id;

-- Query with deduplication
SELECT * FROM users FINAL WHERE user_id = 123;
```

## AggregatingMergeTree

```sql
CREATE TABLE page_views_hourly (
    hour DateTime,
    page_url String,
    views AggregateFunction(count, UInt64),
    unique_users AggregateFunction(uniq, UInt64)
)
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMM(hour)
ORDER BY (hour, page_url);
```

## Materialized Views

```sql
CREATE MATERIALIZED VIEW daily_stats_mv
TO daily_stats
AS SELECT
    toDate(created_at) AS date,
    event_type,
    count() AS event_count,
    uniq(user_id) AS unique_users,
    uniq(session_id) AS unique_sessions
FROM events
GROUP BY date, event_type;

-- Query the pre-aggregated view
SELECT date, event_type, event_count, unique_users
FROM daily_stats
WHERE date >= today() - 30
ORDER BY date DESC, event_count DESC;
```

## Analytics Queries

```sql
-- Funnel analysis
SELECT
    countIf(event_type = 'page_view') AS step1_views,
    countIf(event_type = 'add_to_cart') AS step2_cart,
    countIf(event_type = 'checkout') AS step3_checkout,
    countIf(event_type = 'purchase') AS step4_purchase,
    round(countIf(event_type = 'purchase') / countIf(event_type = 'page_view') * 100, 2) AS conversion_rate
FROM events
WHERE created_at >= now() - INTERVAL 7 DAY;

-- Retention analysis (Day 0 vs Day 7)
WITH day0 AS (
    SELECT DISTINCT user_id FROM events
    WHERE toDate(created_at) = '2024-01-01'
),
day7 AS (
    SELECT DISTINCT user_id FROM events
    WHERE toDate(created_at) = '2024-01-08'
)
SELECT
    count() AS day0_users,
    countIf(user_id IN (SELECT user_id FROM day7)) AS retained,
    round(countIf(user_id IN (SELECT user_id FROM day7)) / count() * 100, 2) AS retention_pct
FROM day0;

-- Top pages with percentiles
SELECT
    page_url,
    count() AS views,
    quantile(0.5)(duration_ms) AS p50,
    quantile(0.95)(duration_ms) AS p95,
    quantile(0.99)(duration_ms) AS p99
FROM page_loads
WHERE created_at >= now() - INTERVAL 1 DAY
GROUP BY page_url
ORDER BY views DESC
LIMIT 20;
```

## Node.js Client

```typescript
import { createClient } from "@clickhouse/client";

const client = createClient({ url: "http://localhost:8123" });

const result = await client.query({
  query: "SELECT event_type, count() as cnt FROM events GROUP BY event_type ORDER BY cnt DESC",
  format: "JSONEachRow",
});
const data = await result.json();
```

## Additional Resources

- ClickHouse: https://clickhouse.com/docs/
- SQL Reference: https://clickhouse.com/docs/en/sql-reference
- MergeTree: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family
