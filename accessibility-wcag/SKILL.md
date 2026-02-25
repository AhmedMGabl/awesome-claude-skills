---
name: accessibility-wcag
description: Web accessibility and WCAG compliance covering semantic HTML, ARIA attributes, keyboard navigation, screen reader compatibility, color contrast, focus management, accessible forms, testing with axe-core and Lighthouse, and inclusive design patterns.
---

# Accessibility & WCAG Compliance

This skill should be used when building, auditing, or fixing web applications for accessibility and WCAG compliance. It covers the WCAG 2.2 success criteria, semantic HTML, ARIA, keyboard interaction, color contrast, accessible components, automated testing, and React-specific patterns.

## When to Use This Skill

- Audit an existing site or component for accessibility issues
- Build accessible components from scratch (modals, menus, tabs, forms)
- Implement keyboard navigation and focus management
- Fix color contrast failures
- Add screen reader support to custom widgets
- Set up automated accessibility testing with axe-core or Lighthouse
- Apply ARIA roles, states, and properties correctly
- Make React applications accessible

---

## WCAG 2.2 Principles

WCAG is organized around four principles, known by the acronym POUR.

### 1. Perceivable

All content must be presentable to users in ways they can perceive.

| Guideline | Level | Key Requirement |
|-----------|-------|-----------------|
| 1.1.1 Non-text Content | A | All images, icons, and media have text alternatives |
| 1.2.1 Audio/Video (prerecorded) | A | Captions and transcripts for media |
| 1.3.1 Info and Relationships | A | Structure conveyed through semantic HTML, not just visual styling |
| 1.3.4 Orientation | AA | Content not restricted to a single display orientation |
| 1.4.1 Use of Color | A | Color is not the only visual means of conveying information |
| 1.4.3 Contrast (Minimum) | AA | 4.5:1 for normal text, 3:1 for large text |
| 1.4.6 Contrast (Enhanced) | AAA | 7:1 for normal text, 4.5:1 for large text |
| 1.4.11 Non-text Contrast | AA | 3:1 for UI components and graphical objects |

### 2. Operable

All UI components and navigation must be operable via keyboard and other input methods.

| Guideline | Level | Key Requirement |
|-----------|-------|-----------------|
| 2.1.1 Keyboard | A | All functionality available from a keyboard |
| 2.1.2 No Keyboard Trap | A | Keyboard focus can always be moved away from any component |
| 2.4.1 Bypass Blocks | A | Skip navigation mechanism for repeated content |
| 2.4.3 Focus Order | A | Focusable components receive focus in a meaningful sequence |
| 2.4.7 Focus Visible | AA | Keyboard focus indicator is visible |
| 2.4.11 Focus Not Obscured (Minimum) | AA | Focused item not entirely hidden by other content |
| 2.5.8 Target Size (Minimum) | AA | Interactive targets at least 24x24 CSS pixels |

### 3. Understandable

Content and UI operation must be understandable.

| Guideline | Level | Key Requirement |
|-----------|-------|-----------------|
| 3.1.1 Language of Page | A | Default language of page is programmatically determinable |
| 3.2.1 On Focus | A | No context changes on focus alone |
| 3.2.2 On Input | A | No unexpected context changes on input |
| 3.3.1 Error Identification | A | Errors are identified and described in text |
| 3.3.2 Labels or Instructions | A | Labels or instructions provided for user input |
| 3.3.8 Accessible Authentication (Minimum) | AA | No cognitive function test required for authentication |

### 4. Robust

Content must be robust enough to be interpreted by a wide variety of user agents, including assistive technologies.

| Guideline | Level | Key Requirement |
|-----------|-------|-----------------|
| 4.1.2 Name, Role, Value | A | All UI components expose name, role, and state to AT |
| 4.1.3 Status Messages | AA | Status messages conveyed to AT without receiving focus |

---

## Semantic HTML

Semantic HTML is the foundation of accessibility. Use the correct elements before reaching for ARIA.

### Document Landmarks

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Descriptive Page Title</title>
</head>
<body>
  <a href="#main-content" class="skip-link">Skip to main content</a>

  <header>
    <nav aria-label="Main navigation">
      <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/products">Products</a></li>
        <li><a href="/about">About</a></li>
        <li><a href="/contact">Contact</a></li>
      </ul>
    </nav>
  </header>

  <main id="main-content">
    <h1>Page Title</h1>

    <section aria-labelledby="featured-heading">
      <h2 id="featured-heading">Featured Products</h2>
      <!-- section content -->
    </section>

    <section aria-labelledby="news-heading">
      <h2 id="news-heading">Latest News</h2>
      <!-- section content -->
    </section>
  </main>

  <aside aria-label="Related links">
    <!-- complementary content -->
  </aside>

  <footer>
    <nav aria-label="Footer navigation">
      <ul>
        <li><a href="/privacy">Privacy Policy</a></li>
        <li><a href="/terms">Terms of Service</a></li>
      </ul>
    </nav>
  </footer>
</body>
</html>
```

### Skip Link CSS

```css
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: #000;
  color: #fff;
  padding: 8px 16px;
  z-index: 100;
  font-size: 1rem;
  text-decoration: none;
}

.skip-link:focus {
  top: 0;
}
```

### Heading Hierarchy

Headings must follow a logical, nested order. Never skip heading levels for visual styling.

```html
<!-- Correct: logical nesting -->
<h1>Annual Report</h1>
  <h2>Executive Summary</h2>
  <h2>Financial Results</h2>
    <h3>Q1 Revenue</h3>
    <h3>Q2 Revenue</h3>
  <h2>Outlook</h2>

<!-- Incorrect: skipping from h1 to h3 -->
<h1>Annual Report</h1>
  <h3>Summary</h3> <!-- violation: skipped h2 -->
