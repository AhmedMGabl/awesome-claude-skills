---
name: redis-caching
description: This skill should be used when implementing caching strategies, session management, rate limiting, real-time features, or performance optimization using Redis in-memory data store.
---

# Redis Caching & Performance

Complete guide for using Redis as a caching layer, session store, rate limiter, and real-time data platform.

## When to Use This Skill

- Implement caching (10-100x performance improvement)
- Manage user sessions across distributed systems
- Rate limiting and request throttling
- Real-time features (notifications, chat, live updates)
- Temporary data with automatic expiration
- Counters, leaderboards, analytics
- Background job queues
- Distributed locks

## Installation & Setup

```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Start Redis
redis-server

# Test connection
redis-cli ping
# Response: PONG
```

## Connection Examples

**Node.js (ioredis)**:
```javascript
const Redis = require('ioredis');

const redis = new Redis({
  host: 'localhost',
  port: 6379,
  password: process.env.REDIS_PASSWORD,
  retryStrategy: (times) => Math.min(times * 50, 2000)
});

await redis.ping(); // PONG
```

**Python (redis-py)**:
```python
import redis
import os

r = redis.Redis(
    host='localhost',
    port=6379,
    password=os.getenv('REDIS_PASSWORD'),
    decode_responses=True
)

print(r.ping())  # True
```

## Core Caching Patterns

### 1. Cache-Aside (Lazy Loading)

Most common pattern - application manages cache:

```javascript
async function getUser(userId) {
  const key = `user:${userId}`;

  // Try cache first
  let user = await redis.get(key);
  if (user) {
    return JSON.parse(user);
  }

  // Cache miss - fetch from database
  user = await db.users.findById(userId);

  // Store in cache with 1 hour TTL
  await redis.setex(key, 3600, JSON.stringify(user));

  return user;
}

// Invalidate on update
async function updateUser(userId, updates) {
  const user = await db.users.update(userId, updates);
  await redis.del(`user:${userId}`);
  return user;
}
```

### 2. Write-Through Cache

Update cache when writing to database:

```javascript
async function createUser(userData) {
  const user = await db.users.create(userData);

  const key = `user:${user.id}`;
  await redis.setex(key, 3600, JSON.stringify(user));

  return user;
}
```

### 3. Cache Stampede Prevention

Prevent multiple requests from hitting database simultaneously:

```javascript
async function getUserSafe(userId) {
  const cacheKey = `user:${userId}`;
  const lockKey = `lock:user:${userId}`;

  // Try cache
  let user = await redis.get(cacheKey);
  if (user) return JSON.parse(user);

  // Acquire lock
  const locked = await redis.set(lockKey, '1', 'EX', 10, 'NX');

  if (locked === 'OK') {
    try {
      user = await db.users.findById(userId);
      if (user) {
        await redis.setex(cacheKey, 3600, JSON.stringify(user));
      }
      return user;
    } finally {
      await redis.del(lockKey);
    }
  } else {
    // Someone else is fetching - wait and retry
    await new Promise(r => setTimeout(r, 100));
    return getUserSafe(userId);
  }
}
```

## Redis Data Structures

### Strings (Simple Key-Value)

```javascript
// Basic operations
await redis.set('key', 'value');
const value = await redis.get('key');

// With expiration (seconds)
await redis.setex('session:abc', 1800, JSON.stringify(sessionData));

// Atomic counters
await redis.incr('page_views');
await redis.incrby('score', 10);
await redis.decr('inventory');

// Multiple keys
await redis.mset('key1', 'val1', 'key2', 'val2');
const values = await redis.mget('key1', 'key2');
```

### Hashes (Objects)

```javascript
// Store object fields
await redis.hset('user:1000', 'name', 'John');
await redis.hset('user:1000', 'email', 'john@example.com');

// Get all fields
const user = await redis.hgetall('user:1000');
// {name: 'John', email: 'john@example.com'}

// Set multiple at once
await redis.hset('user:1000', {
  name: 'John',
  email: 'john@example.com',
  age: 30
});

// Increment field
await redis.hincrby('user:1000', 'login_count', 1);
```

