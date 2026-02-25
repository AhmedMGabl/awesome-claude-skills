---
name: postgresql-operations
description: PostgreSQL database operations including schema design, complex queries, window functions, CTEs, JSONB, full-text search, indexing strategies, transactions, performance tuning, and PostgreSQL-specific best practices.
---

# PostgreSQL Operations

This skill should be used when working with PostgreSQL databases. It covers schema design, advanced query patterns, performance optimization, PostgreSQL-specific features like JSONB and full-text search, and production operations.

## When to Use This Skill

Use this skill when you need to:

- Design PostgreSQL schemas with proper types and constraints
- Write complex queries with CTEs, window functions, and subqueries
- Work with JSONB for semi-structured data
- Implement full-text search
- Optimize queries with proper indexing strategies
- Handle transactions and concurrency
- Use PostgreSQL-specific features (arrays, enums, extensions)
- Monitor and tune database performance

## Schema Design

### Data Types

```sql
-- Integer types
id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
user_id     INTEGER,
views       BIGINT DEFAULT 0,
rating      SMALLINT CHECK (rating BETWEEN 1 AND 5),

-- Text types
name        TEXT NOT NULL,                        -- unlimited
username    VARCHAR(50) NOT NULL,                 -- limited
description TEXT,
status      VARCHAR(20) DEFAULT 'active',

-- Numeric types
price       NUMERIC(10, 2) NOT NULL,              -- exact decimal
lat         DOUBLE PRECISION,                      -- floating point
percentage  REAL,

-- Date/time types
created_at  TIMESTAMPTZ DEFAULT NOW() NOT NULL,   -- timezone-aware (always use!)
updated_at  TIMESTAMPTZ DEFAULT NOW() NOT NULL,
birth_date  DATE,
duration    INTERVAL,
start_time  TIME,

-- Boolean
is_active   BOOLEAN DEFAULT TRUE NOT NULL,
is_deleted  BOOLEAN DEFAULT FALSE,

-- UUID
id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,

-- Arrays
tags        TEXT[] DEFAULT '{}',
scores      INTEGER[],

-- JSONB (binary JSON - indexable, faster than JSON)
metadata    JSONB DEFAULT '{}',
settings    JSONB,

-- Enums
CREATE TYPE user_role AS ENUM ('admin', 'moderator', 'user');
role        user_role DEFAULT 'user' NOT NULL,

-- Network types
ip_address  INET,
mac_addr    MACADDR,

-- Full-text search
search_vector TSVECTOR GENERATED ALWAYS AS (
  to_tsvector('english', coalesce(title, '') || ' ' || coalesce(body, ''))
) STORED,
```

### Complete Schema Example

```sql
-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";    -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "pg_trgm";     -- trigram indexes
CREATE EXTENSION IF NOT EXISTS "btree_gin";   -- GIN indexes for btree types
CREATE EXTENSION IF NOT EXISTS "unaccent";    -- Remove accents in search

-- Users table
CREATE TABLE users (
  id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  email         TEXT NOT NULL UNIQUE,
  username      VARCHAR(50) NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  role          user_role DEFAULT 'user' NOT NULL,
  metadata      JSONB DEFAULT '{}' NOT NULL,
  is_active     BOOLEAN DEFAULT TRUE NOT NULL,
  created_at    TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  updated_at    TIMESTAMPTZ DEFAULT NOW() NOT NULL,

  -- Constraints
  CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z]{2,}$'),
  CONSTRAINT username_format CHECK (username ~ '^[a-zA-Z0-9_]{3,50}$')
);

-- Posts table
CREATE TABLE posts (
  id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title         TEXT NOT NULL,
  slug          TEXT NOT NULL UNIQUE,
  body          TEXT,
  status        TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
  tags          TEXT[] DEFAULT '{}',
  view_count    INTEGER DEFAULT 0 NOT NULL,
  published_at  TIMESTAMPTZ,
  created_at    TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  updated_at    TIMESTAMPTZ DEFAULT NOW() NOT NULL,

  -- Generated full-text search column
  search_vector TSVECTOR GENERATED ALWAYS AS (
    setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(body, '')), 'B')
  ) STORED
);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_updated_at
  BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER posts_updated_at
  BEFORE UPDATE ON posts
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

## Indexing Strategies

```sql
-- B-tree (default) - equality, range, sort
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);
CREATE INDEX idx_posts_status ON posts(status) WHERE status = 'published';  -- partial index

