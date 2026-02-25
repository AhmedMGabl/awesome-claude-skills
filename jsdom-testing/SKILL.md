---
name: jsdom-testing
description: jsdom patterns covering DOM simulation in Node.js, document creation, element querying, event dispatching, form handling, window APIs, and testing with Jest/Vitest.
---

# jsdom Testing

This skill should be used when simulating browser DOM in Node.js with jsdom. It covers document creation, querying, events, forms, and testing integration.

## When to Use This Skill

Use this skill when you need to:

- Simulate browser DOM in Node.js for testing
- Parse and manipulate HTML documents server-side
- Test DOM-dependent code without a browser
- Create virtual documents for SSR validation
- Integrate jsdom with Jest or Vitest

## Setup

```bash
npm install jsdom @types/jsdom
```

## Basic DOM Simulation

```ts
import { JSDOM } from "jsdom";

const html = [
  "<!DOCTYPE html><html><body>",
  "<h1>Hello World</h1>",
  '<ul id="list">',
  '<li class="item">First</li>',
  '<li class="item">Second</li>',
  "</ul>",
  "</body></html>",
].join("");

const dom = new JSDOM(html);
const { document } = dom.window;

// Query elements
const heading = document.querySelector("h1");
console.log(heading?.textContent); // "Hello World"

const items = document.querySelectorAll(".item");
console.log(items.length); // 2

// Manipulate DOM
const newItem = document.createElement("li");
newItem.className = "item";
newItem.textContent = "Third";
document.getElementById("list")?.appendChild(newItem);
```

## Fetch and Parse Remote HTML

```ts
import { JSDOM } from "jsdom";

async function parseRemotePage(url: string) {
  const dom = await JSDOM.fromURL(url, {
    pretendToBeVisual: true,
    resources: "usable",
  });

  const { document } = dom.window;

  const title = document.querySelector("title")?.textContent;
  const metaDescription = document
    .querySelector('meta[name="description"]')
    ?.getAttribute("content");

  const links = Array.from(document.querySelectorAll("a[href]")).map((a) => ({
    text: a.textContent?.trim(),
    href: a.getAttribute("href"),
  }));

  return { title, metaDescription, links };
}
```

## Event Simulation

```ts
import { JSDOM } from "jsdom";

const dom = new JSDOM('<button id="btn">Click</button><div id="out"></div>');
const { document } = dom.window;
const button = document.getElementById("btn")!;
const output = document.getElementById("out")!;

button.addEventListener("click", () => {
  output.textContent = "Clicked!";
});

// Dispatch event
const clickEvent = new dom.window.Event("click", { bubbles: true });
button.dispatchEvent(clickEvent);
console.log(output.textContent); // "Clicked!"

// Keyboard event
const keyEvent = new dom.window.KeyboardEvent("keydown", {
  key: "Enter",
  bubbles: true,
});
document.dispatchEvent(keyEvent);
```

## Form Handling

```ts
import { JSDOM } from "jsdom";

const formHtml = [
  '<form id="login">',
  '<input name="username" type="text" />',
  '<input name="password" type="password" />',
  '<select name="role"><option value="user">User</option><option value="admin">Admin</option></select>',
  '<input name="remember" type="checkbox" />',
  "</form>",
].join("");

const dom = new JSDOM(formHtml);
const { document } = dom.window;
const form = document.getElementById("login") as HTMLFormElement;

// Set values
(form.elements.namedItem("username") as HTMLInputElement).value = "john";
(form.elements.namedItem("password") as HTMLInputElement).value = "secret";
(form.elements.namedItem("role") as HTMLSelectElement).value = "admin";
(form.elements.namedItem("remember") as HTMLInputElement).checked = true;

// Read form data
const formData = new dom.window.FormData(form);
console.log(Object.fromEntries(formData));
```

## Jest/Vitest Integration

```ts
// vitest.config.ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "jsdom",
  },
});

// component.test.ts
import { describe, it, expect, beforeEach } from "vitest";

function setupCounter() {
  const container = document.createElement("div");
  const count = document.createElement("span");
  count.id = "count";
  count.textContent = "0";

  const increment = document.createElement("button");
  increment.id = "increment";
  increment.textContent = "+";

  container.appendChild(count);
  container.appendChild(increment);
  document.body.appendChild(container);

  increment.addEventListener("click", () => {
    const current = parseInt(count.textContent || "0");
    count.textContent = String(current + 1);
  });
}

describe("Counter component", () => {
  beforeEach(() => {
    document.body.textContent = "";
    setupCounter();
  });

  it("should increment counter", () => {
    const count = document.getElementById("count")!;
    const button = document.getElementById("increment")!;
    button.click();
    expect(count.textContent).toBe("1");
  });

  it("should find elements by selector", () => {
    expect(document.querySelectorAll("button").length).toBe(1);
    expect(document.getElementById("count")).not.toBeNull();
  });
});
```

## Additional Resources

- jsdom: https://github.com/jsdom/jsdom
- API: https://github.com/jsdom/jsdom#api
- Jest environment: https://jestjs.io/docs/configuration#testenvironment-string
