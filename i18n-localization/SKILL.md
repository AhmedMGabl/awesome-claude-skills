---
name: i18n-localization
description: Internationalization and localization covering react-intl/FormatJS, next-intl, i18next, ICU message format, pluralization rules, date/number formatting with the Intl API, RTL layout support, translation workflows, locale detection, and language switching patterns. This skill should be used when building multilingual applications or adding i18n support to existing projects.
---

# Internationalization & Localization

This skill should be used when building multilingual applications, adding translation support, formatting dates and numbers for different locales, implementing RTL layouts, or setting up translation workflows.

## ICU Message Format

ICU is the standard message syntax used by react-intl, next-intl, and FormatJS.

```
# Interpolation
Hello, {name}!

# Plurals
{count, plural, =0 {No items} one {1 item} other {{count} items}}

# Select (gender/category)
{gender, select, male {He} female {She} other {They}} left a comment.

# Nested plural + select
{gender, select,
  male {{count, plural, one {He has # follower} other {He has # followers}}}
  other {{count, plural, one {They have # follower} other {They have # followers}}}
}
```

## React with next-intl

```json
// messages/en.json
{
  "HomePage": {
    "title": "Welcome",
    "greeting": "Hello, {name}!",
    "itemCount": "{count, plural, =0 {No items} one {1 item} other {{count} items}}"
  }
}
```

```tsx
// app/[locale]/page.tsx
import { useTranslations } from "next-intl";

export default function HomePage() {
  const t = useTranslations("HomePage");
  return (
    <main>
      <h1>{t("title")}</h1>
      <p>{t("greeting", { name: "Alice" })}</p>
      <p>{t("itemCount", { count: 5 })}</p>
    </main>
  );
}
```

```tsx
// components/LocaleSwitcher.tsx
"use client";
import { useLocale } from "next-intl";
import { useRouter, usePathname } from "next-intl/navigation";

const locales = ["en", "fr", "ar", "ja"] as const;

export default function LocaleSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  function handleChange(event: React.ChangeEvent<HTMLSelectElement>) {
    router.replace(pathname, { locale: event.target.value });
  }

  return (
    <select value={locale} onChange={handleChange} aria-label="Select language">
      {locales.map((loc) => (
        <option key={loc} value={loc}>{loc.toUpperCase()}</option>
      ))}
    </select>
  );
}
```

## React with react-intl (FormatJS)

```tsx
import { IntlProvider, FormattedMessage, useIntl } from "react-intl";
import type { ReactNode } from "react";
import enMessages from "../lang/en.json";
import frMessages from "../lang/fr.json";

const messagesMap: Record<string, Record<string, string>> = { en: enMessages, fr: frMessages };

export default function AppIntlProvider({ locale, children }: { locale: string; children: ReactNode }) {
  return (
    <IntlProvider locale={locale} messages={messagesMap[locale] ?? enMessages} defaultLocale="en">
      {children}
    </IntlProvider>
  );
}

// Usage in components
function OrderSummary({ itemCount }: { itemCount: number }) {
  const intl = useIntl();
  const label = intl.formatMessage(
    { id: "order.summary", defaultMessage: "{count, plural, one {# item} other {# items}}" },
    { count: itemCount }
  );
  return (
    <section aria-label={label}>
      <FormattedMessage id="order.heading" defaultMessage="Your Order" />
    </section>
  );
}
```

## Node.js with i18next

```typescript
// i18n.ts
import i18next from "i18next";
import Backend from "i18next-fs-backend";
import middleware from "i18next-http-middleware";

await i18next.use(Backend).use(middleware.LanguageDetector).init({
  fallbackLng: "en",
  supportedLngs: ["en", "fr", "de", "ar", "ja"],
  backend: { loadPath: "./locales/{{lng}}/{{ns}}.json" },
  detection: { order: ["header", "querystring", "cookie"], lookupHeader: "accept-language" },
});

// Express integration
import express from "express";
const app = express();
app.use(middleware.handle(i18next));

app.get("/api/welcome", (req, res) => {
  res.json({ message: req.t("welcome", { name: req.query.name ?? "Guest" }), locale: req.language });
});
```

```
# Translation file structure
locales/en/translation.json  =>  { "welcome": "Welcome, {{name}}!" }
locales/fr/translation.json  =>  { "welcome": "Bienvenue, {{name}} !" }
```

## Python with gettext and Babel

