---
name: lit-web-components
description: Lit web components covering reactive properties, decorators, templates, shadow DOM styling, lifecycle callbacks, events, context protocol, and SSR with custom element registration.
---

# Lit Web Components

This skill should be used when building web components with Lit. It covers reactive properties, templates, styling, events, and server-side rendering.

## When to Use This Skill

Use this skill when you need to:

- Build framework-agnostic web components
- Create reusable UI elements with shadow DOM
- Use reactive properties and efficient re-rendering
- Build design system component libraries
- Render web components on the server

## Basic Component

```typescript
import { LitElement, html, css } from "lit";
import { customElement, property, state } from "lit/decorators.js";

@customElement("my-counter")
export class MyCounter extends LitElement {
  static styles = css`
    :host {
      display: block;
      padding: 16px;
      border: 1px solid #ccc;
      border-radius: 8px;
    }
    button {
      padding: 8px 16px;
      margin: 0 4px;
      cursor: pointer;
    }
    .count {
      font-size: 2rem;
      font-weight: bold;
      text-align: center;
    }
  `;

  @property({ type: Number }) initial = 0;
  @state() private count = 0;

  connectedCallback() {
    super.connectedCallback();
    this.count = this.initial;
  }

  render() {
    return html`
      <div class="count">${this.count}</div>
      <div>
        <button @click=${() => this.count--}>-</button>
        <button @click=${() => this.count++}>+</button>
      </div>
    `;
  }
}
```

## Reactive Properties

```typescript
@customElement("user-card")
export class UserCard extends LitElement {
  // Reflected to attribute
  @property({ type: String, reflect: true }) name = "";
  @property({ type: String }) avatar = "";
  @property({ type: Boolean }) active = false;

  // Internal state (not an attribute)
  @state() private expanded = false;

  // Custom converter
  @property({
    converter: {
      fromAttribute: (value: string) => JSON.parse(value),
      toAttribute: (value: string[]) => JSON.stringify(value),
    },
  })
  tags: string[] = [];

  render() {
    return html`
      <div class="card ${this.active ? "active" : ""}">
        <img src=${this.avatar} alt=${this.name} />
        <h3>${this.name}</h3>
        ${this.expanded
          ? html`<div class="tags">${this.tags.map((t) => html`<span>${t}</span>`)}</div>`
          : null}
        <button @click=${() => (this.expanded = !this.expanded)}>
          ${this.expanded ? "Less" : "More"}
        </button>
      </div>
    `;
  }
}
```

## Events

```typescript
@customElement("todo-item")
export class TodoItem extends LitElement {
  @property() text = "";
  @property({ type: Boolean }) done = false;
  @property({ type: Number }) index = 0;

  private toggle() {
    this.dispatchEvent(
      new CustomEvent("todo-toggle", {
        detail: { index: this.index },
        bubbles: true,
        composed: true,
      })
    );
  }

  private remove() {
    this.dispatchEvent(
      new CustomEvent("todo-remove", {
        detail: { index: this.index },
        bubbles: true,
        composed: true,
      })
    );
  }

  render() {
    return html`
      <div class="item ${this.done ? "done" : ""}">
        <input type="checkbox" .checked=${this.done} @change=${this.toggle} />
        <span>${this.text}</span>
        <button @click=${this.remove}>x</button>
      </div>
    `;
  }
}
```

## Slots and Composition

```typescript
@customElement("my-dialog")
export class MyDialog extends LitElement {
  static styles = css`
    .overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; }
    .dialog { background: white; border-radius: 8px; padding: 24px; min-width: 300px; }
    ::slotted([slot="title"]) { font-size: 1.5rem; margin: 0 0 16px; }
  `;

  @property({ type: Boolean }) open = false;

  render() {
    if (!this.open) return null;
    return html`
      <div class="overlay" @click=${this.close}>
        <div class="dialog" @click=${(e: Event) => e.stopPropagation()}>
          <slot name="title"></slot>
          <slot></slot>
          <slot name="actions"></slot>
        </div>
      </div>
    `;
  }

  private close() {
    this.open = false;
    this.dispatchEvent(new CustomEvent("dialog-close"));
  }
}

// Usage: <my-dialog open>
//   <h2 slot="title">Confirm</h2>
//   <p>Are you sure?</p>
//   <div slot="actions"><button>Yes</button></div>
// </my-dialog>
```

## Lifecycle

```typescript
@customElement("data-fetcher")
export class DataFetcher extends LitElement {
  @property() url = "";
  @state() private data: unknown = null;
  @state() private loading = false;

  // Called when reactive properties change
  willUpdate(changed: PropertyValues) {
    if (changed.has("url")) {
      this.fetchData();
    }
  }

  // Called after first render
  firstUpdated() {
    console.log("Component first rendered");
  }

  private async fetchData() {
    this.loading = true;
    const res = await fetch(this.url);
    this.data = await res.json();
    this.loading = false;
  }

  render() {
    if (this.loading) return html`<p>Loading...</p>`;
    return html`<pre>${JSON.stringify(this.data, null, 2)}</pre>`;
  }
}
```

## Additional Resources

- Lit docs: https://lit.dev/docs/
- Playground: https://lit.dev/playground/
- Tutorials: https://lit.dev/tutorials/
