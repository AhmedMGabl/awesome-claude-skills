---
name: responsive-design
description: Responsive web design patterns covering mobile-first approach, CSS Grid and Flexbox layouts, container queries, fluid typography with clamp(), responsive images, breakpoint strategies, media queries, touch targets, viewport units, and cross-device testing best practices.
---

# Responsive Design

This skill should be used when building responsive layouts that work across all screen sizes. It covers mobile-first CSS, Grid/Flexbox, container queries, fluid typography, and cross-device patterns.

## When to Use This Skill

Use this skill when you need to:

- Build layouts that work on mobile through desktop
- Implement CSS Grid and Flexbox layouts
- Use container queries for component-level responsiveness
- Create fluid typography and spacing
- Optimize touch targets for mobile

## Mobile-First Breakpoints

```css
/* Tailwind-style breakpoints (mobile-first) */
/* Default: mobile (0px+) */
/* sm: 640px+ */
/* md: 768px+ */
/* lg: 1024px+ */
/* xl: 1280px+ */
/* 2xl: 1536px+ */

/* Mobile-first: start with mobile, add complexity */
.container {
  padding: 1rem;
  width: 100%;
}

@media (min-width: 768px) {
  .container { padding: 2rem; max-width: 768px; margin: 0 auto; }
}

@media (min-width: 1280px) {
  .container { max-width: 1200px; }
}
```

## CSS Grid Layouts

```css
/* Responsive grid — auto-fill columns */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

/* Dashboard layout */
.dashboard {
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: auto 1fr auto;
  min-height: 100dvh;
}

@media (min-width: 768px) {
  .dashboard {
    grid-template-columns: 240px 1fr;
    grid-template-rows: auto 1fr;
  }
  .sidebar { grid-row: 1 / -1; }
}

/* Holy grail layout */
.page {
  display: grid;
  grid-template: "header header header" auto
                 "nav    main   aside" 1fr
                 "footer footer footer" auto
                 / 200px 1fr 200px;
  min-height: 100dvh;
}

@media (max-width: 768px) {
  .page {
    grid-template: "header" auto
                   "nav" auto
                   "main" 1fr
                   "aside" auto
                   "footer" auto
                   / 1fr;
  }
}
```

## Fluid Typography

```css
/* clamp(min, preferred, max) */
:root {
  --font-xs:   clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem);
  --font-sm:   clamp(0.875rem, 0.8rem + 0.35vw, 1rem);
  --font-base: clamp(1rem, 0.9rem + 0.5vw, 1.125rem);
  --font-lg:   clamp(1.125rem, 1rem + 0.6vw, 1.25rem);
  --font-xl:   clamp(1.25rem, 1rem + 1.2vw, 1.875rem);
  --font-2xl:  clamp(1.5rem, 1rem + 2.5vw, 3rem);

  /* Fluid spacing */
  --space-sm:  clamp(0.5rem, 0.4rem + 0.5vw, 0.75rem);
  --space-md:  clamp(1rem, 0.8rem + 1vw, 1.5rem);
  --space-lg:  clamp(1.5rem, 1rem + 2.5vw, 3rem);
  --space-xl:  clamp(2rem, 1.5rem + 2.5vw, 4rem);
}

h1 { font-size: var(--font-2xl); }
body { font-size: var(--font-base); }
```

## Container Queries

```css
/* Component responds to its container, not viewport */
.card-container {
  container-type: inline-size;
  container-name: card;
}

.card {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* When container is wider than 400px */
@container card (min-width: 400px) {
  .card {
    flex-direction: row;
    align-items: center;
    gap: 1rem;
  }
  .card img { width: 120px; flex-shrink: 0; }
}

@container card (min-width: 600px) {
  .card { font-size: 1.125rem; }
}
```

## Touch Target Guidelines

```css
/* Minimum touch target: 44x44px (Apple) / 48x48px (Material) */
.btn, .link, input, select, textarea {
  min-height: 44px;
  min-width: 44px;
}

/* Adequate spacing between touch targets */
.nav-list a {
  display: block;
  padding: 12px 16px;
}

/* Larger hit areas for mobile */
@media (pointer: coarse) {
  .btn { min-height: 48px; padding: 12px 20px; }
}

/* Fine pointer (mouse) */
@media (pointer: fine) {
  .btn { min-height: 36px; padding: 8px 16px; }
}
```

## Responsive Patterns

```
PATTERN           DESCRIPTION
─────────────────────────────────────────────────────
Column Drop       Multi-column → stacked on mobile
Layout Shifter    Different layouts per breakpoint
Off Canvas        Sidebar hidden off-screen on mobile
Mostly Fluid      Fixed max-width, fluid margins
Tiny Tweaks       Same layout, minor adjustments

UNITS:
  rem     Relative to root font-size (accessible)
  dvh     Dynamic viewport height (accounts for mobile browser UI)
  svh     Small viewport height (mobile keyboard visible)
  lvh     Large viewport height (no mobile browser UI)
  cqw     Container query width unit
```

## Additional Resources

- CSS Grid: https://css-tricks.com/snippets/css/complete-guide-grid/
- Flexbox: https://css-tricks.com/snippets/css/a-guide-to-flexbox/
- Container Queries: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_containment/Container_queries
- Every Layout: https://every-layout.dev/
