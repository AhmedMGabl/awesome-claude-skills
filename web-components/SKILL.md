---
name: web-components
description: Web Components development covering Custom Elements, Shadow DOM, HTML templates and slots, Lit framework, reactive properties, CSS encapsulation, lifecycle callbacks, event dispatching, form-associated elements, and cross-framework interoperability.
---

# Web Components

This skill should be used when building reusable Web Components with Custom Elements, Shadow DOM, and the Lit framework. It covers encapsulation, reactivity, slots, and framework interop.

## When to Use This Skill

Use this skill when you need to:

- Create framework-agnostic UI components
- Use Shadow DOM for CSS encapsulation
- Build components with the Lit framework
- Implement slots and composition patterns
- Share components across React, Vue, Angular

## Lit Framework

```typescript
import { LitElement, html, css } from "lit";
import { customElement, property, state } from "lit/decorators.js";

@customElement("todo-list")
export class TodoList extends LitElement {
  static styles = css`
    :host { display: block; }
    ul { list-style: none; padding: 0; }
    li { display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 0; }
    .done { text-decoration: line-through; color: #9ca3af; }
  `;

  @property({ type: String }) heading = "Todos";
  @state() private items: Array<{ text: string; done: boolean }> = [];
  @state() private input = "";

  private addItem() {
    if (!this.input.trim()) return;
    this.items = [...this.items, { text: this.input, done: false }];
    this.input = "";
  }

  private toggleItem(index: number) {
    this.items = this.items.map((item, i) =>
      i === index ? { ...item, done: !item.done } : item,
    );
  }

  render() {
    return html`
      <h2>${this.heading}</h2>
      <div style="display:flex;gap:0.5rem">
        <input
          type="text"
          .value=${this.input}
          @input=${(e: InputEvent) => (this.input = (e.target as HTMLInputElement).value)}
          @keydown=${(e: KeyboardEvent) => e.key === "Enter" && this.addItem()}
          placeholder="Add a todo"
        />
        <button @click=${this.addItem}>Add</button>
      </div>
      <ul>
        ${this.items.map(
          (item, i) => html`
            <li>
              <input type="checkbox" .checked=${item.done} @change=${() => this.toggleItem(i)} />
              <span class=${item.done ? "done" : ""}>${item.text}</span>
            </li>
          `,
        )}
      </ul>
    `;
  }
}
```

## Custom Element Lifecycle

```typescript
class MyElement extends HTMLElement {
  static observedAttributes = ["name", "value"];

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
  }

  // Called when element is added to DOM
  connectedCallback() {
    this.render();
  }

  // Called when element is removed from DOM
  disconnectedCallback() {
    this.cleanup();
  }

  // Called when an observed attribute changes
  attributeChangedCallback(name: string, oldValue: string, newValue: string) {
    if (oldValue !== newValue) this.render();
  }

  private render() {
    const template = document.createElement("template");
    template.textContent = this.getAttribute("name") ?? "";
    this.shadowRoot!.replaceChildren(template.content.cloneNode(true));
  }

  private cleanup() {
    // Remove event listeners, cancel timers, etc.
  }
}

customElements.define("my-element", MyElement);
```

## Shadow DOM & Slots

```typescript
// Composition with named slots
// <card-element>
//   <span slot="title">Card Title</span>
//   <p slot="content">Card body text</p>
//   <button slot="actions">Click me</button>
// </card-element>

const template = document.createElement("template");
template.textContent = `
  <style>
    :host { display: block; border: 1px solid #e5e7eb; border-radius: 0.5rem; }
    .header { padding: 1rem; border-bottom: 1px solid #e5e7eb; font-weight: 600; }
    .body { padding: 1rem; }
    .footer { padding: 0.75rem 1rem; border-top: 1px solid #e5e7eb; }
  </style>
`;

// CSS Parts for external styling
// my-element::part(title) { color: blue; }
```

## React Wrapper

```tsx
import { createComponent } from "@lit/react";
import { TodoList } from "./todo-list";

export const TodoListReact = createComponent({
  tagName: "todo-list",
  elementClass: TodoList,
  react: React,
});

// Usage: <TodoListReact heading="My Todos" />
```

## Form-Associated Elements

```typescript
// Custom form element that participates in <form>
class CustomInput extends HTMLElement {
  static formAssociated = true;
  private internals: ElementInternals;

  constructor() {
    super();
    this.internals = this.attachInternals();
    this.attachShadow({ mode: "open" });
  }

  connectedCallback() {
    const input = document.createElement("input");
    input.setAttribute("type", "text");
    input.setAttribute("part", "input");
    input.addEventListener("input", () => {
      this.internals.setFormValue(input.value);
    });
    this.shadowRoot!.appendChild(input);
  }
}

customElements.define("custom-input", CustomInput);
```

## Additional Resources

- MDN Web Components: https://developer.mozilla.org/en-US/docs/Web/API/Web_components
- Lit: https://lit.dev/
- Open Web Components: https://open-wc.org/
