---
name: state-machines
description: State machine implementation covering XState v5 for complex UI flows, finite state machines for form wizards and checkout flows, statecharts with guards and actions, parallel and hierarchical states, actor model, and integration with React and Vue.
---

# State Machines

This skill should be used when implementing state machines for complex application logic. It covers XState v5, statecharts, guards, actions, actors, and framework integration.

## When to Use This Skill

Use this skill when you need to:

- Model complex UI flows (wizards, checkout, onboarding)
- Implement statecharts with guards and side effects
- Manage parallel and hierarchical states
- Use the actor model for distributed logic
- Integrate state machines with React or Vue

## XState v5 Checkout Machine

```typescript
import { setup, assign, fromPromise } from "xstate";

const orderMachine = setup({
  types: {
    context: {} as {
      items: Array<{ id: string; price: number }>;
      shippingAddress: string | null;
      orderId: string | null;
      error: string | null;
    },
    events: {} as
      | { type: "ADD_ITEM"; item: { id: string; price: number } }
      | { type: "SET_SHIPPING"; address: string }
      | { type: "SUBMIT" }
      | { type: "BACK" }
      | { type: "RETRY" },
  },
  guards: {
    hasItems: ({ context }) => context.items.length > 0,
    hasShipping: ({ context }) => context.shippingAddress !== null,
  },
  actors: {
    submitOrder: fromPromise(async ({ input }: { input: any }) => {
      const res = await fetch("/api/orders", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(input),
      });
      if (!res.ok) throw new Error("Order failed");
      return res.json();
    }),
  },
}).createMachine({
  id: "order",
  initial: "cart",
  context: { items: [], shippingAddress: null, orderId: null, error: null },
  states: {
    cart: {
      on: {
        ADD_ITEM: {
          actions: assign({
            items: ({ context, event }) => [...context.items, event.item],
          }),
        },
        SUBMIT: { target: "shipping", guard: "hasItems" },
      },
    },
    shipping: {
      on: {
        SET_SHIPPING: {
          actions: assign({ shippingAddress: ({ event }) => event.address }),
        },
        SUBMIT: { target: "confirming", guard: "hasShipping" },
        BACK: "cart",
      },
    },
    confirming: {
      invoke: {
        src: "submitOrder",
        input: ({ context }) => context,
        onDone: {
          target: "confirmed",
          actions: assign({ orderId: ({ event }) => event.output.id }),
        },
        onError: {
          target: "error",
          actions: assign({ error: ({ event }) => (event.error as Error).message }),
        },
      },
    },
    confirmed: { type: "final" },
    error: {
      on: { RETRY: "confirming", BACK: "shipping" },
    },
  },
});
```

## React Integration

```tsx
import { useMachine } from "@xstate/react";

function CheckoutFlow() {
  const [state, send] = useMachine(orderMachine);

  return (
    <div>
      {state.matches("cart") && (
        <CartStep
          items={state.context.items}
          onAddItem={(item) => send({ type: "ADD_ITEM", item })}
          onNext={() => send({ type: "SUBMIT" })}
        />
      )}
      {state.matches("shipping") && (
        <ShippingStep
          onSetAddress={(addr) => send({ type: "SET_SHIPPING", address: addr })}
          onNext={() => send({ type: "SUBMIT" })}
          onBack={() => send({ type: "BACK" })}
        />
      )}
      {state.matches("confirming") && <LoadingSpinner />}
      {state.matches("confirmed") && <Confirmation orderId={state.context.orderId!} />}
      {state.matches("error") && (
        <ErrorDisplay message={state.context.error!} onRetry={() => send({ type: "RETRY" })} />
      )}
    </div>
  );
}
```

## When to Use State Machines

```
USE CASE                  WITHOUT SM              WITH SM
────────────────────────────────────────────────────────────────
Multi-step forms          Boolean spaghetti       Clear states
Auth flows                Nested if/else          Guard-protected
Data fetching             isLoading/isError        Loading/Error states
Game logic                Giant switch             Hierarchical states
```

## Additional Resources

- XState v5 docs: https://stately.ai/docs/xstate-v5
- XState visualizer: https://stately.ai/viz
- Statecharts: https://statecharts.dev/
