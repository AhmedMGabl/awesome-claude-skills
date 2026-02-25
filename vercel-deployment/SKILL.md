---
name: vercel-deployment
description: Vercel deployment covering project configuration, environment variables, serverless and edge functions, preview deployments, custom domains, monorepo support, build optimization, ISR revalidation, middleware, analytics, and CI/CD integration with GitHub Actions.
---

# Vercel Deployment

This skill should be used when deploying applications to Vercel. It covers project configuration, serverless functions, preview deployments, custom domains, and production optimization.

## When to Use This Skill

Use this skill when you need to:

- Deploy Next.js, React, or static sites to Vercel
- Configure serverless and edge functions
- Set up preview deployments for PRs
- Manage environment variables and domains
- Optimize builds for monorepo projects

## vercel.json Configuration

```json
{
  "framework": "nextjs",
  "buildCommand": "pnpm build",
  "installCommand": "pnpm install",
  "outputDirectory": ".next",
  "regions": ["iad1"],
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "s-maxage=60, stale-while-revalidate=300" }
      ]
    }
  ],
  "rewrites": [
    { "source": "/api/v1/:path*", "destination": "/api/:path*" }
  ],
  "redirects": [
    { "source": "/old-page", "destination": "/new-page", "permanent": true }
  ]
}
```

## Environment Variables

```bash
# Set environment variables
vercel env add STRIPE_SECRET_KEY production
vercel env add DATABASE_URL preview development

# Pull env vars to local .env
vercel env pull .env.local

# Use in vercel.json
# Reference as process.env.VARIABLE_NAME in code
```

## Serverless Functions

```typescript
// api/users.ts — automatically becomes /api/users
import type { VercelRequest, VercelResponse } from "@vercel/node";

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method === "GET") {
    const users = await db.users.findMany();
    return res.status(200).json(users);
  }

  if (req.method === "POST") {
    const user = await db.users.create({ data: req.body });
    return res.status(201).json(user);
  }

  res.setHeader("Allow", "GET, POST");
  return res.status(405).end();
}
```

## Edge Functions

```typescript
// api/geo.ts
export const config = { runtime: "edge" };

export default async function handler(request: Request) {
  const { geo } = request as any;

  return new Response(
    JSON.stringify({
      country: geo?.country,
      city: geo?.city,
      region: geo?.region,
    }),
    { headers: { "Content-Type": "application/json" } },
  );
}
```

## Monorepo Configuration

```json
// vercel.json at root
{
  "ignoreCommand": "npx turbo-ignore"
}
```

```bash
# Vercel project settings
# Root Directory: apps/web
# Build Command: cd ../.. && pnpm turbo build --filter=web
# Install Command: pnpm install
```

## Preview Deployments

```yaml
# .github/workflows/preview.yml
name: Preview
on: pull_request
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
```

## Custom Domains

```bash
vercel domains add example.com
vercel domains add www.example.com

# DNS records to configure:
# A     @       76.76.21.21
# CNAME www     cname.vercel-dns.com
```

## CLI Commands

```
COMMAND                          PURPOSE
──────────────────────────────────────────────
vercel                           Deploy to preview
vercel --prod                    Deploy to production
vercel env pull                  Pull env vars locally
vercel dev                       Run local dev server
vercel logs <url>                View function logs
vercel inspect <url>             Inspect deployment
vercel rollback                  Rollback to previous
```

## Additional Resources

- Vercel docs: https://vercel.com/docs
- CLI reference: https://vercel.com/docs/cli
- Frameworks: https://vercel.com/docs/frameworks
