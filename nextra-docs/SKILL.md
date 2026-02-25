---
name: nextra-docs
description: Nextra documentation framework covering file-based routing, MDX pages, theme configuration, search integration, sidebar navigation, i18n, and custom components for documentation sites.
---

# Nextra Documentation

This skill should be used when building documentation sites with Nextra. It covers file-based routing, MDX pages, theming, search, and navigation configuration.

## When to Use This Skill

Use this skill when you need to:

- Build documentation sites with Next.js and MDX
- Set up file-based documentation routing
- Configure search, sidebar, and navigation
- Add custom components to documentation pages
- Support internationalization (i18n) for docs

## Setup

```bash
npm install nextra nextra-theme-docs
```

```javascript
// next.config.mjs
import nextra from "nextra";

const withNextra = nextra({
  theme: "nextra-theme-docs",
  themeConfig: "./theme.config.tsx",
  defaultShowCopyCode: true,
  latex: true,
});

export default withNextra({
  // Next.js config
});
```

## Theme Configuration

```tsx
// theme.config.tsx
import type { DocsThemeConfig } from "nextra-theme-docs";

const config: DocsThemeConfig = {
  logo: <span style={{ fontWeight: 800 }}>My Docs</span>,
  project: { link: "https://github.com/myorg/myproject" },
  docsRepositoryBase: "https://github.com/myorg/myproject/tree/main/docs",
  head: (
    <>
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <meta property="og:title" content="My Docs" />
      <meta property="og:description" content="Documentation for My Project" />
    </>
  ),
  footer: { text: `MIT ${new Date().getFullYear()} My Project` },
  sidebar: {
    defaultMenuCollapseLevel: 1,
    toggleButton: true,
  },
  toc: { float: true, title: "On This Page" },
  feedback: { content: "Question? Give us feedback" },
  editLink: { text: "Edit this page on GitHub" },
  useNextSeoProps: () => ({ titleTemplate: "%s - My Docs" }),
  search: { placeholder: "Search documentation..." },
};

export default config;
```

## Page Organization

```
pages/
├── _meta.json          # Top-level navigation
├── index.mdx           # Homepage
├── getting-started.mdx
├── guides/
│   ├── _meta.json      # Guides section navigation
│   ├── installation.mdx
│   ├── configuration.mdx
│   └── deployment.mdx
└── api/
    ├── _meta.json
    ├── overview.mdx
    └── endpoints.mdx
```

```json
// pages/_meta.json
{
  "index": { "title": "Home", "type": "page" },
  "getting-started": "Getting Started",
  "guides": "Guides",
  "api": "API Reference",
  "---": { "type": "separator" },
  "changelog": { "title": "Changelog", "href": "/changelog" }
}
```

```json
// pages/guides/_meta.json
{
  "installation": "Installation",
  "configuration": "Configuration",
  "deployment": {
    "title": "Deployment",
    "theme": { "toc": true, "sidebar": true }
  }
}
```

## MDX Pages with Components

```mdx
---
title: Getting Started
description: Quick start guide for My Project
---

import { Callout, Tabs, Tab, Steps, Cards, Card } from 'nextra/components'

# Getting Started

<Callout type="info">
  This guide assumes you have Node.js 18+ installed.
</Callout>

<Steps>

### Install the package

```bash
npm install my-package
```

### Configure your project

Create a config file:

```json filename="config.json"
{
  "name": "my-project"
}
```

### Start building

```typescript filename="index.ts" {3} copy
import { create } from 'my-package'

const app = create({ name: 'my-project' })
app.start()
```

</Steps>

## Choose Your Framework

<Tabs items={['React', 'Vue', 'Svelte']}>
  <Tab>
    ```bash
    npx create-react-app my-app
    ```
  </Tab>
  <Tab>
    ```bash
    npm create vue@latest
    ```
  </Tab>
  <Tab>
    ```bash
    npx sv create my-app
    ```
  </Tab>
</Tabs>

## Explore

<Cards>
  <Card title="API Reference" href="/api" />
  <Card title="Examples" href="/examples" />
  <Card title="Guides" href="/guides" />
</Cards>
```

## i18n Support

```json
// next.config.mjs addition
export default withNextra({
  i18n: {
    locales: ["en", "es", "ja"],
    defaultLocale: "en",
  },
});
```

## Additional Resources

- Nextra docs: https://nextra.site/docs
- Docs theme: https://nextra.site/docs/docs-theme
- Built-in components: https://nextra.site/docs/guide/built-ins