### Lists (Arrays/Queues)

```javascript
// Push to list
await redis.rpush('queue:jobs', JSON.stringify({task: 'send_email'}));
await redis.lpush('recent_posts', postId);

// Pop from list (blocking)
const job = await redis.blpop('queue:jobs', 0); // Block until available

// Get range
const recent = await redis.lrange('recent_posts', 0, 9); // First 10

// List length
const length = await redis.llen('queue:jobs');

// Trim list
await redis.ltrim('recent_posts', 0, 99); // Keep only 100
```

### Sets (Unique Collections)

```javascript
// Add members
await redis.sadd('tags:post:123', 'nodejs', 'redis', 'caching');

// Check membership
const isMember = await redis.sismember('tags:post:123', 'redis');

// Get all members
const tags = await redis.smembers('tags:post:123');

// Set operations
const common = await redis.sinter('tags:1', 'tags:2'); // Intersection
const all = await redis.sunion('tags:1', 'tags:2'); // Union

// Random member
const random = await redis.srandmember('all_tags');
```

### Sorted Sets (Leaderboards)

```javascript
// Add with score
await redis.zadd('leaderboard', 2000, 'player1');
await redis.zadd('leaderboard', 1500, 'player2');

// Get rank (0-based, descending)
const rank = await redis.zrevrank('leaderboard', 'player1'); // 0 = 1st place

// Get score
const score = await redis.zscore('leaderboard', 'player1');

// Increment score
await redis.zincrby('leaderboard', 50, 'player2');

// Get top N with scores
const top10 = await redis.zrevrange('leaderboard', 0, 9, 'WITHSCORES');

// Get range by score
const midRange = await redis.zrangebyscore('leaderboard', 1000, 2000);

// Count in score range
const count = await redis.zcount('leaderboard', 1500, 2000);
```

## Session Management

### Express Session Store

```javascript
const session = require('express-session');
const RedisStore = require('connect-redis')(session);

app.use(session({
  store: new RedisStore({client: redis}),
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    maxAge: 86400000, // 24 hours
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production'
  }
}));

// Access session
app.get('/profile', (req, res) => {
  if (req.session.userId) {
    res.json({userId: req.session.userId});
  } else {
    res.status(401).json({error: 'Not authenticated'});
  }
});

// Set session
app.post('/login', (req, res) => {
  req.session.userId = user.id;
  res.json({success: true});
});

// Destroy session
app.post('/logout', (req, res) => {
  req.session.destroy();
  res.json({success: true});
});
```

### Manual Session Management

```javascript
const crypto = require('crypto');

async function createSession(userId) {
  const sessionId = crypto.randomUUID();
  const sessionData = {
    userId,
    createdAt: Date.now()
  };

  await redis.setex(
    `session:${sessionId}`,
    1800, // 30 minutes
    JSON.stringify(sessionData)
  );

  return sessionId;
}

async function validateSession(sessionId) {
  const data = await redis.get(`session:${sessionId}`);
  if (!data) return null;

  const session = JSON.parse(data);

  // Refresh expiration on activity
  await redis.expire(`session:${sessionId}`, 1800);

  return session;
}

async function destroySession(sessionId) {
  await redis.del(`session:${sessionId}`);
}
```

## Rate Limiting

### Fixed Window

```javascript
async function rateLimitFixed(userId, limit = 100, windowSec = 60) {
  const windowKey = Math.floor(Date.now() / 1000 / windowSec);
  const key = `rate:${userId}:${windowKey}`;

  const current = await redis.incr(key);

  if (current === 1) {
    await redis.expire(key, windowSec);
  }

  return {
    allowed: current <= limit,
    remaining: Math.max(0, limit - current)
  };
}

// Express middleware
app.use(async (req, res, next) => {
  const userId = req.session?.userId || req.ip;
  const result = await rateLimitFixed(userId);

  res.set('X-RateLimit-Remaining', result.remaining);

  if (!result.allowed) {
    return res.status(429).json({error: 'Rate limit exceeded'});
  }

  next();
});
```

