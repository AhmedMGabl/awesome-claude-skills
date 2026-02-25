---
name: lucia-auth
description: Lucia authentication library covering session management, database adapters for Prisma and Drizzle, OAuth integration with Arctic, password hashing with Argon2, email verification, password reset flows, session cookies, and CSRF protection.
---

# Lucia Authentication

This skill should be used when implementing authentication with Lucia. It covers session management, OAuth, password auth, email verification, and security patterns.

## When to Use This Skill

Use this skill when you need to:

- Implement session-based authentication
- Build email/password registration and login
- Add OAuth login with GitHub, Google, etc.
- Handle email verification and password reset
- Manage sessions with database storage

## Session Setup

```typescript
// lib/auth.ts
import { Lucia } from "lucia";
import { PrismaAdapter } from "@lucia-auth/adapter-prisma";
import { prisma } from "./prisma";

const adapter = new PrismaAdapter(prisma.session, prisma.user);

export const lucia = new Lucia(adapter, {
  sessionCookie: {
    attributes: {
      secure: process.env.NODE_ENV === "production",
    },
  },
  getUserAttributes: (attributes) => ({
    email: attributes.email,
    name: attributes.name,
    emailVerified: attributes.emailVerified,
  }),
});

declare module "lucia" {
  interface Register {
    Lucia: typeof lucia;
    DatabaseUserAttributes: {
      email: string;
      name: string;
      emailVerified: boolean;
    };
  }
}
```

## Prisma Schema

```prisma
model User {
  id            String    @id @default(cuid())
  email         String    @unique
  name          String
  passwordHash  String?
  emailVerified Boolean   @default(false)
  sessions      Session[]
  oauthAccounts OAuthAccount[]
}

model Session {
  id        String   @id
  userId    String
  expiresAt DateTime
  user      User     @relation(fields: [userId], references: [id], onDelete: Cascade)
}

model OAuthAccount {
  providerId     String
  providerUserId String
  userId         String
  user           User   @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@id([providerId, providerUserId])
}
```

## Email/Password Registration

```typescript
import { hash } from "@node-rs/argon2";
import { generateId } from "lucia";

async function register(email: string, password: string, name: string) {
  const passwordHash = await hash(password, {
    memoryCost: 19456,
    timeCost: 2,
    outputLen: 32,
    parallelism: 1,
  });

  const user = await prisma.user.create({
    data: {
      id: generateId(15),
      email: email.toLowerCase(),
      name,
      passwordHash,
    },
  });

  const session = await lucia.createSession(user.id, {});
  const sessionCookie = lucia.createSessionCookie(session.id);

  return { user, sessionCookie };
}
```

## Login

```typescript
import { verify } from "@node-rs/argon2";

async function login(email: string, password: string) {
  const user = await prisma.user.findUnique({
    where: { email: email.toLowerCase() },
  });

  if (!user?.passwordHash) {
    throw new Error("Invalid credentials");
  }

  const valid = await verify(user.passwordHash, password);
  if (!valid) throw new Error("Invalid credentials");

  const session = await lucia.createSession(user.id, {});
  return lucia.createSessionCookie(session.id);
}
```

## Session Validation Middleware

```typescript
// Next.js middleware approach
import { cookies } from "next/headers";

async function getSession() {
  const cookieStore = await cookies();
  const sessionId = cookieStore.get(lucia.sessionCookieName)?.value ?? null;
  if (!sessionId) return { user: null, session: null };

  const result = await lucia.validateSession(sessionId);

  if (result.session?.fresh) {
    const cookie = lucia.createSessionCookie(result.session.id);
    cookieStore.set(cookie.name, cookie.value, cookie.attributes);
  }
  if (!result.session) {
    const cookie = lucia.createBlankSessionCookie();
    cookieStore.set(cookie.name, cookie.value, cookie.attributes);
  }

  return result;
}
```

## OAuth with Arctic (GitHub)

```typescript
import { GitHub } from "arctic";

const github = new GitHub(
  process.env.GITHUB_CLIENT_ID!,
  process.env.GITHUB_CLIENT_SECRET!,
);

// Step 1: Generate authorization URL
async function getGitHubAuthUrl() {
  const state = generateState();
  const url = github.createAuthorizationURL(state, ["user:email"]);
  return { url, state };
}

// Step 2: Handle callback
async function handleGitHubCallback(code: string) {
  const tokens = await github.validateAuthorizationCode(code);
  const githubUser = await fetch("https://api.github.com/user", {
    headers: { Authorization: `Bearer ${tokens.accessToken()}` },
  }).then((r) => r.json());

  // Find or create user
  const existing = await prisma.oAuthAccount.findUnique({
    where: { providerId_providerUserId: { providerId: "github", providerUserId: String(githubUser.id) } },
  });

  let userId: string;
  if (existing) {
    userId = existing.userId;
  } else {
    const user = await prisma.user.create({
      data: {
        id: generateId(15),
        email: githubUser.email,
        name: githubUser.name,
        emailVerified: true,
        oauthAccounts: {
          create: { providerId: "github", providerUserId: String(githubUser.id) },
        },
      },
    });
    userId = user.id;
  }

  const session = await lucia.createSession(userId, {});
  return lucia.createSessionCookie(session.id);
}
```

## Logout

```typescript
async function logout() {
  const { session } = await getSession();
  if (session) {
    await lucia.invalidateSession(session.id);
  }
  const cookie = lucia.createBlankSessionCookie();
  // Set blank cookie to clear session
  return cookie;
}
```

## Additional Resources

- Lucia docs: https://lucia-auth.com/
- Arctic (OAuth): https://arcticjs.dev/
- Database adapters: https://lucia-auth.com/database/
