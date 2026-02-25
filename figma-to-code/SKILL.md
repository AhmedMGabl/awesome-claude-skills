---
name: figma-to-code
description: Figma-to-code translation patterns covering design token extraction, component mapping to React/Tailwind, responsive layout conversion, auto-layout to flexbox/grid mapping, color and typography system generation, variant-to-prop mapping, and pixel-perfect implementation strategies.
---

# Figma to Code

This skill should be used when translating Figma designs into production code. It covers design token extraction, component mapping, layout conversion, and implementation strategies.

## When to Use This Skill

Use this skill when you need to:

- Convert Figma designs to React/HTML/CSS
- Extract design tokens from Figma
- Map Figma auto-layout to flexbox/grid
- Translate Figma variants to component props
- Build responsive layouts from design mockups
- Create a design system from Figma files

## Design Token Extraction

```typescript
// tokens/colors.ts — Extract from Figma color styles
export const colors = {
  // Brand
  brand: {
    50:  "#EEF2FF",
    100: "#E0E7FF",
    500: "#6366F1",
    600: "#4F46E5",
    700: "#4338CA",
    900: "#312E81",
  },
  // Semantic
  text: {
    primary:   "var(--color-gray-900)",
    secondary: "var(--color-gray-600)",
    muted:     "var(--color-gray-400)",
    inverse:   "var(--color-white)",
  },
  bg: {
    primary:   "var(--color-white)",
    secondary: "var(--color-gray-50)",
    tertiary:  "var(--color-gray-100)",
  },
} as const;

// tokens/typography.ts
export const typography = {
  // Figma text styles → CSS
  "heading-xl": { fontSize: "2.25rem", lineHeight: 1.2, fontWeight: 700, letterSpacing: "-0.02em" },
  "heading-lg": { fontSize: "1.875rem", lineHeight: 1.3, fontWeight: 700, letterSpacing: "-0.01em" },
  "heading-md": { fontSize: "1.5rem", lineHeight: 1.4, fontWeight: 600 },
  "body-lg":    { fontSize: "1.125rem", lineHeight: 1.6, fontWeight: 400 },
  "body-md":    { fontSize: "1rem", lineHeight: 1.5, fontWeight: 400 },
  "body-sm":    { fontSize: "0.875rem", lineHeight: 1.5, fontWeight: 400 },
  "caption":    { fontSize: "0.75rem", lineHeight: 1.4, fontWeight: 500 },
} as const;

// tokens/spacing.ts — Figma uses 4px/8px grid
export const spacing = {
  0: "0",
  1: "0.25rem",   // 4px
  2: "0.5rem",    // 8px
  3: "0.75rem",   // 12px
  4: "1rem",      // 16px
  5: "1.25rem",   // 20px
  6: "1.5rem",    // 24px
  8: "2rem",      // 32px
  10: "2.5rem",   // 40px
  12: "3rem",     // 48px
  16: "4rem",     // 64px
} as const;
```

## Auto-Layout to Flexbox/Grid

```
FIGMA AUTO-LAYOUT          →   CSS EQUIVALENT
─────────────────────────────────────────────────
Direction: Horizontal      →   display: flex; flex-direction: row;
Direction: Vertical        →   display: flex; flex-direction: column;

Spacing: 16               →   gap: 1rem;

Padding: 24               →   padding: 1.5rem;
Padding: 16, 24           →   padding: 1rem 1.5rem; (vertical, horizontal)

Alignment: Top Left       →   align-items: flex-start; justify-content: flex-start;
Alignment: Center         →   align-items: center; justify-content: center;
Alignment: Space Between  →   justify-content: space-between;

Fill container (width)    →   flex: 1; or width: 100%;
Hug contents              →   width: fit-content;
Fixed width               →   width: Xpx;

Wrap                      →   flex-wrap: wrap;
```

