---
name: lit-components
description: Lit web component patterns covering reactive properties, decorators, templates with html/css tagged literals, lifecycle callbacks, shadow DOM styling, context protocol, and custom element registration.
---

# Lit Components

This skill should be used when building web components with Lit. It covers reactive properties, templates, styling, lifecycle, context, and custom element patterns.

## When to Use This Skill

Use this skill when you need to:

- Build framework-agnostic web components
- Create reusable UI elements with shadow DOM
- Use reactive properties and decorators
- Share context between components
- Build design system component libraries

## Basic Component

```typescript
import { LitElement, html, css } from "lit";
import { customElement, property, state } from "lit/decorators.js";

@customElement("my-greeting")
export class MyGreeting extends LitElement {
  static styles = css`
    :host {
      display: block;
      padding: 16px;
      border: 1px solid #ddd;
      border-radius: 8px;
    }
    h2 {
      color: var(--greeting-color, #333);
    }
    .count {
      font-weight: bold;
      color: #0066cc;
    }
  `;

  @property() name = "World";
  @property({ type: Number }) count = 0;
  @state() private _clicked = false;

  render() {
    return html`
      <h2>Hello, ${this.name}!</h2>
      <p>Count: <span class="count">${this.count}</span></p>
      <button @click=${this._increment}>Increment</button>
      ${this._clicked ? html`<p>Button was clicked!</p>` : ""}
    `;
  }

  private _increment() {
    this.count++;
    this._clicked = true;
    this.dispatchEvent(
      new CustomEvent("count-changed", {
        detail: { count: this.count },
        bubbles: true,
        composed: true,
      })
    );
  }
}
```

## Reactive Properties

```typescript
import { LitElement, html } from "lit";
import { customElement, property, state, query } from "lit/decorators.js";

@customElement("user-card")
export class UserCard extends LitElement {
  // Public reactive properties (attributes)
  @property() name = "";
  @property({ type: Number }) age = 0;
  @property({ type: Boolean, reflect: true }) active = false;
  @property({ type: Array }) tags: string[] = [];
  @property({ type: Object }) config = { theme: "light" };

  // Attribute name mapping
  @property({ attribute: "full-name" }) fullName = "";

  // Custom converter
  @property({
    converter: {
      fromAttribute: (value: string) => new Date(value),
      toAttribute: (value: Date) => value.toISOString(),
    },
  })
  date = new Date();

  // Internal reactive state (no attribute)
  @state() private _loading = false;

  // Query DOM elements
  @query("#input") private _input!: HTMLInputElement;

  render() {
    return html`
      <div class=${this.active ? "active" : ""}>
        <h3>${this.name}</h3>
        <p>Age: ${this.age}</p>
        <input id="input" />
        ${this._loading ? html`<span>Loading...</span>` : ""}
      </div>
    `;
  }
}
```

## Templates and Conditionals

```typescript
import { html, nothing } from "lit";
import { classMap } from "lit/directives/class-map.js";
import { styleMap } from "lit/directives/style-map.js";
import { repeat } from "lit/directives/repeat.js";
import { when } from "lit/directives/when.js";
import { choose } from "lit/directives/choose.js";

// Conditional rendering
render() {
  return html`
    ${this.show ? html`<div>Visible</div>` : nothing}
    ${when(this.loggedIn,
      () => html`<p>Welcome back!</p>`,
      () => html`<p>Please log in</p>`
    )}
    ${choose(this.status, [
      ["loading", () => html`<spinner-el></spinner-el>`],
      ["error", () => html`<error-el></error-el>`],
      ["success", () => html`<content-el></content-el>`],
    ])}
  `;
}

// Lists with repeat
render() {
  return html`
    <ul>
      ${repeat(
        this.items,
        (item) => item.id,
        (item) => html`<li>${item.name}</li>`
      )}
    </ul>
  `;
}

// Dynamic classes and styles
render() {
  const classes = { active: this.active, disabled: this.disabled };
  const styles = { color: this.color, fontSize: `${this.size}px` };
  return html`
    <div class=${classMap(classes)} style=${styleMap(styles)}>
      Content
    </div>
  `;
}
```

## Lifecycle

```typescript
@customElement("lifecycle-demo")
export class LifecycleDemo extends LitElement {
  connectedCallback() {
    super.connectedCallback();
    // Element added to DOM
    window.addEventListener("resize", this._onResize);
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    // Element removed from DOM
    window.removeEventListener("resize", this._onResize);
  }

  willUpdate(changedProperties: Map<string, unknown>) {
    // Before render, compute derived values
    if (changedProperties.has("items")) {
      this._filteredItems = this.items.filter((i) => i.active);
    }
  }

  updated(changedProperties: Map<string, unknown>) {
    // After render, access updated DOM
    if (changedProperties.has("open")) {
      this._dialog?.toggleAttribute("open", this.open);
    }
  }

  firstUpdated() {
    // After first render only
    this._input?.focus();
  }
}
```

## Slots and Composition

```typescript
@customElement("my-card")
export class MyCard extends LitElement {
  static styles = css`
    ::slotted(h2) { color: blue; }
    ::slotted([slot="footer"]) { border-top: 1px solid #ddd; }
  `;

  render() {
    return html`
      <div class="card">
        <div class="header">
          <slot name="header"></slot>
        </div>
        <div class="body">
          <slot></slot>  <!-- Default slot -->
        </div>
        <div class="footer">
          <slot name="footer"></slot>
        </div>
      </div>
    `;
  }
}

// Usage:
// <my-card>
//   <h2 slot="header">Title</h2>
//   <p>Body content</p>
//   <div slot="footer">Footer</div>
// </my-card>
```

## Context Protocol

```typescript
import { createContext, provide, consume } from "@lit/context";

// Define context
const themeContext = createContext<"light" | "dark">("theme");

// Provider
@customElement("theme-provider")
export class ThemeProvider extends LitElement {
  @provide({ context: themeContext })
  @property()
  theme: "light" | "dark" = "light";

  render() {
    return html`<slot></slot>`;
  }
}

// Consumer
@customElement("themed-button")
export class ThemedButton extends LitElement {
  @consume({ context: themeContext, subscribe: true })
  @state()
  theme?: "light" | "dark";

  render() {
    return html`
      <button class=${this.theme}>
        <slot></slot>
      </button>
    `;
  }
}
```

## Additional Resources

- Lit: https://lit.dev/
- Lit playground: https://lit.dev/playground/
- Lit tutorials: https://lit.dev/tutorials/