### Sliding Window (More Accurate)

```javascript
async function rateLimitSliding(userId, limit = 100, windowSec = 60) {
  const key = `rate:${userId}`;
  const now = Date.now();
  const windowStart = now - (windowSec * 1000);

  // Remove old entries
  await redis.zremrangebyscore(key, 0, windowStart);

  // Count requests in window
  const count = await redis.zcard(key);

  if (count < limit) {
    // Add current request
    await redis.zadd(key, now, `${now}:${Math.random()}`);
    await redis.expire(key, windowSec);

    return {
      allowed: true,
      remaining: limit - count - 1
    };
  }

  return {
    allowed: false,
    remaining: 0
  };
}
```

### Token Bucket

```javascript
async function rateLimitTokenBucket(userId, capacity = 100, refillRate = 10) {
  const key = `rate:bucket:${userId}`;
  const now = Date.now();

  const data = await redis.hgetall(key);
  let tokens = parseFloat(data.tokens || capacity);
  const lastRefill = parseInt(data.lastRefill || now);

  // Refill tokens based on elapsed time
  const elapsed = (now - lastRefill) / 1000;
  tokens = Math.min(capacity, tokens + (elapsed * refillRate));

  if (tokens >= 1) {
    tokens -= 1;

    await redis.hset(key, {
      tokens: tokens.toString(),
      lastRefill: now.toString()
    });
    await redis.expire(key, 3600);

    return {
      allowed: true,
      remaining: Math.floor(tokens)
    };
  }

  return {
    allowed: false,
    remaining: 0
  };
}
```

## Real-Time Features

### Pub/Sub

```javascript
// Publisher
async function publishNotification(channel, message) {
  await redis.publish(channel, JSON.stringify(message));
}

// Subscriber
const subscriber = redis.duplicate();

await subscriber.subscribe('notifications', 'chat');

subscriber.on('message', (channel, message) => {
  const data = JSON.parse(message);
  console.log(`Received on ${channel}:`, data);

  // Broadcast to WebSocket clients
  io.to(channel).emit('message', data);
});

// Pattern subscription
await subscriber.psubscribe('user:*:notifications');

subscriber.on('pmessage', (pattern, channel, message) => {
  console.log(`Pattern ${pattern} matched ${channel}`);
});
```

### Redis Streams

```javascript
// Add to stream
async function addEvent(stream, data) {
  const id = await redis.xadd(
    stream,
    '*', // Auto-generate ID
    'event', JSON.stringify(data)
  );
  return id;
}

// Read from stream
async function readEvents(stream, lastId = '0') {
  const results = await redis.xread(
    'BLOCK', 5000,
    'STREAMS', stream, lastId
  );

  if (!results) return [];

  const [streamName, messages] = results[0];
  return messages.map(([id, fields]) => ({
    id,
    data: JSON.parse(fields[1])
  }));
}

// Consumer groups
async function consumeEvents(stream, group, consumer) {
  const results = await redis.xreadgroup(
    'GROUP', group, consumer,
    'BLOCK', 5000,
    'COUNT', 10,
    'STREAMS', stream, '>'
  );

  if (!results) return [];

  const [streamName, messages] = results[0];

  for (const [id, fields] of messages) {
    const data = JSON.parse(fields[1]);
    await processEvent(data);
    await redis.xack(stream, group, id);
  }

  return messages.length;
}
```

## Performance Optimization

### Pipelines (Batch Commands)

```javascript
// Without pipeline - 4 round trips
await redis.set('key1', 'val1');
await redis.set('key2', 'val2');
await redis.set('key3', 'val3');
await redis.set('key4', 'val4');

// With pipeline - 1 round trip
const pipeline = redis.pipeline();
pipeline.set('key1', 'val1');
pipeline.set('key2', 'val2');
pipeline.set('key3', 'val3');
pipeline.set('key4', 'val4');
const results = await pipeline.exec();
```

### Transactions (MULTI/EXEC)

