---
name: remix-auth
description: Remix Auth patterns covering authentication strategies, session management, OAuth2/OIDC providers, form-based login, TOTP two-factor, role-based access, and protected route loaders.
---

# Remix Auth

This skill should be used when implementing authentication in Remix applications. It covers strategies, sessions, OAuth, form login, 2FA, and route protection.

## When to Use This Skill

Use this skill when you need to:

- Add authentication to Remix applications
- Implement OAuth2/OIDC with social providers
- Handle form-based email/password login
- Manage sessions with cookie storage
- Protect routes with authentication guards

## Setup

```bash
npm install remix-auth remix-auth-form remix-auth-oauth2 remix-auth-totp
```

## Session and Authenticator Setup

```ts
// app/services/session.server.ts
import { createCookieSessionStorage } from "@remix-run/node";

export const sessionStorage = createCookieSessionStorage({
  cookie: {
    name: "__session",
    httpOnly: true,
    path: "/",
    sameSite: "lax",
    secrets: [process.env.SESSION_SECRET!],
    secure: process.env.NODE_ENV === "production",
    maxAge: 60 * 60 * 24 * 30, // 30 days
  },
});

// app/services/auth.server.ts
import { Authenticator } from "remix-auth";
import { sessionStorage } from "./session.server";

export interface User {
  id: string;
  email: string;
  name: string;
  role: "admin" | "user";
}

export const authenticator = new Authenticator<User>(sessionStorage);
```

## Form Strategy (Email/Password)

```ts
// app/services/auth.server.ts
import { FormStrategy } from "remix-auth-form";
import { compare } from "bcryptjs";

authenticator.use(
  new FormStrategy(async ({ form }) => {
    const email = form.get("email") as string;
    const password = form.get("password") as string;

    const user = await db.user.findUnique({ where: { email } });
    if (!user) throw new Error("Invalid credentials");

    const valid = await compare(password, user.passwordHash);
    if (!valid) throw new Error("Invalid credentials");

    return { id: user.id, email: user.email, name: user.name, role: user.role };
  }),
  "form"
);
```

## Login Route

```tsx
// app/routes/login.tsx
import { type ActionFunctionArgs, type LoaderFunctionArgs, redirect } from "@remix-run/node";
import { Form, useActionData } from "@remix-run/react";
import { authenticator } from "~/services/auth.server";

export async function loader({ request }: LoaderFunctionArgs) {
  return authenticator.isAuthenticated(request, { successRedirect: "/dashboard" });
}

export async function action({ request }: ActionFunctionArgs) {
  try {
    return await authenticator.authenticate("form", request, {
      successRedirect: "/dashboard",
      throwOnError: true,
    });
  } catch (error) {
    if (error instanceof Response) throw error;
    return { error: (error as Error).message };
  }
}

export default function LoginPage() {
  const actionData = useActionData<typeof action>();

  return (
    <Form method="post">
      {actionData?.error && <p className="error">{actionData.error}</p>}
      <input type="email" name="email" placeholder="Email" required />
      <input type="password" name="password" placeholder="Password" required />
      <button type="submit">Sign In</button>
    </Form>
  );
}
```

## OAuth2 Strategy (Google)

```ts
// app/services/auth.server.ts
import { OAuth2Strategy } from "remix-auth-oauth2";

authenticator.use(
  new OAuth2Strategy(
    {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      authorizationEndpoint: "https://accounts.google.com/o/oauth2/v2/auth",
      tokenEndpoint: "https://oauth2.googleapis.com/token",
      redirectURI: `${process.env.APP_URL}/auth/google/callback`,
      scopes: ["openid", "email", "profile"],
    },
    async ({ tokens }) => {
      const response = await fetch("https://www.googleapis.com/oauth2/v3/userinfo", {
        headers: { Authorization: `Bearer ${tokens.accessToken()}` },
      });
      const profile = await response.json();
      const user = await findOrCreateUser({
        email: profile.email,
        name: profile.name,
      });
      return { id: user.id, email: user.email, name: user.name, role: user.role };
    }
  ),
  "google"
);

// app/routes/auth.google.tsx
export async function action({ request }: ActionFunctionArgs) {
  return authenticator.authenticate("google", request);
}

// app/routes/auth.google.callback.tsx
export async function loader({ request }: LoaderFunctionArgs) {
  return authenticator.authenticate("google", request, {
    successRedirect: "/dashboard",
    failureRedirect: "/login",
  });
}
```

## Protected Routes

```ts
// app/routes/dashboard.tsx
import { type LoaderFunctionArgs, json } from "@remix-run/node";
import { authenticator } from "~/services/auth.server";

export async function loader({ request }: LoaderFunctionArgs) {
  const user = await authenticator.isAuthenticated(request, {
    failureRedirect: "/login",
  });
  return json({ user });
}

// Role-based protection helper
async function requireRole(request: Request, role: string) {
  const user = await authenticator.isAuthenticated(request, {
    failureRedirect: "/login",
  });
  if (user.role !== role) throw new Response("Forbidden", { status: 403 });
  return user;
}
```

## Logout

```ts
// app/routes/logout.tsx
import { type ActionFunctionArgs } from "@remix-run/node";
import { authenticator } from "~/services/auth.server";

export async function action({ request }: ActionFunctionArgs) {
  return authenticator.logout(request, { redirectTo: "/login" });
}
```

## Additional Resources

- Remix Auth: https://github.com/sergiodxa/remix-auth
- Strategies: https://github.com/sergiodxa/remix-auth/wiki/Strategies
- OAuth2 Strategy: https://github.com/sergiodxa/remix-auth-oauth2
