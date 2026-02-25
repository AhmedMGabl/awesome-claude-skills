---
name: multi-tenant-saas
description: Multi-tenant SaaS architecture patterns covering tenant isolation strategies (schema-per-tenant, row-level security, database-per-tenant), subdomain routing, billing integration with Stripe, tenant-aware middleware, data partitioning, and scalable multi-tenancy in Node.js and Python.
---

# Multi-Tenant SaaS

This skill should be used when building multi-tenant SaaS applications. It covers tenant isolation strategies, subdomain routing, billing integration, middleware patterns, and scalable architecture.

## When to Use This Skill

Use this skill when you need to:

- Design multi-tenant data isolation
- Implement subdomain-based routing
- Add per-tenant billing and quotas
- Build tenant-aware middleware
- Scale SaaS infrastructure

## Row-Level Security (PostgreSQL + Prisma)

```sql
-- Enable RLS on tenant tables
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- Policy: users can only see their tenant's data
CREATE POLICY tenant_isolation ON posts
  USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

-- Set tenant context per request
SET app.current_tenant_id = 'tenant-uuid-here';
```

```typescript
// middleware/tenant.ts
import { Request, Response, NextFunction } from "express";
import { prisma } from "../db";

export async function tenantMiddleware(req: Request, res: Response, next: NextFunction) {
  // Extract tenant from subdomain: acme.app.com → acme
  const host = req.hostname;
  const subdomain = host.split(".")[0];

  const tenant = await prisma.tenant.findUnique({
    where: { slug: subdomain },
  });

  if (!tenant) {
    return res.status(404).json({ error: "Tenant not found" });
  }

  // Attach tenant to request
  req.tenant = tenant;

  // Set RLS context
  await prisma.$executeRawUnsafe(
    `SET app.current_tenant_id = '${tenant.id}'`,
  );

  next();
}
```

## Tenant-Scoped Queries

```typescript
// services/post-service.ts
import { PrismaClient } from "@prisma/client";

// Prisma extension for automatic tenant scoping
function tenantPrisma(tenantId: string) {
  return new PrismaClient().$extends({
    query: {
      $allModels: {
        async $allOperations({ args, query, model }) {
          // Inject tenantId into all queries
          if ("where" in args) {
            args.where = { ...args.where, tenantId };
          }
          if ("data" in args && typeof args.data === "object") {
            args.data = { ...args.data, tenantId };
          }
          return query(args);
        },
      },
    },
  });
}

// Usage
async function getPosts(tenantId: string) {
  const db = tenantPrisma(tenantId);
  // Automatically scoped to tenant — no manual filtering
  return db.post.findMany({ orderBy: { createdAt: "desc" } });
}
```

## Tenant Data Model

```prisma
// schema.prisma
model Tenant {
  id        String   @id @default(uuid())
  name      String
  slug      String   @unique
  plan      Plan     @default(FREE)
  users     User[]
  posts     Post[]
  settings  Json     @default("{}")
  createdAt DateTime @default(now())
}

model User {
  id       String @id @default(uuid())
  email    String
  role     Role   @default(MEMBER)
  tenant   Tenant @relation(fields: [tenantId], references: [id])
  tenantId String

  @@unique([email, tenantId])
}

model Post {
  id       String @id @default(uuid())
  title    String
  content  String
  tenant   Tenant @relation(fields: [tenantId], references: [id])
  tenantId String

  @@index([tenantId])
}

enum Plan {
  FREE
  PRO
  ENTERPRISE
}

enum Role {
  OWNER
  ADMIN
  MEMBER
}
```

## Subdomain Routing (Next.js)

```typescript
// middleware.ts (Next.js)
import { NextRequest, NextResponse } from "next/server";

export function middleware(request: NextRequest) {
  const host = request.headers.get("host") ?? "";
  const subdomain = host.split(".")[0];

  // Skip for main domain, www, and api
  if (["www", "app", "api"].includes(subdomain) || !host.includes(".")) {
    return NextResponse.next();
  }

  // Rewrite to tenant-specific path
  const url = request.nextUrl.clone();
  url.pathname = `/tenant/${subdomain}${url.pathname}`;
  return NextResponse.rewrite(url);
}

export const config = {
  matcher: ["/((?!_next|api|static|favicon.ico).*)"],
};
```

## Billing with Stripe

```typescript
// services/billing.ts
import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

const PLANS: Record<string, { priceId: string; limits: { posts: number; users: number } }> = {
  FREE: { priceId: "", limits: { posts: 10, users: 2 } },
  PRO: { priceId: "price_pro_monthly", limits: { posts: 1000, users: 20 } },
  ENTERPRISE: { priceId: "price_enterprise_monthly", limits: { posts: -1, users: -1 } },
};

export async function createSubscription(tenantId: string, plan: string) {
  const tenant = await prisma.tenant.findUniqueOrThrow({ where: { id: tenantId } });
  const planConfig = PLANS[plan];

  const session = await stripe.checkout.sessions.create({
    mode: "subscription",
    line_items: [{ price: planConfig.priceId, quantity: 1 }],
    success_url: `https://${tenant.slug}.app.com/settings?success=true`,
    cancel_url: `https://${tenant.slug}.app.com/settings?canceled=true`,
    metadata: { tenantId },
  });

  return session.url;
}

export async function checkLimit(tenantId: string, resource: "posts" | "users"): Promise<boolean> {
  const tenant = await prisma.tenant.findUniqueOrThrow({ where: { id: tenantId } });
  const limit = PLANS[tenant.plan].limits[resource];
  if (limit === -1) return true; // Unlimited

  const count = await prisma[resource].count({ where: { tenantId } });
  return count < limit;
}
```

## Isolation Strategy Comparison

```
STRATEGY            ISOLATION  COMPLEXITY  COST     USE CASE
────────────────────────────────────────────────────────────
Row-Level (shared)  Low        Low         Low      Most SaaS apps
Schema-per-tenant   Medium     Medium      Medium   Regulated industries
Database-per-tenant High       High        High     Enterprise / compliance

CHOOSE ROW-LEVEL when:
  - Standard SaaS with many tenants
  - Cost efficiency matters
  - Tenants don't need custom schemas

CHOOSE SCHEMA/DB-PER-TENANT when:
  - Strict data isolation required (HIPAA, SOC2)
  - Tenants need custom schemas
  - Per-tenant backup/restore needed
```

## Additional Resources

- PostgreSQL RLS: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- Prisma multi-tenancy: https://www.prisma.io/docs/guides/other/multi-tenancy
- Stripe Billing: https://stripe.com/docs/billing
