---
name: htmx-patterns
description: htmx hypermedia patterns covering hx-get/post/put/delete attributes, swap strategies, targets, triggers, boosting, server-sent events, WebSocket connections, and progressive enhancement with minimal JavaScript.
---

# htmx Patterns

This skill should be used when building hypermedia-driven web applications with htmx. It covers AJAX attributes, swap strategies, triggers, SSE, WebSockets, and progressive enhancement.

## When to Use This Skill

Use this skill when you need to:

- Add dynamic behavior without writing JavaScript
- Implement AJAX with HTML attributes
- Use server-sent events or WebSockets
- Progressively enhance server-rendered HTML
- Build interactive UIs with hypermedia patterns

## Setup

```html
<script src="https://unpkg.com/htmx.org@2.0.0"></script>
```

## Basic Requests

```html
<!-- GET request -->
<button hx-get="/api/data" hx-target="#result">
  Load Data
</button>
<div id="result"></div>

<!-- POST with form data -->
<form hx-post="/api/contacts" hx-target="#contact-list" hx-swap="beforeend">
  <input name="name" placeholder="Name" />
  <input name="email" placeholder="Email" />
  <button type="submit">Add Contact</button>
</form>
<div id="contact-list"></div>

<!-- PUT to update -->
<div hx-put="/api/contacts/1" hx-trigger="click" hx-target="this" hx-swap="outerHTML">
  Click to edit
</div>

<!-- DELETE with confirmation -->
<button hx-delete="/api/contacts/1"
        hx-confirm="Are you sure?"
        hx-target="closest tr"
        hx-swap="outerHTML swap:500ms">
  Delete
</button>
```

## Swap Strategies

```html
<!-- innerHTML (default) - replace inner content -->
<div hx-get="/content" hx-swap="innerHTML">Replace my content</div>

<!-- outerHTML - replace entire element -->
<div hx-get="/content" hx-swap="outerHTML">Replace me entirely</div>

<!-- beforebegin - insert before element -->
<div hx-get="/content" hx-swap="beforebegin">Insert before me</div>

<!-- afterbegin - insert at start of children -->
<div hx-get="/content" hx-swap="afterbegin">Insert as first child</div>

<!-- beforeend - append to children -->
<ul hx-get="/items" hx-swap="beforeend">
  <li>Existing item</li>
</ul>

<!-- afterend - insert after element -->
<div hx-get="/content" hx-swap="afterend">Insert after me</div>

<!-- Swap with transition -->
<div hx-get="/content" hx-swap="innerHTML transition:true">Animate swap</div>

<!-- Swap with settle delay -->
<div hx-get="/content" hx-swap="innerHTML settle:500ms">Delayed settle</div>
```

## Triggers

```html
<!-- Standard events -->
<input hx-get="/search" hx-trigger="keyup changed delay:300ms" hx-target="#results" name="q" />

<!-- Multiple triggers -->
<div hx-get="/news" hx-trigger="load, every 30s">Live news feed</div>

<!-- Intersection observer (lazy loading) -->
<img hx-get="/api/image/1" hx-trigger="intersect once" hx-swap="outerHTML" />

<!-- Custom event -->
<div hx-get="/notifications" hx-trigger="newMessage from:body">
  Notifications
</div>

<!-- Trigger with filters -->
<input hx-get="/validate" hx-trigger="keyup changed delay:500ms[this.value.length > 2]" name="username" />

<!-- Polling -->
<div hx-get="/api/status" hx-trigger="every 5s">
  Status: Active
</div>
```

## Targets and Selectors

```html
<!-- Target by ID -->
<button hx-get="/data" hx-target="#output">Load</button>

<!-- Target closest ancestor -->
<button hx-delete="/item/1" hx-target="closest .card">Delete</button>

<!-- Target next sibling -->
<button hx-get="/details" hx-target="next .details">Show Details</button>

<!-- Out-of-band swaps (update multiple elements) -->
<!-- Server response: -->
<div id="main-content">Main content here</div>
<div id="sidebar" hx-swap-oob="true">Updated sidebar</div>
<div id="notifications" hx-swap-oob="innerHTML">3 new</div>
```

## Boost and Progressive Enhancement

```html
<!-- Boost all links and forms in a section -->
<div hx-boost="true">
  <a href="/about">About</a>        <!-- Becomes AJAX -->
  <a href="/contact">Contact</a>    <!-- Becomes AJAX -->
  <form action="/search" method="get">
    <input name="q" />
    <button>Search</button>           <!-- Becomes AJAX -->
  </form>
</div>

<!-- Push URL to browser history -->
<a hx-get="/page/2" hx-push-url="true" hx-target="#content">Page 2</a>

<!-- Disable boost for specific elements -->
<div hx-boost="true">
  <a href="/about">About (boosted)</a>
  <a href="/download.pdf" hx-boost="false">Download (not boosted)</a>
</div>
```

## Server-Sent Events

```html
<!-- Connect to SSE endpoint -->
<div hx-ext="sse" sse-connect="/api/events">
  <div sse-swap="message">Waiting for messages...</div>
  <div sse-swap="notification">No notifications</div>
</div>

<!-- Close SSE on specific event -->
<div hx-ext="sse" sse-connect="/api/stream" sse-close="complete">
  <div sse-swap="progress">0%</div>
</div>
```

## WebSocket Connections

```html
<!-- WebSocket connection -->
<div hx-ext="ws" ws-connect="/ws/chat">
  <div id="chat-messages"></div>
  <form ws-send>
    <input name="message" />
    <button>Send</button>
  </form>
</div>
```

## Server Response Patterns

```python
# Flask/FastAPI server responses
from flask import Flask, render_template_string

app = Flask(__name__)

@app.route("/api/search")
def search():
    q = request.args.get("q", "")
    results = search_db(q)
    return render_template_string("""
        {% for item in results %}
        <div class="result">
            <h3>{{ item.title }}</h3>
            <p>{{ item.description }}</p>
        </div>
        {% endfor %}
    """, results=results)

# Return HX-Trigger header to fire client events
@app.route("/api/contacts", methods=["POST"])
def create_contact():
    contact = save_contact(request.form)
    response = make_response(render_template("contact_row.html", contact=contact))
    response.headers["HX-Trigger"] = "contactAdded"
    return response

# Redirect after action
@app.route("/api/items/<id>", methods=["DELETE"])
def delete_item(id):
    delete_from_db(id)
    return "", 200, {"HX-Redirect": "/items"}
```

## Loading Indicators

```html
<!-- Built-in indicator -->
<button hx-get="/slow-endpoint" hx-indicator="#spinner">
  Load Data
  <span id="spinner" class="htmx-indicator">Loading...</span>
</button>

<!-- CSS class for indicator -->
<style>
  .htmx-indicator { display: none; }
  .htmx-request .htmx-indicator { display: inline; }
  .htmx-request.htmx-indicator { display: inline; }
</style>
```

## Additional Resources

- htmx: https://htmx.org/
- htmx examples: https://htmx.org/examples/
- Hypermedia Systems book: https://hypermedia.systems/
