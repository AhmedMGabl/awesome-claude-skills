---
name: state-machines
description: State machine patterns with XState v5 covering finite state machines, statecharts, parallel states, guards, actions, services, context, TypeScript integration, React/Vue bindings, workflow orchestration, and complex UI state management.
---

# State Machines & XState

This skill should be used when managing complex application state, UI workflows, or business process orchestration using state machines. It covers XState v5, statecharts, and state management patterns.

## When to Use This Skill

Use this skill when you need to:

- Manage complex multi-step UI workflows (wizards, checkout flows)
- Model business processes with clear state transitions
- Handle async operations with explicit states (loading, error, success)
- Build reliable form flows with validation states
- Orchestrate parallel or nested processes
- Replace complex boolean flag combinations

## When State Machines Shine

```
USE STATE MACHINES WHEN:
- Component has 3+ distinct states (not just loading/loaded)
- Transitions between states have conditions
- Invalid state combinations are possible with booleans
- Multiple async operations need coordination
- Business logic requires audit trail of state changes

SKIP STATE MACHINES WHEN:
- Simple toggle (on/off)
- Basic CRUD with loading states
- State is just a list of items
```

## Basic Machine (XState v5)

```typescript
import { setup, assign, fromPromise } from "xstate";

// Define the machine with full type safety
const authMachine = setup({
  types: {
    context: {} as {
      user: { id: string; email: string } | null;
      error: string | null;
      attempts: number;
    },
    events: {} as
      | { type: "LOGIN"; email: string; password: string }
      | { type: "LOGOUT" }
      | { type: "RETRY" },
  },
  actors: {
    loginUser: fromPromise(async ({ input }: { input: { email: string; password: string } }) => {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(input),
      });
      if (!res.ok) throw new Error("Invalid credentials");
      return res.json();
    }),
  },
  guards: {
    canRetry: ({ context }) => context.attempts < 3,
  },
}).createMachine({
  id: "auth",
  initial: "idle",
  context: { user: null, error: null, attempts: 0 },
  states: {
    idle: {
      on: { LOGIN: "authenticating" },
    },
    authenticating: {
      invoke: {
        src: "loginUser",
        input: ({ event }) => {
          if (event.type !== "LOGIN") throw new Error("Unexpected event");
          return { email: event.email, password: event.password };
        },
        onDone: {
          target: "authenticated",
          actions: assign({ user: ({ event }) => event.output, error: null }),
        },
        onError: {
          target: "error",
          actions: assign({
            error: ({ event }) => (event.error as Error).message,
            attempts: ({ context }) => context.attempts + 1,
          }),
        },
      },
    },
    authenticated: {
      on: { LOGOUT: { target: "idle", actions: assign({ user: null }) } },
    },
    error: {
      on: {
        RETRY: { target: "idle", guard: "canRetry" },
        LOGIN: "authenticating",
      },
    },
  },
});
```

## React Integration

```typescript
import { useMachine } from "@xstate/react";

function LoginForm() {
  const [state, send] = useMachine(authMachine);

  if (state.matches("authenticated")) {
    return (
      <div>
        <p>Welcome, {state.context.user?.email}</p>
        <button onClick={() => send({ type: "LOGOUT" })}>Logout</button>
      </div>
    );
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
      <input name="email" type="email" required />
      <input name="password" type="password" required />
      <button disabled={state.matches("authenticating")}>
        {state.matches("authenticating") ? "Signing in..." : "Sign in"}
      </button>
      {state.matches("error") && <p className="error">{state.context.error}</p>}
    </form>
  );
}
```

## Multi-Step Wizard

