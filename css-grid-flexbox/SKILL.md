---
name: css-grid-flexbox
description: CSS Grid and Flexbox layout mastery covering grid template areas, auto-fill and auto-fit, subgrid, flexbox alignment, responsive layouts without media queries, container queries, named grid lines, aspect-ratio, and common layout patterns.
---

# CSS Grid & Flexbox

This skill should be used when building responsive layouts with CSS Grid and Flexbox. It covers grid templates, flexbox alignment, container queries, and common layout patterns.

## When to Use This Skill

Use this skill when you need to:

- Build responsive page layouts with Grid
- Create flexible component layouts with Flexbox
- Implement container queries for component-level responsiveness
- Use modern CSS features (subgrid, aspect-ratio, gap)
- Choose between Grid and Flexbox for a given layout

## CSS Grid — Page Layout

```css
.dashboard {
  display: grid;
  grid-template-columns: 250px 1fr;
  grid-template-rows: 60px 1fr auto;
  grid-template-areas:
    "sidebar header"
    "sidebar main"
    "sidebar footer";
  min-height: 100dvh;
}

.header  { grid-area: header; }
.sidebar { grid-area: sidebar; }
.main    { grid-area: main; }
.footer  { grid-area: footer; }

@media (max-width: 768px) {
  .dashboard {
    grid-template-columns: 1fr;
    grid-template-areas:
      "header"
      "main"
      "footer";
  }
  .sidebar { display: none; }
}
```

## Auto-Responsive Grid (No Media Queries)

```css
/* Cards that auto-wrap based on available space */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

/* auto-fill vs auto-fit:
   auto-fill: keeps empty tracks (columns)
   auto-fit: collapses empty tracks (columns stretch to fill) */
.stretch-grid {
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}
```

## Subgrid

```css
/* Parent grid */
.card-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

/* Cards align internal elements across the grid */
.card {
  display: grid;
  grid-template-rows: subgrid;
  grid-row: span 3;  /* header, body, footer */
}
```

## Flexbox — Component Layout

```css
/* Navigation bar */
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1rem;
  height: 60px;
}

.navbar-links {
  display: flex;
  gap: 1rem;
}

/* Center anything */
.center {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Push last item to the right */
.toolbar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.toolbar .spacer { margin-left: auto; }

/* Equal height cards */
.row {
  display: flex;
  gap: 1rem;
}
.row > * {
  flex: 1;
  min-width: 0;  /* prevent overflow */
}
```

## Container Queries

```css
/* Define a container */
.card-container {
  container-type: inline-size;
  container-name: card;
}

/* Respond to container width (not viewport) */
@container card (min-width: 400px) {
  .card {
    display: grid;
    grid-template-columns: 200px 1fr;
  }
}

@container card (max-width: 399px) {
  .card {
    display: flex;
    flex-direction: column;
  }
}
```

## Common Patterns

```css
/* Sticky footer */
body {
  display: grid;
  grid-template-rows: auto 1fr auto;
  min-height: 100dvh;
}

/* Holy grail layout */
.layout {
  display: grid;
  grid-template: "header header header" auto
                 "nav    main   aside"  1fr
                 "footer footer footer" auto
               / 200px  1fr    250px;
}

/* Aspect ratio (modern) */
.thumbnail {
  aspect-ratio: 16 / 9;
  object-fit: cover;
}
```

## Grid vs Flexbox Decision

```
USE CASE                    GRID              FLEXBOX
──────────────────────────────────────────────────────
Page layout                 Yes               No
Card grids                  Yes               Maybe
Navigation bar              No                Yes
Centering                   Either            Either
Unknown number of items     auto-fill         wrap
Two-dimensional             Yes               No
One-dimensional             Overkill          Yes
Alignment across rows       subgrid           No
```

## Additional Resources

- CSS Grid: https://css-tricks.com/snippets/css/complete-guide-grid/
- Flexbox: https://css-tricks.com/snippets/css/a-guide-to-flexbox/
- Container queries: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_containment/Container_queries
