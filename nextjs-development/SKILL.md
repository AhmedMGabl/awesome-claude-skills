---
name: nextjs-development
description: Next.js development covering App Router, Server Components, Client Components, SSR/SSG/ISR, API routes, middleware, authentication, performance optimization, and production deployment patterns.
---

# Next.js Development

This skill should be used when building Next.js applications. It covers the App Router architecture, Server and Client Components, data fetching strategies, API routes, authentication, and deployment best practices for production applications.

## When to Use This Skill

Use this skill when you need to:

- Set up Next.js projects with App Router
- Understand Server vs Client Components
- Implement SSR, SSG, ISR, and streaming
- Create API routes and Route Handlers
- Implement authentication with NextAuth.js or custom solutions
- Optimize performance with caching, lazy loading, and image optimization
- Deploy Next.js applications to Vercel, Docker, or self-hosted environments

## Project Setup

```bash
# Create new Next.js app
npx create-next-app@latest my-app \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --src-dir \
  --import-alias "@/*"

# Project structure
my-app/
├── src/
│   ├── app/
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Home page
│   │   ├── globals.css
│   │   ├── (auth)/             # Route group (no URL segment)
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   ├── dashboard/
│   │   │   ├── layout.tsx      # Nested layout
│   │   │   ├── page.tsx
│   │   │   └── [id]/page.tsx   # Dynamic route
│   │   └── api/
│   │       └── users/route.ts  # Route Handler
│   ├── components/
│   │   ├── ui/                 # Reusable UI components
│   │   └── features/           # Feature-specific components
│   ├── lib/
│   │   ├── db.ts               # Database client
│   │   └── auth.ts             # Auth config
│   └── types/
│       └── index.ts
├── public/
├── next.config.ts
└── middleware.ts
```

### next.config.ts

```typescript
import type { NextConfig } from "next";

const config: NextConfig = {
  // Enable React strict mode
  reactStrictMode: true,

  // Image optimization
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "cdn.example.com",
        pathname: "/images/**",
      },
    ],
  },

  // Environment variables (exposed to browser)
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },

  // Redirect and rewrite rules
  async redirects() {
    return [
      {
        source: "/old-path",
        destination: "/new-path",
        permanent: true,
      },
    ];
  },

  // Headers for security
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        ],
      },
    ];
  },
};

export default config;
```

## App Router Architecture

### Root Layout

```typescript
// src/app/layout.tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: {
    template: "%s | My App",
    default: "My App",
  },
  description: "My application description",
  openGraph: {
    type: "website",
    siteName: "My App",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <main>{children}</main>
      </body>
    </html>
  );
}
```

### Server Components (default in App Router)

```typescript
// src/app/users/page.tsx - Server Component (no "use client")
import { Suspense } from "react";
import { UserList } from "@/components/features/UserList";
import { UserListSkeleton } from "@/components/ui/skeletons";

// Server-side metadata
export const metadata = {
  title: "Users",
};

// Fetch data directly in Server Component
async function getUsers() {
  // This runs on the server - can use env vars, DB, etc.
  const res = await fetch("https://api.example.com/users", {
    next: { revalidate: 60 }, // ISR: revalidate every 60s
  });
  if (!res.ok) throw new Error("Failed to fetch users");
  return res.json();
}

export default async function UsersPage() {
  return (
    <div>
      <h1>Users</h1>
      <Suspense fallback={<UserListSkeleton />}>
        <UserListContent />
      </Suspense>
    </div>
  );
}

// Async component with Suspense boundary
async function UserListContent() {
  const users = await getUsers();
  return <UserList users={users} />;
}
```

### Client Components

```typescript
// src/components/features/UserSearch.tsx
"use client"; // Required for client-side interactivity

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";

export function UserSearch() {
  const [query, setQuery] = useState("");
  const [isPending, startTransition] = useTransition();
  const router = useRouter();

  function handleSearch(value: string) {
    setQuery(value);
    startTransition(() => {
      router.push(`/users?q=${value}`);
    });
  }

  return (
    <div>
      <input
        value={query}
        onChange={(e) => handleSearch(e.target.value)}
        placeholder="Search users..."
        className={isPending ? "opacity-50" : ""}
      />
      {isPending && <span>Searching...</span>}
    </div>
  );
}
```

### Composing Server and Client Components

```typescript
// Server Component that passes data to Client Component
// src/app/dashboard/page.tsx
import { DashboardChart } from "@/components/features/DashboardChart";
import { getMetrics } from "@/lib/metrics";

export default async function DashboardPage() {
  // Server-side data fetching
  const metrics = await getMetrics();

  // Pass serializable data to Client Component
  return (
    <div>
      <h1>Dashboard</h1>
      <DashboardChart data={metrics} />
    </div>
  );
}

// Client Component receives data as props
// src/components/features/DashboardChart.tsx
"use client";
import { LineChart, Line, XAxis, YAxis, Tooltip } from "recharts";

interface Props {
  data: Array<{ date: string; value: number }>;
}

export function DashboardChart({ data }: Props) {
  return (
    <LineChart width={600} height={300} data={data}>
      <XAxis dataKey="date" />
      <YAxis />
      <Tooltip />
      <Line type="monotone" dataKey="value" stroke="#8884d8" />
    </LineChart>
  );
}
```

