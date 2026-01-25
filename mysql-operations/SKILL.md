---
name: mysql-operations
description: This skill should be used when users need to work with MySQL/MariaDB databases, including schema design, SQL queries, optimization, indexing, transactions, and database operations. Provides best practices for relational database development.
---

# MySQL/MariaDB Operations

Comprehensive MySQL and MariaDB database operations, query optimization, schema design, and best practices guide.

## When to Use This Skill

Use this skill when:
- User mentions "MySQL", "MariaDB", or "relational database"
- User needs to design database schemas or tables
- User wants to write SQL queries or optimize performance
- User asks about indexing strategies or query optimization
- User needs help with transactions, stored procedures, or triggers
- User mentions "foreign keys", "joins", or "normalization"

## Key Features

### 1. Schema Design
- Table structure design
- Normalization (1NF, 2NF, 3NF, BCNF)
- Relationships (1-to-1, 1-to-many, many-to-many)
- Primary and foreign keys
- Data types selection

### 2. SQL Queries
- SELECT, INSERT, UPDATE, DELETE
- JOINs (INNER, LEFT, RIGHT, CROSS)
- Subqueries and CTEs
- Window functions
- Aggregations and GROUP BY

### 3. Performance Optimization
- Index strategies
- Query optimization
- EXPLAIN analysis
- Query caching
- Connection pooling

### 4. Advanced Features
- Transactions (ACID)
- Stored procedures
- Triggers
- Views
- Full-text search

## Installation & Connection

### Install MySQL/MariaDB

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server

# macOS (Homebrew)
brew install mysql

# Start service
sudo systemctl start mysql  # Linux
brew services start mysql   # macOS

# Secure installation
sudo mysql_secure_installation
```

### Node.js Connection (mysql2)

```javascript
const mysql = require('mysql2/promise');

// Create connection pool
const pool = mysql.createPool({
  host: 'localhost',
  user: 'root',
  password: 'password',
  database: 'mydb',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

// Execute query
async function queryDatabase() {
  try {
    const [rows] = await pool.execute(
      'SELECT * FROM users WHERE id = ?',
      [1]
    );
    console.log(rows);
  } catch (error) {
    console.error('Database error:', error);
  }
}
```

### Python Connection (mysql-connector-python)

```python
import mysql.connector
from mysql.connector import Error

# Create connection
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='password',
            database='mydb'
        )
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None

# Execute query
def execute_query(connection, query, params=None):
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
```

## Database & Table Management

### Create Database

```sql
-- Create database
CREATE DATABASE mydb
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- Use database
USE mydb;

-- Drop database
DROP DATABASE IF EXISTS mydb;
```

### Create Tables

```sql
-- Basic table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table with foreign key
CREATE TABLE posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    status ENUM('draft', 'published', 'archived') DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
) ENGINE=InnoDB;

-- Alter table
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
ALTER TABLE users MODIFY COLUMN email VARCHAR(150);
ALTER TABLE users DROP COLUMN phone;
ALTER TABLE users ADD CONSTRAINT uq_email UNIQUE (email);
```

## CRUD Operations

### INSERT

```sql
-- Insert single row
INSERT INTO users (username, email, password_hash)
VALUES ('john_doe', 'john@example.com', 'hashed_password');

-- Insert multiple rows
INSERT INTO users (username, email, password_hash) VALUES
('alice', 'alice@example.com', 'hash1'),
('bob', 'bob@example.com', 'hash2'),
('charlie', 'charlie@example.com', 'hash3');

-- Insert with SELECT
INSERT INTO archived_users (username, email)
SELECT username, email FROM users WHERE status = 'inactive';

-- Insert or update (UPSERT)
INSERT INTO users (id, username, email, password_hash)
VALUES (1, 'john', 'john@example.com', 'hash')
ON DUPLICATE KEY UPDATE
    username = VALUES(username),
    email = VALUES(email);
```

### SELECT

```sql
-- Basic SELECT
SELECT * FROM users;
SELECT username, email FROM users;
SELECT DISTINCT status FROM posts;

-- WHERE clause
SELECT * FROM users WHERE id = 1;
SELECT * FROM users WHERE status = 'active' AND created_at > '2024-01-01';
SELECT * FROM posts WHERE title LIKE '%mysql%';
SELECT * FROM users WHERE email IN ('user1@example.com', 'user2@example.com');
SELECT * FROM posts WHERE views BETWEEN 100 AND 1000;

-- ORDER BY and LIMIT
SELECT * FROM posts ORDER BY created_at DESC LIMIT 10;
SELECT * FROM users ORDER BY username ASC, created_at DESC;
SELECT * FROM posts LIMIT 10 OFFSET 20; -- Pagination

