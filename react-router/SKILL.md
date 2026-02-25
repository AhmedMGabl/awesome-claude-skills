---
name: react-router
description: React Router v7 development covering file-based routing, nested layouts, loaders and actions, form handling, data loading patterns, route protection with authentication, lazy loading, error boundaries, search params, and migration from v6.
---

# React Router

This skill should be used when implementing routing in React applications. It covers React Router v7, nested routes, data loading, form actions, authentication, and lazy loading.

## When to Use This Skill

Use this skill when you need to:

- Set up client-side routing with React Router
- Implement nested layouts and outlet patterns
- Load data with loaders and submit with actions
- Protect routes with authentication guards
- Handle search params and URL state

## Basic Setup (React Router v7)

```tsx
// app/routes.ts
import { type RouteConfig, route, layout, index } from "@react-router/dev/routes";

export default [
  layout("layouts/main.tsx", [
    index("routes/home.tsx"),
    route("about", "routes/about.tsx"),
    route("dashboard", "layouts/dashboard.tsx", [
      index("routes/dashboard/index.tsx"),
      route("settings", "routes/dashboard/settings.tsx"),
      route("users/:userId", "routes/dashboard/user.tsx"),
    ]),
  ]),
  route("login", "routes/login.tsx"),
  route("*", "routes/not-found.tsx"),
] satisfies RouteConfig;
```

## Layout with Outlet

```tsx
// layouts/main.tsx
import { Outlet, NavLink } from "react-router";

export default function MainLayout() {
  return (
    <div>
      <nav>
        <NavLink to="/" className={({ isActive }) => isActive ? "active" : ""}>
          Home
        </NavLink>
        <NavLink to="/dashboard">Dashboard</NavLink>
      </nav>
      <main>
        <Outlet />
      </main>
    </div>
  );
}
```

## Loaders and Actions

```tsx
// routes/dashboard/user.tsx
import { useLoaderData, Form, redirect } from "react-router";
import type { Route } from "./+types/user";

export async function loader({ params }: Route.LoaderArgs) {
  const user = await db.user.findUnique({ where: { id: params.userId } });
  if (!user) throw new Response("Not Found", { status: 404 });
  return { user };
}

export async function action({ request, params }: Route.ActionArgs) {
  const formData = await request.formData();
  const name = formData.get("name") as string;
  const email = formData.get("email") as string;

  await db.user.update({
    where: { id: params.userId },
    data: { name, email },
  });

  return redirect("/dashboard");
}

export default function UserPage() {
  const { user } = useLoaderData<typeof loader>();

  return (
    <div>
      <h1>{user.name}</h1>
      <Form method="post">
        <input name="name" defaultValue={user.name} />
        <input name="email" defaultValue={user.email} />
        <button type="submit">Save</button>
      </Form>
    </div>
  );
}
```

## Protected Routes

```tsx
// layouts/authenticated.tsx
import { Outlet, redirect } from "react-router";
import type { Route } from "./+types/authenticated";

export async function loader({ request }: Route.LoaderArgs) {
  const session = await getSession(request);
  if (!session.userId) {
    const url = new URL(request.url);
    throw redirect(`/login?redirectTo=${url.pathname}`);
  }
  return { user: await db.user.findUnique({ where: { id: session.userId } }) };
}

export default function AuthenticatedLayout() {
  return <Outlet />;
}
```

## Search Params

```tsx
import { useSearchParams } from "react-router";

function ProductList() {
  const [searchParams, setSearchParams] = useSearchParams();
  const category = searchParams.get("category") ?? "all";
  const page = Number(searchParams.get("page") ?? "1");

  function setCategory(cat: string) {
    setSearchParams((prev) => {
      prev.set("category", cat);
      prev.delete("page");
      return prev;
    });
  }

  function nextPage() {
    setSearchParams((prev) => {
      prev.set("page", String(page + 1));
      return prev;
    });
  }

  return (
    <div>
      <select value={category} onChange={(e) => setCategory(e.target.value)}>
        <option value="all">All</option>
        <option value="electronics">Electronics</option>
        <option value="clothing">Clothing</option>
      </select>
      {/* Product list */}
      <button onClick={nextPage}>Next Page</button>
    </div>
  );
}
```

## Error Boundary

```tsx
// routes/dashboard/user.tsx
import { useRouteError, isRouteErrorResponse } from "react-router";

export function ErrorBoundary() {
  const error = useRouteError();

  if (isRouteErrorResponse(error)) {
    return (
      <div>
        <h1>{error.status} {error.statusText}</h1>
        <p>{error.data}</p>
      </div>
    );
  }

  return <div>Something went wrong</div>;
}
```

## Lazy Loading

```tsx
// Lazy route component
import { lazy } from "react";

const AdminPanel = lazy(() => import("./routes/admin"));

// In route config — React Router v7 handles this automatically
// with file-based routing. For manual setup:
route("admin", "routes/admin.tsx")  // Automatically code-split
```

## Additional Resources

- React Router v7 docs: https://reactrouter.com/
- Data loading: https://reactrouter.com/start/framework/data-loading
- Route module API: https://reactrouter.com/start/framework/route-module
