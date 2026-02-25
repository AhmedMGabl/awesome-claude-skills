---
name: elasticsearch
description: Elasticsearch integration covering index management, full-text search, aggregations, mappings, bulk operations, query DSL, analyzers, highlighting, and Node.js/Python client patterns.
---

# Elasticsearch

This skill should be used when implementing search functionality with Elasticsearch. It covers indexing, querying, aggregations, mappings, and client integration.

## When to Use This Skill

Use this skill when you need to:

- Implement full-text search
- Build faceted search with aggregations
- Index and query structured/unstructured data
- Set up search autocomplete and suggestions
- Optimize search relevance and performance

## Setup

```typescript
import { Client } from "@elastic/elasticsearch";

const client = new Client({
  node: process.env.ELASTICSEARCH_URL ?? "http://localhost:9200",
  auth: {
    apiKey: process.env.ELASTICSEARCH_API_KEY!,
  },
});
```

## Index Management

```typescript
// Create index with mappings
await client.indices.create({
  index: "products",
  body: {
    settings: {
      number_of_shards: 1,
      number_of_replicas: 1,
      analysis: {
        analyzer: {
          autocomplete: {
            type: "custom",
            tokenizer: "standard",
            filter: ["lowercase", "autocomplete_filter"],
          },
        },
        filter: {
          autocomplete_filter: {
            type: "edge_ngram",
            min_gram: 2,
            max_gram: 20,
          },
        },
      },
    },
    mappings: {
      properties: {
        name: { type: "text", analyzer: "autocomplete", search_analyzer: "standard" },
        description: { type: "text" },
        price: { type: "float" },
        category: { type: "keyword" },
        tags: { type: "keyword" },
        created_at: { type: "date" },
        location: { type: "geo_point" },
      },
    },
  },
});
```

## Indexing Documents

```typescript
// Single document
await client.index({
  index: "products",
  id: "1",
  body: {
    name: "Wireless Headphones",
    description: "Premium noise-cancelling headphones",
    price: 299.99,
    category: "electronics",
    tags: ["audio", "wireless", "premium"],
    created_at: new Date().toISOString(),
  },
});

// Bulk indexing
const products = [/* array of products */];
const operations = products.flatMap((doc) => [
  { index: { _index: "products", _id: doc.id } },
  doc,
]);

const { errors, items } = await client.bulk({ body: operations, refresh: true });

if (errors) {
  const failedItems = items.filter((item) => item.index?.error);
  console.error("Failed items:", failedItems);
}
```

## Search Queries

```typescript
// Full-text search with filters
const result = await client.search({
  index: "products",
  body: {
    query: {
      bool: {
        must: [
          { multi_match: { query: "wireless headphones", fields: ["name^3", "description"] } },
        ],
        filter: [
          { term: { category: "electronics" } },
          { range: { price: { gte: 50, lte: 500 } } },
        ],
      },
    },
    highlight: {
      fields: { name: {}, description: {} },
      pre_tags: ["<mark>"],
      post_tags: ["</mark>"],
    },
    sort: [{ _score: "desc" }, { created_at: "desc" }],
    from: 0,
    size: 20,
  },
});

const hits = result.hits.hits.map((hit) => ({
  id: hit._id,
  score: hit._score,
  ...hit._source,
  highlights: hit.highlight,
}));
```

## Aggregations

```typescript
const result = await client.search({
  index: "products",
  body: {
    size: 0, // Only aggregations, no hits
    aggs: {
      categories: {
        terms: { field: "category", size: 20 },
        aggs: {
          avg_price: { avg: { field: "price" } },
        },
      },
      price_ranges: {
        range: {
          field: "price",
          ranges: [
            { to: 50, key: "budget" },
            { from: 50, to: 200, key: "mid-range" },
            { from: 200, key: "premium" },
          ],
        },
      },
      price_stats: {
        stats: { field: "price" },
      },
    },
  },
});

const categories = result.aggregations.categories.buckets;
const priceRanges = result.aggregations.price_ranges.buckets;
```

## Autocomplete / Suggestions

```typescript
async function autocomplete(prefix: string) {
  const result = await client.search({
    index: "products",
    body: {
      query: {
        match: { name: { query: prefix, analyzer: "standard" } },
      },
      _source: ["name", "category"],
      size: 5,
    },
  });

  return result.hits.hits.map((hit) => hit._source);
}
```

## Additional Resources

- Elasticsearch docs: https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html
- Node.js client: https://www.elastic.co/guide/en/elasticsearch/client/javascript-api/current/index.html
- Query DSL: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html
