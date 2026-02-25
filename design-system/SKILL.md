---
name: design-system
description: Design system and component library patterns covering design tokens, component APIs, variant systems (CVA/Tailwind Variants), accessibility, Storybook documentation, theming, responsive design, animation patterns, and building maintainable UI component libraries.
---

# Design System & Component Library

This skill should be used when building component libraries, establishing design tokens, or creating consistent UI systems. It covers tokens, component APIs, documentation, and theming.

## When to Use This Skill

Use this skill when you need to:

- Build a design system or component library
- Define design tokens (colors, spacing, typography)
- Create variant-based component APIs
- Set up Storybook for documentation
- Implement theming (light/dark mode)
- Build accessible, reusable components

## Design Tokens

```typescript
// tokens.ts — single source of truth
export const tokens = {
  colors: {
    // Semantic colors (use these in components)
    primary: { 50: "#eff6ff", 500: "#3b82f6", 600: "#2563eb", 700: "#1d4ed8" },
    neutral: { 50: "#fafafa", 100: "#f5f5f5", 200: "#e5e5e5", 700: "#404040", 900: "#171717" },
    success: { 500: "#22c55e", 600: "#16a34a" },
    error: { 500: "#ef4444", 600: "#dc2626" },
    warning: { 500: "#f59e0b", 600: "#d97706" },
  },
  spacing: {
    px: "1px", 0.5: "0.125rem", 1: "0.25rem", 2: "0.5rem",
    3: "0.75rem", 4: "1rem", 5: "1.25rem", 6: "1.5rem",
    8: "2rem", 10: "2.5rem", 12: "3rem", 16: "4rem",
  },
  fontSize: {
    xs: ["0.75rem", { lineHeight: "1rem" }],
    sm: ["0.875rem", { lineHeight: "1.25rem" }],
    base: ["1rem", { lineHeight: "1.5rem" }],
    lg: ["1.125rem", { lineHeight: "1.75rem" }],
    xl: ["1.25rem", { lineHeight: "1.75rem" }],
    "2xl": ["1.5rem", { lineHeight: "2rem" }],
  },
  radius: { sm: "0.25rem", md: "0.375rem", lg: "0.5rem", xl: "0.75rem", full: "9999px" },
  shadow: {
    sm: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
    md: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
    lg: "0 10px 15px -3px rgb(0 0 0 / 0.1)",
  },
} as const;
```

## Component Variants with CVA

```typescript
// button.tsx — using class-variance-authority
import { cva, type VariantProps } from "class-variance-authority";
import { forwardRef, type ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  // Base styles
  "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        primary: "bg-primary-600 text-white hover:bg-primary-700 focus-visible:ring-primary-500",
        secondary: "bg-neutral-100 text-neutral-900 hover:bg-neutral-200 focus-visible:ring-neutral-500",
        outline: "border border-neutral-200 bg-transparent hover:bg-neutral-100 focus-visible:ring-neutral-500",
        ghost: "hover:bg-neutral-100 focus-visible:ring-neutral-500",
        destructive: "bg-error-600 text-white hover:bg-error-700 focus-visible:ring-error-500",
        link: "text-primary-600 underline-offset-4 hover:underline p-0 h-auto",
      },
      size: {
        sm: "h-8 px-3 text-sm",
        md: "h-10 px-4 text-sm",
        lg: "h-12 px-6 text-base",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  },
);

interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  loading?: boolean;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, loading, children, disabled, ...props }, ref) => (
    <button
      ref={ref}
      className={cn(buttonVariants({ variant, size, className }))}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <Spinner className="mr-2 h-4 w-4 animate-spin" />}
      {children}
    </button>
  ),
);
Button.displayName = "Button";

export { Button, buttonVariants };
```

## Accessible Form Components

```typescript
// input.tsx
import { forwardRef, type InputHTMLAttributes } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  hint?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, id, className, ...props }, ref) => {
    const inputId = id ?? label.toLowerCase().replace(/\s+/g, "-");
    const errorId = `${inputId}-error`;
    const hintId = `${inputId}-hint`;

    return (
      <div className="space-y-1.5">
        <label htmlFor={inputId} className="text-sm font-medium text-neutral-700">
          {label}
          {props.required && <span className="text-error-500 ml-0.5">*</span>}
        </label>
        <input
          ref={ref}
          id={inputId}
          className={cn(
            "w-full rounded-md border px-3 py-2 text-sm transition-colors",
            "focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500",
            error ? "border-error-500 focus:ring-error-500" : "border-neutral-200",
            className,
          )}
          aria-invalid={!!error}
          aria-describedby={[error && errorId, hint && hintId].filter(Boolean).join(" ") || undefined}
          {...props}
        />
        {hint && !error && (
          <p id={hintId} className="text-xs text-neutral-500">{hint}</p>
        )}
        {error && (
          <p id={errorId} role="alert" className="text-xs text-error-600">{error}</p>
        )}
      </div>
    );
  },
);
```

## Theming (Dark Mode)

```typescript
// theme-provider.tsx
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

type Theme = "light" | "dark" | "system";

const ThemeContext = createContext<{
  theme: Theme;
  setTheme: (theme: Theme) => void;
}>({ theme: "system", setTheme: () => {} });

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() => {
    if (typeof window === "undefined") return "system";
    return (localStorage.getItem("theme") as Theme) ?? "system";
  });

  useEffect(() => {
    const root = document.documentElement;
    const systemDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const isDark = theme === "dark" || (theme === "system" && systemDark);
    root.classList.toggle("dark", isDark);
    localStorage.setItem("theme", theme);
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export const useTheme = () => useContext(ThemeContext);
```

## Storybook Stories

```typescript
// button.stories.tsx
import type { Meta, StoryObj } from "@storybook/react";
import { Button } from "./button";

const meta: Meta<typeof Button> = {
  title: "Components/Button",
  component: Button,
  argTypes: {
    variant: { control: "select", options: ["primary", "secondary", "outline", "ghost", "destructive"] },
    size: { control: "select", options: ["sm", "md", "lg", "icon"] },
    loading: { control: "boolean" },
    disabled: { control: "boolean" },
  },
  tags: ["autodocs"],
};
export default meta;

type Story = StoryObj<typeof Button>;

export const Primary: Story = { args: { children: "Button", variant: "primary" } };
export const Secondary: Story = { args: { children: "Button", variant: "secondary" } };
export const Outline: Story = { args: { children: "Button", variant: "outline" } };
export const Loading: Story = { args: { children: "Saving...", loading: true } };
export const Disabled: Story = { args: { children: "Button", disabled: true } };

export const AllVariants: Story = {
  render: () => (
    <div className="flex gap-4">
      <Button variant="primary">Primary</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="outline">Outline</Button>
      <Button variant="ghost">Ghost</Button>
      <Button variant="destructive">Delete</Button>
    </div>
  ),
};
```

## cn Utility

```typescript
// lib/utils.ts
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

## Additional Resources

- Storybook: https://storybook.js.org/
- CVA: https://cva.style/docs
- Radix UI (primitives): https://www.radix-ui.com/
- shadcn/ui: https://ui.shadcn.com/