```

### Semantic Elements Reference

| Purpose | Correct Element | Avoid |
|---------|----------------|-------|
| Navigation | `<nav>` | `<div class="nav">` |
| Article | `<article>` | `<div class="article">` |
| Sidebar | `<aside>` | `<div class="sidebar">` |
| Page header | `<header>` | `<div class="header">` |
| Page footer | `<footer>` | `<div class="footer">` |
| Main content | `<main>` | `<div class="main">` |
| Section with heading | `<section>` | `<div class="section">` |
| Button | `<button>` | `<div onclick="...">` |
| Link | `<a href="...">` | `<span onclick="...">` |
| Emphasis | `<em>` or `<strong>` | `<span class="bold">` |
| List | `<ul>`, `<ol>`, `<dl>` | Nested `<div>` elements |
| Table | `<table>` with `<th>` | `<div>` grid layout for data |

### Data Tables

```html
<table>
  <caption>Quarterly Sales by Region</caption>
  <thead>
    <tr>
      <th scope="col">Region</th>
      <th scope="col">Q1</th>
      <th scope="col">Q2</th>
      <th scope="col">Q3</th>
      <th scope="col">Q4</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">North America</th>
      <td>$1.2M</td>
      <td>$1.4M</td>
      <td>$1.1M</td>
      <td>$1.8M</td>
    </tr>
    <tr>
      <th scope="row">Europe</th>
      <td>$900K</td>
      <td>$1.1M</td>
      <td>$950K</td>
      <td>$1.3M</td>
    </tr>
  </tbody>
</table>
```

---

## ARIA: Roles, States, and Properties

### The First Rule of ARIA

Do not use ARIA if a native HTML element with the equivalent semantics exists. ARIA supplements HTML when native semantics are insufficient (e.g., custom widgets).

```html
<!-- Do not do this: redundant ARIA -->
<button role="button">Save</button>
<nav role="navigation">...</nav>
<a href="/about" role="link">About</a>

<!-- Correct: native elements already have these roles -->
<button>Save</button>
<nav>...</nav>
<a href="/about">About</a>
```

### When ARIA Is Necessary

ARIA is appropriate for:

- Custom widgets that have no native HTML equivalent (tabs, tree views, comboboxes)
- Dynamic content updates that assistive technology needs to announce
- Relationships between elements that cannot be expressed with HTML alone
- Augmenting native elements with additional state information

### Common ARIA Attributes

#### Labeling

```html
<!-- aria-label: provides an accessible name directly -->
<button aria-label="Close dialog">
  <svg><!-- X icon --></svg>
</button>

<!-- aria-labelledby: references another element as the label -->
<div role="dialog" aria-labelledby="dialog-title">
  <h2 id="dialog-title">Confirm Deletion</h2>
</div>

<!-- aria-describedby: provides additional description -->
<input
  type="password"
  aria-label="Password"
  aria-describedby="password-hint"
>
<p id="password-hint">Must be at least 8 characters with one number.</p>
```

#### Live Regions

```html
<!-- Polite: announced at the next convenient moment -->
<div aria-live="polite" aria-atomic="true">
  3 items in your cart
</div>

<!-- Assertive: announced immediately, interrupting current speech -->
<div aria-live="assertive" role="alert">
  Your session will expire in 2 minutes.
</div>

<!-- Status: implicit aria-live="polite" -->
<div role="status">
  Search results: 42 items found
</div>
```

#### States and Properties

```html
<!-- Expanded/collapsed -->
<button aria-expanded="false" aria-controls="dropdown-menu">
  Options
</button>
<ul id="dropdown-menu" hidden>
  <li><a href="/settings">Settings</a></li>
  <li><a href="/profile">Profile</a></li>
</ul>

<!-- Current page in navigation -->
<nav aria-label="Main">
  <a href="/" aria-current="page">Home</a>
  <a href="/about">About</a>
</nav>

<!-- Disabled vs aria-disabled -->
<!-- Use native disabled for form controls -->
<button disabled>Submit</button>
<!-- Use aria-disabled when you need the element to remain focusable -->
<button aria-disabled="true">Submit</button>

<!-- Busy state for loading content -->
<div aria-busy="true" aria-live="polite">
  Loading results...
</div>

<!-- Invalid form field -->
<input
  type="email"
  aria-invalid="true"
  aria-errormessage="email-error"
>
<span id="email-error" role="alert">Please enter a valid email address.</span>
```

### ARIA Anti-Patterns

```html
<!-- Anti-pattern: role on wrong element type -->
<div role="button" onclick="handleClick()">Click me</div>
<!-- Fix: use a real button -->
<button onclick="handleClick()">Click me</button>

<!-- Anti-pattern: aria-label on non-interactive div -->
<div aria-label="Important note">This is some text</div>
<!-- Fix: use an appropriate element or visually hidden text -->
<section aria-labelledby="note-heading">
  <h3 id="note-heading" class="sr-only">Important note</h3>
  <p>This is some text</p>
</section>

<!-- Anti-pattern: changing native semantics -->
<h2 role="tab">Tab Title</h2>
<!-- Fix: use the tab role on a suitable element -->
<div role="tab"><h2>Tab Title</h2></div>

<!-- Anti-pattern: interactive role without keyboard support -->
<div role="button">Delete</div>
<!-- Fix: add keyboard support or use a real button -->
<div role="button" tabindex="0" onkeydown="handleKeyDown(event)" onclick="handleClick()">Delete</div>
<!-- Better fix: use a real button -->
<button onclick="handleClick()">Delete</button>
```

---

## Keyboard Navigation

### Focus Management Fundamentals

```css
/* Never remove focus outlines without providing an alternative */
/* Anti-pattern */
*:focus {
  outline: none; /* removes focus visibility for all users */
}

/* Correct: custom focus style */
*:focus-visible {
  outline: 2px solid #4A90D9;
  outline-offset: 2px;
}

/* Provide a high-contrast focus indicator */
button:focus-visible,
a:focus-visible,
input:focus-visible,
select:focus-visible,
textarea:focus-visible {
  outline: 2px solid #005fcc;
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(0, 95, 204, 0.3);
}
```

### Tab Order

The natural tab order follows the DOM order. Use `tabindex` sparingly:

```html
<!-- tabindex="0": adds element to natural tab order -->
<div role="button" tabindex="0" onclick="handleClick()">Custom Button</div>

<!-- tabindex="-1": focusable programmatically, not via Tab key -->
<div id="error-summary" tabindex="-1">
  <!-- focused by JavaScript when errors occur -->
</div>

