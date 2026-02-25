---
name: migration-patterns
description: Software migration patterns covering framework migration (CRA to Vite/Next.js), API versioning, data migration strategies, strangler fig pattern, feature flag migration, database schema evolution, gradual TypeScript adoption, and zero-downtime migration techniques.
---

# Migration Patterns

This skill should be used when migrating between frameworks, APIs, databases, or languages. It covers incremental migration, strangler fig, feature flags, and zero-downtime strategies.

## When to Use This Skill

Use this skill when you need to:

- Migrate from one framework to another
- Implement API versioning during migration
- Perform zero-downtime database migrations
- Gradually adopt TypeScript in a JavaScript project
- Use the strangler fig pattern for legacy replacement

## CRA to Vite Migration

```typescript
// 1. Install Vite and dependencies
// npm install vite @vitejs/plugin-react

// 2. Create vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: { port: 3000 },
  resolve: {
    alias: { "~": "/src" },
  },
  define: {
    // CRA environment variable compatibility
    "process.env": {},
  },
});

// 3. Move index.html to root and update
// <script type="module" src="/src/index.tsx"></script>

// 4. Replace REACT_APP_ env vars with VITE_
// Before: process.env.REACT_APP_API_URL
// After:  import.meta.env.VITE_API_URL

// 5. Update package.json scripts
// "dev": "vite",
// "build": "tsc && vite build",
// "preview": "vite preview"
```

## Pages Router to App Router (Next.js)

```typescript
// Migration strategy: coexist pages/ and app/ directories

// Phase 1: Move layouts to app/
// app/layout.tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

// Phase 2: Migrate pages one at a time
// pages/about.tsx → app/about/page.tsx

// Before (pages/about.tsx):
// export async function getStaticProps() { ... }
// export default function About({ data }) { ... }

// After (app/about/page.tsx):
async function getData() {
  const res = await fetch("https://api.example.com/about", { next: { revalidate: 3600 } });
  return res.json();
}

export default async function AboutPage() {
  const data = await getData();
  return <div>{/* ... */}</div>;
}

// Phase 3: Migrate API routes
// pages/api/users.ts → app/api/users/route.ts
```

## Gradual TypeScript Adoption

```jsonc
// tsconfig.json — relaxed for migration
{
  "compilerOptions": {
    "allowJs": true,            // Allow .js files alongside .ts
    "checkJs": false,           // Don't type-check .js files yet
    "strict": false,            // Enable later when more code is migrated
    "noImplicitAny": false,     // Allow implicit any during migration
    "outDir": "dist",
    "jsx": "react-jsx"
  },
  "include": ["src"]
}
```

```typescript
// Strategy: rename files .js → .ts one at a time
// Start with leaf modules (no imports from other .js files)
// Then work up the dependency tree

// Phase 1: Rename utils.js → utils.ts, add basic types
// Phase 2: Rename services → .ts, type API responses
// Phase 3: Rename components → .tsx, type props
// Phase 4: Enable strict mode flags one by one:
//   noImplicitAny → strictNullChecks → strict
```

## API Versioning During Migration

```typescript
// Route-based versioning
app.use("/api/v1", v1Router);
app.use("/api/v2", v2Router);

// v2 router delegates to v1 for unchanged endpoints
const v2Router = express.Router();
v2Router.get("/users", v2GetUsers);         // Changed
v2Router.get("/posts", v1GetPosts);         // Unchanged, reuse v1
v2Router.get("/comments", v2GetComments);   // Changed

// Deprecation header for v1
app.use("/api/v1", (req, res, next) => {
  res.set("Deprecation", "true");
  res.set("Sunset", "2026-06-01");
  res.set("Link", '</api/v2>; rel="successor-version"');
  next();
});
```

## Migration Checklist

```
BEFORE MIGRATION:
  [ ] Document current architecture and dependencies
  [ ] Write characterization tests for existing behavior
  [ ] Set up feature flags for gradual rollout
  [ ] Create rollback plan
  [ ] Benchmark current performance as baseline

DURING MIGRATION:
  [ ] Migrate incrementally (one module/page at a time)
  [ ] Keep old and new code running in parallel
  [ ] Monitor error rates and performance after each step
  [ ] Update documentation as you go

AFTER MIGRATION:
  [ ] Remove old code and feature flags
  [ ] Run full regression test suite
  [ ] Update CI/CD pipelines
  [ ] Document lessons learned
```

## Additional Resources

- Strangler Fig Pattern: https://martinfowler.com/bliki/StranglerFigApplication.html
- Next.js Migration: https://nextjs.org/docs/app/building-your-application/upgrading
- TypeScript Migration: https://www.typescriptlang.org/docs/handbook/migrating-from-javascript.html
