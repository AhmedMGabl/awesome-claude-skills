---
name: timescaledb-timeseries
description: TimescaleDB time-series patterns covering hypertables, continuous aggregates, compression, retention policies, real-time analytics, and PostgreSQL integration.
---

# TimescaleDB Time-Series

This skill should be used when building time-series applications with TimescaleDB. It covers hypertables, continuous aggregates, compression, retention, and analytics.

## When to Use This Skill

Use this skill when you need to:

- Store and query time-series data efficiently
- Create hypertables for automatic partitioning
- Use continuous aggregates for pre-computed rollups
- Configure compression and retention policies
- Run real-time analytics on time-series data

## Setup

```sql
CREATE EXTENSION IF NOT EXISTS timescaledb;
```

## Hypertable Creation

```sql
CREATE TABLE metrics (
    time        TIMESTAMPTZ NOT NULL,
    device_id   TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    value       DOUBLE PRECISION NOT NULL,
    tags        JSONB DEFAULT '{}'
);

SELECT create_hypertable('metrics', by_range('time'));

-- With specific chunk interval
SELECT create_hypertable('metrics', by_range('time', INTERVAL '1 day'));

-- Add indexes
CREATE INDEX idx_metrics_device ON metrics (device_id, time DESC);
CREATE INDEX idx_metrics_name ON metrics (metric_name, time DESC);
```

## Inserting Data

```sql
INSERT INTO metrics (time, device_id, metric_name, value) VALUES
    (NOW(), 'sensor-001', 'temperature', 23.5),
    (NOW(), 'sensor-001', 'humidity', 65.2),
    (NOW(), 'sensor-002', 'temperature', 21.8);

-- Batch insert
INSERT INTO metrics (time, device_id, metric_name, value)
SELECT
    generate_series(NOW() - INTERVAL '24 hours', NOW(), INTERVAL '1 minute'),
    'sensor-001',
    'temperature',
    20 + random() * 10;
```

## Time-Series Queries

```sql
-- Latest value per device
SELECT DISTINCT ON (device_id)
    device_id, value, time
FROM metrics
WHERE metric_name = 'temperature'
ORDER BY device_id, time DESC;

-- Time bucketing
SELECT
    time_bucket('1 hour', time) AS hour,
    device_id,
    AVG(value) AS avg_temp,
    MIN(value) AS min_temp,
    MAX(value) AS max_temp
FROM metrics
WHERE metric_name = 'temperature'
    AND time > NOW() - INTERVAL '24 hours'
GROUP BY hour, device_id
ORDER BY hour DESC;

-- Gap filling
SELECT
    time_bucket_gapfill('1 hour', time) AS hour,
    device_id,
    locf(AVG(value)) AS avg_temp  -- last observation carried forward
FROM metrics
WHERE metric_name = 'temperature'
    AND time > NOW() - INTERVAL '24 hours'
GROUP BY hour, device_id
ORDER BY hour;
```

## Continuous Aggregates

```sql
CREATE MATERIALIZED VIEW hourly_metrics
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    device_id,
    metric_name,
    AVG(value) AS avg_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value,
    COUNT(*) AS sample_count
FROM metrics
GROUP BY bucket, device_id, metric_name;

-- Refresh policy
SELECT add_continuous_aggregate_policy('hourly_metrics',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour'
);

-- Query the aggregate
SELECT * FROM hourly_metrics
WHERE bucket > NOW() - INTERVAL '7 days'
    AND device_id = 'sensor-001'
ORDER BY bucket DESC;
```

## Compression

```sql
ALTER TABLE metrics SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'device_id, metric_name',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy('metrics', INTERVAL '7 days');
```

## Retention

```sql
SELECT add_retention_policy('metrics', INTERVAL '90 days');
```

## Additional Resources

- TimescaleDB: https://docs.timescale.com/
- Hypertables: https://docs.timescale.com/use-timescale/hypertables/
- Continuous Aggregates: https://docs.timescale.com/use-timescale/continuous-aggregates/
