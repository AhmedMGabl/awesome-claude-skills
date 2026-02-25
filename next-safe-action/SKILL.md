---
name: next-safe-action
description: next-safe-action patterns covering type-safe server actions, Zod input validation, middleware chains, optimistic updates, action state management, error handling, and React hook integration for Next.js App Router.
---

# next-safe-action

This skill should be used when building type-safe server actions in Next.js with next-safe-action. It covers action definitions, validation, middleware, and React hook integration.

## When to Use This Skill

Use this skill when you need to:

- Define type-safe server actions with input validation
- Chain middleware for auth, rate limiting, and logging
- Handle optimistic updates with server actions
- Manage action state (loading, error, success) in React
- Build reusable action patterns in Next.js

## Setup and Basic Action

```typescript
// lib/safe-action.ts
import { createSafeActionClient } from "next-safe-action";

export const actionClient = createSafeActionClient({
  handleServerError: (e) => {
    console.error("Action error:", e.message);
    return "Something went wrong";
  },
});

// actions/create-post.ts
"use server";
import { z } from "zod";
import { actionClient } from "@/lib/safe-action";

const createPostSchema = z.object({
  title: z.string().min(1).max(200),
  content: z.string().min(10),
  published: z.boolean().default(false),
});

export const createPost = actionClient
  .schema(createPostSchema)
  .action(async ({ parsedInput }) => {
    const post = await db.post.create({ data: parsedInput });
    revalidatePath("/posts");
    return { post };
  });
```

## Middleware Chains

```typescript
// lib/safe-action.ts
import { createSafeActionClient } from "next-safe-action";
import { auth } from "@/lib/auth";

export const actionClient = createSafeActionClient();

export const authAction = actionClient.use(async ({ next }) => {
  const session = await auth();
  if (!session?.user) {
    throw new Error("Unauthorized");
  }
  return next({ ctx: { user: session.user } });
});

export const adminAction = authAction.use(async ({ next, ctx }) => {
  if (ctx.user.role !== "admin") {
    throw new Error("Forbidden");
  }
  return next({ ctx });
});

// Usage
export const deleteUser = adminAction
  .schema(z.object({ userId: z.string().uuid() }))
  .action(async ({ parsedInput, ctx }) => {
    await db.user.delete({ where: { id: parsedInput.userId } });
    return { success: true, deletedBy: ctx.user.id };
  });
```

## React Hook Integration

```tsx
"use client";
import { useAction } from "next-safe-action/hooks";
import { createPost } from "@/actions/create-post";

function CreatePostForm() {
  const { execute, result, status, isExecuting } = useAction(createPost, {
    onSuccess: ({ data }) => {
      toast.success("Post created!");
      router.push(`/posts/${data?.post.id}`);
    },
    onError: ({ error }) => {
      toast.error(error.serverError ?? "Failed to create post");
    },
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        const formData = new FormData(e.currentTarget);
        execute({
          title: formData.get("title") as string,
          content: formData.get("content") as string,
          published: formData.get("published") === "on",
        });
      }}
    >
      <input name="title" required />
      {result.validationErrors?.title && (
        <p className="error">{result.validationErrors.title._errors[0]}</p>
      )}
      <textarea name="content" required />
      <label>
        <input name="published" type="checkbox" /> Publish
      </label>
      <button type="submit" disabled={isExecuting}>
        {isExecuting ? "Creating..." : "Create Post"}
      </button>
    </form>
  );
}
```

## Optimistic Updates

```tsx
"use client";
import { useOptimisticAction } from "next-safe-action/hooks";
import { toggleTodo } from "@/actions/toggle-todo";

function TodoItem({ todo }: { todo: Todo }) {
  const { execute, optimisticState } = useOptimisticAction(toggleTodo, {
    currentState: todo,
    updateFn: (state, input) => ({
      ...state,
      completed: !state.completed,
    }),
  });

  return (
    <div>
      <input
        type="checkbox"
        checked={optimisticState.completed}
        onChange={() => execute({ id: todo.id })}
      />
      <span>{todo.title}</span>
    </div>
  );
}
```

## Bind Args Pattern

```typescript
// actions/update-post.ts
"use server";
import { z } from "zod";
import { authAction } from "@/lib/safe-action";

export const updatePost = authAction
  .bindArgsSchemas([z.string().uuid()]) // postId bound from server
  .schema(z.object({ title: z.string(), content: z.string() }))
  .action(async ({ parsedInput, bindArgsParsedInputs: [postId], ctx }) => {
    const post = await db.post.update({
      where: { id: postId, authorId: ctx.user.id },
      data: parsedInput,
    });
    return { post };
  });

// Usage - bind the postId
const updateThisPost = updatePost.bind(null, post.id);
```

## Additional Resources

- next-safe-action docs: https://next-safe-action.dev/
- GitHub: https://github.com/TheEdoRan/next-safe-action
