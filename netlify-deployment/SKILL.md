---
name: netlify-deployment
description: Netlify deployment covering build configuration, serverless functions, edge functions, environment variables, redirects and headers, forms, identity authentication, and CI/CD with deploy previews.
---

# Netlify Deployment

This skill should be used when deploying applications to Netlify. It covers build configuration, serverless and edge functions, environment variables, redirects, forms, identity, and deploy previews.

## When to Use This Skill

Use this skill when you need to:

- Deploy Next.js, Vite, or Astro sites to Netlify
- Configure serverless or edge functions
- Manage environment variables per deploy context
- Set up redirects, headers, or form handling
- Enable Netlify Identity for authentication
- Configure deploy previews and branch deploys

## netlify.toml Configuration

```toml
[build]
  command = "npm run build"
  publish = "dist"
  functions = "netlify/functions"

[dev]
  command = "npm run dev"
  targetPort = 5173

[context.production.environment]
  NODE_ENV = "production"
  API_URL = "https://api.example.com"

[context.deploy-preview.environment]
  API_URL = "https://staging.api.example.com"
```

## Build Settings by Framework

```toml
# Next.js
[build]
  command = "next build"
  publish = ".next"
[[plugins]]
  package = "@netlify/plugin-nextjs"

# Vite
[build]
  command = "vite build"
  publish = "dist"

# Astro
[build]
  command = "astro build"
  publish = "dist"
[[plugins]]
  package = "@astrojs/netlify"
```

## Serverless Functions (TypeScript)

```typescript
// netlify/functions/users.ts
import type { Handler, HandlerEvent } from "@netlify/functions";

export const handler: Handler = async (event: HandlerEvent) => {
  if (event.httpMethod !== "GET") {
    return { statusCode: 405, body: "Method Not Allowed" };
  }

  const users = await db.users.findMany();
  return {
    statusCode: 200,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(users),
  };
};
```

## Edge Functions (Deno Runtime)

```typescript
// netlify/edge-functions/geo-redirect.ts
import type { Context } from "@netlify/edge-functions";

export default async function handler(request: Request, context: Context) {
  const country = context.geo?.country?.code ?? "US";
  if (country === "GB") {
    return Response.redirect(new URL("/uk", request.url), 302);
  }
  return context.next();
}

export const config = { path: "/" };
```

## Environment Variables

```bash
# Set per context
netlify env:set STRIPE_SECRET_KEY sk_live_xxx --context production
netlify env:set STRIPE_SECRET_KEY sk_test_xxx --context deploy-preview

# Import from file / list all
netlify env:import .env
netlify env:list
```

## Redirects and Headers

```toml
[[redirects]]
  from = "/old-page"
  to = "/new-page"
  status = 301

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200          # SPA fallback

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"

[[headers]]
  for = "/assets/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"
```

## Netlify Forms

```html
<form name="contact" method="POST" data-netlify="true" netlify-honeypot="bot-field">
  <input type="hidden" name="form-name" value="contact" />
  <input type="hidden" name="bot-field" />
  <input type="text" name="name" required />
  <input type="email" name="email" required />
  <button type="submit">Send</button>
</form>
```

```typescript
// JS-enhanced submission
await fetch("/", {
  method: "POST",
  headers: { "Content-Type": "application/x-www-form-urlencoded" },
  body: new URLSearchParams({ "form-name": "contact", name, email }).toString(),
});
```

## Identity and Authentication

```typescript
// Client — netlify-identity-widget
import netlifyIdentity from "netlify-identity-widget";
netlifyIdentity.init();
netlifyIdentity.on("login", (user) => netlifyIdentity.close());

// Serverless function — verify JWT from Netlify Identity
export const handler: Handler = async (event, context) => {
  const user = context.clientContext?.user;
  if (!user) return { statusCode: 401, body: "Unauthorized" };
  return { statusCode: 200, body: JSON.stringify({ email: user.email }) };
};
```

## Deploy Previews and Branch Deploys

```yaml
# .github/workflows/preview.yml
name: Netlify Preview
on: pull_request
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "20" }
      - run: npm ci && npm run build
      - uses: nwtgck/actions-netlify@v3
        with:
          publish-dir: dist
          github-token: ${{ secrets.GITHUB_TOKEN }}
          enable-pull-request-comment: true
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

## CLI Commands

```
COMMAND                          PURPOSE
──────────────────────────────────────────────────
netlify dev                      Run local dev server with functions
netlify deploy                   Deploy to draft preview URL
netlify deploy --prod            Deploy to production
netlify functions:invoke <name>  Invoke a function locally
netlify logs:function <name>     Stream function logs
netlify env:list                 List environment variables
netlify link                     Link project to a Netlify site
netlify open                     Open site in browser
```

## Additional Resources

- Netlify docs: https://docs.netlify.com
- Functions: https://docs.netlify.com/functions/overview
- Edge functions: https://docs.netlify.com/edge-functions/overview
- CLI reference: https://docs.netlify.com/cli/get-started
