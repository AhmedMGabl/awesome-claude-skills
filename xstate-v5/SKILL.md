---
name: xstate-v5
description: XState v5 state machine patterns covering machine definitions, transitions, guards, actions, actors, invoked services, parallel states, history states, TypeScript integration, and React usage with useMachine and useActor hooks.
---

# XState v5

This skill should be used when building state machines and statecharts with XState v5. It covers machine definitions, guards, actions, actors, services, and React integration.

## When to Use This Skill

Use this skill when you need to:

- Model complex UI state with finite state machines
- Manage async workflows with invoked actors
- Handle parallel and nested states
- Build type-safe state machines with TypeScript
- Integrate XState with React components

## Machine Definition

```typescript
import { setup, assign, fromPromise } from "xstate";

interface AuthContext {
  user: { id: string; name: string } | null;
  error: string | null;
  retries: number;
}

type AuthEvent =
  | { type: "LOGIN"; email: string; password: string }
  | { type: "LOGOUT" }
  | { type: "RETRY" };

const authMachine = setup({
  types: {
    context: {} as AuthContext,
    events: {} as AuthEvent,
  },
  guards: {
    canRetry: ({ context }) => context.retries < 3,
  },
  actions: {
    clearError: assign({ error: null }),
    incrementRetries: assign({ retries: ({ context }) => context.retries + 1 }),
    setUser: assign({
      user: (_, params: { user: AuthContext["user"] }) => params.user,
    }),
    setError: assign({
      error: (_, params: { error: string }) => params.error,
    }),
    clearUser: assign({ user: null }),
  },
  actors: {
    loginUser: fromPromise(
      async ({ input }: { input: { email: string; password: string } }) => {
        const res = await fetch("/api/auth/login", {
          method: "POST",
          body: JSON.stringify(input),
          headers: { "Content-Type": "application/json" },
        });
        if (!res.ok) throw new Error("Login failed");
        return res.json();
      },
    ),
  },
}).createMachine({
  id: "auth",
  initial: "idle",
  context: { user: null, error: null, retries: 0 },
  states: {
    idle: {
      on: {
        LOGIN: {
          target: "authenticating",
          actions: ["clearError"],
        },
      },
    },
    authenticating: {
      invoke: {
        src: "loginUser",
        input: ({ event }) => ({
          email: (event as { email: string }).email,
          password: (event as { password: string }).password,
        }),
        onDone: {
          target: "authenticated",
          actions: [{ type: "setUser", params: ({ event }) => ({ user: event.output }) }],
        },
        onError: {
          target: "error",
          actions: [
            { type: "setError", params: ({ event }) => ({ error: String(event.error) }) },
            "incrementRetries",
          ],
        },
      },
    },
    authenticated: {
      on: {
        LOGOUT: {
          target: "idle",
          actions: ["clearUser"],
        },
      },
    },
    error: {
      on: {
        RETRY: {
          target: "idle",
          guard: "canRetry",
        },
        LOGIN: {
          target: "authenticating",
          actions: ["clearError"],
        },
      },
    },
  },
});
```

## Parallel States

```typescript
const editorMachine = setup({
  types: {
    context: {} as { bold: boolean; italic: boolean; fontSize: number },
  },
}).createMachine({
  id: "editor",
  type: "parallel",
  context: { bold: false, italic: false, fontSize: 16 },
  states: {
    formatting: {
      initial: "normal",
      states: {
        normal: {
          on: { TOGGLE_BOLD: "bold" },
        },
        bold: {
          on: { TOGGLE_BOLD: "normal" },
        },
      },
    },
    fontControl: {
      initial: "default",
      states: {
        default: {
          on: {
            INCREASE_FONT: {
              actions: assign({ fontSize: ({ context }) => context.fontSize + 2 }),
            },
            DECREASE_FONT: {
              actions: assign({
                fontSize: ({ context }) => Math.max(8, context.fontSize - 2),
              }),
            },
          },
        },
      },
    },
    saving: {
      initial: "saved",
      states: {
        saved: {
          on: { EDIT: "unsaved" },
        },
        unsaved: {
          on: { SAVE: "saving" },
        },
        saving: {
          invoke: {
            src: "saveDocument",
            onDone: "saved",
            onError: "unsaved",
          },
        },
      },
    },
  },
});
```

## React Integration

```tsx
import { useMachine, useActor } from "@xstate/react";
import { authMachine } from "./machines/auth";

function LoginForm() {
  const [state, send] = useMachine(authMachine);

  if (state.matches("authenticated")) {
    return (
      <div>
        <p>Welcome, {state.context.user?.name}</p>
        <button onClick={() => send({ type: "LOGOUT" })}>Logout</button>
      </div>
    );
  }

  if (state.matches("authenticating")) {
    return <div>Logging in...</div>;
  }

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        const data = new FormData(e.currentTarget);
        send({
          type: "LOGIN",
          email: data.get("email") as string,
          password: data.get("password") as string,
        });
      }}
    >
      {state.matches("error") && <p className="error">{state.context.error}</p>}
      <input name="email" type="email" required />
      <input name="password" type="password" required />
      <button type="submit">Login</button>
      {state.matches("error") && state.can({ type: "RETRY" }) && (
        <button type="button" onClick={() => send({ type: "RETRY" })}>
          Retry ({3 - state.context.retries} left)
        </button>
      )}
    </form>
  );
}
```

## Spawning Child Actors

```typescript
import { setup, assign, sendTo, fromPromise } from "xstate";

const todoMachine = setup({
  types: {
    context: {} as { title: string; completed: boolean },
    events: {} as { type: "TOGGLE" } | { type: "DELETE" },
  },
}).createMachine({
  id: "todo",
  initial: "active",
  context: ({ input }: { input: { title: string } }) => ({
    title: input.title,
    completed: false,
  }),
  states: {
    active: {
      on: {
        TOGGLE: {
          target: "completed",
          actions: assign({ completed: true }),
        },
      },
    },
    completed: {
      on: {
        TOGGLE: {
          target: "active",
          actions: assign({ completed: false }),
        },
      },
    },
  },
});

const todoListMachine = setup({
  types: {
    context: {} as { todos: Array<{ ref: any; id: string }> },
    events: {} as
      | { type: "ADD_TODO"; title: string }
      | { type: "TODO.DELETE"; todoId: string },
  },
  actors: { todoMachine },
}).createMachine({
  id: "todoList",
  context: { todos: [] },
  on: {
    ADD_TODO: {
      actions: assign({
        todos: ({ context, event, spawn }) => [
          ...context.todos,
          {
            id: crypto.randomUUID(),
            ref: spawn("todoMachine", { input: { title: event.title } }),
          },
        ],
      }),
    },
  },
});
```

## Additional Resources

- XState v5 docs: https://stately.ai/docs/xstate-v5
- Stately Studio: https://stately.ai/
- React integration: https://stately.ai/docs/xstate-react
