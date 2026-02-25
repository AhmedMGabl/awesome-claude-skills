---
name: mysql-patterns
description: MySQL patterns covering schema design, indexes, joins, subqueries, window functions, stored procedures, transactions, replication, and performance optimization.
---

# MySQL Patterns

This skill should be used when working with MySQL databases. It covers schema design, indexes, joins, window functions, stored procedures, transactions, and optimization.

## When to Use This Skill

Use this skill when you need to:

- Design MySQL schemas with proper data types
- Optimize queries with indexes and explain plans
- Use joins, subqueries, and window functions
- Implement stored procedures and triggers
- Configure replication and backups

## Schema Design

```sql
CREATE TABLE users (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'editor', 'user') DEFAULT 'user',
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_role (role),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE posts (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) NOT NULL UNIQUE,
    body TEXT NOT NULL,
    published BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_published (user_id, published),
    FULLTEXT INDEX ft_title_body (title, body)
) ENGINE=InnoDB;
```

## Joins

```sql
-- Inner join
SELECT p.title, u.username
FROM posts p
INNER JOIN users u ON u.id = p.user_id
WHERE p.published = TRUE;

-- Left join with aggregation
SELECT u.username, COUNT(p.id) AS post_count
FROM users u
LEFT JOIN posts p ON p.user_id = u.id AND p.published = TRUE
GROUP BY u.id
ORDER BY post_count DESC;

-- Multi-table join
SELECT p.title, u.username, GROUP_CONCAT(t.name) AS tags
FROM posts p
JOIN users u ON u.id = p.user_id
LEFT JOIN post_tags pt ON pt.post_id = p.id
LEFT JOIN tags t ON t.id = pt.tag_id
WHERE p.published = TRUE
GROUP BY p.id
ORDER BY p.created_at DESC
LIMIT 20;
```

## Window Functions

```sql
-- Rank users by post count
SELECT username, post_count,
    RANK() OVER (ORDER BY post_count DESC) AS ranking
FROM (
    SELECT u.username, COUNT(p.id) AS post_count
    FROM users u LEFT JOIN posts p ON p.user_id = u.id
    GROUP BY u.id
) sub;

-- Running total
SELECT date, revenue,
    SUM(revenue) OVER (ORDER BY date ROWS UNBOUNDED PRECEDING) AS running_total
FROM daily_revenue;

-- Moving average
SELECT date, revenue,
    AVG(revenue) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS avg_7day
FROM daily_revenue;
```

## Full-Text Search

```sql
SELECT title, MATCH(title, body) AGAINST('database optimization' IN NATURAL LANGUAGE MODE) AS relevance
FROM posts
WHERE MATCH(title, body) AGAINST('database optimization' IN NATURAL LANGUAGE MODE)
ORDER BY relevance DESC
LIMIT 10;
```

## Transactions

```sql
START TRANSACTION;

UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

INSERT INTO transfers (from_id, to_id, amount) VALUES (1, 2, 100);

COMMIT;
-- or ROLLBACK on error;
```

## Stored Procedure

```sql
DELIMITER //
CREATE PROCEDURE create_user_with_profile(
    IN p_username VARCHAR(50),
    IN p_email VARCHAR(255),
    IN p_bio TEXT
)
BEGIN
    DECLARE user_id BIGINT;

    START TRANSACTION;
    INSERT INTO users (username, email) VALUES (p_username, p_email);
    SET user_id = LAST_INSERT_ID();
    INSERT INTO profiles (user_id, bio) VALUES (user_id, p_bio);
    COMMIT;
END //
DELIMITER ;

CALL create_user_with_profile('alice', 'alice@example.com', 'Hello world');
```

## Performance

```sql
-- Explain query plan
EXPLAIN ANALYZE SELECT * FROM posts WHERE user_id = 1 AND published = TRUE;

-- Show slow queries
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;
```

## Additional Resources

- MySQL: https://dev.mysql.com/doc/refman/8.0/en/
- Performance: https://dev.mysql.com/doc/refman/8.0/en/optimization.html
- Window Functions: https://dev.mysql.com/doc/refman/8.0/en/window-functions.html
