---
name: tailwind-css
description: This skill should be used when building or styling web interfaces with Tailwind CSS, covering v4 setup, utility classes, responsive design, dark mode, custom theming, component patterns, animations, group/peer modifiers, arbitrary values, @apply extraction, and plugin development.
---

# Tailwind CSS Development

This skill should be used when developing or styling web applications with Tailwind CSS. It covers Tailwind v4 setup, utility classes, responsive design, dark mode, custom themes, component patterns (cards, forms, navbars), animations, group/peer modifiers, arbitrary values, @apply extraction, and plugins.

## Tailwind v4 Setup

```bash
npm install tailwindcss @tailwindcss/vite              # Vite
npm install tailwindcss @tailwindcss/postcss autoprefixer  # PostCSS (Next.js, Webpack)
```

```ts
// vite.config.ts
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";
export default defineConfig({ plugins: [tailwindcss()] });
```

```css
/* src/app.css -- v4 replaces @tailwind directives with a single import */
@import "tailwindcss";
```

## Custom Theme Configuration

Tailwind v4 uses CSS-first configuration via `@theme`. Tokens generate utilities automatically.

```css
@import "tailwindcss";
@theme {
  --color-brand-50: #eff6ff;
  --color-brand-500: #3b82f6;
  --color-brand-600: #2563eb;
  --color-brand-700: #1d4ed8;
  --font-family-sans: "Inter", sans-serif;
  --breakpoint-xs: 475px;
  --animate-fade-in: fade-in 0.3s ease-out;
  --animate-slide-up: slide-up 0.4s ease-out;
}
@keyframes fade-in { from { opacity: 0 } to { opacity: 1 } }
@keyframes slide-up { from { opacity: 0; transform: translateY(10px) } to { opacity: 1; transform: translateY(0) } }
```

## Responsive Design

Breakpoints: `sm:640px` `md:768px` `lg:1024px` `xl:1280px` `2xl:1536px`. Mobile-first -- prefix any utility.

```html
<div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
  <div class="p-4">Responsive grid item</div>
</div>
<nav class="hidden md:flex items-center gap-6">Desktop nav</nav>
<button class="md:hidden p-2">Mobile menu</button>
<section class="px-4 py-8 text-sm sm:px-6 sm:text-base lg:px-8 lg:py-16 lg:text-lg">Content</section>
```

## Dark Mode

Toggle a `dark` class on `<html>` for class-based dark mode. Prefix utilities with `dark:`.
```html
<div class="bg-white text-gray-900 dark:bg-gray-950 dark:text-gray-100">
  <h1 class="font-bold dark:text-white">Title</h1>
  <p class="text-gray-600 dark:text-gray-400">Body text adapts.</p>
</div>
<button onclick="document.documentElement.classList.toggle('dark')">
  <span class="dark:hidden">Dark</span><span class="hidden dark:inline">Light</span>
</button>
```

## Component Patterns

### Navbar

```jsx
<header class="sticky top-0 z-50 border-b bg-white/80 backdrop-blur dark:border-gray-800 dark:bg-gray-950/80">
  <nav class="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
    <a href="/" class="text-xl font-bold text-brand-600">Logo</a>
    <div class="hidden items-center gap-6 md:flex">
      <a href="/docs" class="text-sm hover:text-brand-600 dark:text-gray-300">Docs</a>
      <a href="/login" class="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700">Sign in</a>
    </div>
  </nav>
</header>
```

### Card

```jsx
<article class="group overflow-hidden rounded-xl border bg-white shadow-sm hover:shadow-md dark:border-gray-800 dark:bg-gray-900">
  <div class="aspect-video overflow-hidden">
    <img src="/img.jpg" alt="" class="h-full w-full object-cover transition-transform group-hover:scale-105" />
  </div>
  <div class="p-5">
    <span class="rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800">New</span>
    <h3 class="mt-3 text-lg font-semibold group-hover:text-brand-600">Card Title</h3>
    <p class="mt-2 line-clamp-2 text-sm text-gray-600 dark:text-gray-400">Description text.</p>
  </div>
</article>
```