## Data Fetching

### Static Generation (SSG)

```typescript
// src/app/blog/[slug]/page.tsx
import { notFound } from "next/navigation";
import { marked } from "marked"; // Use a safe renderer, not raw HTML

interface Props {
  params: { slug: string };
}

// Generate static paths at build time
export async function generateStaticParams() {
  const posts = await fetch("https://api.example.com/posts").then(r => r.json());
  return posts.map((post: { slug: string }) => ({ slug: post.slug }));
}

// Generate metadata per page
export async function generateMetadata({ params }: Props) {
  const post = await getPost(params.slug);
  if (!post) return {};
  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      images: [{ url: post.coverImage }],
    },
  };
}

async function getPost(slug: string) {
  const res = await fetch(`https://api.example.com/posts/${slug}`, {
    next: { tags: [`post-${slug}`] }, // For on-demand revalidation
  });
  if (!res.ok) return null;
  return res.json();
}

export default async function BlogPost({ params }: Props) {
  const post = await getPost(params.slug);
  if (!post) notFound();

  // Always sanitize HTML from external sources (e.g. DOMPurify server-side, or use a safe markdown renderer)
  const safeHtml = marked.parse(post.markdownContent); // render markdown safely

  return (
    <article>
      <h1>{post.title}</h1>
      {/* Only use dangerouslySetInnerHTML with trusted/sanitized content */}
      <div dangerouslySetInnerHTML={{ __html: safeHtml }} />
    </article>
  );
}
```

### Parallel Data Fetching

```typescript
// src/app/profile/[id]/page.tsx
export default async function ProfilePage({ params }: { params: { id: string } }) {
  // Fetch in parallel - don't await sequentially!
  const [user, posts, followers] = await Promise.all([
    getUser(params.id),
    getUserPosts(params.id),
    getUserFollowers(params.id),
  ]);

  return (
    <div>
      <UserProfile user={user} />
      <UserPosts posts={posts} />
      <FollowersList followers={followers} />
    </div>
  );
}
```

### Streaming with Suspense

```typescript
// src/app/dashboard/page.tsx
import { Suspense } from "react";

export default function DashboardPage() {
  return (
    <div>
      {/* Fast-loading content shown immediately */}
      <DashboardHeader />

      {/* Each section streams independently */}
      <Suspense fallback={<MetricsSkeleton />}>
        <MetricsPanel />
      </Suspense>

      <Suspense fallback={<ChartSkeleton />}>
        <SalesChart />
      </Suspense>

      <Suspense fallback={<TableSkeleton />}>
        <RecentOrders />
      </Suspense>
    </div>
  );
}
```

## Route Handlers (API Routes)

```typescript
// src/app/api/users/route.ts
import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";

const CreateUserSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
});

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const page = Number(searchParams.get("page") ?? "1");
  const limit = Number(searchParams.get("limit") ?? "10");

  const users = await db.users.findMany({
    skip: (page - 1) * limit,
    take: limit,
  });

  return NextResponse.json({ users, page, limit });
}

export async function POST(request: NextRequest) {
  const body = await request.json();

  const result = CreateUserSchema.safeParse(body);
  if (!result.success) {
    return NextResponse.json(
      { error: "Invalid input", details: result.error.flatten() },
      { status: 400 }
    );
  }

  const user = await db.users.create({ data: result.data });
  return NextResponse.json(user, { status: 201 });
}

// src/app/api/users/[id]/route.ts
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const user = await db.users.findUnique({ where: { id: Number(params.id) } });
  if (!user) {
    return NextResponse.json({ error: "User not found" }, { status: 404 });
  }
  return NextResponse.json(user);
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  await db.users.delete({ where: { id: Number(params.id) } });
  return new NextResponse(null, { status: 204 });
}
```

## Middleware

```typescript
// src/middleware.ts (runs on Edge runtime)
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Auth check for protected routes
  const token = request.cookies.get("session")?.value;
  const isProtected = pathname.startsWith("/dashboard") ||
                      pathname.startsWith("/admin");

  if (isProtected && !token) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    url.searchParams.set("callbackUrl", pathname);
    return NextResponse.redirect(url);
  }

  // Add security headers
  const response = NextResponse.next();
  response.headers.set("X-Request-Id", crypto.randomUUID());

  return response;
}

// Configure which paths middleware runs on
export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|public).*)",
  ],
};
```

## Authentication with NextAuth.js

```typescript
// src/lib/auth.ts
import NextAuth from "next-auth";
import GitHub from "next-auth/providers/github";
import Credentials from "next-auth/providers/credentials";
import { PrismaAdapter } from "@auth/prisma-adapter";
import { prisma } from "@/lib/db";
import bcrypt from "bcryptjs";

