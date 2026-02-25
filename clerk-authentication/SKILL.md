---
name: clerk-authentication
description: Clerk authentication covering user management, sign-in/sign-up components, OAuth and passwordless flows, organization multi-tenancy, role-based access control, webhook integration, middleware protection, and Next.js App Router integration with server-side auth.
---

# Clerk Authentication

This skill should be used when implementing authentication with Clerk in web applications. It covers user management, components, RBAC, organizations, webhooks, and Next.js integration.

## When to Use This Skill

Use this skill when you need to:

- Add drop-in authentication UI to Next.js apps
- Implement organization-based multi-tenancy
- Set up role-based access control
- Handle auth webhooks for user sync
- Protect API routes and pages with middleware

## Next.js Setup

```typescript
// app/layout.tsx
import { ClerkProvider } from "@clerk/nextjs";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body>{children}</body>
      </html>
    </ClerkProvider>
  );
}
```

## Middleware Protection

```typescript
// middleware.ts
import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

const isPublicRoute = createRouteMatcher(["/", "/sign-in(.*)", "/sign-up(.*)", "/api/webhooks(.*)"]);

export default clerkMiddleware(async (auth, request) => {
  if (!isPublicRoute(request)) {
    await auth.protect();
  }
});

export const config = {
  matcher: ["/((?!.*\\..*|_next).*)", "/", "/(api|trpc)(.*)"],
};
```

## Sign In / Sign Up Pages

```tsx
// app/sign-in/[[...sign-in]]/page.tsx
import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <SignIn appearance={{ elements: { rootBox: "mx-auto" } }} />
    </div>
  );
}

// app/sign-up/[[...sign-up]]/page.tsx
import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <SignUp />
    </div>
  );
}
```

## Server-Side Auth

```typescript
// app/dashboard/page.tsx
import { auth, currentUser } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";

export default async function DashboardPage() {
  const { userId, orgId } = await auth();
  if (!userId) redirect("/sign-in");

  const user = await currentUser();

  return (
    <div>
      <h1>Welcome, {user?.firstName}</h1>
      {orgId && <p>Organization: {orgId}</p>}
    </div>
  );
}
```

## Client-Side Auth

```tsx
"use client";
import { useUser, useOrganization, SignedIn, SignedOut, UserButton } from "@clerk/nextjs";

export function Header() {
  return (
    <header>
      <SignedIn>
        <UserButton afterSignOutUrl="/" />
      </SignedIn>
      <SignedOut>
        <a href="/sign-in">Sign in</a>
      </SignedOut>
    </header>
  );
}

export function ProfileCard() {
  const { user, isLoaded } = useUser();
  const { organization } = useOrganization();

  if (!isLoaded) return <p>Loading...</p>;

  return (
    <div>
      <p>Name: {user?.fullName}</p>
      <p>Email: {user?.primaryEmailAddress?.emailAddress}</p>
      {organization && <p>Org: {organization.name}</p>}
    </div>
  );
}
```

## API Route Protection

```typescript
// app/api/protected/route.ts
import { auth } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";

export async function GET() {
  const { userId, orgRole } = await auth();

  if (!userId) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  if (orgRole !== "org:admin") {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  return NextResponse.json({ message: "Admin data" });
}
```

## Webhook Handler

```typescript
// app/api/webhooks/clerk/route.ts
import { Webhook } from "svix";
import { headers } from "next/headers";
import { WebhookEvent } from "@clerk/nextjs/server";

export async function POST(req: Request) {
  const headerPayload = await headers();
  const svixId = headerPayload.get("svix-id");
  const svixTimestamp = headerPayload.get("svix-timestamp");
  const svixSignature = headerPayload.get("svix-signature");

  const body = await req.text();
  const wh = new Webhook(process.env.CLERK_WEBHOOK_SECRET!);

  let evt: WebhookEvent;
  try {
    evt = wh.verify(body, {
      "svix-id": svixId!,
      "svix-timestamp": svixTimestamp!,
      "svix-signature": svixSignature!,
    }) as WebhookEvent;
  } catch {
    return new Response("Invalid signature", { status: 400 });
  }

  switch (evt.type) {
    case "user.created":
      await db.users.create({ data: { clerkId: evt.data.id, email: evt.data.email_addresses[0].email_address } });
      break;
    case "user.deleted":
      await db.users.delete({ where: { clerkId: evt.data.id } });
      break;
  }

  return new Response("OK");
}
```

## Additional Resources

- Clerk docs: https://clerk.com/docs
- Next.js quickstart: https://clerk.com/docs/quickstarts/nextjs
- Organizations: https://clerk.com/docs/organizations/overview