```javascript
// Atomic operations
async function transferPoints(fromUser, toUser, points) {
  const multi = redis.multi();

  multi.hincrby(`user:${fromUser}`, 'points', -points);
  multi.hincrby(`user:${toUser}`, 'points', points);

  const results = await multi.exec();
  return results.every(([err]) => !err);
}

// Optimistic locking with WATCH
async function incrementSafe(key, maxValue) {
  await redis.watch(key);

  const current = parseInt(await redis.get(key) || '0');

  if (current >= maxValue) {
    await redis.unwatch();
    return false;
  }

  const multi = redis.multi();
  multi.incr(key);
  const results = await multi.exec();

  // null means transaction was aborted
  return results !== null;
}
```

### Lua Scripts

```javascript
// Rate limiter as atomic Lua script
const rateLimitScript = `
  local key = KEYS[1]
  local limit = tonumber(ARGV[1])
  local window = tonumber(ARGV[2])
  local now = tonumber(ARGV[3])

  local windowStart = now - window * 1000

  redis.call('ZREMRANGEBYSCORE', key, 0, windowStart)
  local count = redis.call('ZCARD', key)

  if count < limit then
    redis.call('ZADD', key, now, now)
    redis.call('EXPIRE', key, window)
    return {1, limit - count - 1}
  else
    return {0, 0}
  end
`;

// Execute
const result = await redis.eval(
  rateLimitScript,
  1,
  `rate:${userId}`,
  100,
  60,
  Date.now()
);

const [allowed, remaining] = result;
```

## Common Use Cases

### Distributed Lock

```javascript
const crypto = require('crypto');

async function acquireLock(resource, ttlMs = 10000) {
  const lockKey = `lock:${resource}`;
  const lockValue = crypto.randomUUID();

  const acquired = await redis.set(
    lockKey,
    lockValue,
    'PX', ttlMs,
    'NX'
  );

  if (acquired === 'OK') {
    return {
      locked: true,
      unlock: async () => {
        const script = `
          if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
          else
            return 0
          end
        `;
        await redis.eval(script, 1, lockKey, lockValue);
      }
    };
  }

  return {locked: false};
}

// Usage
const lock = await acquireLock('critical_section');
if (lock.locked) {
  try {
    await performCriticalOperation();
  } finally {
    await lock.unlock();
  }
}
```

### Job Queue

```javascript
// Add job to queue
async function enqueueJob(job) {
  await redis.rpush('jobs:pending', JSON.stringify({
    id: crypto.randomUUID(),
    ...job,
    createdAt: Date.now()
  }));
}

// Process jobs
async function processJobs() {
  while (true) {
    const result = await redis.blpop('jobs:pending', 5);

    if (result) {
      const [queue, jobJson] = result;
      const job = JSON.parse(jobJson);

      try {
        await handleJob(job);
        await redis.lpush('jobs:completed', jobJson);
      } catch (error) {
        await redis.lpush('jobs:failed', JSON.stringify({
          ...job,
          error: error.message
        }));
      }
    }
  }
}
```

### Leaderboard

```javascript
// Update player score
async function updateScore(playerId, score) {
  await redis.zincrby('leaderboard:global', score, playerId);
}

// Get player rank and score
async function getPlayerRank(playerId) {
  const score = await redis.zscore('leaderboard:global', playerId);
  const rank = await redis.zrevrank('leaderboard:global', playerId);

  return {
    rank: rank + 1, // 1-based
    score: parseInt(score)
  };
}

// Get top players
async function getLeaderboard(limit = 10) {
  const results = await redis.zrevrange(
    'leaderboard:global',
    0,
    limit - 1,
    'WITHSCORES'
  );

  const leaderboard = [];
  for (let i = 0; i < results.length; i += 2) {
    leaderboard.push({
      rank: (i / 2) + 1,
      playerId: results[i],
      score: parseInt(results[i + 1])
    });
  }

  return leaderboard;
}

// Get players around specific player
async function getPlayersAround(playerId, range = 5) {
  const rank = await redis.zrevrank('leaderboard:global', playerId);

  const start = Math.max(0, rank - range);
  const end = rank + range;

  const results = await redis.zrevrange(
    'leaderboard:global',
    start,
    end,
    'WITHSCORES'
  );

  // Format results
  const players = [];
  for (let i = 0; i < results.length; i += 2) {
    players.push({
      rank: start + (i / 2) + 1,
      playerId: results[i],
      score: parseInt(results[i + 1])
    });
  }

  return players;
}
```

