---
name: next-intl
description: next-intl internationalization patterns covering message definitions, locale routing, middleware configuration, server/client component translation, pluralization, rich text, number/date formatting, and Next.js App Router integration.
---

# next-intl

This skill should be used when adding internationalization to Next.js applications with next-intl. It covers message definitions, routing, middleware, and server/client usage.

## When to Use This Skill

Use this skill when you need to:

- Add multi-language support to Next.js App Router
- Configure locale-based routing with middleware
- Translate content in server and client components
- Format numbers, dates, and pluralized messages
- Handle RTL layouts and locale switching

## Setup and Configuration

```typescript
// i18n/request.ts
import { getRequestConfig } from "next-intl/server";

export default getRequestConfig(async ({ requestLocale }) => {
  const locale = await requestLocale;
  return {
    locale,
    messages: (await import(`../messages/${locale}.json`)).default,
  };
});

// middleware.ts
import createMiddleware from "next-intl/middleware";
import { routing } from "./i18n/routing";

export default createMiddleware(routing);
export const config = { matcher: ["/((?!api|_next|.*\\..*).*)"] };

// i18n/routing.ts
import { defineRouting } from "next-intl/routing";

export const routing = defineRouting({
  locales: ["en", "de", "fr", "ar"],
  defaultLocale: "en",
});
```

## Message Files

```json
// messages/en.json
{
  "common": {
    "welcome": "Welcome to {appName}",
    "loading": "Loading...",
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete"
  },
  "auth": {
    "login": "Log in",
    "logout": "Log out",
    "signUp": "Sign up"
  },
  "users": {
    "count": "You have {count, plural, =0 {no users} one {# user} other {# users}}",
    "greeting": "Hello, {name}!",
    "lastSeen": "Last seen {date, date, medium}",
    "role": "Role: {role, select, admin {Administrator} editor {Editor} other {User}}"
  },
  "errors": {
    "required": "{field} is required",
    "notFound": "Page not found"
  }
}
```

## Server Component Usage

```tsx
// app/[locale]/page.tsx
import { useTranslations } from "next-intl";

export default function HomePage() {
  const t = useTranslations("common");
  const tUsers = useTranslations("users");

  return (
    <div>
      <h1>{t("welcome", { appName: "My App" })}</h1>
      <p>{tUsers("count", { count: 42 })}</p>
      <p>{tUsers("greeting", { name: "Alice" })}</p>
    </div>
  );
}
```

## Client Component Usage

```tsx
"use client";
import { useTranslations } from "next-intl";

export function LoginButton() {
  const t = useTranslations("auth");
  return <button>{t("login")}</button>;
}
```

## Locale Switcher

```tsx
"use client";
import { useLocale } from "next-intl";
import { useRouter, usePathname } from "next-intl/navigation";

export function LocaleSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const switchLocale = (newLocale: string) => {
    router.replace(pathname, { locale: newLocale });
  };

  return (
    <select value={locale} onChange={(e) => switchLocale(e.target.value)}>
      <option value="en">English</option>
      <option value="de">Deutsch</option>
      <option value="fr">Français</option>
      <option value="ar">العربية</option>
    </select>
  );
}
```

## Number and Date Formatting

```tsx
import { useFormatter, useNow } from "next-intl";

function FormattedValues() {
  const format = useFormatter();
  const now = useNow();

  return (
    <div>
      <p>Price: {format.number(49.99, { style: "currency", currency: "USD" })}</p>
      <p>Percent: {format.number(0.85, { style: "percent" })}</p>
      <p>Date: {format.dateTime(now, { dateStyle: "full" })}</p>
      <p>Relative: {format.relativeTime(new Date("2024-01-01"))}</p>
    </div>
  );
}
```

## App Layout

```tsx
// app/[locale]/layout.tsx
import { NextIntlClientProvider } from "next-intl";
import { getMessages } from "next-intl/server";

export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  const messages = await getMessages();

  return (
    <html lang={locale} dir={locale === "ar" ? "rtl" : "ltr"}>
      <body>
        <NextIntlClientProvider messages={messages}>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
```

## Additional Resources

- next-intl docs: https://next-intl-docs.vercel.app/
- App Router setup: https://next-intl-docs.vercel.app/docs/getting-started/app-router