-- Composite index - order matters! Most selective first, then sort order
CREATE INDEX idx_posts_status_created ON posts(status, created_at DESC);

-- Unique index
CREATE UNIQUE INDEX idx_users_email_lower ON users(lower(email));  -- case-insensitive unique

-- GIN for arrays, JSONB, full-text
CREATE INDEX idx_posts_tags ON posts USING GIN(tags);
CREATE INDEX idx_users_metadata ON users USING GIN(metadata);
CREATE INDEX idx_posts_search ON posts USING GIN(search_vector);

-- GiST for geometric, range types
CREATE INDEX idx_events_period ON events USING GIST(period);

-- BRIN for large sequential tables (timestamps, IDs)
CREATE INDEX idx_logs_created_at ON logs USING BRIN(created_at);

-- Trigram for LIKE/ILIKE searches
CREATE INDEX idx_users_username_trgm ON users USING GIN(username gin_trgm_ops);

-- Covering index (include non-key columns to avoid heap fetch)
CREATE INDEX idx_posts_user_published ON posts(user_id, published_at DESC)
  INCLUDE (title, slug);

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
WHERE idx_scan = 0  -- Unused indexes
ORDER BY pg_relation_size(indexrelid) DESC;
```

## Query Patterns

### CTEs (Common Table Expressions)

```sql
-- Basic CTE
WITH active_users AS (
  SELECT id, email, username
  FROM users
  WHERE is_active = TRUE
    AND created_at > NOW() - INTERVAL '30 days'
),
user_post_counts AS (
  SELECT user_id, COUNT(*) AS post_count
  FROM posts
  WHERE status = 'published'
  GROUP BY user_id
)
SELECT u.username, u.email, COALESCE(pc.post_count, 0) AS posts
FROM active_users u
LEFT JOIN user_post_counts pc ON u.id = pc.user_id
ORDER BY posts DESC;

-- Recursive CTE (hierarchical data)
WITH RECURSIVE category_tree AS (
  -- Base case: root categories
  SELECT id, name, parent_id, 0 AS depth, ARRAY[id] AS path
  FROM categories
  WHERE parent_id IS NULL

  UNION ALL

  -- Recursive case
  SELECT c.id, c.name, c.parent_id, ct.depth + 1, ct.path || c.id
  FROM categories c
  JOIN category_tree ct ON c.parent_id = ct.id
  WHERE NOT c.id = ANY(ct.path)  -- Prevent cycles
)
SELECT * FROM category_tree ORDER BY path;

-- CTE with data modification
WITH deleted_posts AS (
  DELETE FROM posts
  WHERE status = 'archived'
    AND updated_at < NOW() - INTERVAL '1 year'
  RETURNING id, user_id, title
)
INSERT INTO posts_archive
SELECT *, NOW() AS archived_at
FROM deleted_posts;
```

### Window Functions

```sql
-- ROW_NUMBER, RANK, DENSE_RANK
SELECT
  username,
  view_count,
  ROW_NUMBER() OVER (ORDER BY view_count DESC) AS row_num,
  RANK() OVER (ORDER BY view_count DESC) AS rank,
  DENSE_RANK() OVER (ORDER BY view_count DESC) AS dense_rank
FROM users;

-- Partition by group
SELECT
  user_id,
  title,
  created_at,
  ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS post_rank
FROM posts
WHERE status = 'published';

-- Get latest post per user (using window function)
SELECT user_id, title, created_at
FROM (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn
  FROM posts
  WHERE status = 'published'
) ranked
WHERE rn = 1;

-- Running totals and moving averages
SELECT
  date_trunc('day', created_at) AS day,
  COUNT(*) AS daily_count,
  SUM(COUNT(*)) OVER (ORDER BY date_trunc('day', created_at)) AS running_total,
  AVG(COUNT(*)) OVER (
    ORDER BY date_trunc('day', created_at)
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) AS moving_avg_7d
FROM posts
WHERE created_at > NOW() - INTERVAL '90 days'
GROUP BY day
ORDER BY day;

-- LAG and LEAD for comparisons
SELECT
  date_trunc('month', created_at) AS month,
  COUNT(*) AS count,
  LAG(COUNT(*)) OVER (ORDER BY date_trunc('month', created_at)) AS prev_month,
  COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY date_trunc('month', created_at)) AS change