## Best Practices

### Key Naming Conventions

```javascript
// Use colons for namespacing
user:1000
user:1000:profile
user:1000:sessions
user:1000:cart

// Include type in key
string:config:max_upload
hash:user:1000
list:queue:emails
set:tags:post:123
zset:leaderboard:global

// Include dates for time-series
stats:2024:01:25:views
logs:2024:01:user:1000
```

### Always Set TTL

```javascript
// Good - with expiration
await redis.setex('cache:user:1000', 3600, data);

// Bad - no expiration (memory leak)
await redis.set('cache:user:1000', data);

// Set TTL on existing key
await redis.expire('key', 3600);

// Check TTL
const ttl = await redis.ttl('key'); // Seconds remaining (-1 = no TTL)
```

### Memory Management

```javascript
// Configure max memory and eviction policy
await redis.config('SET', 'maxmemory', '2gb');
await redis.config('SET', 'maxmemory-policy', 'allkeys-lru');

// Eviction policies:
// - noeviction: Return errors when memory limit reached
// - allkeys-lru: Evict least recently used keys
// - volatile-lru: Evict LRU keys with TTL set
// - allkeys-random: Evict random keys
// - volatile-ttl: Evict keys with nearest TTL
```

### Error Handling

```javascript
// Handle connection errors
redis.on('error', (err) => {
  console.error('Redis error:', err);
});

redis.on('connect', () => {
  console.log('Redis connected');
});

redis.on('reconnecting', () => {
  console.log('Redis reconnecting');
});

// Graceful operations
async function safeGet(key) {
  try {
    return await redis.get(key);
  } catch (error) {
    console.error(`Redis get failed for ${key}:`, error);
    return null; // Fallback
  }
}
```

## Monitoring

```bash
# Monitor commands in real-time
redis-cli monitor

# Server info
redis-cli info

# Connected clients
redis-cli client list

# Slow queries
redis-cli slowlog get 10

# Memory usage
redis-cli info memory

# Key space info
redis-cli dbsize
redis-cli info keyspace

# Scan keys (production-safe)
redis-cli --scan --pattern 'user:*'

# Memory usage of specific key
redis-cli memory usage mykey

# Find largest keys
redis-cli --bigkeys
```

## Security

```bash
# Enable authentication
# In redis.conf:
requirepass your_strong_password

# Disable dangerous commands
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""

# Bind to localhost only
bind 127.0.0.1

# Use TLS for production
tls-port 6380
tls-cert-file /path/to/cert.pem
tls-key-file /path/to/key.pem
```

```javascript
// Connect with auth
const redis = new Redis({
  host: 'localhost',
  port: 6379,
  password: process.env.REDIS_PASSWORD,
  tls: process.env.NODE_ENV === 'production' ? {} : undefined
});
```

## Production Checklist

✅ Enable persistence (RDB and/or AOF)
✅ Set maxmemory and eviction policy
✅ Enable authentication
✅ Use TLS in production
✅ Bind to localhost or private network only
✅ Configure appropriate timeouts
✅ Set up monitoring and alerting
✅ Always set TTL on cache keys
✅ Handle connection failures gracefully
✅ Use pipelines for bulk operations
✅ Monitor memory usage and slow queries
✅ Regular backups of persistent data
✅ Test failover scenarios

## Resources

- Redis Documentation: https://redis.io/docs/
- Redis Commands: https://redis.io/commands/
- ioredis (Node.js): https://github.com/redis/ioredis
- redis-py (Python): https://github.com/redis/redis-py
- Redis University: https://university.redis.com/
