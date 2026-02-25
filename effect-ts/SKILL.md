---
name: effect-ts
description: Effect-TS library covering type-safe error handling, dependency injection, concurrency, streaming, scheduling, retry policies, resource management, and functional programming patterns for TypeScript.
---

# Effect-TS

This skill should be used when building robust TypeScript applications with Effect. It covers typed errors, dependency injection, concurrency, and resource management.

## When to Use This Skill

Use this skill when you need to:

- Handle errors with full type safety (no thrown exceptions)
- Implement dependency injection without a framework
- Manage concurrent operations with structured concurrency
- Build reliable retry and timeout policies
- Process streaming data efficiently

## Core Concepts

```typescript
import { Effect, pipe } from "effect";

// Effect<Success, Error, Requirements>
// - Success: the value on success
// - Error: possible error types
// - Requirements: required services/dependencies

// Creating effects
const succeed = Effect.succeed(42);
const fail = Effect.fail(new Error("oops"));
const sync = Effect.sync(() => Date.now());
const promise = Effect.tryPromise(() => fetch("/api/data"));
```

## Error Handling

```typescript
import { Effect, Data } from "effect";

// Typed errors
class UserNotFound extends Data.TaggedError("UserNotFound")<{ userId: string }> {}
class DatabaseError extends Data.TaggedError("DatabaseError")<{ cause: unknown }> {}

const getUser = (id: string): Effect.Effect<User, UserNotFound | DatabaseError> =>
  Effect.tryPromise({
    try: () => db.users.findById(id),
    catch: (cause) => new DatabaseError({ cause }),
  }).pipe(
    Effect.flatMap((user) =>
      user ? Effect.succeed(user) : Effect.fail(new UserNotFound({ userId: id })),
    ),
  );

// Handle specific errors
const program = getUser("123").pipe(
  Effect.catchTag("UserNotFound", (e) =>
    Effect.succeed({ id: e.userId, name: "Guest" }),
  ),
  Effect.catchTag("DatabaseError", () =>
    Effect.fail(new Error("Service unavailable")),
  ),
);

// Run the effect
const result = await Effect.runPromise(program);
```

## Services (Dependency Injection)

```typescript
import { Effect, Context, Layer } from "effect";

// Define service interface
class UserRepository extends Context.Tag("UserRepository")<
  UserRepository,
  {
    findById: (id: string) => Effect.Effect<User | null>;
    save: (user: User) => Effect.Effect<User>;
  }
>() {}

// Use service in effects
const getUser = (id: string) =>
  Effect.gen(function* () {
    const repo = yield* UserRepository;
    const user = yield* repo.findById(id);
    if (!user) yield* Effect.fail(new UserNotFound({ userId: id }));
    return user!;
  });

// Implement service
const UserRepositoryLive = Layer.succeed(UserRepository, {
  findById: (id) => Effect.tryPromise(() => db.users.findById(id)),
  save: (user) => Effect.tryPromise(() => db.users.save(user)),
});

// Provide layer and run
const program = getUser("123").pipe(Effect.provide(UserRepositoryLive));
await Effect.runPromise(program);
```

## Concurrency

```typescript
import { Effect } from "effect";

// Run effects concurrently
const [users, posts, comments] = await Effect.runPromise(
  Effect.all([fetchUsers(), fetchPosts(), fetchComments()], { concurrency: 3 }),
);

// Race — first to complete wins
const fastest = Effect.race(fetchFromPrimary(), fetchFromFallback());

// Timeout
const withTimeout = fetchData().pipe(Effect.timeout("5 seconds"));

// Retry with policy
import { Schedule } from "effect";

const withRetry = fetchData().pipe(
  Effect.retry(
    Schedule.exponential("100 millis").pipe(
      Schedule.compose(Schedule.recurs(3)),
    ),
  ),
);
```

## Generator Syntax

```typescript
import { Effect } from "effect";

const program = Effect.gen(function* () {
  const user = yield* getUser("123");
  const posts = yield* getUserPosts(user.id);
  const enriched = yield* Effect.all(
    posts.map((post) => enrichPost(post)),
    { concurrency: 5 },
  );
  return { user, posts: enriched };
});
```

## Additional Resources

- Effect docs: https://effect.website/docs/introduction
- API reference: https://effect-ts.github.io/effect/
- Effect GitHub: https://github.com/Effect-TS/effect
