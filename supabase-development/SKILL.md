---
name: supabase-development
description: Supabase backend-as-a-service covering database queries with PostgREST, authentication with email/OAuth/magic links, row-level security policies, real-time subscriptions, storage bucket management, Edge Functions, and integration with Next.js and React applications.
---

# Supabase Development

This skill should be used when building applications with Supabase. It covers database queries, authentication, RLS, real-time subscriptions, storage, Edge Functions, and framework integration.

## When to Use This Skill

Use this skill when you need to:

- Build full-stack apps with Supabase as the backend
- Implement authentication with multiple providers
- Write row-level security (RLS) policies
- Subscribe to real-time database changes
- Manage file uploads with Supabase Storage

## Client Setup

```typescript
import { createClient } from "@supabase/supabase-js";

const supabase = createClient<Database>(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
);
```

## Database Queries

```typescript
// Select with filters and relations
const { data: users, error } = await supabase
  .from("users")
  .select("id, name, email, posts(id, title)")
  .eq("role", "admin")
  .order("created_at", { ascending: false })
  .limit(20);

// Insert
const { data, error } = await supabase
  .from("posts")
  .insert({ title: "Hello", content: "World", author_id: userId })
  .select()
  .single();

// Update
const { data, error } = await supabase
  .from("posts")
  .update({ title: "Updated Title" })
  .eq("id", postId)
  .select()
  .single();

// Delete
const { error } = await supabase.from("posts").delete().eq("id", postId);

// RPC (stored procedure)
const { data, error } = await supabase.rpc("search_posts", {
  search_query: "typescript",
  result_limit: 10,
});
```

## Authentication

```typescript
// Sign up with email
const { data, error } = await supabase.auth.signUp({
  email: "user@example.com",
  password: "password123",
  options: { data: { full_name: "John Doe" } },
});

// Sign in with OAuth
const { data, error } = await supabase.auth.signInWithOAuth({
  provider: "google",
  options: { redirectTo: `${location.origin}/auth/callback` },
});

// Sign in with magic link
const { data, error } = await supabase.auth.signInWithOtp({
  email: "user@example.com",
});

// Get current user
const { data: { user } } = await supabase.auth.getUser();

// Listen to auth changes
supabase.auth.onAuthStateChange((event, session) => {
  if (event === "SIGNED_IN") console.log("Signed in:", session?.user);
  if (event === "SIGNED_OUT") console.log("Signed out");
});
```

## Row-Level Security

```sql
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- Anyone can read
CREATE POLICY "Posts are viewable by everyone"
  ON posts FOR SELECT USING (true);

-- Only own posts can be inserted
CREATE POLICY "Users can create own posts"
  ON posts FOR INSERT WITH CHECK (auth.uid() = author_id);

-- Only own posts can be updated
CREATE POLICY "Users can update own posts"
  ON posts FOR UPDATE
  USING (auth.uid() = author_id)
  WITH CHECK (auth.uid() = author_id);

-- Only own posts can be deleted
CREATE POLICY "Users can delete own posts"
  ON posts FOR DELETE USING (auth.uid() = author_id);
```

## Real-Time Subscriptions

```typescript
const channel = supabase
  .channel("posts-changes")
  .on(
    "postgres_changes",
    { event: "*", schema: "public", table: "posts" },
    (payload) => {
      console.log("Change:", payload.eventType, payload.new);
    },
  )
  .subscribe();

// Cleanup
supabase.removeChannel(channel);
```

## Storage

```typescript
// Upload file
const { data, error } = await supabase.storage
  .from("avatars")
  .upload(`${userId}/avatar.png`, file, { cacheControl: "3600", upsert: true });

// Get public URL
const { data } = supabase.storage
  .from("avatars")
  .getPublicUrl(`${userId}/avatar.png`);

// Create signed URL (private files)
const { data, error } = await supabase.storage
  .from("documents")
  .createSignedUrl("report.pdf", 3600);
```

## Edge Functions

```typescript
// supabase/functions/send-email/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

serve(async (req) => {
  const { to, subject, body } = await req.json();
  const authHeader = req.headers.get("Authorization");

  const supabase = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_ANON_KEY")!,
    { global: { headers: { Authorization: authHeader! } } },
  );

  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return new Response("Unauthorized", { status: 401 });

  await sendEmail({ to, subject, body });
  return Response.json({ success: true });
});
```

## Additional Resources

- Supabase docs: https://supabase.com/docs
- Client library: https://supabase.com/docs/reference/javascript
- CLI: https://supabase.com/docs/guides/cli