FROM posts
GROUP BY month
ORDER BY month;

-- NTILE for percentiles
SELECT
  username,
  view_count,
  NTILE(4) OVER (ORDER BY view_count) AS quartile
FROM users;
```

### JSONB Operations

```sql
-- Insert JSONB
INSERT INTO users (email, username, password_hash, metadata)
VALUES ('user@example.com', 'johndoe', 'hash', '{
  "preferences": {"theme": "dark", "language": "en"},
  "social": {"twitter": "@johndoe"},
  "subscription": "premium"
}');

-- Query JSONB
SELECT username, metadata->>'subscription' AS plan           -- text extraction
FROM users
WHERE metadata->>'subscription' = 'premium';

SELECT username, metadata->'preferences'->>'theme' AS theme  -- nested
FROM users;

SELECT username, metadata @> '{"subscription": "premium"}'  -- contains
FROM users;

-- JSONB in WHERE clause
SELECT * FROM users
WHERE metadata ? 'social'                                    -- key exists
  AND metadata->>'subscription' IN ('premium', 'enterprise')
  AND (metadata->'preferences'->>'theme') = 'dark';

-- Update JSONB
UPDATE users
SET metadata = metadata || '{"subscription": "enterprise"}'::jsonb
WHERE id = $1;

-- Set nested value
UPDATE users
SET metadata = jsonb_set(metadata, '{preferences, theme}', '"light"')
WHERE id = $1;

-- Remove key
UPDATE users
SET metadata = metadata - 'old_field'
WHERE metadata ? 'old_field';

-- Aggregate JSONB
SELECT
  jsonb_agg(jsonb_build_object('id', id, 'title', title)) AS posts
FROM posts
WHERE user_id = $1;

-- JSONB array operations
SELECT * FROM posts WHERE tags @> ARRAY['postgresql'];      -- array contains
SELECT * FROM posts WHERE tags && ARRAY['postgresql', 'sql']; -- overlap

-- Expand JSONB array
SELECT id, jsonb_array_elements_text(metadata->'skills') AS skill
FROM users
WHERE metadata ? 'skills';
```

### Full-Text Search

```sql
-- Basic full-text search
SELECT id, title, ts_rank(search_vector, query) AS rank
FROM posts,
     to_tsquery('english', 'postgresql & optimization') AS query
WHERE search_vector @@ query
ORDER BY rank DESC
LIMIT 20;

-- Phrase search
SELECT title FROM posts
WHERE search_vector @@ phraseto_tsquery('english', 'query optimization');

-- With highlighting
SELECT
  title,
  ts_headline(
    'english',
    body,
    to_tsquery('english', 'postgresql'),
    'StartSel=<mark>, StopSel=</mark>, MaxWords=50, MinWords=20'
  ) AS excerpt
FROM posts
WHERE search_vector @@ to_tsquery('english', 'postgresql');

-- Weighted search (title matters more than body)
SELECT
  title,
  ts_rank_cd(
    setweight(to_tsvector('english', title), 'A') ||
    setweight(to_tsvector('english', coalesce(body, '')), 'B'),
    to_tsquery('english', 'query & optimization')
  ) AS rank
FROM posts
ORDER BY rank DESC;

-- Trigram similarity (fuzzy search)
SELECT username, similarity(username, 'johndoe') AS sim
FROM users
WHERE username % 'johndoe'  -- threshold ~0.3
ORDER BY sim DESC
LIMIT 10;
```

## Transactions and Concurrency

```sql
-- Basic transaction
BEGIN;
  UPDATE accounts SET balance = balance - 100 WHERE id = 1;
  UPDATE accounts SET balance = balance + 100 WHERE id = 2;
  -- Check constraint
  SELECT balance FROM accounts WHERE id = 1 AND balance >= 0;
COMMIT;

-- Savepoints
BEGIN;
  INSERT INTO orders (user_id, total) VALUES (1, 100) RETURNING id;
  SAVEPOINT before_items;
  INSERT INTO order_items VALUES (1, 'product1', 50);
  -- If this fails, rollback to savepoint
  ROLLBACK TO SAVEPOINT before_items;
  INSERT INTO order_items VALUES (1, 'product2', 100);
COMMIT;

