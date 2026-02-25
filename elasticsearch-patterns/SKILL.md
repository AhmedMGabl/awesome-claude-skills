---
name: elasticsearch-patterns
description: Elasticsearch patterns covering index management, mappings, queries, aggregations, analyzers, bulk operations, and search optimization techniques.
---

# Elasticsearch Patterns

This skill should be used when building search and analytics features with Elasticsearch. It covers indexes, mappings, queries, aggregations, analyzers, and performance tuning.

## When to Use This Skill

Use this skill when you need to:

- Build full-text search functionality
- Implement complex query and filtering
- Use aggregations for analytics
- Configure custom analyzers and mappings
- Optimize search performance at scale

## Index Management

```typescript
import { Client } from "@elastic/elasticsearch";

const client = new Client({ node: "http://localhost:9200" });

// Create index with mappings
await client.indices.create({
  index: "products",
  body: {
    settings: {
      number_of_shards: 3,
      number_of_replicas: 1,
      analysis: {
        analyzer: {
          product_analyzer: {
            type: "custom",
            tokenizer: "standard",
            filter: ["lowercase", "stop", "snowball"],
          },
        },
      },
    },
    mappings: {
      properties: {
        name: { type: "text", analyzer: "product_analyzer" },
        description: { type: "text", analyzer: "product_analyzer" },
        price: { type: "float" },
        category: { type: "keyword" },
        tags: { type: "keyword" },
        created_at: { type: "date" },
        in_stock: { type: "boolean" },
        location: { type: "geo_point" },
      },
    },
  },
});
```

## Queries

```typescript
// Full-text search with boosting
const result = await client.search({
  index: "products",
  body: {
    query: {
      bool: {
        must: [
          {
            multi_match: {
              query: "wireless headphones",
              fields: ["name^3", "description"],
              type: "best_fields",
              fuzziness: "AUTO",
            },
          },
        ],
        filter: [
          { range: { price: { gte: 20, lte: 200 } } },
          { term: { in_stock: true } },
          { terms: { category: ["electronics", "audio"] } },
        ],
        should: [
          { term: { tags: { value: "bestseller", boost: 2 } } },
        ],
        minimum_should_match: 0,
      },
    },
    sort: [
      { _score: "desc" },
      { price: "asc" },
    ],
    from: 0,
    size: 20,
    highlight: {
      fields: {
        name: {},
        description: { fragment_size: 150 },
      },
    },
  },
});
```

## Aggregations

```typescript
const analytics = await client.search({
  index: "products",
  body: {
    size: 0,
    aggs: {
      categories: {
        terms: { field: "category", size: 20 },
        aggs: {
          avg_price: { avg: { field: "price" } },
          price_ranges: {
            range: {
              field: "price",
              ranges: [
                { to: 50 },
                { from: 50, to: 100 },
                { from: 100, to: 200 },
                { from: 200 },
              ],
            },
          },
        },
      },
      price_histogram: {
        histogram: { field: "price", interval: 25 },
      },
      monthly_created: {
        date_histogram: {
          field: "created_at",
          calendar_interval: "month",
        },
      },
    },
  },
});
```

## Bulk Operations

```typescript
const documents = [
  { id: "1", name: "Product A", price: 29.99, category: "electronics" },
  { id: "2", name: "Product B", price: 49.99, category: "clothing" },
];

const body = documents.flatMap((doc) => [
  { index: { _index: "products", _id: doc.id } },
  doc,
]);

const { errors, items } = await client.bulk({ body });

if (errors) {
  const failedItems = items.filter((item) => item.index?.error);
  console.error("Failed items:", failedItems);
}
```

## Autocomplete

```typescript
// Add completion field to mapping
await client.indices.create({
  index: "suggestions",
  body: {
    mappings: {
      properties: {
        suggest: {
          type: "completion",
          contexts: [{ name: "category", type: "category" }],
        },
      },
    },
  },
});

// Search suggestions
const suggestions = await client.search({
  index: "suggestions",
  body: {
    suggest: {
      product_suggest: {
        prefix: "wir",
        completion: {
          field: "suggest",
          size: 5,
          fuzzy: { fuzziness: "AUTO" },
          contexts: { category: ["electronics"] },
        },
      },
    },
  },
});
```

## Additional Resources

- Elasticsearch: https://www.elastic.co/guide/en/elasticsearch/reference/current/
- Node.js Client: https://www.elastic.co/guide/en/elasticsearch/client/javascript-api/current/
- Query DSL: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html
