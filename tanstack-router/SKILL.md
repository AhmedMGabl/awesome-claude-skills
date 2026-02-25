---
name: tanstack-router
description: TanStack Router covering type-safe routing, file-based routes, search params validation, data loading, route context, authentication guards, code splitting, and SSR with TanStack Start.
---

# TanStack Router

This skill should be used when implementing routing with TanStack Router in React applications. It covers type-safe routes, search params, data loading, and authentication patterns.

## When to Use This Skill

Use this skill when you need to:

- Build type-safe React routing with full TypeScript inference
- Validate and serialize URL search parameters
- Load data with route loaders
- Implement authentication guards
- Use file-based routing conventions

## Setup

```bash
npm install @tanstack/react-router
npm install -D @tanstack/router-plugin @tanstack/router-devtools
```

```typescript
// vite.config.ts
import { TanStackRouterVite } from "@tanstack/router-plugin/vite";

export default defineConfig({
  plugins: [TanStackRouterVite(), react()],
});
```

## Route Tree (File-Based)

```
src/routes/
├── __root.tsx        # Root layout
├── index.tsx         # /
├── about.tsx         # /about
├── posts/
│   ├── index.tsx     # /posts
│   └── $postId.tsx   # /posts/:postId
├── _auth/            # Layout route group (no URL segment)
│   ├── route.tsx     # Auth layout
│   ├── dashboard.tsx # /dashboard
│   └── settings.tsx  # /settings
```

## Root Route

```tsx
// src/routes/__root.tsx
import { createRootRouteWithContext, Outlet, Link } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/router-devtools";

interface RouterContext {
  auth: { user: User | null; isAuthenticated: boolean };
}

export const Route = createRootRouteWithContext<RouterContext>()({
  component: () => (
    <>
      <nav>
        <Link to="/" activeProps={{ className: "active" }}>Home</Link>
        <Link to="/posts" activeProps={{ className: "active" }}>Posts</Link>
        <Link to="/dashboard" activeProps={{ className: "active" }}>Dashboard</Link>
      </nav>
      <Outlet />
      <TanStackRouterDevtools />
    </>
  ),
  notFoundComponent: () => <div>404 Not Found</div>,
});
```

## Search Params Validation

```tsx
// src/routes/posts/index.tsx
import { createFileRoute } from "@tanstack/react-router";
import { z } from "zod";

const postsSearchSchema = z.object({
  page: z.number().int().positive().default(1),
  sort: z.enum(["newest", "popular"]).default("newest"),
  tag: z.string().optional(),
});

export const Route = createFileRoute("/posts/")({
  validateSearch: postsSearchSchema,
  loaderDeps: ({ search }) => search,
  loader: async ({ deps: { page, sort, tag } }) => {
    return fetchPosts({ page, sort, tag });
  },
  component: PostsPage,
});

function PostsPage() {
  const posts = Route.useLoaderData();
  const { page, sort, tag } = Route.useSearch();
  const navigate = Route.useNavigate();

  return (
    <div>
      <select
        value={sort}
        onChange={(e) => navigate({ search: { sort: e.target.value as any } })}
      >
        <option value="newest">Newest</option>
        <option value="popular">Popular</option>
      </select>
      {posts.map((post) => <PostCard key={post.id} post={post} />)}
      <button onClick={() => navigate({ search: (prev) => ({ ...prev, page: page + 1 }) })}>
        Next Page
      </button>
    </div>
  );
}
```

## Data Loading

```tsx
// src/routes/posts/$postId.tsx
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/posts/$postId")({
  loader: async ({ params: { postId } }) => {
    const post = await fetchPost(postId);
    if (!post) throw new Error("Post not found");
    return post;
  },
  pendingComponent: () => <div>Loading...</div>,
  errorComponent: ({ error }) => <div>Error: {error.message}</div>,
  component: PostPage,
});

function PostPage() {
  const post = Route.useLoaderData();
  const { postId } = Route.useParams();

  return (
    <article>
      <h1>{post.title}</h1>
      <p>{post.content}</p>
    </article>
  );
}
```

## Authentication Guard

```tsx
// src/routes/_auth/route.tsx
import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";

export const Route = createFileRoute("/_auth")({
  beforeLoad: ({ context }) => {
    if (!context.auth.isAuthenticated) {
      throw redirect({ to: "/login", search: { redirect: location.pathname } });
    }
  },
  component: () => <Outlet />,
});
```

## App Entry

```tsx
// src/main.tsx
import { RouterProvider, createRouter } from "@tanstack/react-router";
import { routeTree } from "./routeTree.gen"; // Auto-generated

const router = createRouter({
  routeTree,
  context: { auth: { user: null, isAuthenticated: false } },
  defaultPreload: "intent",
});

declare module "@tanstack/react-router" {
  interface Register { router: typeof router }
}

function App() {
  const auth = useAuth();
  return <RouterProvider router={router} context={{ auth }} />;
}
```

## Additional Resources

- TanStack Router docs: https://tanstack.com/router/latest
- File-based routing: https://tanstack.com/router/latest/docs/framework/react/guide/file-based-routing
- Search params: https://tanstack.com/router/latest/docs/framework/react/guide/search-params