-- SELECT FOR UPDATE (pessimistic locking)
BEGIN;
  SELECT * FROM inventory WHERE product_id = $1 FOR UPDATE;
  -- Only proceed if stock > 0
  UPDATE inventory SET stock = stock - 1 WHERE product_id = $1 AND stock > 0;
COMMIT;

-- SELECT FOR UPDATE SKIP LOCKED (queue processing)
BEGIN;
  SELECT id FROM job_queue
  WHERE status = 'pending'
  ORDER BY created_at
  LIMIT 1
  FOR UPDATE SKIP LOCKED;

  UPDATE job_queue SET status = 'processing' WHERE id = $1;
COMMIT;

-- Advisory locks (application-level)
SELECT pg_advisory_lock(hashtext('resource_name'));
-- ... critical section ...
SELECT pg_advisory_unlock(hashtext('resource_name'));

-- Isolation levels
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
-- ...
COMMIT;
```

## Performance Optimization

### Query Analysis

```sql
-- EXPLAIN ANALYZE
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT u.username, COUNT(p.id) AS post_count
FROM users u
LEFT JOIN posts p ON u.id = p.user_id
WHERE u.is_active = TRUE
GROUP BY u.id, u.username
ORDER BY post_count DESC
LIMIT 10;

-- Find slow queries
SELECT
  query,
  calls,
  total_exec_time / calls AS avg_ms,
  rows / calls AS avg_rows,
  100.0 * shared_blks_hit / NULLIF(shared_blks_hit + shared_blks_read, 0) AS hit_pct
FROM pg_stat_statements
ORDER BY avg_ms DESC
LIMIT 20;

-- Table statistics
SELECT
  relname,
  n_live_tup AS live_rows,
  n_dead_tup AS dead_rows,
  last_vacuum,
  last_autovacuum,
  last_analyze
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;

-- Missing indexes (high sequential scans)
SELECT relname, seq_scan, idx_scan,
  n_live_tup AS row_count,
  CASE WHEN seq_scan > 0
    THEN seq_tup_read::float / seq_scan
    ELSE 0
  END AS avg_seq_read
FROM pg_stat_user_tables
WHERE seq_scan > 10
  AND n_live_tup > 1000
ORDER BY seq_scan DESC;
```

### Partitioning

```sql
-- Range partitioning (good for time-series)
CREATE TABLE events (
  id          BIGINT NOT NULL,
  event_type  TEXT NOT NULL,
  payload     JSONB,
  created_at  TIMESTAMPTZ NOT NULL
) PARTITION BY RANGE (created_at);

CREATE TABLE events_2024_q1 PARTITION OF events
  FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

CREATE TABLE events_2024_q2 PARTITION OF events
  FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');

-- List partitioning (good for categorical data)
CREATE TABLE orders (
  id     BIGINT NOT NULL,
  region TEXT NOT NULL,
  total  NUMERIC(12, 2)
) PARTITION BY LIST (region);

CREATE TABLE orders_us PARTITION OF orders
  FOR VALUES IN ('us-east', 'us-west', 'us-central');

CREATE TABLE orders_eu PARTITION OF orders
  FOR VALUES IN ('eu-west', 'eu-central');
