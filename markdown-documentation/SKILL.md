---
name: markdown-documentation
description: Technical documentation and Markdown writing covering API documentation with OpenAPI, README templates, JSDoc/TSDoc annotations, Docusaurus and VitePress site generation, ADR (Architecture Decision Records), changelog conventions, and documentation-as-code workflows.
---

# Markdown & Documentation

This skill should be used when writing technical documentation, API docs, READMEs, or setting up documentation sites. It covers Markdown patterns, doc generators, and documentation-as-code workflows.

## When to Use This Skill

Use this skill when you need to:

- Write clear technical documentation
- Create comprehensive READMEs
- Set up documentation sites (Docusaurus, VitePress)
- Write API documentation
- Create Architecture Decision Records (ADRs)
- Add JSDoc/TSDoc to codebases

## README Template

```markdown
# Project Name

One-sentence description of what this project does and why it exists.

## Quick Start

\`\`\`bash
npm install project-name
\`\`\`

\`\`\`typescript
import { something } from "project-name";
const result = something({ option: true });
\`\`\`

## Features

- **Feature 1** — Brief explanation
- **Feature 2** — Brief explanation
- **Feature 3** — Brief explanation

## Installation

\`\`\`bash
# npm
npm install project-name

# pnpm
pnpm add project-name
\`\`\`

## Usage

### Basic Example

\`\`\`typescript
// code example
\`\`\`

### Advanced Example

\`\`\`typescript
// code example
\`\`\`

## API Reference

### `functionName(options)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `option1` | `string` | — | Required. Description |
| `option2` | `number` | `10` | Optional. Description |

Returns: `Promise<Result>`

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_KEY` | Yes | — | Your API key |
| `DEBUG` | No | `false` | Enable debug logging |

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## License

MIT
```

## JSDoc / TSDoc

```typescript
/**
 * Processes an order and returns the confirmation.
 *
 * @param order - The order to process
 * @param options - Processing options
 * @returns The processed order with confirmation ID
 * @throws {ValidationError} If the order data is invalid
 * @throws {PaymentError} If payment processing fails
 *
 * @example
 * ```typescript
 * const result = await processOrder(
 *   { items: [{ id: "prod-1", quantity: 2 }] },
 *   { sendEmail: true },
 * );
 * console.log(result.confirmationId); // "ORD-12345"
 * ```
 */
async function processOrder(
  order: OrderInput,
  options: ProcessOptions = {},
): Promise<OrderConfirmation> {
  // implementation
}

/**
 * Configuration options for the API client.
 *
 * @remarks
 * The `timeout` and `retries` options apply to all requests
 * unless overridden per-request.
 */
interface ClientConfig {
  /** Base URL for API requests */
  baseUrl: string;
  /** Request timeout in milliseconds @defaultValue 30000 */
  timeout?: number;
  /** Number of retry attempts @defaultValue 3 */
  retries?: number;
}
```

## Architecture Decision Record (ADR)

```markdown
# ADR-001: Use PostgreSQL as Primary Database

## Status
Accepted (2024-03-15)

## Context
We need a primary database for our application that handles
transactional data, user accounts, and product catalog.

## Decision
Use PostgreSQL 16 as the primary relational database.

## Alternatives Considered
- **MySQL 8** — Less robust JSONB support, weaker extension ecosystem
- **MongoDB** — No ACID transactions across collections needed for our data model
- **CockroachDB** — Overkill for current scale; adds operational complexity

## Consequences
### Positive
- Strong JSONB support for semi-structured data
- Excellent extension ecosystem (PostGIS, pg_trgm, pgvector)
- Row-level security for multi-tenant isolation

### Negative
- Requires connection pooling at scale (PgBouncer)
- Horizontal scaling requires careful partitioning or Citus

### Risks
- Team has limited PostgreSQL-specific expertise (mitigated by training)
```

## Docusaurus Setup

```typescript
// docusaurus.config.ts
import type { Config } from "@docusaurus/types";

const config: Config = {
  title: "My Project Docs",
  tagline: "Documentation for My Project",
  url: "https://docs.example.com",
  baseUrl: "/",
  onBrokenLinks: "throw",
  themeConfig: {
    navbar: {
      title: "My Project",
      items: [
        { type: "docSidebar", sidebarId: "docs", label: "Docs" },
        { to: "/api", label: "API" },
        { href: "https://github.com/org/project", label: "GitHub", position: "right" },
      ],
    },
    algolia: {
      appId: "YOUR_APP_ID",
      apiKey: "YOUR_SEARCH_KEY",
      indexName: "my-project",
    },
  },
  presets: [
    ["classic", {
      docs: { sidebarPath: "./sidebars.ts", editUrl: "https://github.com/org/project/edit/main/" },
      blog: false,
    }],
  ],
};

export default config;
```

## Changelog Convention

```markdown
# Changelog

All notable changes to this project will be documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
- New user profile page with avatar upload

### Changed
- Updated authentication flow to use PKCE

## [1.2.0] - 2024-03-15

### Added
- Dark mode support across all pages
- Export data as CSV from dashboard

### Fixed
- Login redirect loop on expired sessions
- Memory leak in WebSocket connection handler

### Security
- Updated dependencies to patch CVE-2024-XXXX
```

## Additional Resources

- Docusaurus: https://docusaurus.io/
- VitePress: https://vitepress.dev/
- TSDoc: https://tsdoc.org/
- Keep a Changelog: https://keepachangelog.com/
- ADR GitHub: https://adr.github.io/
