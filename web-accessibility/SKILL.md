---
name: web-accessibility
description: Web accessibility (a11y) covering WCAG 2.2 compliance, ARIA attributes, keyboard navigation, screen reader optimization, focus management, color contrast, semantic HTML, and automated testing with axe-core and Playwright.
---

# Web Accessibility (a11y)

This skill should be used when implementing accessible web interfaces. It covers WCAG guidelines, ARIA patterns, keyboard navigation, screen readers, focus management, and automated accessibility testing.

## When to Use This Skill

Use this skill when you need to:

- Build WCAG 2.2 AA compliant interfaces
- Implement keyboard-navigable components
- Add ARIA attributes for screen reader support
- Create accessible forms, modals, and navigation
- Set up automated accessibility testing

## Semantic HTML First

```html
<!-- BAD — div soup -->
<div class="header">
  <div class="nav">
    <div class="link" onclick="navigate()">Home</div>
  </div>
</div>

<!-- GOOD — semantic elements -->
<header>
  <nav aria-label="Main navigation">
    <a href="/">Home</a>
  </nav>
</header>
<main>
  <article>
    <h1>Page Title</h1>
    <section aria-labelledby="section-heading">
      <h2 id="section-heading">Section</h2>
    </section>
  </article>
</main>
<footer>...</footer>
```

## ARIA Patterns

```tsx
// Accessible modal dialog
function Modal({ open, onClose, title, children }: ModalProps) {
  const titleId = useId();

  useEffect(() => {
    if (open) {
      document.body.style.overflow = "hidden";
      return () => { document.body.style.overflow = ""; };
    }
  }, [open]);

  if (!open) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby={titleId}
      className="fixed inset-0 z-50 flex items-center justify-center"
    >
      <div className="fixed inset-0 bg-black/50" aria-hidden="true" onClick={onClose} />
      <div className="relative bg-white rounded-lg p-6 max-w-md w-full">
        <h2 id={titleId}>{title}</h2>
        {children}
        <button onClick={onClose} aria-label="Close dialog">
          <XIcon aria-hidden="true" />
        </button>
      </div>
    </div>
  );
}

// Accessible tabs
function Tabs({ tabs }: { tabs: Tab[] }) {
  const [activeIndex, setActiveIndex] = useState(0);

  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    if (e.key === "ArrowRight") setActiveIndex((index + 1) % tabs.length);
    if (e.key === "ArrowLeft") setActiveIndex((index - 1 + tabs.length) % tabs.length);
    if (e.key === "Home") setActiveIndex(0);
    if (e.key === "End") setActiveIndex(tabs.length - 1);
  };

  return (
    <div>
      <div role="tablist" aria-label="Content tabs">
        {tabs.map((tab, i) => (
          <button
            key={tab.id}
            role="tab"
            id={`tab-${tab.id}`}
            aria-selected={i === activeIndex}
            aria-controls={`panel-${tab.id}`}
            tabIndex={i === activeIndex ? 0 : -1}
            onClick={() => setActiveIndex(i)}
            onKeyDown={(e) => handleKeyDown(e, i)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      {tabs.map((tab, i) => (
        <div
          key={tab.id}
          role="tabpanel"
          id={`panel-${tab.id}`}
          aria-labelledby={`tab-${tab.id}`}
          hidden={i !== activeIndex}
          tabIndex={0}
        >
          {tab.content}
        </div>
      ))}
    </div>
  );
}
```

## Accessible Forms

```tsx
function ContactForm() {
  const [errors, setErrors] = useState<Record<string, string>>({});

  return (
    <form aria-label="Contact form" noValidate onSubmit={handleSubmit}>
      {Object.keys(errors).length > 0 && (
        <div role="alert" aria-live="assertive" className="text-red-600">
          <p>Please fix the following errors:</p>
          <ul>
            {Object.entries(errors).map(([field, msg]) => (
              <li key={field}>
                <a href={`#${field}`}>{msg}</a>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div>
        <label htmlFor="name">
          Name <span aria-hidden="true">*</span>
          <span className="sr-only">(required)</span>
        </label>
        <input
          id="name"
          name="name"
          required
          aria-required="true"
          aria-invalid={!!errors.name}
          aria-describedby={errors.name ? "name-error" : undefined}
        />
        {errors.name && (
          <p id="name-error" role="alert" className="text-red-600">
            {errors.name}
          </p>
        )}
      </div>

      <fieldset>
        <legend>Preferred contact method</legend>
        <label>
          <input type="radio" name="contact" value="email" /> Email
        </label>
        <label>
          <input type="radio" name="contact" value="phone" /> Phone
        </label>
      </fieldset>

      <button type="submit">Send Message</button>
    </form>
  );
}
```

## Focus Management

```typescript
// Focus trap for modals
function useFocusTrap(ref: React.RefObject<HTMLElement>, active: boolean) {
  useEffect(() => {
    if (!active || !ref.current) return;

    const element = ref.current;
    const focusable = element.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
    );
    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    first?.focus();

    const handler = (e: KeyboardEvent) => {
      if (e.key !== "Tab") return;
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last?.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first?.focus();
      }
    };

    element.addEventListener("keydown", handler);
    return () => element.removeEventListener("keydown", handler);
  }, [ref, active]);
}

// Skip to main content link
function SkipLink() {
  return (
    <a
      href="#main-content"
      className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-50 focus:px-4 focus:py-2 focus:bg-white focus:text-black"
    >
      Skip to main content
    </a>
  );
}
```

## Automated Testing with axe-core

```typescript
// Playwright accessibility test
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("homepage has no accessibility violations", async ({ page }) => {
  await page.goto("/");
  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag22aa"])
    .analyze();
  expect(results.violations).toEqual([]);
});

// Jest + Testing Library
import { render } from "@testing-library/react";
import { axe, toHaveNoViolations } from "jest-axe";

expect.extend(toHaveNoViolations);

test("form is accessible", async () => {
  const { container } = render(<ContactForm />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

## Screen Reader Utilities

```css
/* Visually hidden but accessible to screen readers */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

.sr-only:focus {
  position: static;
  width: auto;
  height: auto;
  padding: inherit;
  margin: inherit;
  overflow: visible;
  clip: auto;
  white-space: normal;
}
```

## WCAG Quick Reference

```
LEVEL A (Minimum)                    LEVEL AA (Standard Target)
───────────────────────────────────────────────────────────────
Non-text content has alt text        Color contrast ≥ 4.5:1 (text)
Keyboard accessible                  Color contrast ≥ 3:1 (large text)
No keyboard traps                    Text resizable to 200%
Page has title                       Consistent navigation
Link purpose is clear                Error identification
Language declared                    Labels or instructions
Focus order is meaningful            Focus visible
```

## Additional Resources

- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- WAI-ARIA Practices: https://www.w3.org/WAI/ARIA/apg/
- axe-core: https://github.com/dequelabs/axe-core
