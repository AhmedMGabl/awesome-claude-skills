---
name: strapi-v5
description: Strapi v5 patterns covering content type builder, REST/GraphQL APIs, custom controllers, middleware, lifecycle hooks, role-based access, media uploads, and plugin development.
---

# Strapi v5

This skill should be used when building content-driven applications with Strapi v5 headless CMS. It covers content types, APIs, custom logic, permissions, and plugin development.

## When to Use This Skill

Use this skill when you need to:

- Build a headless CMS with visual content type builder
- Generate REST and GraphQL APIs automatically
- Add custom controllers, services, and middleware
- Configure role-based access control
- Develop custom Strapi plugins

## Setup

```bash
npx create-strapi@latest my-project
cd my-project
npm run develop
```

## Content Type Schema

```json
// src/api/article/content-types/article/schema.json
{
  "kind": "collectionType",
  "collectionName": "articles",
  "info": {
    "singularName": "article",
    "pluralName": "articles",
    "displayName": "Article"
  },
  "attributes": {
    "title": { "type": "string", "required": true, "maxLength": 200 },
    "slug": { "type": "uid", "targetField": "title" },
    "content": { "type": "richtext" },
    "excerpt": { "type": "text", "maxLength": 500 },
    "cover": { "type": "media", "allowedTypes": ["images"] },
    "status": {
      "type": "enumeration",
      "enum": ["draft", "published", "archived"],
      "default": "draft"
    },
    "author": { "type": "relation", "relation": "manyToOne", "target": "plugin::users-permissions.user" },
    "categories": { "type": "relation", "relation": "manyToMany", "target": "api::category.category" },
    "publishedAt": { "type": "datetime" },
    "seo": {
      "type": "component",
      "component": "shared.seo"
    }
  }
}
```

## Custom Controller

```ts
// src/api/article/controllers/article.ts
import { factories } from "@strapi/strapi";

export default factories.createCoreController("api::article.article", ({ strapi }) => ({
  async find(ctx) {
    const { query } = ctx;
    const entity = await strapi.entityService.findMany("api::article.article", {
      ...query,
      filters: { ...query.filters, status: "published" },
      populate: ["author", "categories", "cover"],
    });
    return entity;
  },

  async findBySlug(ctx) {
    const { slug } = ctx.params;
    const entities = await strapi.entityService.findMany("api::article.article", {
      filters: { slug },
      populate: ["author", "categories", "cover", "seo"],
    });
    if (!entities.length) return ctx.notFound("Article not found");
    return entities[0];
  },
}));
```

## Custom Route

```ts
// src/api/article/routes/custom-article.ts
export default {
  routes: [
    {
      method: "GET",
      path: "/articles/slug/:slug",
      handler: "article.findBySlug",
      config: { auth: false },
    },
  ],
};
```

## Custom Service

```ts
// src/api/article/services/article.ts
import { factories } from "@strapi/strapi";

export default factories.createCoreService("api::article.article", ({ strapi }) => ({
  async findPublished(filters = {}) {
    return strapi.entityService.findMany("api::article.article", {
      filters: { ...filters, status: "published" },
      sort: { publishedAt: "desc" },
      populate: ["author", "categories"],
    });
  },

  async incrementViews(id: string) {
    const article = await strapi.entityService.findOne("api::article.article", id);
    return strapi.entityService.update("api::article.article", id, {
      data: { views: (article.views || 0) + 1 },
    });
  },
}));
```

## Lifecycle Hooks

```ts
// src/api/article/content-types/article/lifecycles.ts
export default {
  async beforeCreate(event: any) {
    const { data } = event.params;
    if (!data.slug && data.title) {
      data.slug = data.title.toLowerCase().replace(/\s+/g, "-");
    }
  },

  async afterUpdate(event: any) {
    const { result } = event;
    if (result.status === "published") {
      await strapi.service("api::notification.notification").notifySubscribers(result);
    }
  },
};
```

## REST API Usage

```ts
// Fetch articles
const response = await fetch(
  "http://localhost:1337/api/articles?filters[status][$eq]=published&populate=*&sort=publishedAt:desc&pagination[page]=1&pagination[pageSize]=10"
);
const { data, meta } = await response.json();

// Create article (authenticated)
const createResponse = await fetch("http://localhost:1337/api/articles", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${jwt}`,
  },
  body: JSON.stringify({
    data: { title: "New Article", content: "Hello World", status: "draft" },
  }),
});
```

## Additional Resources

- Strapi: https://docs.strapi.io/
- REST API: https://docs.strapi.io/dev-docs/api/rest
- Content Types: https://docs.strapi.io/dev-docs/backend-customization/models
