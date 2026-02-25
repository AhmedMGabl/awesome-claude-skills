---
name: better-auth
description: Better Auth library covering email/password authentication, OAuth providers, session management, two-factor auth, organization multi-tenancy, rate limiting, database adapters, and framework integration for Next.js, Nuxt, and SvelteKit.
---

# Better Auth

This skill should be used when implementing authentication with Better Auth. It covers email/password, OAuth, 2FA, organizations, and framework integration.

## When to Use This Skill

Use this skill when you need to:

- Add authentication to a full-stack TypeScript app
- Support multiple OAuth providers (Google, GitHub, etc.)
- Implement two-factor authentication
- Handle multi-tenant organizations
- Use a framework-agnostic auth solution

## Setup

```bash
npm install better-auth
```

```typescript
// src/lib/auth.ts
import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { db } from "./db";

export const auth = betterAuth({
  database: drizzleAdapter(db, { provider: "pg" }),
  emailAndPassword: { enabled: true },
  socialProviders: {
    github: {
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    },
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    },
  },
});

export type Session = typeof auth.$Infer.Session;
```

## Client Setup

```typescript
// src/lib/auth-client.ts
import { createAuthClient } from "better-auth/react"; // or /vue, /svelte

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL,
});

export const { signIn, signUp, signOut, useSession } = authClient;
```

## Sign Up / Sign In

```tsx
function SignUpForm() {
  const handleSignUp = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);

    await signUp.email({
      email: formData.get("email") as string,
      password: formData.get("password") as string,
      name: formData.get("name") as string,
    });
  };

  return (
    <form onSubmit={handleSignUp}>
      <input name="name" placeholder="Name" required />
      <input name="email" type="email" placeholder="Email" required />
      <input name="password" type="password" placeholder="Password" required />
      <button type="submit">Sign Up</button>
    </form>
  );
}

// Social sign in
function SocialLogin() {
  return (
    <div className="flex gap-2">
      <button onClick={() => signIn.social({ provider: "github" })}>
        Sign in with GitHub
      </button>
      <button onClick={() => signIn.social({ provider: "google" })}>
        Sign in with Google
      </button>
    </div>
  );
}
```

## Session Hook

```tsx
function UserProfile() {
  const { data: session, isPending } = useSession();

  if (isPending) return <div>Loading...</div>;
  if (!session) return <div>Not authenticated</div>;

  return (
    <div>
      <p>Welcome, {session.user.name}</p>
      <p>{session.user.email}</p>
      <button onClick={() => signOut()}>Sign Out</button>
    </div>
  );
}
```

## API Route (Next.js)

```typescript
// app/api/auth/[...all]/route.ts
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
```

## Two-Factor Authentication

```typescript
import { betterAuth } from "better-auth";
import { twoFactor } from "better-auth/plugins";

export const auth = betterAuth({
  plugins: [twoFactor({ issuer: "MyApp" })],
  // ...other config
});

// Client: Enable 2FA
const { data } = await authClient.twoFactor.enable();
// Returns TOTP URI for QR code

// Client: Verify during login
await authClient.twoFactor.verifyTotp({ code: "123456" });
```

## Organizations (Multi-Tenant)

```typescript
import { organization } from "better-auth/plugins";

export const auth = betterAuth({
  plugins: [
    organization({
      allowUserToCreateOrganization: true,
    }),
  ],
});

// Client: Create organization
await authClient.organization.create({ name: "My Company", slug: "my-company" });

// Client: Invite member
await authClient.organization.inviteMember({
  email: "teammate@example.com",
  role: "member",
  organizationId: orgId,
});
```

## Middleware Protection

```typescript
// middleware.ts (Next.js)
import { auth } from "@/lib/auth";
import { NextRequest, NextResponse } from "next/server";

export async function middleware(request: NextRequest) {
  const session = await auth.api.getSession({ headers: request.headers });

  if (!session && request.nextUrl.pathname.startsWith("/dashboard")) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = { matcher: ["/dashboard/:path*"] };
```

## Additional Resources

- Better Auth docs: https://www.better-auth.com/docs
- Plugins: https://www.better-auth.com/docs/plugins
- Framework guides: https://www.better-auth.com/docs/integrations
