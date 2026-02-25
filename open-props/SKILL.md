---
name: open-props
description: Open Props patterns covering CSS custom properties, adaptive design tokens, animations, gradients, shadows, responsive utilities, and PostCSS JIT integration.
---

# Open Props

This skill should be used when building UIs with Open Props CSS custom properties. It covers design tokens, adaptive colors, animations, gradients, shadows, and PostCSS JIT.

## When to Use This Skill

Use this skill when you need to:

- Use pre-built CSS custom properties for design consistency
- Apply adaptive color tokens (light/dark)
- Use animation and easing presets
- Implement responsive design with size tokens
- Optimize with PostCSS JIT (tree-shake unused props)

## Setup

```bash
npm install open-props
```

```css
/* Import all props */
@import "open-props/style";
@import "open-props/normalize";

/* Or individual modules */
@import "open-props/colors";
@import "open-props/sizes";
@import "open-props/animations";
```

## Colors

```css
.card {
  background: var(--surface-1);
  color: var(--text-1);
  border: 1px solid var(--surface-3);
}

.primary-btn {
  background: var(--blue-7);
  color: var(--gray-0);
}

.success {
  color: var(--green-7);
  background: var(--green-0);
  border: 1px solid var(--green-3);
}

.danger {
  color: var(--red-7);
  background: var(--red-0);
}
```

## Sizes and Spacing

```css
.container {
  max-width: var(--size-content-3); /* 60ch */
  margin-inline: auto;
  padding: var(--size-fluid-3);
}

.card {
  padding: var(--size-3); /* 1rem */
  border-radius: var(--radius-2);
  gap: var(--size-2);
}

h1 { font-size: var(--font-size-fluid-3); }
h2 { font-size: var(--font-size-fluid-2); }
p  { font-size: var(--font-size-fluid-1); }
```

## Animations

```css
.fade-in {
  animation: var(--animation-fade-in);
}

.slide-in {
  animation: var(--animation-slide-in-right);
}

.scale-up {
  animation: var(--animation-scale-up);
  animation-timing-function: var(--ease-spring-3);
}

.bounce {
  animation: var(--animation-bounce);
  animation-timing-function: var(--ease-squish-3);
}
```

## Shadows and Gradients

```css
.card-elevated {
  box-shadow: var(--shadow-3);
}

.card-hover:hover {
  box-shadow: var(--shadow-5);
  transition: box-shadow 0.2s var(--ease-3);
}

.gradient-bg {
  background: var(--gradient-1);
}

.noise-overlay {
  background: var(--noise-1);
}
```

## Adaptive (Dark Mode)

```css
/* Automatically adapts with prefers-color-scheme */
@import "open-props/colors";

/* These tokens change based on color scheme: */
.page {
  background: var(--surface-1); /* light: gray-1, dark: gray-9 */
  color: var(--text-1);         /* light: gray-9, dark: gray-1 */
}

/* Manual dark mode toggle */
[data-theme="dark"] {
  color-scheme: dark;
}
```

## PostCSS JIT (Tree-Shaking)

```javascript
// postcss.config.js
const OpenProps = require("open-props");
const jitProps = require("postcss-jit-props");

module.exports = {
  plugins: [
    jitProps(OpenProps),  // Only outputs used props
  ],
};
```

## Additional Resources

- Open Props: https://open-props.style/
- Docs: https://open-props.style/#getting-started
- Playground: https://codepen.io/argyleink/pen/KKvRORE
