---
name: supabase-development
description: Supabase backend-as-a-service covering PostgreSQL database, authentication, real-time subscriptions, storage, edge functions, Row Level Security policies, and full-stack TypeScript patterns with React and Next.js.
---

# Supabase Development

This skill should be used when building applications with Supabase as the backend. It covers database setup, authentication, real-time features, storage, edge functions, and Row Level Security patterns.

## When to Use This Skill

Use this skill when you need to:

- Set up Supabase projects with PostgreSQL
- Implement authentication (email, OAuth, magic links)
- Write Row Level Security (RLS) policies
- Build real-time features with subscriptions
- Store and serve files with Supabase Storage
- Create Edge Functions (Deno-based serverless)
- Generate TypeScript types from database schema
- Integrate Supabase with React, Next.js, or mobile apps

## Project Setup

```bash
# Install CLI
npm install -g supabase
supabase init
supabase start  # Local development

# Install client
npm install @supabase/supabase-js

# Generate types from database
supabase gen types typescript --local > src/types/database.ts
```

### Client Setup

```typescript
// lib/supabase.ts
import { createClient } from "@supabase/supabase-js";
import type { Database } from "@/types/database";

export const supabase = createClient<Database>(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

// Server-side client (Next.js App Router)
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

export function createServerSupabase() {
  const cookieStore = cookies();
  return createServerClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() { return cookieStore.getAll(); },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) =>
            cookieStore.set(name, value, options));
        },
      },
    }
  );
}
```

## Database Schema

```sql
-- supabase/migrations/001_initial.sql

-- Enable extensions
create extension if not exists "uuid-ossp";

-- Users profile (extends auth.users)
create table public.profiles (
  id uuid references auth.users(id) on delete cascade primary key,
  username text unique not null,
  display_name text,
  avatar_url text,
  bio text,
  created_at timestamptz default now() not null,
  updated_at timestamptz default now() not null
);

-- Posts
create table public.posts (
  id uuid default uuid_generate_v4() primary key,
  author_id uuid references public.profiles(id) on delete cascade not null,
  title text not null,
  content text,
  slug text unique not null,
  published boolean default false,
  tags text[] default '{}',
  created_at timestamptz default now() not null,
  updated_at timestamptz default now() not null
);

-- Auto-create profile on signup
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, username, display_name, avatar_url)
  values (
    new.id,
    new.raw_user_meta_data->>'username',
    new.raw_user_meta_data->>'display_name',
    new.raw_user_meta_data->>'avatar_url'
  );
  return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();
```

## Row Level Security (RLS)

```sql
-- Enable RLS
alter table public.profiles enable row level security;
alter table public.posts enable row level security;

-- Profiles: anyone can read, owners can update
create policy "Public profiles are viewable by everyone"
  on public.profiles for select using (true);

create policy "Users can update own profile"
  on public.profiles for update
  using (auth.uid() = id)
  with check (auth.uid() = id);

-- Posts: published visible to all, drafts only to author
create policy "Published posts are viewable by everyone"
  on public.posts for select
  using (published = true or auth.uid() = author_id);

create policy "Users can create own posts"
  on public.posts for insert
  with check (auth.uid() = author_id);

create policy "Users can update own posts"
  on public.posts for update
  using (auth.uid() = author_id);

create policy "Users can delete own posts"
  on public.posts for delete
  using (auth.uid() = author_id);
```

## Authentication

```typescript
// Sign up
const { data, error } = await supabase.auth.signUp({
  email: "user@example.com",
  password: "secure-password",
  options: {
    data: { username: "johndoe", display_name: "John Doe" },
  },
});

// Sign in with email
const { data, error } = await supabase.auth.signInWithPassword({
  email: "user@example.com",
  password: "secure-password",
});

// OAuth (Google, GitHub, etc.)
const { data, error } = await supabase.auth.signInWithOAuth({
  provider: "github",
  options: { redirectTo: `${window.location.origin}/auth/callback` },
});

// Magic link
const { error } = await supabase.auth.signInWithOtp({
  email: "user@example.com",
});

// Get current user
const { data: { user } } = await supabase.auth.getUser();

// Sign out
await supabase.auth.signOut();

// Auth state listener
supabase.auth.onAuthStateChange((event, session) => {
  if (event === "SIGNED_IN") console.log("User signed in:", session?.user);
  if (event === "SIGNED_OUT") console.log("User signed out");
});

// React hook
import { useEffect, useState } from "react";
import type { User } from "@supabase/supabase-js";

export function useUser() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => {
      setUser(data.user);
      setLoading(false);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_, session) => setUser(session?.user ?? null)
    );

    return () => subscription.unsubscribe();
  }, []);

  return { user, loading };
}
```

