---
name: neo4j-graph
description: Neo4j graph database patterns covering Cypher queries, node/relationship modeling, indexes, path algorithms, APOC procedures, and JavaScript/Python driver integration.
---

# Neo4j Graph Database

This skill should be used when building applications with Neo4j graph database. It covers Cypher queries, graph modeling, indexes, algorithms, APOC procedures, and driver integration.

## When to Use This Skill

Use this skill when you need to:

- Model data as nodes and relationships
- Write Cypher queries for graph traversal
- Use graph algorithms for recommendations
- Integrate Neo4j with Node.js or Python
- Optimize with indexes and constraints

## Schema and Constraints

```cypher
// Unique constraints
CREATE CONSTRAINT user_email IF NOT EXISTS
FOR (u:User) REQUIRE u.email IS UNIQUE;

CREATE CONSTRAINT post_id IF NOT EXISTS
FOR (p:Post) REQUIRE p.id IS UNIQUE;

// Indexes
CREATE INDEX user_name IF NOT EXISTS FOR (u:User) ON (u.name);
CREATE TEXT INDEX post_title IF NOT EXISTS FOR (p:Post) ON (p.title);
```

## Creating Nodes and Relationships

```cypher
// Create users
CREATE (alice:User {id: 'u1', name: 'Alice', email: 'alice@example.com'})
CREATE (bob:User {id: 'u2', name: 'Bob', email: 'bob@example.com'})

// Create relationships
MATCH (a:User {name: 'Alice'}), (b:User {name: 'Bob'})
CREATE (a)-[:FOLLOWS {since: date()}]->(b)

// Create post with author relationship
MATCH (u:User {name: 'Alice'})
CREATE (p:Post {id: 'p1', title: 'Graph Databases', content: '...', createdAt: datetime()})
CREATE (u)-[:AUTHORED]->(p)
CREATE (p)-[:TAGGED]->(:Tag {name: 'database'})
```

## Querying

```cypher
// Find user's posts
MATCH (u:User {name: 'Alice'})-[:AUTHORED]->(p:Post)
RETURN p.title, p.createdAt
ORDER BY p.createdAt DESC;

// Friends of friends
MATCH (me:User {name: 'Alice'})-[:FOLLOWS]->()-[:FOLLOWS]->(fof:User)
WHERE NOT (me)-[:FOLLOWS]->(fof) AND fof <> me
RETURN DISTINCT fof.name;

// Shortest path
MATCH path = shortestPath(
    (a:User {name: 'Alice'})-[:FOLLOWS*]-(b:User {name: 'Dave'})
)
RETURN path, length(path);

// All paths up to depth 4
MATCH path = (a:User {name: 'Alice'})-[:FOLLOWS*1..4]->(b:User {name: 'Dave'})
RETURN path, length(path)
ORDER BY length(path);
```

## Aggregation

```cypher
// Most followed users
MATCH (u:User)<-[:FOLLOWS]-(follower)
RETURN u.name, count(follower) AS followers
ORDER BY followers DESC
LIMIT 10;

// Tag popularity
MATCH (p:Post)-[:TAGGED]->(t:Tag)
RETURN t.name, count(p) AS posts
ORDER BY posts DESC;
```

## Recommendations

```cypher
// Recommend users to follow (collaborative filtering)
MATCH (me:User {name: 'Alice'})-[:FOLLOWS]->(friend)-[:FOLLOWS]->(suggestion)
WHERE NOT (me)-[:FOLLOWS]->(suggestion) AND suggestion <> me
RETURN suggestion.name, count(friend) AS mutual_friends
ORDER BY mutual_friends DESC
LIMIT 5;

// Content recommendations
MATCH (me:User {name: 'Alice'})-[:LIKED]->(p:Post)-[:TAGGED]->(t:Tag)<-[:TAGGED]-(rec:Post)
WHERE NOT (me)-[:LIKED]->(rec)
RETURN rec.title, collect(DISTINCT t.name) AS shared_tags, count(t) AS relevance
ORDER BY relevance DESC
LIMIT 10;
```

## Node.js Driver

```typescript
import neo4j from "neo4j-driver";

const driver = neo4j.driver("bolt://localhost:7687", neo4j.auth.basic("neo4j", "password"));

async function getUser(name: string) {
  const session = driver.session();
  try {
    const result = await session.run(
      "MATCH (u:User {name: $name})-[:AUTHORED]->(p:Post) RETURN u, collect(p) AS posts",
      { name }
    );
    return result.records.map((record) => ({
      user: record.get("u").properties,
      posts: record.get("posts").map((p: any) => p.properties),
    }));
  } finally {
    await session.close();
  }
}

// Cleanup
await driver.close();
```

## Python Driver

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

def get_recommendations(name):
    with driver.session() as session:
        result = session.run("""
            MATCH (me:User {name: $name})-[:FOLLOWS]->()-[:FOLLOWS]->(rec)
            WHERE NOT (me)-[:FOLLOWS]->(rec) AND rec <> me
            RETURN rec.name, count(*) AS score
            ORDER BY score DESC LIMIT 5
        """, name=name)
        return [dict(record) for record in result]

driver.close()
```

## Additional Resources

- Neo4j: https://neo4j.com/docs/
- Cypher: https://neo4j.com/docs/cypher-manual/
- Drivers: https://neo4j.com/docs/drivers-apis/
