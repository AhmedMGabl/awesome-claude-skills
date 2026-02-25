---
name: date-handling
description: Date and time handling covering date-fns, dayjs, Temporal API proposal, timezone management with Luxon, formatting, parsing, duration calculations, relative time, and internationalization with Intl.DateTimeFormat. This skill should be used when working with dates, times, timezones, durations, or locale-aware date formatting in JavaScript and TypeScript projects.
---

# Date Handling

This skill should be used when formatting, parsing, or manipulating dates and times in JavaScript or TypeScript, selecting a date library, managing timezones, computing durations, or formatting dates for different locales.

## When to Use This Skill

- Format or parse dates and times in JavaScript/TypeScript
- Compute date differences, durations, or relative time strings
- Handle timezone conversions and DST-safe arithmetic
- Generate date ranges, calculate business days, or model recurring dates
- Format dates for multiple locales using `Intl.DateTimeFormat`
- Decide between date-fns, dayjs, Luxon, or the Temporal API

## Library Comparison

| Library        | Size (min+gz) | Immutable | Tree-shakeable | Timezone support       | Status          |
|----------------|--------------|-----------|----------------|------------------------|-----------------|
| date-fns v3    | ~13 kB       | Yes       | Yes            | Via date-fns-tz        | Stable          |
| dayjs          | ~2 kB        | Yes       | Plugin-based   | Via plugin             | Stable          |
| Luxon          | ~23 kB       | Yes       | Partial        | Built-in (Intl-based)  | Stable          |
| Temporal API   | Native       | Yes       | N/A            | Built-in               | Stage 3 (polyfill available) |
| date-fns-tz    | ~3 kB add-on | Yes       | Yes            | IANA via Intl           | Stable          |

**Choose date-fns** for tree-shaken bundles with comprehensive utilities. **Choose dayjs** for minimal footprint. **Choose Luxon** when robust timezone arithmetic is the primary concern. **Choose Temporal** for new projects that can tolerate a polyfill.

## date-fns

```typescript
import {
  format, parse, parseISO, isValid, compareAsc,
  addDays, subMonths, differenceInDays, differenceInCalendarWeeks,
  startOfMonth, endOfMonth, eachDayOfInterval,
  formatDuration, intervalToDuration,
} from "date-fns";

// Formatting
const d = new Date(2026, 0, 15); // Jan 15 2026
format(d, "yyyy-MM-dd");          // "2026-01-15"
format(d, "MMMM d, yyyy");        // "January 15, 2026"
format(d, "EEE, MMM d 'at' HH:mm"); // "Thu, Jan 15 at 00:00"

// Parsing
const parsed = parse("15/01/2026", "dd/MM/yyyy", new Date());
const fromIso = parseISO("2026-01-15T09:30:00Z");
isValid(parsed); // true

// Arithmetic
addDays(d, 10);         // Jan 25
subMonths(d, 3);        // Oct 15 2025

// Comparison
compareAsc(new Date("2026-01-01"), new Date("2026-06-01")); // -1

// Difference
differenceInDays(new Date("2026-03-01"), new Date("2026-01-15")); // 45

// Duration formatting
const duration = intervalToDuration({
  start: new Date("2026-01-01"),
  end:   new Date("2026-06-15"),
});
formatDuration(duration, { format: ["months", "days"] }); // "5 months 14 days"

// Date ranges
const range = eachDayOfInterval({
  start: startOfMonth(d),
  end:   endOfMonth(d),
}); // Array of 31 Date objects for January 2026
```

### date-fns-tz (timezone support)

```typescript
import { fromZonedTime, toZonedTime, formatInTimeZone } from "date-fns-tz";

const tz = "America/New_York";
const utc = fromZonedTime("2026-01-15 09:00", tz); // UTC Date
const local = toZonedTime(utc, tz);                  // Date in NY wall time
formatInTimeZone(utc, tz, "yyyy-MM-dd HH:mm zzz");  // "2026-01-15 09:00 EST"
```

## dayjs

```typescript
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import duration from "dayjs/plugin/duration";
import timezone from "dayjs/plugin/timezone";
import utc from "dayjs/plugin/utc";
import "dayjs/locale/fr";

dayjs.extend(relativeTime);
dayjs.extend(duration);
dayjs.extend(utc);
dayjs.extend(timezone);

// Basic operations
const d = dayjs("2026-01-15");
d.format("MMMM D, YYYY");  // "January 15, 2026"
d.add(10, "day").toISOString();
d.subtract(3, "month").format("YYYY-MM-DD");
d.diff(dayjs("2025-12-01"), "day"); // 45

// Locale
dayjs("2026-01-15").locale("fr").format("dddd D MMMM YYYY"); // "jeudi 15 janvier 2026"

// Relative time
dayjs("2025-12-01").fromNow();          // "2 months ago"
dayjs("2026-03-01").toNow();            // "in a month"
dayjs.duration(2, "hours").humanize();  // "2 hours"

// Timezone
dayjs.tz("2026-01-15 09:00", "America/New_York").utc().format(); // UTC ISO string
dayjs.utc("2026-01-15T14:00:00Z").tz("Asia/Tokyo").format("HH:mm"); // "23:00"
```

