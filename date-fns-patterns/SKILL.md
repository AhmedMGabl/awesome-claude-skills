---
name: date-fns-patterns
description: date-fns utility patterns covering date formatting, parsing, comparison, interval operations, timezone handling with date-fns-tz, relative time, duration, and locale-aware date display.
---

# date-fns Patterns

This skill should be used when working with dates using date-fns. It covers formatting, parsing, comparison, timezone handling, and common date utility patterns.

## When to Use This Skill

Use this skill when you need to:

- Format and parse dates in various formats
- Calculate date differences and intervals
- Handle timezone conversions
- Display relative time (e.g., "2 hours ago")
- Build locale-aware date displays

## Formatting

```typescript
import { format, formatISO, formatDistanceToNow, formatRelative } from "date-fns";

const date = new Date(2024, 2, 15, 14, 30);

format(date, "yyyy-MM-dd");           // "2024-03-15"
format(date, "MMMM do, yyyy");        // "March 15th, 2024"
format(date, "h:mm a");               // "2:30 PM"
format(date, "EEE, MMM d");           // "Fri, Mar 15"
format(date, "yyyy-MM-dd'T'HH:mm:ss"); // "2024-03-15T14:30:00"

formatISO(date);                       // "2024-03-15T14:30:00+00:00"
formatDistanceToNow(date, { addSuffix: true }); // "2 months ago"
formatRelative(date, new Date());      // "last Friday at 2:30 PM"
```

## Parsing

```typescript
import { parse, parseISO, isValid } from "date-fns";

const d1 = parseISO("2024-03-15");
const d2 = parse("15/03/2024", "dd/MM/yyyy", new Date());
const d3 = parse("March 15, 2024", "MMMM d, yyyy", new Date());

// Validate
isValid(d1);                  // true
isValid(new Date("invalid")); // false
```

## Comparison and Checking

```typescript
import {
  isBefore, isAfter, isEqual, isToday, isFuture, isPast,
  isWithinInterval, isSameDay, isSameMonth,
} from "date-fns";

const start = new Date(2024, 0, 1);
const end = new Date(2024, 11, 31);
const now = new Date();

isBefore(start, end);          // true
isAfter(now, start);           // true
isToday(now);                  // true
isFuture(end);                 // depends on current date
isPast(start);                 // depends on current date
isSameDay(now, now);           // true
isWithinInterval(now, { start, end }); // true if now is in 2024
```

## Arithmetic

```typescript
import {
  addDays, addMonths, addYears, subDays, subHours,
  startOfDay, endOfDay, startOfMonth, endOfMonth,
  startOfWeek, endOfWeek,
} from "date-fns";

const now = new Date();

addDays(now, 7);               // 7 days from now
addMonths(now, 3);             // 3 months from now
subDays(now, 30);              // 30 days ago
subHours(now, 2);              // 2 hours ago

startOfDay(now);               // today at 00:00:00
endOfDay(now);                 // today at 23:59:59.999
startOfMonth(now);             // first day of month
endOfMonth(now);               // last day of month
startOfWeek(now, { weekStartsOn: 1 }); // Monday
```

## Intervals and Differences

```typescript
import {
  differenceInDays, differenceInHours, differenceInMinutes,
  intervalToDuration, eachDayOfInterval, eachMonthOfInterval,
} from "date-fns";

const start = new Date(2024, 0, 1);
const end = new Date(2024, 5, 15);

differenceInDays(end, start);    // 166
differenceInHours(end, start);   // ~3984

// Duration breakdown
const duration = intervalToDuration({ start, end });
// { years: 0, months: 5, days: 14, hours: 0, ... }

// Generate array of dates
const days = eachDayOfInterval({ start, end: addDays(start, 6) });
// [Jan 1, Jan 2, ..., Jan 7]

const months = eachMonthOfInterval({ start, end });
// [Jan 1, Feb 1, Mar 1, Apr 1, May 1, Jun 1]
```

## Timezone Handling

```typescript
import { formatInTimeZone, toZonedTime, fromZonedTime } from "date-fns-tz";

const utcDate = new Date("2024-03-15T12:00:00Z");

// Format in specific timezone
formatInTimeZone(utcDate, "America/New_York", "yyyy-MM-dd h:mm a zzz");
// "2024-03-15 8:00 AM EDT"

formatInTimeZone(utcDate, "Asia/Tokyo", "yyyy-MM-dd HH:mm zzz");
// "2024-03-15 21:00 JST"

// Convert UTC to zoned time
const nyTime = toZonedTime(utcDate, "America/New_York");

// Convert zoned time to UTC
const utc = fromZonedTime(new Date(2024, 2, 15, 8, 0), "America/New_York");
```

## Locale Support

```typescript
import { format, formatDistanceToNow } from "date-fns";
import { ja } from "date-fns/locale/ja";
import { de } from "date-fns/locale/de";
import { fr } from "date-fns/locale/fr";

const date = new Date(2024, 2, 15);

format(date, "PPP", { locale: ja });  // "2024年3月15日"
format(date, "PPP", { locale: de });  // "15. März 2024"
format(date, "PPP", { locale: fr });  // "15 mars 2024"

formatDistanceToNow(date, { locale: ja, addSuffix: true }); // "約2ヶ月前"
```

## Additional Resources

- date-fns docs: https://date-fns.org/docs/
- date-fns-tz: https://github.com/marnusw/date-fns-tz
- Format tokens: https://date-fns.org/docs/format
