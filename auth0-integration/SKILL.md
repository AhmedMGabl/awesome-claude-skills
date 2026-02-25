---
name: auth0-integration
description: Auth0 identity platform integration covering Universal Login, social connections, JWT validation, role-based access control, organizations and multi-tenancy, machine-to-machine tokens, Auth0 Actions, Next.js SDK, and Express middleware patterns.
---

# Auth0 Integration

This skill should be used when integrating Auth0 for authentication and authorization. It covers Universal Login, social auth, RBAC, multi-tenancy, and SDK patterns.

## When to Use This Skill

Use this skill when you need to:

- Add Auth0 authentication to web applications
- Implement social login (Google, GitHub, etc.)
- Set up role-based access control with Auth0
- Handle machine-to-machine authentication
- Use Auth0 Organizations for multi-tenancy

## Next.js Integration

```typescript
// app/api/auth/[auth0]/route.ts
import { handleAuth, handleLogin } from "@auth0/nextjs-auth0";

export const GET = handleAuth({
  login: handleLogin({
    authorizationParams: {
      audience: process.env.AUTH0_AUDIENCE,
      scope: "openid profile email",
    },
  }),
});
```

```tsx
// app/layout.tsx
import { UserProvider } from "@auth0/nextjs-auth0/client";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        <UserProvider>{children}</UserProvider>
      </body>
    </html>
  );
}
```

```tsx
// components/AuthButtons.tsx
"use client";
import { useUser } from "@auth0/nextjs-auth0/client";

export function AuthButtons() {
  const { user, isLoading } = useUser();

  if (isLoading) return <div>Loading...</div>;

  if (user) {
    return (
      <div>
        <span>Welcome, {user.name}</span>
        <a href="/api/auth/logout">Logout</a>
      </div>
    );
  }

  return <a href="/api/auth/login">Login</a>;
}
```

## Protected API Routes

```typescript
// app/api/protected/route.ts
import { withApiAuthRequired, getSession } from "@auth0/nextjs-auth0";
import { NextResponse } from "next/server";

export const GET = withApiAuthRequired(async (req) => {
  const session = await getSession();
  const user = session?.user;

  return NextResponse.json({ message: `Hello ${user?.name}` });
});
```

## Express JWT Middleware

```typescript
import { auth, requiredScopes } from "express-oauth2-jwt-bearer";

// Validate JWT from Auth0
const checkJwt = auth({
  audience: process.env.AUTH0_AUDIENCE,
  issuerBaseURL: `https://${process.env.AUTH0_DOMAIN}`,
  tokenSigningAlg: "RS256",
});

// Require specific permissions
app.get("/api/admin", checkJwt, requiredScopes("admin:read"), (req, res) => {
  res.json({ data: "admin content" });
});
```

## RBAC with Permissions

```typescript
// middleware/rbac.ts
function requirePermission(permission: string) {
  return (req: Request, res: Response, next: NextFunction) => {
    const permissions = req.auth?.payload.permissions as string[] ?? [];

    if (!permissions.includes(permission)) {
      return res.status(403).json({ error: "Insufficient permissions" });
    }

    next();
  };
}

// Usage
app.delete("/api/users/:id", checkJwt, requirePermission("users:delete"), deleteUser);
app.put("/api/users/:id", checkJwt, requirePermission("users:update"), updateUser);
```

## Machine-to-Machine Tokens

```typescript
async function getM2MToken(): Promise<string> {
  const res = await fetch(`https://${process.env.AUTH0_DOMAIN}/oauth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      client_id: process.env.AUTH0_M2M_CLIENT_ID,
      client_secret: process.env.AUTH0_M2M_CLIENT_SECRET,
      audience: process.env.AUTH0_AUDIENCE,
      grant_type: "client_credentials",
    }),
  });

  const { access_token } = await res.json();
  return access_token;
}
```

## Additional Resources

- Auth0 docs: https://auth0.com/docs
- Next.js SDK: https://github.com/auth0/nextjs-auth0
- Auth0 Actions: https://auth0.com/docs/customize/actions