```

## Stored Procedures and Functions

```sql
-- Function returning a value
CREATE OR REPLACE FUNCTION get_user_stats(p_user_id UUID)
RETURNS TABLE (
  post_count    BIGINT,
  total_views   BIGINT,
  avg_views     NUMERIC
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    COUNT(*) AS post_count,
    SUM(view_count)::BIGINT AS total_views,
    ROUND(AVG(view_count), 2) AS avg_views
  FROM posts
  WHERE user_id = p_user_id
    AND status = 'published';
END;
$$ LANGUAGE plpgsql STABLE;

-- Procedure (for transactions)
CREATE OR REPLACE PROCEDURE transfer_balance(
  p_from_id INTEGER,
  p_to_id   INTEGER,
  p_amount  NUMERIC
)
LANGUAGE plpgsql AS $$
DECLARE
  v_balance NUMERIC;
BEGIN
  SELECT balance INTO v_balance FROM accounts WHERE id = p_from_id FOR UPDATE;

  IF v_balance < p_amount THEN
    RAISE EXCEPTION 'Insufficient balance: % < %', v_balance, p_amount;
  END IF;

  UPDATE accounts SET balance = balance - p_amount WHERE id = p_from_id;
  UPDATE accounts SET balance = balance + p_amount WHERE id = p_to_id;

  INSERT INTO transactions (from_id, to_id, amount, created_at)
  VALUES (p_from_id, p_to_id, p_amount, NOW());
END;
$$;

-- Call procedure
CALL transfer_balance(1, 2, 50.00);

-- Trigger function for audit log
CREATE OR REPLACE FUNCTION audit_changes()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'DELETE' THEN
    INSERT INTO audit_log (table_name, operation, old_data, changed_at)
    VALUES (TG_TABLE_NAME, 'DELETE', row_to_json(OLD), NOW());
    RETURN OLD;
  ELSE
    INSERT INTO audit_log (table_name, operation, old_data, new_data, changed_at)
    VALUES (TG_TABLE_NAME, TG_OP, row_to_json(OLD), row_to_json(NEW), NOW());
    RETURN NEW;
  END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_audit
  AFTER INSERT OR UPDATE OR DELETE ON users
  FOR EACH ROW EXECUTE FUNCTION audit_changes();
```

## Node.js Integration (with pg/postgres.js)

```typescript
// Using postgres.js (modern, recommended)
import postgres from "postgres";

const sql = postgres(process.env.DATABASE_URL!, {
  max: 10,           // connection pool size
  idle_timeout: 20,  // close idle connections after 20s
  connect_timeout: 10,
});

// Parameterized queries (safe from SQL injection)
async function getUsers(page: number, limit: number) {
  return sql`
    SELECT id, email, username, created_at
    FROM users
    WHERE is_active = TRUE
    ORDER BY created_at DESC
    LIMIT ${limit} OFFSET ${(page - 1) * limit}
  `;
}

// Transaction
async function createPostWithTags(userId: string, title: string, tags: string[]) {
  return sql.begin(async (sql) => {
    const [post] = await sql`
      INSERT INTO posts (user_id, title, slug, tags)
      VALUES (${userId}, ${title}, ${slugify(title)}, ${sql.array(tags)})
      RETURNING *
    `;

    await sql`
      UPDATE users SET post_count = post_count + 1 WHERE id = ${userId}
    `;

    return post;
  });
}

// JSON aggregation
async function getUserWithPosts(userId: string) {
  const [result] = await sql`
    SELECT
      u.id,
      u.username,
      u.email,
      json_agg(
        json_build_object(
          'id', p.id,
          'title', p.title,
          'created_at', p.created_at
        ) ORDER BY p.created_at DESC
      ) FILTER (WHERE p.id IS NOT NULL) AS posts
    FROM users u
    LEFT JOIN posts p ON u.id = p.user_id AND p.status = 'published'
    WHERE u.id = ${userId}
    GROUP BY u.id
  `;
  return result;
}
```

## Maintenance and Monitoring

```sql
-- Database sizes
SELECT
  datname AS database,
  pg_size_pretty(pg_database_size(datname)) AS size
FROM pg_database
ORDER BY pg_database_size(datname) DESC;

-- Table sizes with indexes
SELECT
  relname AS table,
  pg_size_pretty(pg_total_relation_size(oid)) AS total,
  pg_size_pretty(pg_relation_size(oid)) AS table_size,
  pg_size_pretty(pg_indexes_size(oid)) AS indexes_size
FROM pg_class
WHERE relkind = 'r'
  AND relnamespace = 'public'::regnamespace
ORDER BY pg_total_relation_size(oid) DESC;

-- Active connections
SELECT
  pid,
  usename,
  application_name,
  state,
  wait_event_type,
  wait_event,
  query_start,
  LEFT(query, 100) AS query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY query_start;

-- Lock waits
SELECT
  blocked_locks.pid AS blocked_pid,
  blocked_activity.query AS blocked_query,
  blocking_locks.pid AS blocking_pid,
  blocking_activity.query AS blocking_query
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
  AND blocking_locks.pid != blocked_locks.pid
  AND blocking_locks.granted
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

-- Manual vacuum and analyze
VACUUM ANALYZE users;
VACUUM FULL posts;  -- Rewrites table (locks table, reclaims disk space)
```

## Additional Resources

- PostgreSQL Documentation: https://www.postgresql.org/docs/current/
- postgres.js: https://github.com/porsager/postgres
- pgvector (vector search): https://github.com/pgvector/pgvector
- EXPLAIN analyzer: https://explain.dalibo.com/
- pg_stat_statements: https://www.postgresql.org/docs/current/pgstatstatements.html