<!-- tabindex with a positive value: NEVER DO THIS -->
<!-- It creates unpredictable tab order and maintenance nightmares -->
<input tabindex="3"> <!-- Do not use positive tabindex -->
```

### Keyboard Patterns for Custom Widgets

#### Dropdown Menu

```javascript
function handleMenuKeyDown(event, items, currentIndex) {
  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault();
      const nextIndex = (currentIndex + 1) % items.length;
      items[nextIndex].focus();
      break;

    case 'ArrowUp':
      event.preventDefault();
      const prevIndex = (currentIndex - 1 + items.length) % items.length;
      items[prevIndex].focus();
      break;

    case 'Home':
      event.preventDefault();
      items[0].focus();
      break;

    case 'End':
      event.preventDefault();
      items[items.length - 1].focus();
      break;

    case 'Escape':
      closeMenu();
      triggerButton.focus();
      break;

    case 'Enter':
    case ' ':
      event.preventDefault();
      items[currentIndex].click();
      break;
  }
}
```

#### Roving Tabindex Pattern

Used for widget groups (tabs, toolbars, radio groups) where only one item in the group is in the tab order at a time.

```html
<div role="tablist">
  <button role="tab" tabindex="0" aria-selected="true" id="tab-1">Tab 1</button>
  <button role="tab" tabindex="-1" aria-selected="false" id="tab-2">Tab 2</button>
  <button role="tab" tabindex="-1" aria-selected="false" id="tab-3">Tab 3</button>
