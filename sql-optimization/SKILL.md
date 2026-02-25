---
name: sql-optimization
description: SQL query optimization covering EXPLAIN ANALYZE, index strategies (B-tree, GIN, partial, covering), query rewriting, N+1 detection, materialized views, partitioning, connection pooling, slow query analysis, and database performance tuning for PostgreSQL and MySQL.
---

# SQL Optimization

This skill should be used when optimizing database queries and improving application performance at the database layer. It covers query analysis, indexing strategies, and performance tuning.

## When to Use This Skill

Use this skill when you need to:

- Analyze and optimize slow queries
- Design effective indexing strategies
- Fix N+1 query problems
- Implement partitioning and materialized views
- Tune database connection pooling
- Read and interpret EXPLAIN plans

## EXPLAIN ANALYZE

```sql
-- PostgreSQL: Read execution plan
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.created_at > '2024-01-01'
GROUP BY u.id
ORDER BY order_count DESC
LIMIT 20;

-- Key metrics to look for:
-- Seq Scan → Consider adding an index
-- Nested Loop with high row count → May need different join strategy
-- Sort with high memory → Consider index for ORDER BY
-- Buffers: shared hit vs read → Cache hit ratio
```

## Index Strategies

```sql
-- B-tree index (default) — equality and range queries
CREATE INDEX idx_users_email ON users (email);
CREATE INDEX idx_orders_created ON orders (created_at DESC);

-- Composite index — column order matters (left-to-right)
-- Supports: WHERE status = 'active' AND created_at > X
-- Also supports: WHERE status = 'active' (prefix)
-- Does NOT support: WHERE created_at > X (skips first column)
CREATE INDEX idx_orders_status_date ON orders (status, created_at DESC);

-- Covering index — includes columns to avoid table lookups
CREATE INDEX idx_orders_covering ON orders (user_id)
  INCLUDE (total, status, created_at);

-- Partial index — index only relevant rows
CREATE INDEX idx_orders_active ON orders (created_at DESC)
  WHERE status = 'active';

-- GIN index for arrays and JSONB (PostgreSQL)
CREATE INDEX idx_products_tags ON products USING GIN (tags);
CREATE INDEX idx_data_jsonb ON events USING GIN (metadata jsonb_path_ops);

-- Expression index
CREATE INDEX idx_users_lower_email ON users (LOWER(email));

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
WHERE idx_scan = 0  -- Unused indexes (candidates for removal)
ORDER BY pg_relation_size(indexrelid) DESC;
```

## Query Rewriting

```sql
-- ANTI-PATTERN: Correlated subquery (runs once per row)
SELECT * FROM products p
WHERE price > (SELECT AVG(price) FROM products WHERE category = p.category);

-- BETTER: CTE or JOIN
WITH category_avg AS (
  SELECT category, AVG(price) as avg_price FROM products GROUP BY category
)
SELECT p.*
FROM products p
JOIN category_avg ca ON p.category = ca.category
WHERE p.price > ca.avg_price;

-- ANTI-PATTERN: SELECT * with unused columns
SELECT * FROM orders WHERE user_id = 123;

-- BETTER: Select only needed columns
SELECT id, total, status, created_at FROM orders WHERE user_id = 123;

-- ANTI-PATTERN: OR on different columns (can't use index)
SELECT * FROM users WHERE email = 'a@b.com' OR phone = '555-1234';

-- BETTER: UNION (each branch can use its own index)
SELECT * FROM users WHERE email = 'a@b.com'
UNION ALL
SELECT * FROM users WHERE phone = '555-1234' AND email != 'a@b.com';

-- ANTI-PATTERN: Function on indexed column
SELECT * FROM users WHERE YEAR(created_at) = 2024;

-- BETTER: Range query (uses index)
SELECT * FROM users WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01';
```

## N+1 Query Detection and Fix

```typescript
// ANTI-PATTERN: N+1 queries (1 query + N queries per result)
const users = await db.query("SELECT * FROM users LIMIT 100");
for (const user of users) {
  // This runs 100 separate queries!
  user.orders = await db.query("SELECT * FROM orders WHERE user_id = $1", [user.id]);
}

// FIX 1: JOIN query
const results = await db.query(`
  SELECT u.*, o.id as order_id, o.total
  FROM users u
  LEFT JOIN orders o ON o.user_id = u.id
  LIMIT 100
`);

// FIX 2: Batch loading (DataLoader pattern)
const users = await db.query("SELECT * FROM users LIMIT 100");
const userIds = users.map((u) => u.id);
const orders = await db.query(
  "SELECT * FROM orders WHERE user_id = ANY($1)",
  [userIds],
);
// Group orders by user_id
const ordersByUser = Map.groupBy(orders, (o) => o.user_id);

// Prisma: Use include (generates efficient queries)
const users = await prisma.user.findMany({
  take: 100,
  include: { orders: { select: { id: true, total: true } } },
});
```

## Materialized Views

```sql
-- Pre-compute expensive aggregations
CREATE MATERIALIZED VIEW mv_daily_sales AS
SELECT
  date_trunc('day', created_at) as day,
  category,
  COUNT(*) as order_count,
  SUM(total) as revenue,
  AVG(total) as avg_order_value
FROM orders
JOIN products ON products.id = orders.product_id
WHERE status = 'completed'
GROUP BY 1, 2;

-- Create index on materialized view
CREATE UNIQUE INDEX idx_mv_daily_sales ON mv_daily_sales (day, category);

-- Refresh (schedule with cron or pg_cron)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_sales;
```

## Table Partitioning

```sql
-- PostgreSQL range partitioning by date
CREATE TABLE events (
  id bigint GENERATED ALWAYS AS IDENTITY,
  event_type text NOT NULL,
  payload jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE events_2024_01 PARTITION OF events
  FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE TABLE events_2024_02 PARTITION OF events
  FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Partition pruning happens automatically
-- This query only scans events_2024_01:
SELECT * FROM events WHERE created_at >= '2024-01-15' AND created_at < '2024-01-20';
```

## Connection Pooling

```typescript
// Node.js with PgBouncer or built-in pooling
import { Pool } from "pg";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,                    // Max connections in pool
  idleTimeoutMillis: 30000,   // Close idle connections after 30s
  connectionTimeoutMillis: 5000, // Fail if no connection in 5s
});

// Use pool for queries
const { rows } = await pool.query("SELECT * FROM users WHERE id = $1", [userId]);

// For transactions, check out a dedicated client
const client = await pool.connect();
try {
  await client.query("BEGIN");
  await client.query("UPDATE accounts SET balance = balance - $1 WHERE id = $2", [100, fromId]);
  await client.query("UPDATE accounts SET balance = balance + $1 WHERE id = $2", [100, toId]);
  await client.query("COMMIT");
} catch (e) {
  await client.query("ROLLBACK");
  throw e;
} finally {
  client.release();
}
```

## Additional Resources

- PostgreSQL EXPLAIN: https://www.postgresql.org/docs/current/using-explain.html
- Use The Index, Luke: https://use-the-index-luke.com/
- pgMustard (EXPLAIN visualizer): https://www.pgmustard.com/
- PgHero: https://github.com/ankane/pghero
