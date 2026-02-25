---
name: nuqs-url-state
description: nuqs URL state management patterns covering type-safe search params, parsers for numbers/booleans/arrays/dates, shallow routing, history modes, server-side access, and Next.js App Router integration.
---

# nuqs URL State

This skill should be used when managing URL search params as state with nuqs. It covers typed parsers, shallow routing, history modes, and Next.js integration.

## When to Use This Skill

Use this skill when you need to:

- Sync React state with URL search parameters
- Parse and validate URL params with type safety
- Use shallow routing to avoid full page reloads
- Manage complex filter/sort state in the URL
- Share application state via URLs

## Basic Usage

```tsx
"use client";
import { useQueryState, parseAsInteger, parseAsString } from "nuqs";

function SearchPage() {
  const [search, setSearch] = useQueryState("q", parseAsString.withDefault(""));
  const [page, setPage] = useQueryState("page", parseAsInteger.withDefault(1));

  return (
    <div>
      <input
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Search..."
      />
      <p>Page: {page}</p>
      <button onClick={() => setPage((p) => p + 1)}>Next page</button>
      <button onClick={() => setPage(1)}>Reset</button>
    </div>
  );
}
// URL: ?q=hello&page=2
```

## Built-in Parsers

```tsx
import {
  parseAsString,
  parseAsInteger,
  parseAsFloat,
  parseAsBoolean,
  parseAsArrayOf,
  parseAsStringEnum,
  parseAsStringLiteral,
  parseAsTimestamp,
  parseAsIsoDateTime,
  parseAsJson,
} from "nuqs";

// String enum
const [sort, setSort] = useQueryState(
  "sort",
  parseAsStringEnum(["newest", "oldest", "popular"]).withDefault("newest"),
);

// Boolean
const [showArchived, setShowArchived] = useQueryState(
  "archived",
  parseAsBoolean.withDefault(false),
);

// Array (comma-separated)
const [tags, setTags] = useQueryState(
  "tags",
  parseAsArrayOf(parseAsString, ",").withDefault([]),
);

// JSON for complex state
const [filters, setFilters] = useQueryState(
  "filters",
  parseAsJson<{ minPrice: number; maxPrice: number }>().withDefault({
    minPrice: 0,
    maxPrice: 1000,
  }),
);

// Timestamp
const [date, setDate] = useQueryState("date", parseAsTimestamp);
```

## Multiple Params with useQueryStates

```tsx
"use client";
import { useQueryStates, parseAsInteger, parseAsString, parseAsStringEnum } from "nuqs";

function ProductFilters() {
  const [filters, setFilters] = useQueryStates({
    search: parseAsString.withDefault(""),
    category: parseAsStringEnum(["all", "electronics", "clothing"]).withDefault("all"),
    minPrice: parseAsInteger.withDefault(0),
    maxPrice: parseAsInteger.withDefault(1000),
    page: parseAsInteger.withDefault(1),
  });

  const resetFilters = () =>
    setFilters({
      search: null,
      category: null,
      minPrice: null,
      maxPrice: null,
      page: null,
    });

  return (
    <div>
      <input
        value={filters.search}
        onChange={(e) => setFilters({ search: e.target.value, page: 1 })}
      />
      <select
        value={filters.category}
        onChange={(e) => setFilters({ category: e.target.value as any, page: 1 })}
      >
        <option value="all">All</option>
        <option value="electronics">Electronics</option>
        <option value="clothing">Clothing</option>
      </select>
      <button onClick={resetFilters}>Reset</button>
    </div>
  );
}
```

## History Modes

```tsx
import { useQueryState, parseAsString } from "nuqs";

// Push (default) - adds to browser history
const [search, setSearch] = useQueryState("q", parseAsString.withOptions({ history: "push" }));

// Replace - replaces current history entry (good for filters)
const [sort, setSort] = useQueryState("sort", parseAsString.withOptions({ history: "replace" }));

// Shallow (default in Next.js App Router) - no server round-trip
const [tab, setTab] = useQueryState("tab", parseAsString.withOptions({ shallow: true }));
```

## Server-Side Access (Next.js)

```tsx
// app/products/page.tsx
import { SearchParams } from "nuqs/server";
import { createSearchParamsCache, parseAsInteger, parseAsString } from "nuqs/server";

const searchParamsCache = createSearchParamsCache({
  q: parseAsString.withDefault(""),
  page: parseAsInteger.withDefault(1),
});

export default async function ProductsPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const { q, page } = await searchParamsCache.parse(searchParams);

  const products = await db.products.findMany({
    where: q ? { name: { contains: q } } : {},
    skip: (page - 1) * 20,
    take: 20,
  });

  return <ProductList products={products} />;
}
```

## Additional Resources

- nuqs docs: https://nuqs.47ng.com/
- GitHub: https://github.com/47ng/nuqs
