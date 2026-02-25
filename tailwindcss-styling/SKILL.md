---
name: tailwindcss-styling
description: Tailwind CSS styling covering utility-first workflow, responsive design, dark mode, custom themes, component patterns, animations, plugin creation, and production optimization for modern web applications.
---

# Tailwind CSS Styling

This skill should be used when styling web applications with Tailwind CSS. It covers the utility-first workflow, responsive design, dark mode, theming, component patterns, animations, and performance optimization.

## When to Use This Skill

Use this skill when you need to:

- Style components with Tailwind utility classes
- Implement responsive layouts and dark mode
- Create custom design systems and themes
- Build reusable component patterns
- Add animations and transitions
- Optimize Tailwind for production builds
- Create custom plugins and utilities

## Project Setup

### Installation

```bash
# Vite + React/Vue
npm install -D tailwindcss @tailwindcss/vite
# or Next.js (built-in support)
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### tailwind.config.ts

```typescript
import type { Config } from "tailwindcss";
import defaultTheme from "tailwindcss/defaultTheme";

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",  // or "media" for system preference
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eff6ff",
          100: "#dbeafe",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
          900: "#1e3a5f",
        },
      },
      fontFamily: {
        sans: ["Inter", ...defaultTheme.fontFamily.sans],
        mono: ["JetBrains Mono", ...defaultTheme.fontFamily.mono],
      },
      spacing: {
        "18": "4.5rem",
        "128": "32rem",
      },
      animation: {
        "fade-in": "fadeIn 0.3s ease-out",
        "slide-up": "slideUp 0.3s ease-out",
        "spin-slow": "spin 3s linear infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [
    require("@tailwindcss/forms"),
    require("@tailwindcss/typography"),
    require("@tailwindcss/aspect-ratio"),
  ],
} satisfies Config;
```

### Base Styles

```css
/* src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  html {
    @apply scroll-smooth antialiased;
  }
  body {
    @apply bg-white text-gray-900 dark:bg-gray-950 dark:text-gray-100;
  }
}

@layer components {
  .btn {
    @apply inline-flex items-center justify-center rounded-lg px-4 py-2
           font-medium transition-colors focus-visible:outline-none
           focus-visible:ring-2 focus-visible:ring-offset-2
           disabled:pointer-events-none disabled:opacity-50;
  }
  .btn-primary {
    @apply btn bg-brand-600 text-white hover:bg-brand-700
           focus-visible:ring-brand-600;
  }
  .btn-secondary {
    @apply btn border border-gray-300 bg-white text-gray-700
           hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-800
           dark:text-gray-200 dark:hover:bg-gray-700;
  }
}
```

## Layout Patterns

### Responsive Grid

```html
<!-- Responsive card grid -->
<div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
  <div class="rounded-xl border bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
    <h3 class="text-lg font-semibold">Card Title</h3>
    <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">Description text</p>
  </div>
</div>

<!-- Sidebar layout -->
<div class="flex min-h-screen">
  <aside class="hidden w-64 shrink-0 border-r bg-gray-50 p-4 lg:block dark:border-gray-800 dark:bg-gray-900">
    <!-- Sidebar content -->
  </aside>
  <main class="flex-1 p-6">
    <!-- Main content -->
  </main>
</div>

<!-- Sticky header + scrollable content -->
<div class="flex h-screen flex-col">
  <header class="sticky top-0 z-50 border-b bg-white/80 px-6 py-3 backdrop-blur dark:border-gray-800 dark:bg-gray-950/80">
    <nav class="flex items-center justify-between">
      <span class="text-xl font-bold">Logo</span>
      <div class="flex items-center gap-4">
        <a href="#" class="text-sm hover:text-brand-600">Link</a>
      </div>
    </nav>
  </header>
  <main class="flex-1 overflow-y-auto p-6">
    <!-- Scrollable content -->
  </main>
</div>

<!-- Centered content with max-width -->
<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
  <!-- Constrained content -->
</div>
```

### Flexbox Patterns

```html
<!-- Space between with wrap -->
<div class="flex flex-wrap items-center justify-between gap-4">
  <h1 class="text-2xl font-bold">Title</h1>
  <div class="flex gap-2">
    <button class="btn-secondary">Cancel</button>
    <button class="btn-primary">Save</button>
  </div>
</div>

<!-- Vertical stack with gap -->
<div class="flex flex-col gap-4">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
</div>

<!-- Center both axes -->
<div class="flex min-h-[400px] items-center justify-center">
  <div class="text-center">Centered content</div>
</div>
```

## Component Patterns

### Form Elements

```html
<!-- Input with label and error -->
<div>
  <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
    Email
  </label>
  <input
    id="email"
    type="email"
    class="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2
           shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1
           focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800
           dark:text-white"
    placeholder="you@example.com"
  />
  <p class="mt-1 text-sm text-red-600">Please enter a valid email</p>
</div>

<!-- Select -->
<select class="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2
               focus:border-brand-500 focus:ring-brand-500 dark:border-gray-600
               dark:bg-gray-800 dark:text-white">
  <option>Option 1</option>
  <option>Option 2</option>
</select>

<!-- Toggle switch -->
<button
  role="switch"
  aria-checked="true"
  class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full
         border-2 border-transparent bg-brand-600 transition-colors
         focus-visible:outline-none focus-visible:ring-2
         focus-visible:ring-brand-600 focus-visible:ring-offset-2"
>
  <span class="pointer-events-none inline-block h-5 w-5 translate-x-5
               rounded-full bg-white shadow ring-0 transition-transform" />
</button>
```

### Cards and Badges

```html
<!-- Card with image -->
<article class="group overflow-hidden rounded-xl border bg-white shadow-sm
                transition-shadow hover:shadow-md dark:border-gray-800 dark:bg-gray-900">
  <div class="aspect-video overflow-hidden">
    <img src="..." alt="..." class="h-full w-full object-cover transition-transform
         group-hover:scale-105" />
  </div>
  <div class="p-5">
    <div class="flex items-center gap-2">
      <span class="rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium
                   text-green-800 dark:bg-green-900 dark:text-green-200">
        Published
      </span>
      <time class="text-xs text-gray-500">Mar 15, 2024</time>
    </div>
    <h3 class="mt-3 text-lg font-semibold leading-tight group-hover:text-brand-600">
      Article Title
    </h3>
    <p class="mt-2 line-clamp-2 text-sm text-gray-600 dark:text-gray-400">
      Description that gets truncated after two lines of text...
    </p>
  </div>
</article>

<!-- Badge variants -->
<span class="rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800">Info</span>
<span class="rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800">Success</span>
<span class="rounded-full bg-yellow-100 px-2.5 py-0.5 text-xs font-medium text-yellow-800">Warning</span>
<span class="rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-800">Error</span>
```

### Modal / Dialog

```html
<!-- Modal overlay + panel -->
<div class="fixed inset-0 z-50 flex items-center justify-center p-4">
  <!-- Backdrop -->
  <div class="fixed inset-0 bg-black/50 backdrop-blur-sm" aria-hidden="true"></div>

  <!-- Panel -->
  <div class="relative w-full max-w-md rounded-xl bg-white p-6 shadow-xl
              animate-fade-in dark:bg-gray-900">
    <h2 class="text-lg font-semibold">Confirm Action</h2>
    <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
      Are you sure you want to proceed?
    </p>
    <div class="mt-6 flex justify-end gap-3">
      <button class="btn-secondary">Cancel</button>
      <button class="btn-primary">Confirm</button>
    </div>
  </div>
</div>
```

## Dark Mode

```html
<!-- Toggle dark mode with class strategy -->
<button onclick="document.documentElement.classList.toggle('dark')">
  <!-- Sun icon (shown in dark mode) -->
  <svg class="hidden h-5 w-5 dark:block">...</svg>
  <!-- Moon icon (shown in light mode) -->
  <svg class="block h-5 w-5 dark:hidden">...</svg>
</button>

<!-- Dark mode patterns -->
<div class="bg-white dark:bg-gray-900">
  <h1 class="text-gray-900 dark:text-white">Title</h1>
  <p class="text-gray-600 dark:text-gray-400">Body text</p>
  <div class="border border-gray-200 dark:border-gray-700">
    <span class="text-gray-500 dark:text-gray-500">Muted text</span>
  </div>
</div>
```

## Responsive Design

```html
<!-- Breakpoint reference:
  sm: 640px    md: 768px    lg: 1024px    xl: 1280px    2xl: 1536px
-->

<!-- Mobile-first responsive -->
<div class="text-sm md:text-base lg:text-lg">Responsive text</div>

<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <!-- Cards -->
</div>

<!-- Hide/show at breakpoints -->
<nav class="hidden md:flex">Desktop nav</nav>
<button class="md:hidden">Mobile menu toggle</button>

<!-- Responsive padding -->
<section class="px-4 py-8 sm:px-6 sm:py-12 lg:px-8 lg:py-16">
  Content
</section>

<!-- Container queries (Tailwind v3.4+) -->
<div class="@container">
  <div class="@sm:flex @sm:items-center @lg:grid @lg:grid-cols-2">
    Content adapts to container, not viewport
  </div>
</div>
```

## Animations

```html
<!-- Built-in animations -->
<div class="animate-spin">Loading spinner</div>
<div class="animate-pulse">Skeleton loader</div>
<div class="animate-bounce">Bouncing arrow</div>

<!-- Transitions -->
<button class="transform transition-all duration-200 hover:scale-105 hover:shadow-lg
               active:scale-95">
  Click me
</button>

<!-- Skeleton loader pattern -->
<div class="animate-pulse space-y-4">
  <div class="h-4 w-3/4 rounded bg-gray-200 dark:bg-gray-700"></div>
  <div class="h-4 w-1/2 rounded bg-gray-200 dark:bg-gray-700"></div>
  <div class="flex items-center gap-4">
    <div class="h-12 w-12 rounded-full bg-gray-200 dark:bg-gray-700"></div>
    <div class="flex-1 space-y-2">
      <div class="h-4 rounded bg-gray-200 dark:bg-gray-700"></div>
      <div class="h-4 w-5/6 rounded bg-gray-200 dark:bg-gray-700"></div>
    </div>
  </div>
</div>

<!-- Staggered animation with custom delay -->
<div class="space-y-2">
  <div class="animate-fade-in" style="animation-delay: 0ms">Item 1</div>
  <div class="animate-fade-in" style="animation-delay: 100ms">Item 2</div>
  <div class="animate-fade-in" style="animation-delay: 200ms">Item 3</div>
</div>
```

## Typography Plugin

```html
<!-- @tailwindcss/typography for rich content -->
<article class="prose prose-lg dark:prose-invert max-w-none
                prose-headings:font-bold prose-a:text-brand-600
                prose-img:rounded-xl prose-pre:bg-gray-900">
  <!-- Markdown/HTML content rendered beautifully -->
  <h1>Article Title</h1>
  <p>Body text with <a href="#">links</a> styled automatically.</p>
  <pre><code>Code blocks too</code></pre>
</article>
```

## Production Tips

```bash
# Tailwind v4 uses Vite plugin (automatic optimization)
# Tailwind v3 uses PostCSS (needs content paths in config)

# Check bundle size
npx tailwindcss --minify -i src/index.css -o dist/output.css
```

### Class organization (recommended order):

```
Layout → Box model → Typography → Visual → Misc
```

```html
<!-- Good ordering -->
<div class="flex items-center gap-4 rounded-lg border bg-white px-4 py-3
            text-sm font-medium text-gray-900 shadow-sm transition-colors
            hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800
            dark:text-gray-100">
```

## Additional Resources

- Tailwind CSS: https://tailwindcss.com/docs
- Tailwind UI: https://tailwindui.com/
- Headless UI: https://headlessui.com/
- Tailwind Play: https://play.tailwindcss.com/
- heroicons: https://heroicons.com/