export const { handlers, auth, signIn, signOut } = NextAuth({
  adapter: PrismaAdapter(prisma),
  providers: [
    GitHub({
      clientId: process.env.GITHUB_ID,
      clientSecret: process.env.GITHUB_SECRET,
    }),
    Credentials({
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) return null;

        const user = await prisma.user.findUnique({
          where: { email: credentials.email as string },
        });

        if (!user?.password) return null;

        const isValid = await bcrypt.compare(
          credentials.password as string,
          user.password
        );

        return isValid ? user : null;
      },
    }),
  ],
  callbacks: {
    jwt({ token, user }) {
      if (user) token.role = user.role;
      return token;
    },
    session({ session, token }) {
      session.user.role = token.role as string;
      return session;
    },
  },
  pages: {
    signIn: "/login",
    error: "/auth/error",
  },
});

// src/app/api/auth/[...nextauth]/route.ts
export { handlers as GET, handlers as POST } from "@/lib/auth";

// Use in Server Components
import { auth } from "@/lib/auth";

export default async function ProtectedPage() {
  const session = await auth();
  if (!session) redirect("/login");

  return <div>Welcome, {session.user.name}</div>;
}
```

## Server Actions

```typescript
// src/app/actions/user.ts
"use server";
import { revalidatePath, revalidateTag } from "next/cache";
import { redirect } from "next/navigation";
import { auth } from "@/lib/auth";
import { z } from "zod";

const UpdateProfileSchema = z.object({
  name: z.string().min(1).max(100),
  bio: z.string().max(500).optional(),
});

export async function updateProfile(formData: FormData) {
  const session = await auth();
  if (!session) throw new Error("Unauthorized");

  const data = {
    name: formData.get("name"),
    bio: formData.get("bio"),
  };

  const result = UpdateProfileSchema.safeParse(data);
  if (!result.success) {
    return { error: result.error.flatten().fieldErrors };
  }

  await db.users.update({
    where: { id: session.user.id },
    data: result.data,
  });

  revalidatePath("/profile");
  revalidateTag(`user-${session.user.id}`);
  redirect("/profile");
}

// Use in Client Component
"use client";
import { updateProfile } from "@/app/actions/user";
import { useFormStatus } from "react-dom";

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <button type="submit" disabled={pending}>
      {pending ? "Saving..." : "Save Profile"}
    </button>
  );
}

export function ProfileForm() {
  return (
    <form action={updateProfile}>
      <input name="name" placeholder="Name" />
      <textarea name="bio" placeholder="Bio" />
      <SubmitButton />
    </form>
  );
}
```

## Performance Optimization

### Image Optimization

```typescript
import Image from "next/image";

// Responsive image
<Image
  src="/hero.jpg"
  alt="Hero image"
  width={1200}
  height={600}
  priority  // LCP image - skip lazy loading
  sizes="(max-width: 768px) 100vw, 50vw"
/>

// Fill container
<div className="relative h-64 w-full">
  <Image
    src={user.avatar}
    alt={user.name}
    fill
    className="object-cover"
    sizes="(max-width: 640px) 100vw, 300px"
  />
</div>
```

### Dynamic Imports

```typescript
import dynamic from "next/dynamic";

// Lazy load heavy Client Components
const HeavyChart = dynamic(() => import("@/components/HeavyChart"), {
  loading: () => <div>Loading chart...</div>,
  ssr: false,  // Skip server rendering (for browser-only libs)
});
```

### Caching Strategies

```typescript
// Static (no revalidation)
fetch(url, { cache: "force-cache" });

// ISR (revalidate every N seconds)
fetch(url, { next: { revalidate: 3600 } });

// Dynamic (always fresh)
fetch(url, { cache: "no-store" });

// On-demand revalidation via tag
fetch(url, { next: { tags: ["users", `user-${id}`] } });

// Trigger revalidation in Server Action
import { revalidateTag } from "next/cache";
await revalidateTag("users");

// Route segment config
export const dynamic = "force-static";       // Always static
export const dynamic = "force-dynamic";      // Always dynamic
export const revalidate = 60;                // ISR
export const fetchCache = "force-no-store";  // Never cache fetches
```

## Error Handling

```typescript
// src/app/error.tsx - Error boundary (Client Component)
"use client";
import { useEffect } from "react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={() => reset()}>Try again</button>
    </div>
  );
}

// src/app/not-found.tsx
export default function NotFound() {
  return (
    <div>
      <h2>Page Not Found</h2>
      <p>The page you requested does not exist.</p>
    </div>
  );
}

// Trigger not-found
import { notFound } from "next/navigation";

export default async function UserPage({ params }: { params: { id: string } }) {
  const user = await getUser(params.id);
  if (!user) notFound();
  return <UserProfile user={user} />;
}
```

## Deployment

```dockerfile
# Dockerfile for standalone output
FROM node:20-alpine AS base

FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT=3000
CMD ["node", "server.js"]
```

```javascript
// next.config.js - Enable standalone output
module.exports = {
  output: "standalone",
};
```

## Additional Resources

- Next.js Docs: https://nextjs.org/docs
- App Router: https://nextjs.org/docs/app
- NextAuth.js: https://next-auth.js.org/
- Server Actions: https://nextjs.org/docs/app/api-reference/functions/server-actions
- Vercel Deployment: https://vercel.com/docs/frameworks/nextjs
