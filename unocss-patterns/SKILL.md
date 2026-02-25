---
name: unocss-patterns
description: UnoCSS patterns covering atomic utility classes, presets, shortcuts, rules, variants, icons, attributify mode, and build-time optimization.
---

# UnoCSS Patterns

This skill should be used when styling with UnoCSS instant on-demand atomic CSS. It covers presets, shortcuts, custom rules, variants, icons, and attributify mode.

## When to Use This Skill

Use this skill when you need to:

- Use atomic CSS with instant on-demand generation
- Create custom utility presets and rules
- Configure shortcuts for common patterns
- Use attributify mode for cleaner HTML
- Integrate icons as CSS classes

## Configuration

```typescript
// uno.config.ts
import { defineConfig, presetUno, presetIcons, presetAttributify } from "unocss";

export default defineConfig({
  presets: [
    presetUno(),
    presetAttributify(),
    presetIcons({
      scale: 1.2,
      cdn: "https://esm.sh/",
    }),
  ],
  shortcuts: {
    "btn": "px-4 py-2 rounded font-medium cursor-pointer inline-flex items-center justify-center",
    "btn-primary": "btn bg-blue-600 text-white hover:bg-blue-700",
    "btn-outline": "btn border-2 border-blue-600 text-blue-600 hover:bg-blue-50",
    "card": "p-4 rounded-lg shadow-md bg-white",
    "input": "px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500",
  },
  theme: {
    colors: {
      brand: {
        primary: "#0066cc",
        secondary: "#6c757d",
      },
    },
  },
  rules: [
    ["text-balance", { "text-wrap": "balance" }],
    [/^grid-cols-auto-(\d+)$/, ([, d]) => ({
      "grid-template-columns": `repeat(auto-fill, minmax(${d}px, 1fr))`,
    })],
  ],
});
```

## Usage

```html
<!-- Utility classes -->
<div class="flex items-center gap-4 p-6">
  <h1 class="text-2xl font-bold text-gray-900">Title</h1>
  <p class="text-gray-600 leading-relaxed">Content</p>
</div>

<!-- Shortcuts -->
<button class="btn-primary">Save</button>
<button class="btn-outline">Cancel</button>
<div class="card">Card content</div>

<!-- Icons (with presetIcons) -->
<span class="i-carbon-sun text-xl" />
<span class="i-mdi-github text-2xl" />

<!-- Responsive -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <div class="card">Item</div>
</div>

<!-- Dark mode -->
<div class="bg-white dark:bg-gray-900 text-black dark:text-white">
  Content
</div>
```

## Attributify Mode

```html
<!-- Instead of class strings -->
<button
  bg="blue-600 hover:blue-700"
  text="white sm"
  p="x-4 y-2"
  border="rounded"
  font="medium"
>
  Button
</button>

<div
  flex="~ col"
  items="center"
  gap="4"
  p="6"
>
  Content
</div>
```

## Dynamic Rules

```typescript
rules: [
  // Custom spacing scale
  [/^space-(\d+)$/, ([, d]) => ({ gap: `${parseInt(d) * 0.25}rem` })],

  // Custom gradient
  [/^gradient-([\w-]+)-([\w-]+)$/, ([, from, to]) => ({
    background: `linear-gradient(135deg, var(--un-color-${from}) 0%, var(--un-color-${to}) 100%)`,
  })],
],
```

## Vite Integration

```typescript
// vite.config.ts
import UnoCSS from "unocss/vite";

export default defineConfig({
  plugins: [UnoCSS()],
});
```

```typescript
// main.ts
import "virtual:uno.css";
```

## Additional Resources

- UnoCSS: https://unocss.dev/
- Interactive Docs: https://unocss.dev/interactive/
- Presets: https://unocss.dev/presets/