```tsx
// Figma frame with auto-layout → React component
function CardGrid({ items }: { items: CardItem[] }) {
  return (
    // Figma: Auto-layout, Horizontal, Wrap, Gap 24, Padding 32
    <div className="flex flex-wrap gap-6 p-8">
      {items.map((item) => (
        // Figma: Fixed width 320, Vertical auto-layout, Gap 16, Padding 24
        <div key={item.id} className="w-80 flex flex-col gap-4 p-6 rounded-xl border bg-white shadow-sm">
          {/* Figma: Fill container width, Fixed height 180 */}
          <img src={item.image} className="w-full h-[180px] object-cover rounded-lg" alt={item.title} />
          {/* Figma: Vertical, Gap 8 */}
          <div className="flex flex-col gap-2">
            <h3 className="text-lg font-semibold text-gray-900">{item.title}</h3>
            <p className="text-sm text-gray-600 line-clamp-2">{item.description}</p>
          </div>
          {/* Figma: Horizontal, Space between, Align center */}
          <div className="flex items-center justify-between mt-auto">
            <span className="text-xl font-bold text-brand-600">${item.price}</span>
            <button className="px-4 py-2 bg-brand-600 text-white rounded-lg text-sm font-medium hover:bg-brand-700">
              Add to Cart
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
```

## Figma Variants to Component Props

```tsx
// Figma component with variants:
//   Size: sm, md, lg
//   Variant: primary, secondary, outline, ghost
//   State: default, hover, disabled
//   Icon: none, left, right

import { cva, type VariantProps } from "class-variance-authority";

const buttonVariants = cva(
  "inline-flex items-center justify-center font-medium rounded-lg transition-colors focus-visible:outline-none focus-visible:ring-2",
  {
    variants: {
      variant: {
        primary:   "bg-brand-600 text-white hover:bg-brand-700",
        secondary: "bg-gray-100 text-gray-900 hover:bg-gray-200",
        outline:   "border border-gray-300 bg-white text-gray-700 hover:bg-gray-50",
        ghost:     "text-gray-700 hover:bg-gray-100",
      },
      size: {
        sm: "h-8 px-3 text-sm gap-1.5",
        md: "h-10 px-4 text-sm gap-2",
        lg: "h-12 px-6 text-base gap-2.5",
      },
    },
    defaultVariants: { variant: "primary", size: "md" },
  },
);

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> &
  VariantProps<typeof buttonVariants> & {
    leftIcon?: React.ReactNode;
    rightIcon?: React.ReactNode;
  };

function Button({ variant, size, leftIcon, rightIcon, children, ...props }: ButtonProps) {
  return (
    <button className={buttonVariants({ variant, size })} {...props}>
      {leftIcon}
      {children}
      {rightIcon}
    </button>
  );
}
```

## Responsive Breakpoint Mapping

```
FIGMA FRAMES              →   TAILWIND BREAKPOINTS
─────────────────────────────────────────────────
Mobile (375px)            →   default (mobile-first)
Tablet (768px)            →   md:
Desktop (1280px)          →   lg: or xl:
Wide (1440px)             →   2xl:

FIGMA CONSTRAINTS         →   CSS RESPONSIVE
─────────────────────────────────────────────────
Left & Right (stretch)    →   w-full
Center                    →   mx-auto
Scale                     →   max-w-7xl w-full px-4
```

```tsx
// Responsive layout from Figma frames
function HeroSection() {
  return (
    // Mobile: stack, Tablet: side-by-side
    <section className="px-4 py-12 md:py-20 lg:py-28 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center gap-8 md:gap-12 lg:gap-16">
        {/* Text — Mobile: full width, Desktop: 50% */}
        <div className="md:w-1/2 flex flex-col gap-4 md:gap-6">
          <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900">
            Hero Headline
          </h1>
          <p className="text-base md:text-lg text-gray-600">
            Supporting text from the Figma design.
          </p>
          <div className="flex flex-col sm:flex-row gap-3">
            <Button size="lg">Get Started</Button>
            <Button size="lg" variant="outline">Learn More</Button>
          </div>
        </div>
        {/* Image — Mobile: full width, Desktop: 50% */}
        <div className="md:w-1/2">
          <img src="/hero.png" className="w-full rounded-2xl" alt="Hero" />
        </div>
      </div>
    </section>
  );
}
```

## Additional Resources

- Figma Dev Mode: https://www.figma.com/dev-mode/
- Tailwind CSS: https://tailwindcss.com/docs
- CVA (Class Variance Authority): https://cva.style/docs
- Style Dictionary (design tokens): https://amzn.github.io/style-dictionary/