-- Aggregations
SELECT COUNT(*) FROM users;
SELECT status, COUNT(*) as count FROM posts GROUP BY status;
SELECT user_id, AVG(rating) as avg_rating FROM reviews GROUP BY user_id;
SELECT MAX(created_at), MIN(created_at) FROM posts;
SELECT SUM(price) FROM orders WHERE status = 'completed';

-- HAVING (filter after GROUP BY)
SELECT user_id, COUNT(*) as post_count
FROM posts
GROUP BY user_id
HAVING post_count > 5;
```

### UPDATE

```sql
-- Update single row
UPDATE users SET email = 'newemail@example.com' WHERE id = 1;

-- Update multiple rows
UPDATE posts SET status = 'published' WHERE status = 'draft' AND created_at < NOW();

-- Update with JOIN
UPDATE users u
INNER JOIN profiles p ON u.id = p.user_id
SET u.display_name = p.full_name
WHERE p.is_verified = 1;

-- Increment value
UPDATE posts SET views = views + 1 WHERE id = 123;
```

### DELETE

```sql
-- Delete specific rows
DELETE FROM users WHERE id = 1;
DELETE FROM posts WHERE created_at < DATE_SUB(NOW(), INTERVAL 1 YEAR);

-- Delete with JOIN
DELETE p FROM posts p
INNER JOIN users u ON p.user_id = u.id
WHERE u.status = 'deleted';

-- Truncate table (faster, resets AUTO_INCREMENT)
TRUNCATE TABLE temp_data;
```

## JOINs

### INNER JOIN

```sql
-- Get posts with user information
SELECT
    p.id,
    p.title,
    u.username,
    u.email
FROM posts p
INNER JOIN users u ON p.user_id = u.id
WHERE p.status = 'published';
```

### LEFT JOIN

```sql
-- Get all users and their posts (including users with no posts)
SELECT
    u.id,
    u.username,
    COUNT(p.id) as post_count
FROM users u
LEFT JOIN posts p ON u.id = p.user_id
GROUP BY u.id, u.username;
```

### RIGHT JOIN

```sql
-- Get all posts and their authors (including orphaned posts)
SELECT
    p.title,
    u.username
FROM posts p
RIGHT JOIN users u ON p.user_id = u.id;
```

### Multiple JOINs

```sql
-- Posts with author and category
SELECT
    p.title,
    u.username as author,
    c.name as category,
    COUNT(cm.id) as comment_count
FROM posts p
INNER JOIN users u ON p.user_id = u.id
INNER JOIN categories c ON p.category_id = c.id
LEFT JOIN comments cm ON p.id = cm.post_id
GROUP BY p.id, u.username, c.name;
```

## Subqueries

```sql
-- Subquery in WHERE
SELECT * FROM users
WHERE id IN (
    SELECT DISTINCT user_id FROM posts WHERE status = 'published'
);

-- Subquery in SELECT
SELECT
    username,
    (SELECT COUNT(*) FROM posts WHERE user_id = u.id) as post_count
FROM users u;

-- Correlated subquery
SELECT u.username
FROM users u
WHERE (
    SELECT COUNT(*) FROM posts p WHERE p.user_id = u.id
) > 5;
```

## Common Table Expressions (CTEs)

```sql
-- Basic CTE
WITH active_users AS (
    SELECT id, username FROM users WHERE status = 'active'
)
SELECT * FROM active_users WHERE username LIKE 'a%';

-- Multiple CTEs
WITH
    user_stats AS (
        SELECT user_id, COUNT(*) as post_count
        FROM posts
        GROUP BY user_id
    ),
    top_users AS (
        SELECT user_id FROM user_stats WHERE post_count > 10
    )
SELECT u.username, us.post_count
FROM users u
INNER JOIN user_stats us ON u.id = us.user_id
WHERE u.id IN (SELECT user_id FROM top_users);

