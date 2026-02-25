---
name: alpine-js
description: Alpine.js patterns covering x-data, x-bind, x-on, x-show/x-if, x-for, x-model, transitions, Alpine stores, plugins (Intersect, Persist, Morph), and progressive enhancement of server-rendered HTML.
---

# Alpine.js

This skill should be used when adding interactivity to server-rendered HTML with Alpine.js. It covers directives, reactivity, stores, transitions, and plugins.

## When to Use This Skill

Use this skill when you need to:

- Add lightweight interactivity to HTML pages
- Build dropdowns, modals, and tabs without a build step
- Create reactive UI with declarative syntax
- Progressively enhance server-rendered content
- Use Alpine stores for shared state

## Setup

```html
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
```

## Core Directives

```html
<!-- x-data: Define reactive state -->
<div x-data="{ open: false, count: 0, name: '' }">
  <button @click="open = !open">Toggle</button>
  <div x-show="open">Dropdown content</div>

  <button @click="count++">Count: <span x-text="count"></span></button>

  <input x-model="name" placeholder="Your name" />
  <p x-show="name">Hello, <span x-text="name"></span>!</p>
</div>

<!-- x-bind: Bind attributes -->
<div x-data="{ active: false }">
  <button
    :class="active ? 'bg-blue-500 text-white' : 'bg-gray-200'"
    :disabled="!active"
    @click="active = !active"
  >
    Toggle Active
  </button>
</div>

<!-- x-html: Set innerHTML -->
<div x-data="{ content: '<strong>Bold text</strong>' }">
  <div x-html="content"></div>
</div>
```

## Lists and Conditionals

```html
<!-- x-for: Loop over arrays -->
<div x-data="{ items: ['Apple', 'Banana', 'Cherry'] }">
  <ul>
    <template x-for="(item, index) in items" :key="index">
      <li x-text="item"></li>
    </template>
  </ul>
  <button @click="items.push('Date')">Add Item</button>
</div>

<!-- x-if: Conditional rendering (removes from DOM) -->
<div x-data="{ loggedIn: false }">
  <template x-if="loggedIn">
    <p>Welcome back!</p>
  </template>
  <template x-if="!loggedIn">
    <button @click="loggedIn = true">Log In</button>
  </template>
</div>

<!-- Nested data with x-for -->
<div x-data="{
  todos: [
    { id: 1, text: 'Learn Alpine', done: false },
    { id: 2, text: 'Build UI', done: true }
  ]
}">
  <template x-for="todo in todos" :key="todo.id">
    <div>
      <input type="checkbox" x-model="todo.done" />
      <span :class="todo.done && 'line-through'" x-text="todo.text"></span>
    </div>
  </template>
  <p x-text="`${todos.filter(t => t.done).length}/${todos.length} done`"></p>
</div>
```

## Events and Modifiers

```html
<div x-data="{ query: '' }">
  <!-- Event modifiers -->
  <button @click.prevent="handleSubmit()">Submit</button>
  <button @click.stop="handleClick()">Stop Propagation</button>
  <button @click.once="initOnce()">Run Once</button>
  <button @click.outside="open = false">Click Outside</button>

  <!-- Keyboard modifiers -->
  <input @keydown.enter="search()" @keydown.escape="query = ''" x-model="query" />

  <!-- Debounce -->
  <input @input.debounce.300ms="fetchResults()" x-model="query" />

  <!-- Window/document events -->
  <div @resize.window="handleResize()" @scroll.window.throttle.100ms="handleScroll()">
    Listening to window events
  </div>
</div>
```

## Transitions

```html
<div x-data="{ open: false }">
  <button @click="open = !open">Toggle</button>

  <!-- CSS transition classes -->
  <div
    x-show="open"
    x-transition:enter="transition ease-out duration-300"
    x-transition:enter-start="opacity-0 transform scale-90"
    x-transition:enter-end="opacity-100 transform scale-100"
    x-transition:leave="transition ease-in duration-200"
    x-transition:leave-start="opacity-100 transform scale-100"
    x-transition:leave-end="opacity-0 transform scale-90"
  >
    Animated content
  </div>

  <!-- Shorthand with modifiers -->
  <div x-show="open" x-transition.duration.300ms.opacity.scale.80>
    Quick transition
  </div>
</div>
```

## Alpine Stores

```html
<script>
  document.addEventListener("alpine:init", () => {
    Alpine.store("cart", {
      items: [],
      get total() {
        return this.items.reduce((sum, item) => sum + item.price * item.qty, 0);
      },
      add(product) {
        const existing = this.items.find((i) => i.id === product.id);
        if (existing) {
          existing.qty++;
        } else {
          this.items.push({ ...product, qty: 1 });
        }
      },
      remove(id) {
        this.items = this.items.filter((i) => i.id !== id);
      },
    });
  });
</script>

<div x-data>
  <button @click="$store.cart.add({ id: 1, name: 'Widget', price: 9.99 })">
    Add to Cart
  </button>
  <span x-text="$store.cart.items.length"></span> items
  <span x-text="'$' + $store.cart.total.toFixed(2)"></span>
</div>
```

## Reusable Components with Alpine.data

```html
<script>
  document.addEventListener("alpine:init", () => {
    Alpine.data("dropdown", () => ({
      open: false,
      toggle() { this.open = !this.open; },
      close() { this.open = false; },
    }));

    Alpine.data("tabs", (initialTab = "tab1") => ({
      activeTab: initialTab,
      isActive(tab) { return this.activeTab === tab; },
      select(tab) { this.activeTab = tab; },
    }));
  });
</script>

<div x-data="dropdown" @click.outside="close()">
  <button @click="toggle()">Menu</button>
  <ul x-show="open">
    <li><a href="#">Option 1</a></li>
    <li><a href="#">Option 2</a></li>
  </ul>
</div>

<div x-data="tabs('settings')">
  <button :class="isActive('profile') && 'active'" @click="select('profile')">Profile</button>
  <button :class="isActive('settings') && 'active'" @click="select('settings')">Settings</button>
  <div x-show="isActive('profile')">Profile content</div>
  <div x-show="isActive('settings')">Settings content</div>
</div>
```

## Additional Resources

- Alpine.js: https://alpinejs.dev/
- Alpine.js directives: https://alpinejs.dev/directives
- Alpine.js plugins: https://alpinejs.dev/plugins