## Temporal API (Stage 3 — use @js-temporal/polyfill)

```typescript
import { Temporal } from "@js-temporal/polyfill";

// PlainDate: date without time or timezone
const date = Temporal.PlainDate.from("2026-01-15");
date.add({ months: 2 });            // 2026-03-15
date.until("2026-06-01").days;      // 137
date.with({ month: 12 });           // 2026-12-15
date.dayOfWeek;                     // 4 (Thursday, ISO: Mon=1)

// ZonedDateTime: timezone-aware instant
const zdt = Temporal.ZonedDateTime.from(
  "2026-01-15T09:00:00[America/New_York]"
);
zdt.add({ hours: 5 }).timeZoneId;       // "America/New_York"
zdt.toInstant().toString();             // "2026-01-15T14:00:00Z"
zdt.withTimeZone("Asia/Tokyo").hour;    // 23

// Duration
const dur = Temporal.Duration.from({ months: 3, days: 5 });
Temporal.PlainDate.from("2026-01-01").add(dur); // 2026-04-06

// Instant: exact point in time (no timezone)
const now = Temporal.Now.instant();
now.epochMilliseconds;
```

## Luxon (timezone-first)

```typescript
import { DateTime, Duration, Interval } from "luxon";

// Create
const dt = DateTime.fromISO("2026-01-15T09:00:00", { zone: "America/New_York" });
const fromMillis = DateTime.fromMillis(Date.now());
const local = DateTime.local(2026, 1, 15, 9, 0);

// Format
dt.toFormat("yyyy-MM-dd HH:mm ZZZZ"); // "2026-01-15 09:00 EST"
dt.toLocaleString(DateTime.DATETIME_FULL); // locale-aware full string

// Timezone conversion
dt.setZone("Asia/Tokyo").hour;   // 23
dt.toUTC().toISO();              // "2026-01-15T14:00:00.000Z"

// Arithmetic (DST-safe)
dt.plus({ months: 2, days: 5 }).toISODate();  // "2026-03-22"
dt.startOf("month").toISODate();              // "2026-01-01"

// Duration
const dur = Duration.fromObject({ hours: 90 });
dur.shiftTo("days", "hours").toHuman(); // "3 days, 18 hours"

// Interval
const interval = Interval.fromDateTimes(dt, dt.plus({ days: 30 }));
interval.count("days"); // 30
interval.contains(DateTime.local(2026, 1, 20)); // true
```

## Intl.DateTimeFormat (built-in i18n)

```typescript
// Basic locale formatting
function formatDate(date: Date, locale: string): string {
  return new Intl.DateTimeFormat(locale, {
    year: "numeric", month: "long", day: "numeric",
  }).format(date);
}
// "January 15, 2026" (en-US) | "15 janvier 2026" (fr-FR) | "2026年1月15日" (ja-JP)

// Timezone-aware formatting
function formatInTz(date: Date, locale: string, timeZone: string): string {
  return new Intl.DateTimeFormat(locale, {
    dateStyle: "medium", timeStyle: "short", timeZone,
  }).format(date);
}

// Relative time
function relativeTime(value: number, unit: Intl.RelativeTimeFormatUnit, locale = "en"): string {
  return new Intl.RelativeTimeFormat(locale, { numeric: "auto" }).format(value, unit);
}
relativeTime(-1, "day");  // "yesterday"
relativeTime(3, "week");  // "in 3 weeks"

// Reuse formatter instance (performance)
const fmt = new Intl.DateTimeFormat("en-US", {
  weekday: "short", month: "short", day: "numeric",
});
fmt.format(new Date("2026-01-15")); // "Thu, Jan 15"
```

## Common Patterns

### Date Ranges

```typescript
import { eachDayOfInterval, eachWeekOfInterval, startOfDay, endOfDay } from "date-fns";

function daysInRange(start: Date, end: Date): Date[] {
  return eachDayOfInterval({ start: startOfDay(start), end: endOfDay(end) });
}
```

### Business Days

```typescript
import { isWeekend, addDays } from "date-fns";

function addBusinessDays(date: Date, days: number): Date {
  let result = date;
  let remaining = days;
  while (remaining > 0) {
    result = addDays(result, 1);
    if (!isWeekend(result)) remaining--;
  }
  return result;
}

function businessDaysBetween(start: Date, end: Date): number {
  let count = 0;
  let current = addDays(start, 1);
  while (current <= end) {
    if (!isWeekend(current)) count++;
    current = addDays(current, 1);
  }
  return count;
}
```

### Recurring Dates

```typescript
import { addWeeks, addMonths, isBefore } from "date-fns";

type Frequency = "weekly" | "monthly";

function generateOccurrences(start: Date, frequency: Frequency, count: number): Date[] {
  const advance = frequency === "weekly" ? addWeeks : addMonths;
  return Array.from({ length: count }, (_, i) => advance(start, i));
}
```

### ISO Week and Quarter

```typescript
import { getISOWeek, getQuarter, startOfISOWeek, startOfQuarter } from "date-fns";

const d = new Date("2026-01-15");
getISOWeek(d);            // 3
getQuarter(d);            // 1
startOfISOWeek(d);        // 2026-01-12 (Monday)
startOfQuarter(d);        // 2026-01-01
```