</div>
```

```javascript
function handleTabKeyDown(event, tabs, currentIndex) {
  let newIndex = currentIndex;

  switch (event.key) {
    case 'ArrowRight':
      newIndex = (currentIndex + 1) % tabs.length;
      break;
    case 'ArrowLeft':
      newIndex = (currentIndex - 1 + tabs.length) % tabs.length;
      break;
    case 'Home':
      newIndex = 0;
      break;
    case 'End':
      newIndex = tabs.length - 1;
      break;
    default:
      return;
  }

  event.preventDefault();

  // Move tabindex
  tabs[currentIndex].setAttribute('tabindex', '-1');
  tabs[currentIndex].setAttribute('aria-selected', 'false');
  tabs[newIndex].setAttribute('tabindex', '0');
  tabs[newIndex].setAttribute('aria-selected', 'true');
  tabs[newIndex].focus();

  // Activate corresponding panel
  activatePanel(tabs[newIndex].id);
}
```

### Focus Trapping (for Modals)

```javascript
function trapFocus(containerElement) {
  const focusableSelectors = [
    'a[href]',
    'button:not([disabled])',
    'input:not([disabled])',
    'select:not([disabled])',
    'textarea:not([disabled])',
    '[tabindex]:not([tabindex="-1"])',
  ].join(', ');

  const focusableElements = containerElement.querySelectorAll(focusableSelectors);
  const firstFocusable = focusableElements[0];
  const lastFocusable = focusableElements[focusableElements.length - 1];

  function handleKeyDown(event) {
    if (event.key !== 'Tab') return;

    if (event.shiftKey) {
      // Shift+Tab: if on first element, wrap to last
      if (document.activeElement === firstFocusable) {
        event.preventDefault();
        lastFocusable.focus();
      }
    } else {
      // Tab: if on last element, wrap to first
      if (document.activeElement === lastFocusable) {
        event.preventDefault();
        firstFocusable.focus();
      }
    }
  }

  containerElement.addEventListener('keydown', handleKeyDown);

  // Return cleanup function
  return () => containerElement.removeEventListener('keydown', handleKeyDown);
}
```

---

## Color Contrast

### Requirements

| Level | Normal Text (<18pt / <14pt bold) | Large Text (>=18pt / >=14pt bold) | UI Components |
|-------|----------------------------------|-----------------------------------|---------------|
| AA    | 4.5:1                            | 3:1                               | 3:1           |
| AAA   | 7:1                              | 4.5:1                             | N/A           |

Large text is defined as 18pt (24px) or 14pt (18.66px) bold.

### Contrast Calculation in JavaScript

```javascript
function getLuminance(r, g, b) {
  const [rs, gs, bs] = [r, g, b].map(c => {
    c = c / 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
}

function getContrastRatio(color1, color2) {
  const l1 = getLuminance(...color1);
  const l2 = getLuminance(...color2);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

// Usage
const white = [255, 255, 255];
const darkGray = [51, 51, 51]; // #333
const ratio = getContrastRatio(white, darkGray);
console.log(`Contrast ratio: ${ratio.toFixed(2)}:1`);
// Output: Contrast ratio: 12.63:1 (passes AAA)
```

### Accessible Color Palette Example

```css
:root {
  /* Text colors that pass AA on white (#fff) background */
  --color-text-primary: #1a1a1a;     /* 16.75:1 */
  --color-text-secondary: #4a4a4a;   /* 9.73:1  */
  --color-text-muted: #6b6b6b;       /* 5.74:1  */
  --color-text-link: #0055cc;        /* 7.21:1  */

  /* Danger/success/warning with sufficient contrast */
  --color-error: #c7254e;            /* 5.64:1 on white */
  --color-success: #276749;          /* 7.08:1 on white */
  --color-warning-bg: #fef3cd;       /* Use dark text on this */
  --color-warning-text: #664d03;     /* 8.55:1 on #fef3cd */

  /* Focus indicator */
  --color-focus: #005fcc;            /* 7.0:1 on white */
}
```

### Do Not Rely on Color Alone

```html
<!-- Anti-pattern: only color indicates error -->
<input style="border-color: red;">

<!-- Correct: color + icon + text -->
<div class="field-group field-error">
  <label for="email">Email address</label>
  <input id="email" type="email" aria-invalid="true" aria-describedby="email-error">
  <p id="email-error" class="error-message">
    <svg aria-hidden="true" class="error-icon"><!-- icon --></svg>
    Please enter a valid email address.
  </p>
</div>
```

### Contrast Checking Tools

- **Browser DevTools**: Chrome/Edge DevTools show contrast ratios in the color picker
- **axe-core**: Automated scanner catches contrast failures
- **WebAIM Contrast Checker**: https://webaim.org/resources/contrastchecker/
- **Colour Contrast Analyser (CCA)**: Desktop tool from TPGi

---

## Accessible Forms

### Labels and Instructions

```html
<form novalidate>
  <!-- Every input must have an associated label -->
  <div class="form-group">
    <label for="full-name">Full name</label>
    <input type="text" id="full-name" name="fullName" autocomplete="name" required>
  </div>

  <!-- Required fields: indicate visually and programmatically -->
  <div class="form-group">
    <label for="user-email">
      Email address
      <span aria-hidden="true">*</span>
    </label>
    <input
      type="email"
      id="user-email"
      name="email"
      autocomplete="email"
      required
      aria-required="true"
    >
  </div>

  <!-- Group related fields with fieldset/legend -->
  <fieldset>
    <legend>Shipping Address</legend>
    <div class="form-group">
      <label for="street">Street</label>
      <input type="text" id="street" name="street" autocomplete="street-address">
    </div>
    <div class="form-group">
      <label for="city">City</label>
      <input type="text" id="city" name="city" autocomplete="address-level2">
    </div>
    <div class="form-group">
      <label for="zip">ZIP Code</label>
      <input type="text" id="zip" name="zip" autocomplete="postal-code">
    </div>
  </fieldset>

  <!-- Radio buttons in a fieldset -->
  <fieldset>
    <legend>Payment Method</legend>
    <div>
      <input type="radio" id="credit" name="payment" value="credit">
      <label for="credit">Credit Card</label>
    </div>
    <div>
      <input type="radio" id="debit" name="payment" value="debit">
      <label for="debit">Debit Card</label>
    </div>
    <div>
      <input type="radio" id="paypal" name="payment" value="paypal">
      <label for="paypal">PayPal</label>
    </div>
  </fieldset>

  <button type="submit">Place Order</button>
</form>
```

### Error Handling

```html
<!-- Error summary at the top of the form -->
<div role="alert" id="error-summary" tabindex="-1">
  <h2>There were 2 errors with your submission</h2>
  <ul>
    <li><a href="#user-email">Email address is required</a></li>
    <li><a href="#password">Password must be at least 8 characters</a></li>
  </ul>
</div>

<!-- Individual field error -->
<div class="form-group">
  <label for="password">Password</label>
  <input
    type="password"
    id="password"
    name="password"
    aria-invalid="true"
    aria-describedby="password-error password-requirements"
    autocomplete="new-password"
  >
  <p id="password-error" class="error-message" role="alert">
    Password must be at least 8 characters.
  </p>
  <p id="password-requirements" class="hint">
    Include at least one uppercase letter, one number, and one special character.
  </p>
</div>
```

```javascript
function handleFormSubmit(event) {
  event.preventDefault();
  const errors = validateForm(event.target);

  if (errors.length > 0) {
    // Build and display error summary
    const summary = document.getElementById('error-summary');
    const heading = summary.querySelector('h2');
    const list = summary.querySelector('ul');

    heading.textContent = errors.length === 1
      ? 'There was 1 error with your submission'
      : `There were ${errors.length} errors with your submission`;

    // Clear previous error links
    list.textContent = '';

    // Add new error links using safe DOM methods
    errors.forEach(error => {
      const li = document.createElement('li');
      const a = document.createElement('a');
      a.href = `#${error.fieldId}`;
      a.textContent = error.message;
      li.appendChild(a);
      list.appendChild(li);
    });

    // Mark invalid fields
    errors.forEach(error => {
      const field = document.getElementById(error.fieldId);
      field.setAttribute('aria-invalid', 'true');

      const errorEl = document.getElementById(`${error.fieldId}-error`);
      if (errorEl) {
        errorEl.textContent = error.message;
      }
    });

    // Move focus to error summary
    summary.focus();
  }
}
```

---

## Accessible Images

### Alt Text Decision Tree

```
Is the image purely decorative?
  Yes -> alt="" (empty alt, not missing alt)
  No -> Does it contain text?
    Yes -> alt should include the text in the image
    No -> Is it a link or button?
      Yes -> alt describes the destination/action
      No -> Is it a complex image (chart, diagram)?
        Yes -> Provide brief alt + longer description via aria-describedby or a visible caption
        No -> Describe the meaningful content
```

### Examples

```html
<!-- Decorative: empty alt, presentational role -->
<img src="divider.png" alt="" role="presentation">

<!-- Informative: describe the content -->
<img src="chart-q3-revenue.png" alt="Q3 2025 revenue chart showing 23% growth year-over-year">

<!-- Linked image: describe the destination -->
<a href="/profile">
  <img src="avatar.jpg" alt="Your profile">
</a>

<!-- Image with visible caption -->
<figure>
  <img
    src="architecture-diagram.png"
    alt="System architecture showing three microservices connected through an API gateway"
  >
  <figcaption>
    Figure 1: Production architecture. The API gateway routes traffic to the
    user service, order service, and notification service. Each service
    connects to its own database instance.
  </figcaption>
</figure>

<!-- Complex image with long description -->
<img
  src="data-flow.png"
  alt="Data processing pipeline overview"
  aria-describedby="data-flow-desc"
>
<div id="data-flow-desc">
  <p>The pipeline consists of four stages:</p>
  <ol>
    <li>Data ingestion from Kafka topics</li>
    <li>Transformation via Apache Spark</li>
    <li>Storage in PostgreSQL and S3</li>
    <li>Visualization through Grafana dashboards</li>
  </ol>
</div>

<!-- Icon with text: icon is decorative -->
<button>
  <svg aria-hidden="true" focusable="false"><!-- trash icon --></svg>
  Delete item
</button>

<!-- Icon-only button: needs accessible name -->
<button aria-label="Delete item">
  <svg aria-hidden="true" focusable="false"><!-- trash icon --></svg>
</button>
```

### SVG Accessibility

```html
<!-- Decorative SVG -->
<svg aria-hidden="true" focusable="false">
  <!-- decorative graphic -->
</svg>

<!-- Informative SVG -->
<svg role="img" aria-labelledby="svg-title svg-desc">
  <title id="svg-title">Monthly Revenue</title>
  <desc id="svg-desc">Bar chart showing revenue increasing from $10K in January to $25K in June.</desc>
  <!-- chart content -->
</svg>
```

---

## Accessible Custom Components

### Accessible Modal Dialog

```html
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="modal-title"
  aria-describedby="modal-desc"
>
  <h2 id="modal-title">Delete Account</h2>
  <p id="modal-desc">
    This action cannot be undone. All your data will be permanently deleted.
  </p>
  <div class="modal-actions">
    <button onclick="closeModal()">Cancel</button>
    <button onclick="deleteAccount()" class="btn-danger">Delete Account</button>
  </div>
  <button aria-label="Close dialog" class="modal-close" onclick="closeModal()">
    <svg aria-hidden="true"><!-- X icon --></svg>
  </button>
</div>
<div class="modal-backdrop" aria-hidden="true"></div>
```

```javascript
let previouslyFocusedElement = null;
let cleanupFocusTrap = null;

function openModal(modalElement) {
  // Store the element that triggered the modal
  previouslyFocusedElement = document.activeElement;

  // Show the modal
  modalElement.removeAttribute('hidden');
  document.body.style.overflow = 'hidden';

  // Set up inert on background content
  document.getElementById('app-root').setAttribute('inert', '');

  // Trap focus
  cleanupFocusTrap = trapFocus(modalElement);

  // Focus the first interactive element (or the modal itself)
  const firstFocusable = modalElement.querySelector(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  (firstFocusable || modalElement).focus();

  // Close on Escape
  modalElement.addEventListener('keydown', handleModalKeyDown);
}

function closeModal(modalElement) {
  modalElement.setAttribute('hidden', '');
  document.body.style.overflow = '';

  // Remove inert from background
  document.getElementById('app-root').removeAttribute('inert');

  // Clean up focus trap
  if (cleanupFocusTrap) cleanupFocusTrap();

  // Restore focus to the triggering element
  if (previouslyFocusedElement) {
    previouslyFocusedElement.focus();
    previouslyFocusedElement = null;
  }

  modalElement.removeEventListener('keydown', handleModalKeyDown);
}

function handleModalKeyDown(event) {
  if (event.key === 'Escape') {
    closeModal(event.currentTarget);
  }
}
```

### Accessible Dropdown Menu

```html
<div class="dropdown">
  <button
    id="menu-button"
    aria-haspopup="true"
    aria-expanded="false"
    aria-controls="menu-list"
  >
    Account Settings
    <svg aria-hidden="true"><!-- chevron icon --></svg>
  </button>

  <ul id="menu-list" role="menu" aria-labelledby="menu-button" hidden>
    <li role="none">
      <a role="menuitem" href="/profile" tabindex="-1">Profile</a>
    </li>
    <li role="none">
      <a role="menuitem" href="/settings" tabindex="-1">Settings</a>
    </li>
    <li role="separator"></li>
    <li role="none">
      <button role="menuitem" tabindex="-1" onclick="logout()">Sign Out</button>
    </li>
  </ul>
</div>
```

```javascript
const menuButton = document.getElementById('menu-button');
const menuList = document.getElementById('menu-list');
const menuItems = menuList.querySelectorAll('[role="menuitem"]');

menuButton.addEventListener('click', () => {
  const isExpanded = menuButton.getAttribute('aria-expanded') === 'true';
  toggleMenu(!isExpanded);
});

menuButton.addEventListener('keydown', (event) => {
  if (event.key === 'ArrowDown' || event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    toggleMenu(true);
    menuItems[0].focus();
  }
});

function toggleMenu(open) {
  menuButton.setAttribute('aria-expanded', String(open));
  if (open) {
    menuList.removeAttribute('hidden');
  } else {
    menuList.setAttribute('hidden', '');
  }
}

menuList.addEventListener('keydown', (event) => {
  const currentIndex = Array.from(menuItems).indexOf(document.activeElement);

  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault();
      menuItems[(currentIndex + 1) % menuItems.length].focus();
      break;
    case 'ArrowUp':
      event.preventDefault();
      menuItems[(currentIndex - 1 + menuItems.length) % menuItems.length].focus();
      break;
    case 'Home':
      event.preventDefault();
      menuItems[0].focus();
      break;
    case 'End':
      event.preventDefault();
      menuItems[menuItems.length - 1].focus();
      break;
    case 'Escape':
      toggleMenu(false);
      menuButton.focus();
      break;
  }
});

// Close when clicking outside
document.addEventListener('click', (event) => {
  if (!event.target.closest('.dropdown')) {
    toggleMenu(false);
  }
});
```

### Accessible Tabs

```html
<div class="tabs">
  <div role="tablist" aria-label="Project information">
    <button
      role="tab"
      id="tab-overview"
      aria-selected="true"
      aria-controls="panel-overview"
      tabindex="0"
    >
      Overview
    </button>
    <button
      role="tab"
      id="tab-members"
      aria-selected="false"
      aria-controls="panel-members"
      tabindex="-1"
    >
      Members
    </button>
    <button
      role="tab"
      id="tab-settings"
      aria-selected="false"
      aria-controls="panel-settings"
      tabindex="-1"
    >
      Settings
    </button>
  </div>

  <div
    role="tabpanel"
    id="panel-overview"
    aria-labelledby="tab-overview"
    tabindex="0"
  >
    <h3>Project Overview</h3>
    <p>Content for the overview panel.</p>
  </div>

  <div
    role="tabpanel"
    id="panel-members"
    aria-labelledby="tab-members"
    tabindex="0"
    hidden
  >
    <h3>Team Members</h3>
    <p>Content for the members panel.</p>
  </div>

  <div
    role="tabpanel"
    id="panel-settings"
    aria-labelledby="tab-settings"
    tabindex="0"
    hidden
  >
    <h3>Settings</h3>
    <p>Content for the settings panel.</p>
  </div>
</div>
```

### Accessible Toast/Notification

```html
<!-- Toast container: lives in the DOM, content changes dynamically -->
<div id="toast-region" aria-live="polite" aria-relevant="additions" class="toast-container">
  <!-- Toasts are injected here -->
</div>
```

```javascript
function showToast(message, type = 'info', duration = 5000) {
  const container = document.getElementById('toast-region');
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.setAttribute('role', 'status');
  toast.textContent = message;

  container.appendChild(toast);

  // Auto-dismiss
  setTimeout(() => {
    toast.remove();
  }, duration);
}

// Usage
showToast('File saved successfully.', 'success');
showToast('Unable to connect. Retrying...', 'error');
```

---

## Accessible Media

### Video

```html
<video controls>
  <source src="demo.mp4" type="video/mp4">
  <track kind="captions" src="demo-en.vtt" srclang="en" label="English" default>
  <track kind="descriptions" src="demo-desc-en.vtt" srclang="en" label="English Audio Descriptions">
  <p>Your browser does not support the video element.
    <a href="demo.mp4">Download the video</a>.
  </p>
</video>
```

### Audio

```html
<audio controls>
  <source src="podcast-ep12.mp3" type="audio/mpeg">
  <p>Your browser does not support the audio element.
    <a href="podcast-ep12.mp3">Download the audio</a>.
  </p>
</audio>
<details>
  <summary>Read transcript</summary>
  <div class="transcript">
    <p><strong>Host:</strong> Welcome to episode 12...</p>
    <!-- full transcript -->
  </div>
</details>
```

---

## Testing Accessibility

### axe-core Integration

#### In Unit Tests (jest/vitest)

```bash
npm install -D @axe-core/react jest-axe
```

```typescript
// components/__tests__/LoginForm.test.tsx
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { LoginForm } from '../LoginForm';

expect.extend(toHaveNoViolations);

describe('LoginForm', () => {
  it('has no accessibility violations', async () => {
    const { container } = render(<LoginForm />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('has no violations in error state', async () => {
    const { container } = render(<LoginForm showErrors />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

#### In Integration Tests (Playwright)

```bash
npm install -D @axe-core/playwright
```

```typescript
// tests/accessibility.spec.ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Accessibility', () => {
  test('home page has no critical violations', async ({ page }) => {
    await page.goto('/');
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag22aa'])
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('login form has no violations', async ({ page }) => {
    await page.goto('/login');
    const results = await new AxeBuilder({ page })
      .include('#login-form')
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('modal dialog has no violations when open', async ({ page }) => {
    await page.goto('/dashboard');
    await page.click('button:has-text("Delete")');
    await page.waitForSelector('[role="dialog"]');

    const results = await new AxeBuilder({ page })
      .include('[role="dialog"]')
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('focus is trapped inside modal', async ({ page }) => {
    await page.goto('/dashboard');
    await page.click('button:has-text("Delete")');
    await page.waitForSelector('[role="dialog"]');

    // Tab through all focusable elements
    const dialog = page.locator('[role="dialog"]');
    const focusableElements = await dialog.locator(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    ).all();

    // Press Tab enough times to cycle through all elements
    for (let i = 0; i < focusableElements.length + 1; i++) {
      await page.keyboard.press('Tab');
      const activeElement = page.locator(':focus');
      // Verify focus stays within the dialog
      await expect(dialog).toContainText(await activeElement.textContent() || '');
    }
  });
});
```

#### In Cypress

```bash
npm install -D cypress-axe axe-core
```

```javascript
// cypress/support/e2e.js
import 'cypress-axe';

// cypress/e2e/accessibility.cy.js
describe('Accessibility', () => {
  it('checks the entire page', () => {
    cy.visit('/');
    cy.injectAxe();
    cy.checkA11y(null, {
      runOnly: {
        type: 'tag',
        values: ['wcag2a', 'wcag2aa', 'wcag22aa'],
      },
    });
  });

  it('checks a specific component', () => {
    cy.visit('/contact');
    cy.injectAxe();
    cy.checkA11y('#contact-form');
  });
});
```

### Lighthouse CI

```bash
npm install -D @lhci/cli
```

```json
// lighthouserc.json
{
  "ci": {
    "collect": {
      "url": ["http://localhost:3000/", "http://localhost:3000/login", "http://localhost:3000/dashboard"],
      "numberOfRuns": 3
    },
    "assert": {
      "assertions": {
        "categories:accessibility": ["error", { "minScore": 0.9 }]
      }
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}
```

```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse CI
on: [pull_request]
jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npm run build
      - run: npm run start &
      - run: npx wait-on http://localhost:3000
      - run: npx @lhci/cli autorun
```

### Manual Screen Reader Testing

Key screen reader and browser pairings to test:

| Screen Reader | Platform | Best With |
|--------------|----------|-----------|
| NVDA | Windows | Firefox, Chrome |
| JAWS | Windows | Chrome, Edge |
| VoiceOver | macOS/iOS | Safari |
| TalkBack | Android | Chrome |

Essential manual checks:

1. Navigate by headings (H key in NVDA/JAWS, VO+Command+H in VoiceOver)
2. Navigate by landmarks (D key in NVDA, R key in JAWS, VO+U in VoiceOver)
3. Tab through all interactive elements -- verify focus order and announced names
4. Operate custom widgets with keyboard only
5. Verify form labels are announced when fields receive focus
6. Check that error messages are announced
7. Verify live regions announce dynamic content changes

---

## React Accessibility Patterns

### Accessible React Component Library Pattern

```tsx
// components/ui/Button.tsx
import { forwardRef, ButtonHTMLAttributes } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  isLoading?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', isLoading, children, disabled, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={`btn btn-${variant}`}
        disabled={disabled || isLoading}
        aria-busy={isLoading || undefined}
        {...props}
      >
        {isLoading ? (
          <>
            <span className="spinner" aria-hidden="true" />
            <span className="sr-only">Loading...</span>
            <span aria-hidden="true">{children}</span>
          </>
        ) : (
          children
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';
```

### Accessible Modal in React

```tsx
// components/ui/Modal.tsx
import { useEffect, useRef, ReactNode, useCallback } from 'react';
import { createPortal } from 'react-dom';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: ReactNode;
}

export function Modal({ isOpen, onClose, title, description, children }: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (event.key === 'Escape') {
      onClose();
    }
  }, [onClose]);

  useEffect(() => {
    if (isOpen) {
      previousFocusRef.current = document.activeElement as HTMLElement;
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';

      // Focus the modal after render
      requestAnimationFrame(() => {
        modalRef.current?.focus();
      });
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';

      // Restore focus when modal closes
      if (previousFocusRef.current) {
        previousFocusRef.current.focus();
      }
    };
  }, [isOpen, handleKeyDown]);

  if (!isOpen) return null;

  return createPortal(
    <>
      <div className="modal-backdrop" aria-hidden="true" onClick={onClose} />
      <div
        ref={modalRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        aria-describedby={description ? 'modal-desc' : undefined}
        tabIndex={-1}
        className="modal"
      >
        <h2 id="modal-title">{title}</h2>
        {description && <p id="modal-desc">{description}</p>}
        {children}
        <button
          aria-label="Close dialog"
          className="modal-close"
          onClick={onClose}
        >
          <svg aria-hidden="true">
            <path d="M6 6L18 18M6 18L18 6" stroke="currentColor" strokeWidth="2" />
          </svg>
        </button>
      </div>
    </>,
    document.body
  );
}

// Usage
function DeleteConfirmation() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button onClick={() => setIsOpen(true)}>Delete Project</button>
      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="Delete Project"
        description="This action cannot be undone."
      >
        <div className="modal-actions">
          <button onClick={() => setIsOpen(false)}>Cancel</button>
          <button className="btn-danger" onClick={handleDelete}>Delete</button>
        </div>
      </Modal>
    </>
  );
}
```

### Accessible Form with React Hook Form

```tsx
// components/ContactForm.tsx
import { useForm } from 'react-hook-form';
import { useRef, useEffect } from 'react';

interface ContactFormData {
  name: string;
  email: string;
  message: string;
}

export function ContactForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting, isSubmitSuccessful },
  } = useForm<ContactFormData>();
  const errorSummaryRef = useRef<HTMLDivElement>(null);

  // Focus error summary when errors appear
  useEffect(() => {
    if (Object.keys(errors).length > 0 && errorSummaryRef.current) {
      errorSummaryRef.current.focus();
    }
  }, [errors]);

  const onSubmit = async (data: ContactFormData) => {
    await submitContactForm(data);
  };

  if (isSubmitSuccessful) {
    return (
      <div role="status">
        <h2>Message sent</h2>
        <p>Thank you for reaching out. We will reply within 24 hours.</p>
      </div>
    );
  }

  const errorMessages = Object.entries(errors).map(([field, error]) => ({
    field,
    message: error?.message || 'This field is invalid',
  }));

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      {errorMessages.length > 0 && (
        <div ref={errorSummaryRef} role="alert" tabIndex={-1} className="error-summary">
          <h2>
            {errorMessages.length === 1
              ? 'There was 1 error with your submission'
              : `There were ${errorMessages.length} errors with your submission`}
          </h2>
          <ul>
            {errorMessages.map(({ field, message }) => (
              <li key={field}>
                <a href={`#${field}`}>{message}</a>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="form-group">
        <label htmlFor="name">Name</label>
        <input
          id="name"
          type="text"
          aria-invalid={!!errors.name || undefined}
          aria-describedby={errors.name ? 'name-error' : undefined}
          {...register('name', { required: 'Name is required' })}
        />
        {errors.name && (
          <p id="name-error" className="error-message" role="alert">
            {errors.name.message}
          </p>
        )}
      </div>

      <div className="form-group">
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          aria-invalid={!!errors.email || undefined}
          aria-describedby={errors.email ? 'email-error' : undefined}
          {...register('email', {
            required: 'Email is required',
            pattern: {
              value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
              message: 'Please enter a valid email address',
            },
          })}
        />
        {errors.email && (
          <p id="email-error" className="error-message" role="alert">
            {errors.email.message}
          </p>
        )}
      </div>

      <div className="form-group">
        <label htmlFor="message">Message</label>
        <textarea
          id="message"
          rows={5}
          aria-invalid={!!errors.message || undefined}
          aria-describedby={errors.message ? 'message-error' : undefined}
          {...register('message', {
            required: 'Message is required',
            minLength: { value: 10, message: 'Message must be at least 10 characters' },
          })}
        />
        {errors.message && (
          <p id="message-error" className="error-message" role="alert">
            {errors.message.message}
          </p>
        )}
      </div>

      <button type="submit" disabled={isSubmitting} aria-busy={isSubmitting || undefined}>
        {isSubmitting ? 'Sending...' : 'Send Message'}
      </button>
    </form>
  );
}
```

### Accessible Route Announcements in React

```tsx
// components/RouteAnnouncer.tsx
import { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';

export function RouteAnnouncer() {
  const location = useLocation();
  const announcerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Announce the new page title after navigation
    const pageTitle = document.title;
    if (announcerRef.current) {
      announcerRef.current.textContent = `Navigated to ${pageTitle}`;
    }
  }, [location.pathname]);

  return (
    <div
      ref={announcerRef}
      role="status"
      aria-live="polite"
      aria-atomic="true"
      className="sr-only"
    />
  );
}
```

### Visually Hidden Utility

```css
/* Screen-reader-only class */
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

/* Allow the element to be focusable when navigated to */
.sr-only-focusable:focus,
.sr-only-focusable:active {
  position: static;
  width: auto;
  height: auto;
  padding: inherit;
  margin: inherit;
  overflow: visible;
  clip: auto;
  white-space: inherit;
}
```

### useAnnounce Hook

```tsx
// hooks/useAnnounce.ts
import { useCallback, useRef } from 'react';

export function useAnnounce() {
  const regionRef = useRef<HTMLDivElement | null>(null);

  const announce = useCallback((message: string, priority: 'polite' | 'assertive' = 'polite') => {
    if (!regionRef.current) {
      const region = document.createElement('div');
      region.setAttribute('aria-live', priority);
      region.setAttribute('aria-atomic', 'true');
      region.setAttribute('role', priority === 'assertive' ? 'alert' : 'status');
      region.className = 'sr-only';
      document.body.appendChild(region);
      regionRef.current = region;
    }

    regionRef.current.setAttribute('aria-live', priority);

    // Clear and re-set to trigger announcement even if same message
    regionRef.current.textContent = '';
    requestAnimationFrame(() => {
      if (regionRef.current) {
        regionRef.current.textContent = message;
      }
    });
  }, []);

  return announce;
}

// Usage
function SearchResults({ results }: { results: Item[] }) {
  const announce = useAnnounce();

  useEffect(() => {
    announce(`${results.length} results found`);
  }, [results, announce]);

  return (
    <ul>
      {results.map(item => (
        <li key={item.id}>{item.name}</li>
      ))}
    </ul>
  );
}
```

---

## Common Anti-Patterns

### 1. Div Soup

```html
<!-- Anti-pattern -->
<div class="header">
  <div class="nav">
    <div class="nav-item" onclick="navigate('/')">Home</div>
    <div class="nav-item" onclick="navigate('/about')">About</div>
  </div>
</div>

<!-- Correct -->
<header>
  <nav aria-label="Main">
    <ul>
      <li><a href="/">Home</a></li>
      <li><a href="/about">About</a></li>
    </ul>
  </nav>
</header>
```

### 2. Missing Form Labels

```html
<!-- Anti-pattern: placeholder as label -->
<input type="email" placeholder="Email address">

<!-- Correct: visible label -->
<label for="email">Email address</label>
<input type="email" id="email" placeholder="e.g. user@example.com">

<!-- Acceptable when design constraints exist: visually hidden label -->
<label for="search" class="sr-only">Search products</label>
<input type="search" id="search" placeholder="Search products...">
```

### 3. Non-interactive Elements Made Clickable

```html
<!-- Anti-pattern -->
<span onclick="doSomething()" class="link-style">Click here</span>

<!-- Correct: use a button for actions -->
<button onclick="doSomething()" class="link-style">Perform action</button>

<!-- Correct: use a link for navigation -->
<a href="/destination">Go to destination</a>
```

### 4. Auto-Playing Media

```html
<!-- Anti-pattern -->
<video autoplay>...</video>

<!-- Correct: no autoplay, or muted with controls -->
<video controls>...</video>
<!-- Acceptable: muted autoplay with controls to pause -->
<video autoplay muted controls>...</video>
```

### 5. Missing Document Language

```html
<!-- Anti-pattern -->
<html>

<!-- Correct -->
<html lang="en">

<!-- For multilingual content -->
<p>This is English text.</p>
<p lang="fr">Ceci est du texte en francais.</p>
```

### 6. Opening Links in New Windows Without Warning

```html
<!-- Anti-pattern: unexpected new window -->
<a href="/terms" target="_blank">Terms of Service</a>

<!-- Correct: warn the user -->
<a href="/terms" target="_blank" rel="noopener noreferrer">
  Terms of Service
  <span class="sr-only">(opens in a new tab)</span>
</a>
```

### 7. Poor Focus Management After DOM Changes

```javascript
// Anti-pattern: removing element without moving focus
deleteButton.addEventListener('click', () => {
  listItem.remove(); // focus is now lost
});

// Correct: move focus to a meaningful location
deleteButton.addEventListener('click', () => {
  const nextItem = listItem.nextElementSibling || listItem.previousElementSibling;
  listItem.remove();
  if (nextItem) {
    nextItem.focus();
  } else {
    document.getElementById('empty-list-message').focus();
  }
});
```

### 8. Using Title Attribute for Essential Information

```html
<!-- Anti-pattern: title is not reliably exposed to all users -->
<button title="This will permanently delete your account">Delete</button>

<!-- Correct: use visible text or aria-describedby -->
<button aria-describedby="delete-warning">Delete Account</button>
<p id="delete-warning">This will permanently delete your account and all associated data.</p>
```

### 9. Disabled Buttons Without Explanation

```html
<!-- Anti-pattern: disabled with no explanation -->
<button disabled>Submit</button>

<!-- Correct: explain why the button is disabled -->
<button disabled aria-describedby="submit-hint">Submit</button>
<p id="submit-hint">Complete all required fields to enable submission.</p>

<!-- Alternative: use aria-disabled to keep it focusable -->
<button aria-disabled="true" aria-describedby="submit-hint">Submit</button>
<p id="submit-hint">Complete all required fields to enable submission.</p>
```

### 10. Infinite Scroll Without Alternative

```html
<!-- Anti-pattern: infinite scroll with no way to reach footer -->
<div class="infinite-list" onscroll="loadMore()">...</div>
<footer><!-- unreachable --></footer>

<!-- Correct: provide a "Load More" button and ensure footer is reachable -->
<ul id="results">...</ul>
<button onclick="loadMore()">Load more results</button>
<p aria-live="polite">Showing 20 of 156 results</p>
<footer><!-- always reachable --></footer>
```

---

## Accessibility Audit Checklist

Use this checklist when auditing a page or component.

### Automated (axe-core / Lighthouse)

- [ ] Run axe-core: zero violations at `wcag2a`, `wcag2aa`, `wcag22aa` rule tags
- [ ] Lighthouse accessibility score >= 90

### Keyboard

- [ ] All interactive elements reachable via Tab
- [ ] Focus order matches visual order
- [ ] Focus indicator always visible
- [ ] No keyboard traps
- [ ] Custom widgets follow WAI-ARIA authoring practices keyboard patterns
- [ ] Escape closes modals, dropdowns, and popups
- [ ] Focus returns to trigger element after closing overlay

### Screen Reader

- [ ] Page title is descriptive
- [ ] Heading hierarchy is logical (no skipped levels)
- [ ] All images have appropriate alt text
- [ ] Form fields have associated labels
- [ ] Error messages are announced
- [ ] Dynamic content updates are announced via live regions
- [ ] ARIA roles and states are correct

### Visual

- [ ] Text contrast meets AA (4.5:1 normal, 3:1 large)
- [ ] UI component contrast meets 3:1
- [ ] Information not conveyed by color alone
- [ ] Content readable at 200% zoom
- [ ] Interactive targets are at least 24x24 CSS pixels
- [ ] No content flashes more than 3 times per second

### Forms

- [ ] All inputs have visible labels
- [ ] Required fields are indicated
- [ ] Error messages are descriptive and associated with fields
- [ ] Autocomplete attributes are present for personal data fields
- [ ] Related fields are grouped with fieldset/legend

---

## Resources

- WCAG 2.2 Specification: https://www.w3.org/TR/WCAG22/
- WAI-ARIA Authoring Practices: https://www.w3.org/WAI/ARIA/apg/
- WebAIM: https://webaim.org/
- axe-core: https://github.com/dequelabs/axe-core
- Inclusive Components: https://inclusive-components.design/
- A11y Project Checklist: https://www.a11yproject.com/checklist/
