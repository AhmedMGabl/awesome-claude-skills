---
name: strapi-cms
description: Strapi headless CMS covering content type creation, REST and GraphQL APIs, custom controllers, lifecycle hooks, authentication, role-based access, media handling, custom plugins, and deployment patterns. This skill should be used when building or integrating with a Strapi backend, including content modeling, API customization, access control, and production deployment.
---

# Strapi CMS

## When to Use This Skill

- Define or modify content type schemas
- Query or mutate data via REST or GraphQL APIs
- Extend default controllers and services with custom logic
- Add lifecycle hooks for before/after database operations
- Configure JWT authentication and role-based access control
- Handle file and image uploads with cloud providers
- Build custom plugins or extend the admin panel
- Deploy Strapi with Docker or on DigitalOcean

## Content Type Schema Definition

```json
// src/api/article/content-types/article/schema.json
{
  "kind": "collectionType",
  "collectionName": "articles",
  "info": { "singularName": "article", "pluralName": "articles", "displayName": "Article" },
  "options": { "draftAndPublish": true },
  "attributes": {
    "title":  { "type": "string", "required": true, "maxLength": 200 },
    "slug":   { "type": "uid", "targetField": "title", "required": true },
    "body":   { "type": "richtext" },
    "cover":  { "type": "media", "multiple": false, "allowedTypes": ["images"] },
    "author": { "type": "relation", "relation": "manyToOne", "target": "api::author.author" },
    "tags":   { "type": "relation", "relation": "manyToMany", "target": "api::tag.tag" }
  }
}
```

## REST API

```typescript
const BASE = "http://localhost:1337/api";
const h = { Authorization: `Bearer ${JWT}`, "Content-Type": "application/json" };

// find — filters, sort, pagination, populate
const list = await fetch(
  `${BASE}/articles?populate=cover,author&sort=publishedAt:desc&pagination[page]=1&pagination[pageSize]=10&filters[tags][name][$eq]=typescript`,
  { headers: h }
).then((r) => r.json());

const one     = await fetch(`${BASE}/articles/${id}?populate=*`, { headers: h }).then((r) => r.json());
const created = await fetch(`${BASE}/articles`, { method: "POST", headers: h, body: JSON.stringify({ data: { title: "Hello", author: 1 } }) }).then((r) => r.json());
await fetch(`${BASE}/articles/${id}`, { method: "PUT",    headers: h, body: JSON.stringify({ data: { title: "Updated" } }) });
await fetch(`${BASE}/articles/${id}`, { method: "DELETE", headers: h });
```

## GraphQL Setup and Queries

```bash
npm install @strapi/plugin-graphql   # restart Strapi after install
```

```graphql
query GetArticles($tag: String!) {
  articles(
    filters: { tags: { name: { eq: $tag } } }
    sort: "publishedAt:desc"
    pagination: { page: 1, pageSize: 10 }
  ) {
    data {
      id
      attributes {
        title slug publishedAt
        cover  { data { attributes { url alternativeText } } }
        author { data { attributes { name } } }
      }
    }
    meta { pagination { total pageCount } }
  }
}

mutation CreateArticle($data: ArticleInput!) {
  createArticle(data: $data) { data { id attributes { slug } } }
}
```

## Custom Controllers and Services

```typescript
// src/api/article/controllers/article.ts
import { factories } from "@strapi/strapi";
export default factories.createCoreController("api::article.article", ({ strapi }) => ({
  async findBySlug(ctx) {
    const entity = await strapi.service("api::article.article").findBySlug(ctx.params.slug, ctx.query);
    if (!entity) return ctx.notFound();
    return this.transformResponse(entity);
  },
}));
// src/api/article/services/article.ts
export default factories.createCoreService("api::article.article", ({ strapi }) => ({
  async findBySlug(slug: string, params = {}) {
    const [entity] = await strapi.entityService.findMany("api::article.article", {
      ...params, filters: { slug }, limit: 1,
    });
    return entity ?? null;
  },
}));
```

## Lifecycle Hooks

