---
name: angular-signals
description: Angular Signals patterns covering signal(), computed(), effect(), input signals, model signals, output(), resource API, RxJS interop with toSignal/toObservable, and migration from zone-based change detection.
---

# Angular Signals

This skill should be used when building reactive Angular applications with Signals. It covers signal primitives, computed values, effects, input/output signals, and RxJS interop.

## When to Use This Skill

Use this skill when you need to:

- Use Angular's reactive signal primitives
- Create computed values and side effects
- Define component inputs and outputs with signals
- Interop between Signals and RxJS Observables
- Migrate from zone-based change detection

## Basic Signals

```typescript
import { Component, signal, computed, effect } from "@angular/core";

@Component({
  selector: "app-counter",
  template: `
    <div>
      <p>Count: {{ count() }}</p>
      <p>Doubled: {{ doubled() }}</p>
      <button (click)="increment()">+</button>
      <button (click)="decrement()">-</button>
      <button (click)="reset()">Reset</button>
    </div>
  `,
})
export class CounterComponent {
  count = signal(0);
  doubled = computed(() => this.count() * 2);

  constructor() {
    // Effect runs when dependencies change
    effect(() => {
      console.log(`Count changed to: ${this.count()}`);
    });
  }

  increment() {
    this.count.update((c) => c + 1);
  }

  decrement() {
    this.count.update((c) => c - 1);
  }

  reset() {
    this.count.set(0);
  }
}
```

## Signal Inputs and Outputs

```typescript
import { Component, input, output, model, computed } from "@angular/core";

@Component({
  selector: "app-user-card",
  template: `
    <div class="card">
      <h3>{{ name() }}</h3>
      <p>{{ email() }}</p>
      <span class="badge">{{ displayRole() }}</span>
      <input [value]="searchQuery()" (input)="searchQuery.set($event.target.value)" />
      <button (click)="onEdit.emit(id())">Edit</button>
      <button (click)="onDelete.emit(id())">Delete</button>
    </div>
  `,
})
export class UserCardComponent {
  // Required input
  id = input.required<string>();
  name = input.required<string>();
  email = input.required<string>();

  // Optional input with default
  role = input<string>("user");

  // Two-way binding with model
  searchQuery = model<string>("");

  // Outputs
  onEdit = output<string>();
  onDelete = output<string>();

  // Computed from inputs
  displayRole = computed(() => this.role().toUpperCase());
}

// Usage in parent
@Component({
  template: `
    <app-user-card
      [id]="user.id"
      [name]="user.name"
      [email]="user.email"
      [role]="user.role"
      [(searchQuery)]="query"
      (onEdit)="editUser($event)"
      (onDelete)="deleteUser($event)"
    />
  `,
})
export class ParentComponent {
  query = signal("");
}
```

## Computed Signals

```typescript
import { signal, computed } from "@angular/core";

interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
}

const items = signal<CartItem[]>([]);
const taxRate = signal(0.1);

const subtotal = computed(() =>
  items().reduce((sum, item) => sum + item.price * item.quantity, 0),
);

const tax = computed(() => subtotal() * taxRate());
const total = computed(() => subtotal() + tax());
const itemCount = computed(() =>
  items().reduce((sum, item) => sum + item.quantity, 0),
);

// Computed signals are lazy and cached
```

## RxJS Interop

```typescript
import { Component, signal } from "@angular/core";
import { toSignal, toObservable } from "@angular/core/rxjs-interop";
import { HttpClient } from "@angular/common/http";
import { switchMap, debounceTime } from "rxjs";

@Component({
  selector: "app-search",
  template: `
    <input (input)="query.set($event.target.value)" />
    @if (results(); as data) {
      @for (item of data; track item.id) {
        <div>{{ item.name }}</div>
      }
    }
  `,
})
export class SearchComponent {
  query = signal("");

  // Convert signal to observable for RxJS operators
  results = toSignal(
    toObservable(this.query).pipe(
      debounceTime(300),
      switchMap((q) =>
        this.http.get<Item[]>(`/api/search?q=${q}`),
      ),
    ),
    { initialValue: [] },
  );

  constructor(private http: HttpClient) {}
}
```

## Resource API

```typescript
import { Component, signal, resource } from "@angular/core";

@Component({
  selector: "app-user-profile",
  template: `
    @if (userResource.isLoading()) {
      <p>Loading...</p>
    }
    @if (userResource.value(); as user) {
      <h1>{{ user.name }}</h1>
      <p>{{ user.email }}</p>
    }
    @if (userResource.error(); as error) {
      <p class="error">{{ error.message }}</p>
    }
  `,
})
export class UserProfileComponent {
  userId = signal("1");

  userResource = resource({
    request: () => this.userId(),
    loader: async ({ request: id }) => {
      const res = await fetch(`/api/users/${id}`);
      if (!res.ok) throw new Error("Failed to load user");
      return res.json();
    },
  });
}
```

## Additional Resources

- Angular Signals: https://angular.dev/guide/signals
- Signal inputs: https://angular.dev/guide/signals/inputs
- RxJS interop: https://angular.dev/guide/signals/rxjs-interop
