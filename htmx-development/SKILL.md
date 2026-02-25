---
name: htmx-development
description: HTMX development covering hx-get/post/put/delete attributes, server-sent events, WebSocket integration, CSS transitions, out-of-band swaps, hyperscript, and server-side framework integration.
---

# HTMX Development

This skill should be used when building hypermedia-driven web applications with HTMX. It covers AJAX attributes, server interaction, transitions, and framework integration.

## When to Use This Skill

Use this skill when you need to:

- Add dynamic behavior without JavaScript frameworks
- Build server-rendered UIs with partial page updates
- Implement infinite scroll, active search, or live updates
- Use progressive enhancement patterns
- Integrate HTMX with backend frameworks

## Core Attributes

```html
<!-- GET request, swap inner HTML -->
<button hx-get="/api/data" hx-target="#result" hx-swap="innerHTML">
  Load Data
</button>
<div id="result"></div>

<!-- POST form -->
<form hx-post="/api/items" hx-target="#items-list" hx-swap="beforeend">
  <input name="title" required />
  <button type="submit">Add Item</button>
</form>

<!-- DELETE with confirmation -->
<button
  hx-delete="/api/items/1"
  hx-confirm="Are you sure?"
  hx-target="closest tr"
  hx-swap="outerHTML swap:1s"
>
  Delete
</button>

<!-- PUT with JSON body -->
<form hx-put="/api/items/1" hx-ext="json-enc" hx-target="#item-1">
  <input name="title" value="Updated" />
  <button type="submit">Save</button>
</form>
```

## Swap Strategies

```html
<!-- Replace inner content (default) -->
<div hx-get="/partial" hx-swap="innerHTML">...</div>

<!-- Replace entire element -->
<div hx-get="/partial" hx-swap="outerHTML">...</div>

<!-- Append/prepend -->
<div hx-get="/items" hx-swap="beforeend">...</div>
<div hx-get="/items" hx-swap="afterbegin">...</div>

<!-- Swap with transition -->
<div hx-get="/page" hx-swap="innerHTML transition:true">...</div>

<!-- Delete after swap (for delete operations) -->
<tr hx-delete="/items/1" hx-swap="outerHTML swap:500ms">...</tr>
```

## Active Search

```html
<input
  type="search"
  name="q"
  hx-get="/search"
  hx-trigger="input changed delay:300ms, search"
  hx-target="#search-results"
  hx-indicator=".spinner"
  placeholder="Search..."
/>
<span class="spinner htmx-indicator">Searching...</span>
<div id="search-results"></div>
```

## Infinite Scroll

```html
<table>
  <tbody id="items">
    <!-- Server returns rows + trigger element -->
    <tr>
      <td>Item 1</td>
    </tr>
    <!-- Last row triggers next page load -->
    <tr
      hx-get="/items?page=2"
      hx-trigger="revealed"
      hx-target="#items"
      hx-swap="beforeend"
    >
      <td>Loading more...</td>
    </tr>
  </tbody>
</table>
```

## Out-of-Band Swaps

```html
<!-- Server response can update multiple elements -->
<!-- Primary response swaps into target -->
<div id="main-content">Updated content</div>

<!-- OOB elements swap independently -->
<div id="notification-count" hx-swap-oob="true">
  <span class="badge">5</span>
</div>
<div id="last-updated" hx-swap-oob="innerHTML">
  Just now
</div>
```

## Server-Sent Events

```html
<div hx-ext="sse" sse-connect="/events">
  <!-- Update on specific event -->
  <div sse-swap="message">Waiting for updates...</div>

  <!-- Multiple event types -->
  <div sse-swap="notification">No notifications</div>
  <div sse-swap="status">Status: OK</div>
</div>
```

## Express.js Integration

```typescript
import express from "express";

const app = express();

app.get("/search", (req, res) => {
  const query = req.query.q as string;
  const results = searchItems(query);

  // Return HTML partial
  res.send(`
    ${results.map((item) => `
      <div class="result">
        <h3>${item.title}</h3>
        <p>${item.description}</p>
      </div>
    `).join("")}
  `);
});

app.delete("/items/:id", (req, res) => {
  deleteItem(req.params.id);
  // Return empty string to remove element
  res.send("");
});
```

## CSS Transitions

```css
/* Fade in new content */
.htmx-added {
  opacity: 0;
}
.htmx-added {
  opacity: 1;
  transition: opacity 300ms ease-in;
}

/* Fade out removed content */
.htmx-swapping {
  opacity: 0;
  transition: opacity 300ms ease-out;
}

/* Loading indicator */
.htmx-indicator {
  display: none;
}
.htmx-request .htmx-indicator {
  display: inline;
}
```

## Additional Resources

- HTMX docs: https://htmx.org/docs/
- Examples: https://htmx.org/examples/
- Extensions: https://htmx.org/extensions/