```typescript
// src/api/article/content-types/article/lifecycles.ts
export default {
  async beforeCreate(event) {
    const { data } = event.params;
    if (!data.slug && data.title) {
      data.slug = data.title.toLowerCase().replace(/\s+/g, "-").replace(/[^\w-]/g, "");
    }
  },
  async afterCreate(event) {
    strapi.log.info(`Article created: ${event.result.title}`);
  },
};
```

## Authentication and RBAC

```typescript
// Login
const { jwt } = await fetch("http://localhost:1337/api/auth/local", {
  method: "POST", headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ identifier: "alice@example.com", password: "Secret1!" }),
}).then((r) => r.json());

// Grant permission in bootstrap — src/index.ts
export default {
  async bootstrap({ strapi }) {
    const role = await strapi.query("plugin::users-permissions.role").findOne({ where: { type: "authenticated" } });
    await strapi.query("plugin::users-permissions.permission").updateMany({
      where: { role: role.id, action: "api::article.article.create" }, data: { enabled: true },
    });
  },
};
```

## Media Upload Handling

```typescript
// Upload and attach to entity
const form = new FormData();
form.append("files", blob, "photo.jpg");
form.append("ref", "api::article.article");
form.append("refId", String(articleId));
form.append("field", "cover");
const [file] = await fetch("http://localhost:1337/api/upload", {
  method: "POST", headers: { Authorization: `Bearer ${JWT}` }, body: form,
}).then((r) => r.json());

// config/plugins.ts — switch to S3
export default ({ env }) => ({
  upload: { config: { provider: "aws-s3", providerOptions: {
    accessKeyId: env("AWS_ACCESS_KEY_ID"), secretAccessKey: env("AWS_SECRET_ACCESS_KEY"),
    region: env("AWS_REGION"), params: { Bucket: env("AWS_BUCKET") },
  } } },
});
```

## Custom Plugin Structure

```
src/plugins/my-plugin/
├── strapi-server.ts        # Entry point — register/bootstrap/routes/controllers/services
└── admin/src/index.tsx     # Admin panel extension (optional)
```

```typescript
// strapi-server.ts
export default () => ({
  register({ strapi }) {
    strapi.customFields.register({ name: "color", plugin: "my-plugin", type: "string" });
  },
  controllers: require("./server/controllers"),
  routes:      require("./server/routes"),
  services:    require("./server/services"),
});
```

## Deployment

### Docker

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
ENV NODE_ENV=production
EXPOSE 1337
CMD ["npm", "start"]
```

```yaml
# docker-compose.yml
services:
  strapi:
    build: .
    ports: ["1337:1337"]
    environment:
      DATABASE_CLIENT: postgres
      DATABASE_HOST: db
      DATABASE_NAME: strapi
      DATABASE_USERNAME: strapi
      DATABASE_PASSWORD: strapi
      JWT_SECRET: ${JWT_SECRET}
      APP_KEYS: ${APP_KEYS}
    depends_on: [db]
  db:
    image: postgres:16-alpine
    environment: { POSTGRES_DB: strapi, POSTGRES_USER: strapi, POSTGRES_PASSWORD: strapi }
    volumes: [pgdata:/var/lib/postgresql/data]
volumes:
  pgdata:
```

### DigitalOcean App Platform

```yaml
# .do/app.yaml
name: strapi-cms
services:
  - name: api
    github: { repo: org/repo, branch: main }
    build_command: npm run build
    run_command: npm start
    envs:
      - { key: NODE_ENV, value: production }
      - { key: DATABASE_URL, scope: RUN_TIME, value: "${db.DATABASE_URL}" }
databases:
  - { name: db, engine: PG, version: "16" }
```

## Additional Resources

- Strapi docs: https://docs.strapi.io
- REST API filters: https://docs.strapi.io/dev-docs/api/rest/filters-locale-publication
- GraphQL plugin: https://docs.strapi.io/dev-docs/plugins/graphql
- Upload providers: https://docs.strapi.io/dev-docs/providers