### Form

```html
<form class="mx-auto max-w-md space-y-4">
  <div>
    <label for="email" class="block text-sm font-medium dark:text-gray-300">Email</label>
    <input id="email" type="email" placeholder="you@example.com"
      class="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm
             focus:border-brand-500 focus:ring-1 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white" />
  </div>
  <button type="submit" class="w-full rounded-lg bg-brand-600 px-4 py-2 font-medium text-white hover:bg-brand-700
    focus-visible:ring-2 focus-visible:ring-brand-600 focus-visible:ring-offset-2 disabled:opacity-50">Submit</button>
</form>
```

## Animations and Transitions

```html
<div class="animate-spin h-5 w-5 border-2 border-brand-600 border-t-transparent rounded-full"></div>
<div class="animate-pulse"><div class="h-4 w-3/4 rounded bg-gray-200 dark:bg-gray-700"></div></div>
<button class="rounded-lg bg-brand-600 px-4 py-2 text-white transition-all duration-200
               hover:scale-105 hover:shadow-lg active:scale-95">Click me</button>
<div class="animate-fade-in">Custom fade-in from @theme</div>
```

## Group and Peer Modifiers

```html
<!-- group: style children on parent hover -->
<a href="#" class="group flex items-center gap-3 rounded-lg p-3 hover:bg-gray-100">
  <span class="text-gray-500 group-hover:text-brand-600">Menu item</span>
</a>
<!-- peer: style sibling based on element state -->
<input type="checkbox" id="toggle" class="peer sr-only" />
<label for="toggle" class="cursor-pointer peer-checked:text-brand-600">Toggle</label>
<div class="hidden peer-checked:block text-sm">Visible when checked.</div>
```

## Arbitrary Values and Custom Properties

```html
<div class="top-[117px] grid grid-cols-[1fr_2fr_1fr] bg-[#1a1a2e]">One-off values</div>
<div class="[mask-image:linear-gradient(to_bottom,black,transparent)]">Arbitrary CSS property</div>
<div class="bg-[var(--ui-bg)] text-[var(--ui-text)]">CSS variable driven</div>
```

## Extracting Classes with @apply
```css
@layer components {
  .btn {
    @apply inline-flex items-center justify-center rounded-lg px-4 py-2 font-medium
           transition-colors focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50;
  }
  .btn-primary { @apply btn bg-brand-600 text-white hover:bg-brand-700; }
  .btn-secondary { @apply btn border border-gray-300 bg-white hover:bg-gray-50 dark:bg-gray-800; }
}
```

## Plugins

```css
@plugin "@tailwindcss/typography";  /* Official plugins via @plugin in v4 */
@plugin "@tailwindcss/forms";
```

```html
<article class="prose dark:prose-invert prose-a:text-brand-600 max-w-none">
  <p>Typography plugin styles rendered markdown beautifully.</p>
</article>
```

Custom plugin (`@plugin "./plugins/gradient-text.js"` in app.css):

```js
// plugins/gradient-text.js
import plugin from "tailwindcss/plugin";
export default plugin(({ addUtilities }) => {
  addUtilities({
    ".text-gradient": {
      "background-image": "linear-gradient(to right, var(--tw-gradient-stops))",
      "-webkit-background-clip": "text",
      "-webkit-text-fill-color": "transparent",
    },
  });
});
```

## Additional Resources

- Tailwind CSS Docs: https://tailwindcss.com/docs
- v4 Upgrade Guide: https://tailwindcss.com/docs/upgrade-guide
- Tailwind UI: https://tailwindui.com/
- Headless UI: https://headlessui.com/
- Tailwind Play: https://play.tailwindcss.com/
- Heroicons: https://heroicons.com/
