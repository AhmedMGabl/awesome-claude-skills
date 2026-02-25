---
name: htmx-hypermedia
description: HTMX and hypermedia-driven development covering hx-get/post/put/delete attributes, server-side rendering with Express/Flask, partial HTML responses, infinite scroll, active search, inline editing, WebSocket integration, CSS transitions, and progressive enhancement patterns.
---

# HTMX & Hypermedia

This skill should be used when building interactive web applications with HTMX and server-rendered HTML. It covers HTMX attributes, server-side patterns, partial updates, and progressive enhancement.

## When to Use This Skill

Use this skill when you need to:

- Add interactivity without JavaScript frameworks
- Build server-rendered apps with partial updates
- Implement infinite scroll, active search, or inline editing
- Use progressive enhancement patterns
- Reduce client-side JavaScript complexity

## Core HTMX Patterns

```html
<!-- Load partial HTML into element -->
<button hx-get="/api/users" hx-target="#user-list" hx-swap="innerHTML">
  Load Users
</button>
<div id="user-list"></div>

<!-- Form submission with partial update -->
<form hx-post="/api/contacts" hx-target="#contact-list" hx-swap="beforeend" hx-on::after-request="this.reset()">
  <input name="name" placeholder="Name" required />
  <input name="email" type="email" placeholder="Email" required />
  <button type="submit">Add Contact</button>
</form>
<div id="contact-list"></div>

<!-- Delete with confirmation -->
<button hx-delete="/api/users/123"
        hx-target="closest tr"
        hx-swap="outerHTML swap:500ms"
        hx-confirm="Are you sure?"
        class="text-red-600">
  Delete
</button>

<!-- Inline editing -->
<div hx-get="/api/users/123/edit" hx-trigger="dblclick" hx-swap="outerHTML">
  <span>John Doe</span>
  <span class="text-gray-500">john@example.com</span>
</div>
```

## Active Search

```html
<!-- Search with debounce -->
<input type="search"
       name="q"
       hx-get="/api/search"
       hx-trigger="input changed delay:300ms, search"
       hx-target="#search-results"
       hx-indicator="#search-spinner"
       placeholder="Search users..." />
<span id="search-spinner" class="htmx-indicator">Searching...</span>
<div id="search-results"></div>
```

```typescript
// Server: return partial HTML
app.get("/api/search", (req, res) => {
  const query = req.query.q as string;
  const users = searchUsers(query);

  res.send(`
    ${users.map((u) => `
      <div class="p-3 border-b flex items-center gap-3">
        <img src="${u.avatar}" class="w-8 h-8 rounded-full" alt="" />
        <div>
          <div class="font-medium">${u.name}</div>
          <div class="text-sm text-gray-500">${u.email}</div>
        </div>
      </div>
    `).join("")}
    ${users.length === 0 ? '<div class="p-3 text-gray-500">No results found</div>' : ""}
  `);
});
```

## Infinite Scroll

```html
<div id="post-list">
  <!-- Initial posts rendered server-side -->
  <div class="post">Post 1</div>
  <div class="post">Post 2</div>
  <!-- Sentinel element triggers next page -->
  <div hx-get="/api/posts?page=2"
       hx-trigger="revealed"
       hx-swap="outerHTML"
       hx-indicator="#load-spinner">
    <div id="load-spinner" class="htmx-indicator">Loading more...</div>
  </div>
</div>
```

```typescript
// Server: return next page + new sentinel
app.get("/api/posts", (req, res) => {
  const page = parseInt(req.query.page as string) || 1;
  const posts = getPosts(page, 20);
  const hasMore = posts.length === 20;

  res.send(`
    ${posts.map((p) => `<div class="post p-4 border-b">${p.title}</div>`).join("")}
    ${hasMore ? `
      <div hx-get="/api/posts?page=${page + 1}"
           hx-trigger="revealed"
           hx-swap="outerHTML">
        <div class="htmx-indicator text-center p-4">Loading...</div>
      </div>
    ` : '<div class="text-center p-4 text-gray-500">No more posts</div>'}
  `);
});
```

## Python Flask Server

```python
from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route("/api/todos", methods=["POST"])
def create_todo():
    title = request.form["title"]
    todo = db.create_todo(title=title)
    return render_template_string("""
        <li id="todo-{{ todo.id }}" class="flex items-center gap-2 p-2">
            <input type="checkbox"
                   hx-patch="/api/todos/{{ todo.id }}/toggle"
                   hx-target="#todo-{{ todo.id }}"
                   hx-swap="outerHTML" />
            <span>{{ todo.title }}</span>
            <button hx-delete="/api/todos/{{ todo.id }}"
                    hx-target="#todo-{{ todo.id }}"
                    hx-swap="outerHTML"
                    class="ml-auto text-red-500">x</button>
        </li>
    """, todo=todo)

@app.route("/api/todos/<int:id>/toggle", methods=["PATCH"])
def toggle_todo(id):
    todo = db.toggle_todo(id)
    completed_class = "line-through text-gray-400" if todo.completed else ""
    return render_template_string("""
        <li id="todo-{{ todo.id }}" class="flex items-center gap-2 p-2">
            <input type="checkbox" {{ "checked" if todo.completed }}
                   hx-patch="/api/todos/{{ todo.id }}/toggle"
                   hx-target="#todo-{{ todo.id }}"
                   hx-swap="outerHTML" />
            <span class="{{ cls }}">{{ todo.title }}</span>
        </li>
    """, todo=todo, cls=completed_class)
```

## CSS Transitions

```css
/* Fade in new content */
.htmx-added { opacity: 0; }
.htmx-added { animation: fadeIn 0.3s ease forwards; }

/* Fade out removed content */
.htmx-swapping { opacity: 0; transition: opacity 0.3s ease; }

@keyframes fadeIn {
  to { opacity: 1; }
}

/* Loading indicator */
.htmx-indicator { display: none; }
.htmx-request .htmx-indicator { display: inline-block; }
.htmx-request.htmx-indicator { display: inline-block; }
```

## Additional Resources

- HTMX docs: https://htmx.org/docs/
- Hypermedia Systems (book): https://hypermedia.systems/
- HTMX examples: https://htmx.org/examples/
- Alpine.js (companion): https://alpinejs.dev/