```python
from gettext import gettext as _, ngettext
import gettext, os

def setup_locale(lang: str) -> None:
    t = gettext.translation("messages", os.path.join(os.path.dirname(__file__), "locales"),
                            languages=[lang], fallback=True)
    t.install()

def cart_message(count: int) -> str:
    return ngettext("{count} item in cart", "{count} items in cart", count).format(count=count)
```

```bash
pybabel extract -F babel.cfg -o locales/messages.pot .   # Extract strings
pybabel init -i locales/messages.pot -d locales -l fr     # Init locale
pybabel compile -d locales                                # Compile .po to .mo
pybabel update -i locales/messages.pot -d locales         # Update after changes
```

## Intl API: Date and Number Formatting

```typescript
function formatDate(date: Date, locale: string): string {
  return new Intl.DateTimeFormat(locale, { year: "numeric", month: "long", day: "numeric" }).format(date);
}
// "January 15, 2026" (en-US) | "15 janvier 2026" (fr-FR) | "2026年1月15日" (ja-JP)

function formatRelativeTime(value: number, unit: Intl.RelativeTimeFormatUnit, locale: string): string {
  return new Intl.RelativeTimeFormat(locale, { numeric: "auto" }).format(value, unit);
}
// formatRelativeTime(-1, "day", "en") => "yesterday"
// formatRelativeTime(-1, "day", "fr") => "hier"

function formatCurrency(amount: number, currency: string, locale: string): string {
  return new Intl.NumberFormat(locale, { style: "currency", currency }).format(amount);
}
// formatCurrency(1234.5, "USD", "en-US") => "$1,234.50"
// formatCurrency(1234.5, "EUR", "de-DE") => "1.234,50 €"

function formatCompact(value: number, locale: string): string {
  return new Intl.NumberFormat(locale, { notation: "compact" }).format(value);
}
// formatCompact(1500000, "en") => "1.5M" | formatCompact(1500000, "ja") => "150万"
```

## RTL Layout Support

### CSS Logical Properties

```css
/* Use logical properties so layouts adapt automatically for RTL locales */
.card {
  margin-inline-start: 1rem;    /* replaces margin-left */
  padding-inline-end: 2rem;     /* replaces padding-right */
  text-align: start;            /* replaces text-align: left */
  border-inline-start: 3px solid blue; /* replaces border-left */
}
```

| Physical             | Logical                    |
|----------------------|----------------------------|
| `margin-left/right`  | `margin-inline-start/end`  |
| `padding-left/right` | `padding-inline-start/end` |
| `border-left/right`  | `border-inline-start/end`  |
| `left/right`         | `inset-inline-start/end`   |
| `text-align: left`   | `text-align: start`        |
| `width / height`     | `inline-size / block-size` |

### Dynamic Direction in React

```tsx
import { useLocale } from "next-intl";

const rtlLocales = new Set(["ar", "he", "fa", "ur"]);

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const locale = useLocale();
  const dir = rtlLocales.has(locale) ? "rtl" : "ltr";
  return <html lang={locale} dir={dir}><body>{children}</body></html>;
}
```

## Locale Detection

```typescript
// Browser-side
function detectLocale(supported: string[], fallback: string): string {
  for (const lang of navigator.languages ?? [navigator.language]) {
    const exact = supported.find((s) => s === lang);
    if (exact) return exact;
    const partial = supported.find((s) => s.startsWith(lang.split("-")[0]));
    if (partial) return partial;
  }
  return fallback;
}

// Server-side (Accept-Language header)
function parseAcceptLanguage(header: string, supported: string[], fallback: string): string {
  const entries = header.split(",").map((part) => {
    const [lang, q] = part.trim().split(";q=");
    return { lang: lang.trim(), quality: q ? parseFloat(q) : 1.0 };
  }).sort((a, b) => b.quality - a.quality);

  for (const { lang } of entries) {
    const match = supported.find((s) => s === lang || s.startsWith(lang.split("-")[0]));
    if (match) return match;
  }
  return fallback;
}
```

## Translation Workflow Checklist

- [ ] All user-visible strings extracted into message files (no hardcoded text)
- [ ] ICU message format used for plurals and gendered text
- [ ] Dates, numbers, and currencies formatted with the Intl API
- [ ] CSS uses logical properties for RTL compatibility
- [ ] `lang` and `dir` attributes set on the `<html>` element
- [ ] Locale detection via Accept-Language header and/or browser API
- [ ] Language switcher UI allows users to override detected locale
- [ ] Fallback locale configured for missing translations
- [ ] UI layout accounts for text expansion (some languages need 30-40% more space)