```typescript
const checkoutMachine = setup({
  types: {
    context: {} as {
      shipping: { address: string; city: string; zip: string } | null;
      payment: { method: string; last4: string } | null;
      orderId: string | null;
    },
    events: {} as
      | { type: "NEXT" }
      | { type: "BACK" }
      | { type: "SET_SHIPPING"; data: { address: string; city: string; zip: string } }
      | { type: "SET_PAYMENT"; data: { method: string; last4: string } }
      | { type: "CONFIRM" },
  },
}).createMachine({
  id: "checkout",
  initial: "shipping",
  context: { shipping: null, payment: null, orderId: null },
  states: {
    shipping: {
      on: {
        SET_SHIPPING: { actions: assign({ shipping: ({ event }) => event.data }) },
        NEXT: { target: "payment", guard: ({ context }) => context.shipping !== null },
      },
    },
    payment: {
      on: {
        SET_PAYMENT: { actions: assign({ payment: ({ event }) => event.data }) },
        BACK: "shipping",
        NEXT: { target: "review", guard: ({ context }) => context.payment !== null },
      },
    },
    review: {
      on: {
        BACK: "payment",
        CONFIRM: "processing",
      },
    },
    processing: {
      invoke: {
        src: "submitOrder",
        onDone: {
          target: "complete",
          actions: assign({ orderId: ({ event }) => event.output.id }),
        },
        onError: "review",
      },
    },
    complete: { type: "final" },
  },
});
```

## Parallel States

```typescript
const editorMachine = setup({
  types: {
    context: {} as { document: string; saved: boolean },
    events: {} as
      | { type: "EDIT"; content: string }
      | { type: "SAVE" }
      | { type: "TOGGLE_PREVIEW" }
      | { type: "UNDO" }
      | { type: "REDO" },
  },
}).createMachine({
  id: "editor",
  type: "parallel",
  context: { document: "", saved: true },
  states: {
    editing: {
      initial: "source",
      states: {
        source: { on: { TOGGLE_PREVIEW: "preview" } },
        preview: { on: { TOGGLE_PREVIEW: "source" } },
      },
    },
    saving: {
      initial: "idle",
      states: {
        idle: { on: { SAVE: "saving" } },
        saving: {
          invoke: {
            src: "saveDocument",
            onDone: { target: "idle", actions: assign({ saved: true }) },
            onError: "error",
          },
        },
        error: { on: { SAVE: "saving" } },
      },
    },
    history: {
      initial: "idle",
      states: {
        idle: {
          on: {
            EDIT: { actions: assign({ document: ({ event }) => event.content, saved: false }) },
            UNDO: "undoing",
            REDO: "redoing",
          },
        },
        undoing: { always: "idle" },
        redoing: { always: "idle" },
      },
    },
  },
});
```

## Patterns

```
COMMON STATE MACHINE PATTERNS:

1. Fetch Machine: idle → loading → success/error (→ retry)
2. Form Machine: editing → validating → submitting → success/error
3. Wizard: step1 → step2 → ... → stepN → complete
4. Toggle: on ↔ off (with guards for conditional transitions)
5. Debounce: idle → debouncing → executing → idle
6. Polling: idle → polling → waiting → polling (with stop)
7. Auth: unauthenticated → authenticating → authenticated → idle
```

## Testing

```typescript
import { createActor } from "xstate";

describe("authMachine", () => {
  test("transitions from idle to authenticating on LOGIN", () => {
    const actor = createActor(authMachine);
    actor.start();
    expect(actor.getSnapshot().value).toBe("idle");
    actor.send({ type: "LOGIN", email: "test@test.com", password: "pass" });
    expect(actor.getSnapshot().value).toBe("authenticating");
    actor.stop();
  });

  test("limits retry attempts to 3", () => {
    const actor = createActor(authMachine, {
      snapshot: { ...authMachine.resolveState({ value: "error", context: { user: null, error: "fail", attempts: 3 } }) },
    });
    actor.start();
    actor.send({ type: "RETRY" });
    // Should stay in error state (guard prevents transition)
    expect(actor.getSnapshot().value).toBe("error");
    actor.stop();
  });
});
```

## Additional Resources

- XState v5 Docs: https://stately.ai/docs
- XState Visualizer: https://stately.ai/viz
- XState Catalogue (patterns): https://xstate-catalogue.com/
