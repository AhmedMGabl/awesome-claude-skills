---
name: elasticsearch-search
description: Elasticsearch and search engine patterns covering index management, mappings, full-text search, aggregations, autocomplete, fuzzy matching, relevance tuning, OpenSearch compatibility, and production search architecture.
---

# Elasticsearch & Search

This skill should be used when implementing search functionality in applications. It covers Elasticsearch index design, mappings, full-text search, aggregations, autocomplete, and production search patterns.

## When to Use This Skill

Use this skill when you need to:

- Implement full-text search in applications
- Design Elasticsearch indices and mappings
- Build autocomplete and typeahead features
- Create faceted search with aggregations
- Optimize search relevance and performance
- Implement fuzzy matching and synonym handling
- Build search APIs with filtering and pagination

## Setup

```bash
# Docker (development)
docker run -d --name elasticsearch \
  -p 9200:9200 -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  elasticsearch:8.15.0

# Node.js client
npm install @elastic/elasticsearch
```

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
// Create index with mappings and settings
await client.indices.create({
  index: "products",
  body: {
    settings: {
      number_of_shards: 1,
      number_of_replicas: 1,
      analysis: {
        analyzer: {
          autocomplete_analyzer: {
            type: "custom",
            tokenizer: "autocomplete_tokenizer",
            filter: ["lowercase", "asciifolding"],
          },
          search_analyzer: {
            type: "custom",
            tokenizer: "standard",
            filter: ["lowercase", "asciifolding"],
          },
        },
        tokenizer: {
          autocomplete_tokenizer: {
            type: "edge_ngram",
            min_gram: 2,
            max_gram: 15,
            token_chars: ["letter", "digit"],
          },
        },
      },
    },
    mappings: {
      properties: {
        name: {
          type: "text",
          analyzer: "autocomplete_analyzer",
          search_analyzer: "search_analyzer",
          fields: {
            keyword: { type: "keyword" },
            suggest: { type: "completion" },
          },
        },
        description: { type: "text" },
        category: { type: "keyword" },
        price: { type: "float" },
        tags: { type: "keyword" },
        in_stock: { type: "boolean" },
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
    description: "Premium noise-cancelling wireless headphones",
    category: "electronics",
    price: 299.99,
    tags: ["audio", "wireless", "premium"],
    in_stock: true,
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
  const failed = items.filter((item) => item.index?.error);
  console.error("Failed documents:", failed);
}
```

## Full-Text Search

```typescript
// Multi-match search with boosting
async function searchProducts(query: string, filters: Record<string, unknown> = {}) {
  const must: object[] = [];
  const filterClauses: object[] = [];

  if (query) {
    must.push({
      multi_match: {
        query,
        fields: ["name^3", "description", "tags^2"],
        type: "best_fields",
        fuzziness: "AUTO",
        prefix_length: 2,
      },
    });
  }

  if (filters.category) {
    filterClauses.push({ term: { category: filters.category } });
  }
  if (filters.minPrice || filters.maxPrice) {
    filterClauses.push({
      range: {
        price: {
          ...(filters.minPrice && { gte: filters.minPrice }),
          ...(filters.maxPrice && { lte: filters.maxPrice }),
        },
      },
    });
  }
  if (filters.inStock) {
    filterClauses.push({ term: { in_stock: true } });
  }

  const response = await client.search({
    index: "products",
    body: {
      query: {
        bool: {
          must: must.length ? must : [{ match_all: {} }],
          filter: filterClauses,
        },
      },
      highlight: {
        fields: {
          name: { pre_tags: ["<mark>"], post_tags: ["</mark>"] },
          description: { pre_tags: ["<mark>"], post_tags: ["</mark>"], fragment_size: 150 },
        },
      },
      sort: query ? ["_score", { created_at: "desc" }] : [{ created_at: "desc" }],
      from: (filters.page as number ?? 0) * 20,
      size: 20,
    },
  });

  return {
    total: (response.hits.total as { value: number }).value,
    results: response.hits.hits.map((hit) => ({
      id: hit._id,
      score: hit._score,
      ...hit._source as Record<string, unknown>,
      highlights: hit.highlight,
    })),
  };
}
```

## Aggregations (Faceted Search)

```typescript
// Faceted search with aggregations
async function searchWithFacets(query: string) {
  const response = await client.search({
    index: "products",
    body: {
      query: { multi_match: { query, fields: ["name^3", "description"] } },
      aggs: {
        categories: {
          terms: { field: "category", size: 20 },
        },
        price_ranges: {
          range: {
            field: "price",
            ranges: [
              { key: "budget", to: 50 },
              { key: "mid", from: 50, to: 200 },
              { key: "premium", from: 200 },
            ],
          },
        },
        avg_price: { avg: { field: "price" } },
        tags: {
          terms: { field: "tags", size: 30 },
        },
      },
      size: 20,
    },
  });

  return {
    results: response.hits.hits,
    facets: {
      categories: response.aggregations?.categories,
      priceRanges: response.aggregations?.price_ranges,
      avgPrice: response.aggregations?.avg_price,
      tags: response.aggregations?.tags,
    },
  };
}
```

## Autocomplete

```typescript
// Completion suggester
async function autocomplete(prefix: string) {
  const response = await client.search({
    index: "products",
    body: {
      suggest: {
        product_suggest: {
          prefix,
          completion: {
            field: "name.suggest",
            size: 10,
            fuzzy: { fuzziness: "AUTO" },
          },
        },
      },
    },
  });

  return response.suggest?.product_suggest?.[0]?.options.map((opt) => ({
    text: opt.text,
    score: opt._score,
    id: opt._id,
  }));
}

// Search-as-you-type with edge ngram
async function searchAsYouType(query: string) {
  const response = await client.search({
    index: "products",
    body: {
      query: {
        bool: {
          should: [
            { match: { name: { query, boost: 2 } } },
            { match_phrase_prefix: { name: { query, max_expansions: 10 } } },
          ],
        },
      },
      size: 10,
    },
  });

  return response.hits.hits;
}
```

## Synonyms and Relevance Tuning

```typescript
// Index with synonyms
await client.indices.create({
  index: "products_v2",
  body: {
    settings: {
      analysis: {
        filter: {
          synonym_filter: {
            type: "synonym",
            synonyms: [
              "laptop,notebook,portable computer",
              "phone,mobile,smartphone,cell phone",
              "tv,television,monitor,display",
            ],
          },
        },
        analyzer: {
          search_with_synonyms: {
            tokenizer: "standard",
            filter: ["lowercase", "synonym_filter"],
          },
        },
      },
    },
  },
});

// Function score for relevance boosting
const response = await client.search({
  index: "products",
  body: {
    query: {
      function_score: {
        query: { multi_match: { query: "headphones", fields: ["name", "description"] } },
        functions: [
          { filter: { term: { in_stock: true } }, weight: 2 },
          { field_value_factor: { field: "rating", modifier: "log1p", factor: 0.5 } },
          { gauss: { created_at: { origin: "now", scale: "30d", decay: 0.5 } } },
        ],
        score_mode: "sum",
        boost_mode: "multiply",
      },
    },
  },
});
```

## Production Patterns

```typescript
// Reindex with zero downtime (alias swap)
const newIndex = `products_${Date.now()}`;
await client.indices.create({ index: newIndex, body: { /* mappings */ } });
await client.reindex({
  body: { source: { index: "products" }, dest: { index: newIndex } },
});
await client.indices.updateAliases({
  body: {
    actions: [
      { remove: { index: "products_*", alias: "products" } },
      { add: { index: newIndex, alias: "products" } },
    ],
  },
});

// Index lifecycle management
await client.ilm.putLifecycle({
  policy: "products_policy",
  body: {
    policy: {
      phases: {
        hot: { actions: { rollover: { max_size: "50gb", max_age: "30d" } } },
        warm: { min_age: "30d", actions: { shrink: { number_of_shards: 1 } } },
        delete: { min_age: "90d", actions: { delete: {} } },
      },
    },
  },
});
```

## Additional Resources

- Elasticsearch docs: https://www.elastic.co/guide/en/elasticsearch/reference/current/
- Elasticsearch Node.js client: https://www.elastic.co/guide/en/elasticsearch/client/javascript-api/current/
- OpenSearch: https://opensearch.org/docs/latest/
