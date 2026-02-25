---
name: typesafe-i18n
description: typesafe-i18n patterns covering locale definitions, typed translation functions, plural rules, formatters, async locale loading, namespace organization, React/Svelte/Vue integration, and type-safe interpolation with compile-time checks.
---

# typesafe-i18n

This skill should be used when adding internationalization with typesafe-i18n. It covers locale definitions, typed translations, plurals, formatters, and framework integration.

## When to Use This Skill

Use this skill when you need to:

- Add type-safe translations with compile-time checks
- Define plural rules and custom formatters
- Lazy-load locales for performance
- Integrate i18n with React, Svelte, or Vue
- Organize translations by namespaces

## Locale Definitions

```typescript
// src/i18n/en/index.ts
import type { BaseTranslation } from "../i18n-types";

const en = {
  greeting: "Hello, {name:string}!",
  items: "{count:number} {{item|items}}",
  welcome: "Welcome to {app:string}",
  nav: {
    home: "Home",
    about: "About",
    settings: "Settings",
  },
  auth: {
    login: "Log in",
    logout: "Log out",
    signUp: "Sign up",
    forgotPassword: "Forgot password?",
    resetSent: "Password reset email sent to {email:string}",
  },
  errors: {
    required: "{field:string} is required",
    minLength: "{field:string} must be at least {min:number} characters",
    notFound: "Page not found",
    serverError: "Something went wrong. Please try again later.",
  },
  dates: {
    today: "Today",
    yesterday: "Yesterday",
    daysAgo: "{days:number} {{day|days}} ago",
  },
} satisfies BaseTranslation;

export default en;

// src/i18n/de/index.ts
import type { Translation } from "../i18n-types";

const de = {
  greeting: "Hallo, {name}!",
  items: "{count} {{Artikel|Artikel}}",
  welcome: "Willkommen bei {app}",
  nav: {
    home: "Startseite",
    about: "Über uns",
    settings: "Einstellungen",
  },
  auth: {
    login: "Anmelden",
    logout: "Abmelden",
    signUp: "Registrieren",
    forgotPassword: "Passwort vergessen?",
    resetSent: "E-Mail zum Zurücksetzen des Passworts an {email} gesendet",
  },
  errors: {
    required: "{field} ist erforderlich",
    minLength: "{field} muss mindestens {min} Zeichen lang sein",
    notFound: "Seite nicht gefunden",
    serverError: "Etwas ist schiefgelaufen. Bitte versuchen Sie es später erneut.",
  },
  dates: {
    today: "Heute",
    yesterday: "Gestern",
    daysAgo: "vor {days} {{Tag|Tagen}}",
  },
} satisfies Translation;

export default de;
```

## Custom Formatters

```typescript
// src/i18n/formatters.ts
import type { FormattersInitializer } from "typesafe-i18n";
import type { Locales, Formatters } from "./i18n-types";

export const initFormatters: FormattersInitializer<Locales, Formatters> = (
  locale,
) => {
  const dateFormatter = new Intl.DateTimeFormat(locale, {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  const currencyFormatter = new Intl.NumberFormat(locale, {
    style: "currency",
    currency: locale === "en" ? "USD" : "EUR",
  });

  const relativeFormatter = new Intl.RelativeTimeFormat(locale, {
    numeric: "auto",
  });

  return {
    date: (value: Date) => dateFormatter.format(value),
    currency: (value: number) => currencyFormatter.format(value),
    relative: (value: number) => relativeFormatter.format(value, "day"),
  };
};
```

## React Integration

```tsx
// src/i18n/i18n-react.tsx
import { useContext, useEffect, useState } from "react";
import TypesafeI18n from "./i18n-react-context";
import { loadLocaleAsync } from "./i18n-util.async";
import type { Locales } from "./i18n-types";

export function I18nProvider({
  locale,
  children,
}: {
  locale: Locales;
  children: React.ReactNode;
}) {
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    loadLocaleAsync(locale).then(() => setLoaded(true));
  }, [locale]);

  if (!loaded) return null;

  return <TypesafeI18n locale={locale}>{children}</TypesafeI18n>;
}

// Component usage
import { useI18nContext } from "../i18n/i18n-react-context";

function Header() {
  const { LL, locale, setLocale } = useI18nContext();

  return (
    <header>
      <nav>
        <a href="/">{LL.nav.home()}</a>
        <a href="/about">{LL.nav.about()}</a>
      </nav>
      <p>{LL.greeting({ name: "Alice" })}</p>
      <p>{LL.items({ count: 5 })}</p>
      <select value={locale} onChange={(e) => setLocale(e.target.value as Locales)}>
        <option value="en">English</option>
        <option value="de">Deutsch</option>
      </select>
    </header>
  );
}

function LoginForm() {
  const { LL } = useI18nContext();

  return (
    <form>
      <button type="submit">{LL.auth.login()}</button>
      <a href="/forgot">{LL.auth.forgotPassword()}</a>
      <p>{LL.errors.required({ field: "Email" })}</p>
    </form>
  );
}
```

## CLI Generator

```bash
# Initialize typesafe-i18n
npx typesafe-i18n setup

# Watch mode - regenerates types on locale changes
npx typesafe-i18n

# Generate types once
npx typesafe-i18n --no-watch
```

## Configuration

```typescript
// .typesafe-i18n.json
{
  "$schema": "https://unpkg.com/typesafe-i18n/schema/typesafe-i18n.json",
  "baseLocale": "en",
  "locales": ["en", "de", "fr", "es"],
  "outputPath": "src/i18n/{locale}",
  "generateOnlyTypes": false,
  "adapter": "react"
}
```

## Additional Resources

- typesafe-i18n docs: https://github.com/ivanhofer/typesafe-i18n
- React adapter: https://github.com/ivanhofer/typesafe-i18n/tree/main/packages/adapter-react
