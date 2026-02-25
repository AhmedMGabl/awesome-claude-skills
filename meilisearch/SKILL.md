---
name: meilisearch
description: Meilisearch full-text search engine covering index management, document operations, search queries, filtering, faceting, sorting, typo tolerance, synonyms, and JavaScript/Python SDK integration.
---

# Meilisearch

This skill should be used when integrating Meilisearch for search functionality. It covers indexing, search queries, filtering, faceting, and SDK usage.

## When to Use This Skill

Use this skill when you need to:

- Add fast full-text search to applications
- Implement typo-tolerant, instant search
- Build faceted search with filters
- Index and search structured documents
- Replace Algolia or Elasticsearch for simpler use cases

## Setup and Indexing

```typescript
import { MeiliSearch } from "meilisearch";

const client = new MeiliSearch({
  host: "http://localhost:7700",
  apiKey: process.env.MEILI_MASTER_KEY,
});

// Create index and add documents
const index = client.index("products");

await index.addDocuments([
  {
    id: 1,
    title: "Wireless Headphones",
    description: "Noise-cancelling over-ear headphones",
    category: "Electronics",
    price: 149.99,
    rating: 4.5,
    tags: ["audio", "wireless", "bluetooth"],
  },
  {
    id: 2,
    title: "Running Shoes",
    description: "Lightweight trail running shoes",
    category: "Sports",
    price: 89.99,
    rating: 4.2,
    tags: ["shoes", "running", "outdoor"],
  },
]);

// Wait for indexing to complete
const task = await index.addDocuments(documents);
await client.waitForTask(task.taskUid);
```

## Index Settings

```typescript
await index.updateSettings({
  // Fields used for search
  searchableAttributes: ["title", "description", "tags"],

  // Fields returned in results
  displayedAttributes: ["id", "title", "description", "price", "category", "rating"],

  // Fields available for filtering
  filterableAttributes: ["category", "price", "rating", "tags"],

  // Fields available for sorting
  sortableAttributes: ["price", "rating", "created_at"],

  // Custom ranking rules
  rankingRules: [
    "words",
    "typo",
    "proximity",
    "attribute",
    "sort",
    "exactness",
    "rating:desc",
  ],

  // Synonyms
  synonyms: {
    phone: ["smartphone", "mobile"],
    laptop: ["notebook", "computer"],
  },

  // Typo tolerance
  typoTolerance: {
    enabled: true,
    minWordSizeForTypos: { oneTypo: 4, twoTypos: 8 },
  },
});
```

## Search Queries

```typescript
// Basic search
const results = await index.search("headphones");

// Search with filters
const filtered = await index.search("shoes", {
  filter: ['category = "Sports"', "price < 100"],
  sort: ["price:asc"],
  limit: 20,
  offset: 0,
});

// Faceted search
const faceted = await index.search("", {
  facets: ["category", "tags"],
  filter: ["rating >= 4"],
});
// faceted.facetDistribution = { category: { Electronics: 5, Sports: 3 }, ... }

// Highlight matches
const highlighted = await index.search("wireless head", {
  attributesToHighlight: ["title", "description"],
  highlightPreTag: "<mark>",
  highlightPostTag: "</mark>",
});

// Crop long descriptions
const cropped = await index.search("running", {
  attributesToCrop: ["description"],
  cropLength: 30,
});
```

## React Integration

```tsx
import { InstantSearch, SearchBox, Hits, RefinementList } from "react-instantsearch";
import { instantMeiliSearch } from "@meilisearch/instant-meilisearch";

const { searchClient } = instantMeiliSearch("http://localhost:7700", "apiKey");

function SearchPage() {
  return (
    <InstantSearch indexName="products" searchClient={searchClient}>
      <SearchBox placeholder="Search products..." />
      <div style={{ display: "flex", gap: "2rem" }}>
        <div>
          <h3>Category</h3>
          <RefinementList attribute="category" />
        </div>
        <Hits hitComponent={ProductHit} />
      </div>
    </InstantSearch>
  );
}

function ProductHit({ hit }: { hit: any }) {
  return (
    <div>
      <h4>{hit.title}</h4>
      <p>{hit.description}</p>
      <span>${hit.price}</span>
    </div>
  );
}
```

## Document Operations

```typescript
// Update documents (partial)
await index.updateDocuments([
  { id: 1, price: 129.99 },
]);

// Delete documents
await index.deleteDocument(1);
await index.deleteDocuments([1, 2, 3]);
await index.deleteDocuments({ filter: 'category = "Archived"' });

// Get document
const doc = await index.getDocument(1);

// List documents
const docs = await index.getDocuments({ limit: 20, offset: 0 });
```

## Additional Resources

- Meilisearch docs: https://www.meilisearch.com/docs
- JavaScript SDK: https://github.com/meilisearch/meilisearch-js
- Guides: https://www.meilisearch.com/docs/guides
