---
name: elasticsearch-search
description: Elasticsearch implementation covering index mapping design, full-text search queries, aggregations, fuzzy matching, autocomplete with edge n-grams, filtering, pagination with search_after, bulk indexing, relevance tuning, and integration with Node.js and Python clients.
---

# Elasticsearch Search

This skill should be used when implementing search functionality with Elasticsearch. It covers index design, queries, aggregations, autocomplete, and client integration.

## When to Use This Skill

Use this skill when you need to:

- Build full-text search for applications
- Design index mappings and analyzers
- Implement autocomplete and fuzzy search
- Run aggregations for analytics dashboards
- Optimize search relevance and performance

## Index Mapping

```json
{
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "analyzer": "standard",
        "fields": {
          "keyword": { "type": "keyword" },
          "autocomplete": {
            "type": "text",
            "analyzer": "autocomplete_analyzer",
            "search_analyzer": "standard"
          }
        }
      },
      "description": { "type": "text" },
      "price": { "type": "float" },
      "category": { "type": "keyword" },
      "tags": { "type": "keyword" },
      "created_at": { "type": "date" },
      "location": { "type": "geo_point" }
    }
  },
  "settings": {
    "analysis": {
      "analyzer": {
        "autocomplete_analyzer": {
          "type": "custom",
          "tokenizer": "autocomplete_tokenizer",
          "filter": ["lowercase"]
        }
      },
      "tokenizer": {
        "autocomplete_tokenizer": {
          "type": "edge_ngram",
          "min_gram": 2,
          "max_gram": 15,
          "token_chars": ["letter", "digit"]
        }
      }
    },
    "number_of_shards": 1,
    "number_of_replicas": 1
  }
}
```

## Node.js Client

```typescript
import { Client } from "@elastic/elasticsearch";

const client = new Client({
  node: process.env.ELASTICSEARCH_URL || "http://localhost:9200",
  auth: {
    apiKey: process.env.ELASTICSEARCH_API_KEY!,
  },
});

// Full-text search with filters
async function searchProducts(query: string, filters: {
  category?: string;
  minPrice?: number;
  maxPrice?: number;
  page?: number;
  size?: number;
}) {
  const { page = 1, size = 20 } = filters;

  const must: any[] = [
    {
      multi_match: {
        query,
        fields: ["title^3", "description", "tags^2"],
        fuzziness: "AUTO",
        type: "best_fields",
      },
    },
  ];

  const filter: any[] = [];
  if (filters.category) filter.push({ term: { category: filters.category } });
  if (filters.minPrice || filters.maxPrice) {
    filter.push({
      range: { price: { gte: filters.minPrice, lte: filters.maxPrice } },
    });
  }

  const result = await client.search({
    index: "products",
    body: {
      query: { bool: { must, filter } },
      highlight: { fields: { title: {}, description: {} } },
      from: (page - 1) * size,
      size,
      sort: [{ _score: "desc" }, { created_at: "desc" }],
    },
  });

  return {
    total: (result.hits.total as any).value,
    hits: result.hits.hits.map((hit) => ({
      ...hit._source,
      score: hit._score,
      highlights: hit.highlight,
    })),
  };
}
```

## Autocomplete

```typescript
async function autocomplete(prefix: string, size = 10) {
  const result = await client.search({
    index: "products",
    body: {
      query: {
        match: {
          "title.autocomplete": { query: prefix, operator: "and" },
        },
      },
      _source: ["title", "category"],
      size,
    },
  });

  return result.hits.hits.map((hit) => hit._source);
}
```

## Aggregations

```typescript
async function getCategoryStats(query?: string) {
  const body: any = {
    size: 0,
    aggs: {
      categories: {
        terms: { field: "category", size: 50 },
        aggs: {
          avg_price: { avg: { field: "price" } },
          price_ranges: {
            range: {
              field: "price",
              ranges: [
                { to: 25 },
                { from: 25, to: 100 },
                { from: 100, to: 500 },
                { from: 500 },
              ],
            },
          },
        },
      },
    },
  };

  if (query) {
    body.query = { match: { title: query } };
  }

  const result = await client.search({ index: "products", body });
  return result.aggregations;
}
```

## Bulk Indexing

```typescript
async function bulkIndex(documents: any[]) {
  const operations = documents.flatMap((doc) => [
    { index: { _index: "products", _id: doc.id } },
    doc,
  ]);

  const result = await client.bulk({ refresh: true, operations });

  if (result.errors) {
    const errors = result.items
      .filter((item) => item.index?.error)
      .map((item) => item.index?.error);
    console.error("Bulk indexing errors:", errors);
  }

  return { indexed: documents.length, errors: result.errors };
}
```

## Deep Pagination with search_after

```typescript
async function scrollAllProducts(batchSize = 1000) {
  let searchAfter: any[] | undefined;
  const allResults: any[] = [];

  while (true) {
    const body: any = {
      size: batchSize,
      sort: [{ created_at: "asc" }, { _id: "asc" }],
    };
    if (searchAfter) body.search_after = searchAfter;

    const result = await client.search({ index: "products", body });
    const hits = result.hits.hits;
    if (hits.length === 0) break;

    allResults.push(...hits.map((h) => h._source));
    searchAfter = hits[hits.length - 1].sort;
  }

  return allResults;
}
```

## Additional Resources

- Elasticsearch docs: https://www.elastic.co/guide/en/elasticsearch/reference/current/
- Node.js client: https://www.elastic.co/guide/en/elasticsearch/client/javascript-api/current/