## CRUD Operations

```typescript
// Create
const { data, error } = await supabase.from("posts").insert({
  author_id: user.id,
  title: "My Post",
  slug: "my-post",
  content: "Hello world",
  tags: ["intro", "welcome"],
}).select().single();

// Read with filters
const { data: posts } = await supabase
  .from("posts")
  .select("*, profiles(username, avatar_url)")  // Join profiles
  .eq("published", true)
  .order("created_at", { ascending: false })
  .range(0, 9);  // Pagination: first 10

// Complex filters
const { data } = await supabase
  .from("posts")
  .select("*")
  .or("title.ilike.%search%,content.ilike.%search%")
  .contains("tags", ["typescript"])
  .gte("created_at", "2024-01-01")
  .limit(20);

// Update
const { error } = await supabase
  .from("posts")
  .update({ title: "Updated Title", updated_at: new Date().toISOString() })
  .eq("id", postId);

// Upsert
const { data } = await supabase.from("profiles").upsert({
  id: user.id,
  username: "newusername",
  updated_at: new Date().toISOString(),
}).select().single();

// Delete
const { error } = await supabase.from("posts").delete().eq("id", postId);

// RPC (call database functions)
const { data } = await supabase.rpc("search_posts", {
  search_query: "typescript",
  result_limit: 10,
});
```

## Real-time Subscriptions

```typescript
// Subscribe to changes
const channel = supabase
  .channel("posts-changes")
  .on(
    "postgres_changes",
    {
      event: "*",         // INSERT, UPDATE, DELETE, or *
      schema: "public",
      table: "posts",
      filter: "published=eq.true",
    },
    (payload) => {
      console.log("Change:", payload.eventType, payload.new);
      if (payload.eventType === "INSERT") addPost(payload.new);
      if (payload.eventType === "UPDATE") updatePost(payload.new);
      if (payload.eventType === "DELETE") removePost(payload.old);
    }
  )
  .subscribe();

// Presence (who's online)
const presenceChannel = supabase.channel("room-1");
presenceChannel
  .on("presence", { event: "sync" }, () => {
    const state = presenceChannel.presenceState();
    console.log("Online users:", state);
  })
  .subscribe(async (status) => {
    if (status === "SUBSCRIBED") {
      await presenceChannel.track({ user_id: user.id, username: user.name });
    }
  });

// Cleanup
supabase.removeChannel(channel);
```

## Storage

```typescript
// Upload file
const { data, error } = await supabase.storage
  .from("avatars")
  .upload(`${user.id}/avatar.png`, file, {
    cacheControl: "3600",
    upsert: true,
    contentType: "image/png",
  });

// Get public URL
const { data: { publicUrl } } = supabase.storage
  .from("avatars")
  .getPublicUrl(`${user.id}/avatar.png`);

// Download
const { data, error } = await supabase.storage
  .from("documents")
  .download("reports/2024-q1.pdf");

// List files
const { data: files } = await supabase.storage
  .from("avatars")
  .list(user.id, { limit: 10, sortBy: { column: "created_at", order: "desc" } });

// Delete
const { error } = await supabase.storage
  .from("avatars")
  .remove([`${user.id}/old-avatar.png`]);
```

## Edge Functions

```typescript
// supabase/functions/send-email/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

serve(async (req) => {
  const { to, subject, body } = await req.json();

  // Create admin client (bypasses RLS)
  const supabase = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
  );

  // Send email via Resend
  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${Deno.env.get("RESEND_API_KEY")}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ from: "app@example.com", to, subject, html: body }),
  });

  const result = await res.json();
  return new Response(JSON.stringify(result), {
    headers: { "Content-Type": "application/json" },
  });
});

// Call from client
const { data, error } = await supabase.functions.invoke("send-email", {
  body: { to: "user@example.com", subject: "Welcome", body: "<h1>Hello!</h1>" },
});
```

## Additional Resources

- Supabase docs: https://supabase.com/docs
- Supabase JS client: https://supabase.com/docs/reference/javascript
- Row Level Security: https://supabase.com/docs/guides/auth/row-level-security
- Edge Functions: https://supabase.com/docs/guides/functions
- Local development: https://supabase.com/docs/guides/cli
