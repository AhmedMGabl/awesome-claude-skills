---
name: htmx-alpine
description: HTMX with Alpine.js patterns covering server-driven UI, partial page updates, inline editing, infinite scroll, modals, form validation, and progressive enhancement.
---

# HTMX + Alpine.js

This skill should be used when building server-driven interactive UIs with HTMX and Alpine.js. It covers partial updates, inline editing, infinite scroll, modals, and progressive enhancement.

## When to Use This Skill

Use this skill when you need to:

- Build interactive UIs without heavy JavaScript frameworks
- Use HTMX for server-driven partial page updates
- Add client-side behavior with Alpine.js
- Implement infinite scroll and live search
- Create modals, tabs, and inline editing

## Setup

```html
<head>
  <script src="https://unpkg.com/htmx.org@2.0.0"></script>
  <script src="https://unpkg.com/alpinejs@3.14.0" defer></script>
</head>
```

## HTMX Basics

```html
<!-- Click to load content -->
<button hx-get="/api/users" hx-target="#user-list" hx-swap="innerHTML">
  Load Users
</button>
<div id="user-list"></div>

<!-- Form submission -->
<form hx-post="/api/users" hx-target="#user-list" hx-swap="afterbegin"
      hx-on::after-request="this.reset()">
  <input name="name" required />
  <input name="email" type="email" required />
  <button type="submit">Add User</button>
</form>

<!-- Delete with confirmation -->
<button hx-delete="/api/users/1" hx-target="closest tr" hx-swap="outerHTML"
        hx-confirm="Are you sure?">
  Delete
</button>
```

## Live Search

```html
<input type="search" name="q"
       hx-get="/api/search"
       hx-trigger="input changed delay:300ms, search"
       hx-target="#results"
       hx-indicator="#spinner"
       placeholder="Search..." />

<span id="spinner" class="htmx-indicator">Loading...</span>
<div id="results"></div>
```

## Infinite Scroll

```html
<div id="posts">
  <!-- Server renders initial posts -->
  <div class="post">Post 1</div>
  <div class="post">Post 2</div>

  <!-- Sentinel element triggers next page load -->
  <div hx-get="/api/posts?page=2"
       hx-trigger="revealed"
       hx-swap="outerHTML"
       hx-indicator="#load-more">
    <span id="load-more" class="htmx-indicator">Loading more...</span>
  </div>
</div>
```

## Alpine.js State

```html
<!-- Toggle panel -->
<div x-data="{ open: false }">
  <button @click="open = !open" x-text="open ? 'Hide' : 'Show'"></button>
  <div x-show="open" x-transition>
    <p>Panel content</p>
  </div>
</div>

<!-- Counter with Alpine -->
<div x-data="{ count: 0 }">
  <button @click="count--">-</button>
  <span x-text="count"></span>
  <button @click="count++">+</button>
</div>

<!-- Dropdown -->
<div x-data="{ open: false }" @click.outside="open = false">
  <button @click="open = !open">Menu</button>
  <ul x-show="open" x-transition>
    <li><a href="/profile">Profile</a></li>
    <li><a href="/settings">Settings</a></li>
    <li><button @click="$dispatch('logout')">Logout</button></li>
  </ul>
</div>
```

## HTMX + Alpine Together

```html
<!-- Inline editing -->
<div x-data="{ editing: false }">
  <template x-if="!editing">
    <span @dblclick="editing = true">Click to edit</span>
  </template>
  <template x-if="editing">
    <form hx-put="/api/items/1" hx-target="closest div" hx-swap="outerHTML"
          @htmx:after-request="editing = false">
      <input name="value" value="Current value" />
      <button type="submit">Save</button>
      <button type="button" @click="editing = false">Cancel</button>
    </form>
  </template>
</div>

<!-- Modal -->
<div x-data="{ showModal: false }">
  <button @click="showModal = true"
          hx-get="/api/users/1/edit"
          hx-target="#modal-content">
    Edit
  </button>

  <div x-show="showModal" x-transition @keydown.escape.window="showModal = false"
       class="modal-overlay" @click.self="showModal = false">
    <div class="modal" id="modal-content">
      <!-- HTMX loads content here -->
    </div>
  </div>
</div>

<!-- Tabs -->
<div x-data="{ tab: 'details' }">
  <nav>
    <button :class="{ active: tab === 'details' }" @click="tab = 'details'"
            hx-get="/api/users/1/details" hx-target="#tab-content">Details</button>
    <button :class="{ active: tab === 'posts' }" @click="tab = 'posts'"
            hx-get="/api/users/1/posts" hx-target="#tab-content">Posts</button>
  </nav>
  <div id="tab-content"></div>
</div>
```

## Additional Resources

- HTMX: https://htmx.org/docs/
- Alpine.js: https://alpinejs.dev/start-here
- HTMX Examples: https://htmx.org/examples/
