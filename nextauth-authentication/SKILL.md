---
name: nextauth-authentication
description: NextAuth.js (Auth.js) authentication covering OAuth providers (Google, GitHub, Discord), credentials provider, JWT and database sessions, role-based access control, middleware protection, custom sign-in pages, adapter configuration for Prisma and Drizzle, and App Router integration.
---

# NextAuth.js Authentication

This skill should be used when implementing authentication in Next.js applications with NextAuth.js (Auth.js v5). It covers OAuth, credentials, sessions, RBAC, middleware, and database adapters.

## When to Use This Skill

Use this skill when you need to:

- Add OAuth login (Google, GitHub, Discord) to Next.js
- Implement email/password authentication
- Configure JWT or database sessions
- Protect routes with middleware
- Set up role-based access control

## Auth.js v5 Setup (App Router)

```typescript
// auth.ts
import NextAuth from "next-auth";
import Google from "next-auth/providers/google";
import GitHub from "next-auth/providers/github";
import Credentials from "next-auth/providers/credentials";
import { PrismaAdapter } from "@auth/prisma-adapter";
import { prisma } from "@/lib/prisma";
import bcrypt from "bcryptjs";

export const { handlers, auth, signIn, signOut } = NextAuth({
  adapter: PrismaAdapter(prisma),
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    GitHub({
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    }),
    Credentials({
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        const user = await prisma.user.findUnique({
          where: { email: credentials.email as string },
        });
        if (!user?.hashedPassword) return null;

        const valid = await bcrypt.compare(
          credentials.password as string,
          user.hashedPassword,
        );
        if (!valid) return null;

        return { id: user.id, name: user.name, email: user.email, role: user.role };
      },
    }),
  ],
  session: { strategy: "jwt" },
  pages: {
    signIn: "/login",
    error: "/auth/error",
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.role = (user as any).role;
        token.id = user.id;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string;
        session.user.role = token.role as string;
      }
      return session;
    },
    authorized({ auth, request: { nextUrl } }) {
      const isLoggedIn = !!auth?.user;
      const isProtected = nextUrl.pathname.startsWith("/dashboard");
      if (isProtected && !isLoggedIn) {
        return Response.redirect(new URL("/login", nextUrl));
      }
      return true;
    },
  },
});
```

## Route Handlers

```typescript
// app/api/auth/[...nextauth]/route.ts
import { handlers } from "@/auth";
export const { GET, POST } = handlers;
```

## Middleware Protection

```typescript
// middleware.ts
export { auth as middleware } from "@/auth";

export const config = {
  matcher: ["/dashboard/:path*", "/api/protected/:path*", "/settings/:path*"],
};
```

## Server Component Auth

```typescript
// app/dashboard/page.tsx
import { auth } from "@/auth";
import { redirect } from "next/navigation";

export default async function DashboardPage() {
  const session = await auth();

  if (!session) redirect("/login");

  return (
    <div>
      <h1>Welcome, {session.user?.name}</h1>
      {session.user?.role === "admin" && <AdminPanel />}
    </div>
  );
}
```

## Client Component Auth

```typescript
"use client";
import { useSession, signIn, signOut } from "next-auth/react";

export function AuthButton() {
  const { data: session, status } = useSession();

  if (status === "loading") return <p>Loading...</p>;

  if (session) {
    return (
      <div>
        <p>Signed in as {session.user?.email}</p>
        <button onClick={() => signOut()}>Sign out</button>
      </div>
    );
  }

  return (
    <div>
      <button onClick={() => signIn("google")}>Sign in with Google</button>
      <button onClick={() => signIn("github")}>Sign in with GitHub</button>
    </div>
  );
}
```

## Session Provider

```typescript
// app/layout.tsx
import { SessionProvider } from "next-auth/react";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        <SessionProvider>{children}</SessionProvider>
      </body>
    </html>
  );
}
```

## Role-Based Access Control

```typescript
// lib/auth-utils.ts
import { auth } from "@/auth";

export async function requireRole(role: string) {
  const session = await auth();
  if (!session) throw new Error("Unauthenticated");
  if (session.user?.role !== role) throw new Error("Unauthorized");
  return session;
}

// Usage in Server Action
export async function deleteUser(userId: string) {
  const session = await requireRole("admin");
  await prisma.user.delete({ where: { id: userId } });
}
```

## Type Augmentation

```typescript
// types/next-auth.d.ts
import "next-auth";

declare module "next-auth" {
  interface User {
    role?: string;
  }
  interface Session {
    user: {
      id: string;
      role: string;
    } & DefaultSession["user"];
  }
}
```

## Additional Resources

- Auth.js v5 docs: https://authjs.dev/
- Next.js Auth guide: https://nextjs.org/docs/app/building-your-application/authentication
- Prisma Adapter: https://authjs.dev/getting-started/adapters/prisma
