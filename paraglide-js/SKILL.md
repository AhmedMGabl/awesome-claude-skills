---
name: paraglide-js
description: Paraglide JS internationalization patterns covering message definitions, tree-shakeable translations, compiler-generated functions, language switching, SvelteKit/Next.js/Astro integration, and type-safe message parameters.
---

# Paraglide JS

This skill should be used when adding internationalization with Paraglide JS. It covers message definitions, tree-shakeable translations, language switching, and framework integration.

## When to Use This Skill

Use this skill when you need to:

- Add tree-shakeable i18n to web applications
- Generate fully typed translation functions
- Integrate with SvelteKit, Next.js, or Astro
- Switch languages at runtime
- Keep bundle size minimal with only used translations

## Setup

```bash
npx @inlang/paraglide-js init
```

```json
// project.inlang/settings.json
{
  "$schema": "https://inlang.com/schema/project-settings",
  "sourceLanguageTag": "en",
  "languageTags": ["en", "de", "fr"],
  "modules": [
    "https://cdn.jsdelivr.net/npm/@inlang/message-lint-rule-empty-pattern@latest/dist/index.js",
    "https://cdn.jsdelivr.net/npm/@inlang/message-lint-rule-missing-translation@latest/dist/index.js",
    "https://cdn.jsdelivr.net/npm/@inlang/plugin-message-format@latest/dist/index.js",
    "https://cdn.jsdelivr.net/npm/@inlang/plugin-m-function-matcher@latest/dist/index.js"
  ]
}
```

## Message Definitions

```
// messages/en.json
{
  "greeting": "Hello, {name}!",
  "items_count": "{count, plural, =0 {No items} one {# item} other {# items}}",
  "nav_home": "Home",
  "nav_about": "About",
  "nav_settings": "Settings",
  "auth_login": "Log in",
  "auth_logout": "Log out",
  "error_required": "{field} is required",
  "error_not_found": "Page not found"
}

// messages/de.json
{
  "greeting": "Hallo, {name}!",
  "items_count": "{count, plural, =0 {Keine Artikel} one {# Artikel} other {# Artikel}}",
  "nav_home": "Startseite",
  "nav_about": "Über uns",
  "nav_settings": "Einstellungen",
  "auth_login": "Anmelden",
  "auth_logout": "Abmelden",
  "error_required": "{field} ist erforderlich",
  "error_not_found": "Seite nicht gefunden"
}
```

## Usage in Code

```typescript
// Generated functions are fully typed
import * as m from "./paraglide/messages";
import { setLanguageTag, languageTag } from "./paraglide/runtime";

// Simple message
m.nav_home(); // "Home"

// Message with parameters
m.greeting({ name: "Alice" }); // "Hello, Alice!"

// Pluralized message
m.items_count({ count: 0 }); // "No items"
m.items_count({ count: 1 }); // "1 item"
m.items_count({ count: 5 }); // "5 items"

// Switch language
setLanguageTag("de");
m.greeting({ name: "Alice" }); // "Hallo, Alice!"

// Get current language
const currentLang = languageTag(); // "de"
```

## SvelteKit Integration

```typescript
// vite.config.ts
import { paraglide } from "@inlang/paraglide-sveltekit/vite";

export default defineConfig({
  plugins: [
    paraglide({
      project: "./project.inlang",
      outdir: "./src/lib/paraglide",
    }),
    sveltekit(),
  ],
});
```

```svelte
<!-- src/routes/+layout.svelte -->
<script>
  import { ParaglideJS } from "@inlang/paraglide-sveltekit";
  import { i18n } from "$lib/i18n";
</script>

<ParaglideJS {i18n}>
  <slot />
</ParaglideJS>

<!-- src/routes/+page.svelte -->
<script>
  import * as m from "$lib/paraglide/messages";
</script>

<h1>{m.greeting({ name: "World" })}</h1>
<nav>
  <a href="/">{m.nav_home()}</a>
  <a href="/about">{m.nav_about()}</a>
</nav>
```

## Next.js Integration

```typescript
// next.config.js
import { paraglide } from "@inlang/paraglide-next/plugin";

export default paraglide({
  paraglide: {
    project: "./project.inlang",
    outdir: "./src/paraglide",
  },
});
```

```tsx
// app/[locale]/page.tsx
import * as m from "@/paraglide/messages";

export default function Home() {
  return (
    <div>
      <h1>{m.greeting({ name: "World" })}</h1>
      <p>{m.items_count({ count: 42 })}</p>
    </div>
  );
}
```

## Language Switcher

```tsx
import { setLanguageTag, languageTag, availableLanguageTags } from "./paraglide/runtime";

function LanguageSwitcher() {
  return (
    <select
      value={languageTag()}
      onChange={(e) => setLanguageTag(e.target.value as any)}
    >
      {availableLanguageTags.map((tag) => (
        <option key={tag} value={tag}>
          {tag.toUpperCase()}
        </option>
      ))}
    </select>
  );
}
```

## Additional Resources

- Paraglide JS: https://inlang.com/m/gerre34r/library-inlang-paraglideJs
- SvelteKit integration: https://inlang.com/m/dxnzrydw/paraglide-sveltekit-i18n