-- Recursive CTE (hierarchical data)
WITH RECURSIVE category_tree AS (
    -- Base case
    SELECT id, name, parent_id, 1 as level
    FROM categories
    WHERE parent_id IS NULL

    UNION ALL

    -- Recursive case
    SELECT c.id, c.name, c.parent_id, ct.level + 1
    FROM categories c
    INNER JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT * FROM category_tree;
```

## Window Functions

```sql
-- Row number
SELECT
    username,
    created_at,
    ROW_NUMBER() OVER (ORDER BY created_at) as row_num
FROM users;

-- Rank (with gaps for ties)
SELECT
    username,
    score,
    RANK() OVER (ORDER BY score DESC) as rank
FROM users;

-- Dense rank (no gaps)
SELECT
    username,
    score,
    DENSE_RANK() OVER (ORDER BY score DESC) as rank
FROM users;

-- Partition by
SELECT
    category,
    title,
    price,
    AVG(price) OVER (PARTITION BY category) as avg_category_price
FROM products;

-- Running total
SELECT
    date,
    amount,
    SUM(amount) OVER (ORDER BY date) as running_total
FROM transactions;
```

## Indexes

### Create Indexes

```sql
-- Single column index
CREATE INDEX idx_username ON users(username);

-- Composite index
CREATE INDEX idx_user_status ON posts(user_id, status);

-- Unique index
CREATE UNIQUE INDEX uq_email ON users(email);

-- Full-text index
CREATE FULLTEXT INDEX ft_content ON posts(title, content);

-- Prefix index (for long strings)
CREATE INDEX idx_url_prefix ON pages(url(50));
```

### Manage Indexes

```sql
-- Show indexes
SHOW INDEX FROM users;

-- Drop index
DROP INDEX idx_username ON users;

-- Analyze table (update index statistics)
ANALYZE TABLE users;
```

### Index Best Practices

```sql
-- Good: Use indexes for WHERE, JOIN, ORDER BY
CREATE INDEX idx_status_created ON posts(status, created_at DESC);

SELECT * FROM posts
WHERE status = 'published'
ORDER BY created_at DESC
LIMIT 10;

-- Good: Covering index (includes all columns needed)
CREATE INDEX idx_user_info ON users(id, username, email);

SELECT id, username, email FROM users WHERE id = 1;
```

## Query Optimization

### EXPLAIN

```sql
-- Analyze query execution
EXPLAIN SELECT * FROM users WHERE username = 'john';

-- Extended EXPLAIN
EXPLAIN EXTENDED SELECT u.*, COUNT(p.id) as post_count
FROM users u
LEFT JOIN posts p ON u.id = p.user_id
GROUP BY u.id;

-- JSON format (more details)
EXPLAIN FORMAT=JSON SELECT * FROM posts WHERE status = 'published';
```

### Optimization Tips

```sql
-- Bad: SELECT *
SELECT * FROM users; -- Retrieves unnecessary columns

-- Good: Select only needed columns
SELECT id, username, email FROM users;

-- Bad: No index on WHERE clause
SELECT * FROM posts WHERE YEAR(created_at) = 2024; -- Function prevents index use

-- Good: Range query using index
SELECT * FROM posts WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01';

-- Bad: Leading wildcard prevents index use
SELECT * FROM users WHERE email LIKE '%@example.com';

-- Good: Trailing wildcard can use index
SELECT * FROM users WHERE email LIKE 'john%';

-- Use LIMIT for large result sets
SELECT * FROM logs ORDER BY created_at DESC LIMIT 100;
```

## Transactions

```sql
-- Basic transaction
START TRANSACTION;

UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

COMMIT; -- or ROLLBACK on error

-- Transaction with savepoint
START TRANSACTION;

INSERT INTO orders (user_id, total) VALUES (1, 100);
SAVEPOINT order_created;

INSERT INTO order_items (order_id, product_id) VALUES (LAST_INSERT_ID(), 5);

-- Rollback to savepoint if needed
-- ROLLBACK TO SAVEPOINT order_created;

COMMIT;

-- Transaction isolation levels
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
```

## Stored Procedures

```sql
-- Create stored procedure
DELIMITER //

CREATE PROCEDURE GetUserPosts(IN userId INT)
BEGIN
    SELECT * FROM posts WHERE user_id = userId;
END //

DELIMITER ;

-- Call procedure
CALL GetUserPosts(1);

-- Procedure with output parameter
DELIMITER //

CREATE PROCEDURE CountUserPosts(IN userId INT, OUT postCount INT)
BEGIN
    SELECT COUNT(*) INTO postCount
    FROM posts
    WHERE user_id = userId;
END //

DELIMITER ;

-- Call with output
CALL CountUserPosts(1, @count);
SELECT @count;

-- Drop procedure
DROP PROCEDURE IF EXISTS GetUserPosts;
```

## Triggers

```sql
-- Before insert trigger
DELIMITER //

CREATE TRIGGER before_user_insert
BEFORE INSERT ON users
FOR EACH ROW
BEGIN
    SET NEW.created_at = NOW();
    SET NEW.updated_at = NOW();
END //

DELIMITER ;

-- After update trigger
DELIMITER //

CREATE TRIGGER after_post_update
AFTER UPDATE ON posts
FOR EACH ROW
BEGIN
    IF NEW.status != OLD.status THEN
        INSERT INTO post_history (post_id, old_status, new_status, changed_at)
        VALUES (NEW.id, OLD.status, NEW.status, NOW());
    END IF;
END //

DELIMITER ;

-- Drop trigger
DROP TRIGGER IF EXISTS before_user_insert;
```

## Views

```sql
-- Create view
CREATE VIEW active_users AS
SELECT id, username, email
FROM users
WHERE status = 'active';

-- Use view
SELECT * FROM active_users;

-- Updatable view
CREATE VIEW user_profiles AS
SELECT id, username, email, bio
FROM users;

-- Update through view
UPDATE user_profiles SET bio = 'New bio' WHERE id = 1;

-- Drop view
DROP VIEW IF EXISTS active_users;
```

## Full-Text Search

```sql
-- Create full-text index
CREATE FULLTEXT INDEX ft_search ON articles(title, content);

-- Natural language search
SELECT * FROM articles
WHERE MATCH(title, content) AGAINST('mysql database' IN NATURAL LANGUAGE MODE);

-- Boolean mode search
SELECT * FROM articles
WHERE MATCH(title, content) AGAINST('+mysql -oracle' IN BOOLEAN MODE);

-- With relevance score
SELECT *, MATCH(title, content) AGAINST('mysql') as relevance
FROM articles
WHERE MATCH(title, content) AGAINST('mysql')
ORDER BY relevance DESC;
```

## Database Security

```sql
-- Create user
CREATE USER 'appuser'@'localhost' IDENTIFIED BY 'secure_password';

-- Grant privileges
GRANT SELECT, INSERT, UPDATE, DELETE ON mydb.* TO 'appuser'@'localhost';

-- Grant specific table access
GRANT SELECT ON mydb.users TO 'readonly'@'localhost';

-- Show grants
SHOW GRANTS FOR 'appuser'@'localhost';

-- Revoke privileges
REVOKE DELETE ON mydb.* FROM 'appuser'@'localhost';

-- Drop user
DROP USER 'appuser'@'localhost';

-- Change password
ALTER USER 'appuser'@'localhost' IDENTIFIED BY 'new_password';
```

## Backup & Restore

```bash
# Backup single database
mysqldump -u root -p mydb > backup.sql

# Backup all databases
mysqldump -u root -p --all-databases > all_backup.sql

# Backup specific tables
mysqldump -u root -p mydb users posts > tables_backup.sql

# Backup with gzip compression
mysqldump -u root -p mydb | gzip > backup.sql.gz

# Restore database
mysql -u root -p mydb < backup.sql

# Restore from gzip
gunzip < backup.sql.gz | mysql -u root -p mydb
```

## Performance Tuning

### Configuration (my.cnf)

```ini
[mysqld]
# InnoDB settings
innodb_buffer_pool_size = 1G  # 70-80% of available RAM
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2

# Query cache (deprecated in MySQL 8.0+)
query_cache_type = 1
query_cache_size = 64M

# Connection settings
max_connections = 200
wait_timeout = 600

# Slow query log
slow_query_log = 1
long_query_time = 2
slow_query_log_file = /var/log/mysql/slow.log
```

### Query Cache

```sql
-- Show cache status
SHOW STATUS LIKE 'Qcache%';

-- Clear cache
FLUSH QUERY CACHE;
RESET QUERY CACHE;
```

## Common Patterns

### Pagination

```sql
-- Limit/Offset (simple but slow for large offsets)
SELECT * FROM posts ORDER BY created_at DESC LIMIT 10 OFFSET 20;

-- Keyset pagination (faster for large datasets)
SELECT * FROM posts
WHERE id < last_seen_id
ORDER BY id DESC
LIMIT 10;
```

### Soft Delete

```sql
-- Add deleted_at column
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP NULL;

-- Soft delete
UPDATE users SET deleted_at = NOW() WHERE id = 1;

-- Query excluding deleted
SELECT * FROM users WHERE deleted_at IS NULL;

-- Restore soft deleted
UPDATE users SET deleted_at = NULL WHERE id = 1;
```

### Audit Trail

```sql
CREATE TABLE audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(50),
    record_id INT,
    action ENUM('INSERT', 'UPDATE', 'DELETE'),
    old_values JSON,
    new_values JSON,
    user_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## References

- MySQL Documentation: https://dev.mysql.com/doc/
- MariaDB Documentation: https://mariadb.com/kb/en/documentation/
- SQL Style Guide: https://www.sqlstyle.guide/
- MySQL Performance Blog: https://www.percona.com/blog/

---

**Created for**: awesome-claude-skills repository
**Version**: 1.0.0
**Last Updated**: January 25, 2026
