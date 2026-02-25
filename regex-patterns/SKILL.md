---
name: regex-patterns
description: Regular expression patterns and techniques covering common validation patterns (email, URL, phone), text extraction, lookaheads/lookbehinds, named groups, Unicode support, performance optimization, and language-specific regex APIs for JavaScript, Python, and Go.
---

# Regex Patterns

This skill should be used when writing, debugging, or optimizing regular expressions. It covers common validation patterns, advanced features, and language-specific APIs.

## When to Use This Skill

Use this skill when you need to:

- Validate input formats (email, phone, URL, etc.)
- Extract data from text or logs
- Search and replace with complex patterns
- Parse structured text formats
- Optimize regex performance

## Common Validation Patterns

```javascript
// Email (simplified, covers 99% of valid emails)
/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/

// URL
/^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&/=]*)$/

// Phone (international, flexible)
/^\+?[1-9]\d{1,14}$/

// US Phone
/^\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})$/

// UUID v4
/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i

// ISO Date (YYYY-MM-DD)
/^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/

// IPv4
/^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$/

// Hex color
/^#([0-9a-f]{3}|[0-9a-f]{6}|[0-9a-f]{8})$/i

// Semantic version
/^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$/

// Strong password (8+ chars, upper, lower, digit, special)
/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/

// Slug (URL-safe)
/^[a-z0-9]+(-[a-z0-9]+)*$/
```

## Named Groups and Extraction

```javascript
// Named capture groups
const dateRegex = /(?<year>\d{4})-(?<month>\d{2})-(?<day>\d{2})/;
const match = "2024-12-25".match(dateRegex);
// match.groups = { year: "2024", month: "12", day: "25" }

// Extract structured data from log lines
const logRegex = /^\[(?<timestamp>[^\]]+)\]\s+(?<level>INFO|WARN|ERROR)\s+(?<message>.+)$/;
const log = '[2024-01-15T10:30:00Z] ERROR Connection timeout to database';
const { groups } = log.match(logRegex);
// groups = { timestamp: "2024-01-15T10:30:00Z", level: "ERROR", message: "Connection timeout to database" }

// Parse URL components
const urlRegex = /^(?<protocol>https?):\/\/(?<host>[^/:]+)(?::(?<port>\d+))?(?<path>\/[^?#]*)?(?:\?(?<query>[^#]*))?(?:#(?<hash>.*))?$/;
```

## Lookahead and Lookbehind

```javascript
// Positive lookahead (?=...) — match only if followed by
/\d+(?=px)/g                     // "12px 3em 5px" → ["12", "5"]

// Negative lookahead (?!...) — match only if NOT followed by
/\d+(?!px)/g                     // "12px 3em 5px" → ["3", "5"] (the "5" from "5px" won't match due to "px")

// Positive lookbehind (?<=...) — match only if preceded by
/(?<=\$)\d+(\.\d{2})?/g         // "$12.50 and €30" → ["12.50"]

// Negative lookbehind (?<!...) — match only if NOT preceded by
/(?<!\\)\"/g                     // Match " not preceded by backslash

// Password validation with lookaheads
/^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*]).{8,}$/
// Requires: uppercase + lowercase + digit + special, min 8 chars
```

## JavaScript API

```javascript
// matchAll — iterate all matches
const text = "Call 555-1234 or 555-5678";
for (const match of text.matchAll(/(\d{3})-(\d{4})/g)) {
  console.log(`Full: ${match[0]}, Area: ${match[1]}, Number: ${match[2]}`);
}

// replaceAll with function
"hello world".replaceAll(/\b\w/g, (char) => char.toUpperCase());
// "Hello World"

// split with captured groups (keeps delimiters)
"one,two;three".split(/([,;])/);
// ["one", ",", "two", ";", "three"]

// Flags
// g = global, i = case-insensitive, m = multiline, s = dotAll, u = unicode, d = indices
const regex = new RegExp("pattern", "giu");
```

## Python API

```python
import re

# Compile for reuse (performance)
email_re = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
email_re.match("test@example.com")  # Match object or None

# findall — all matches
re.findall(r'\b\d+\b', "I have 3 cats and 7 dogs")  # ['3', '7']

# sub — replace
re.sub(r'\b(\w)', lambda m: m.group(1).upper(), "hello world")  # "Hello World"

# Named groups
m = re.match(r'(?P<year>\d{4})-(?P<month>\d{2})', "2024-12")
m.group('year')   # '2024'
m.groupdict()     # {'year': '2024', 'month': '12'}

# VERBOSE flag for readable patterns
phone_re = re.compile(r"""
    ^
    (\+\d{1,3})?    # Optional country code
    [-.\s]?          # Optional separator
    \(?(\d{3})\)?    # Area code
    [-.\s]?          # Optional separator
    (\d{3})          # First 3 digits
    [-.\s]?          # Optional separator
    (\d{4})          # Last 4 digits
    $
""", re.VERBOSE)
```

## Performance Tips

```
REGEX PERFORMANCE RULES:

1. Avoid catastrophic backtracking:
   BAD:  (a+)+$     — exponential backtracking on "aaaaX"
   GOOD: a+$        — linear

2. Be specific — avoid .* when possible:
   BAD:  <.*>       — greedy, matches "<a>text</a>" as one match
   GOOD: <[^>]*>    — matches individual tags

3. Use non-capturing groups when you don't need capture:
   BAD:  (foo|bar)
   GOOD: (?:foo|bar)

4. Anchor when possible:
   Faster: ^pattern$
   Slower: pattern (searches entire string)

5. Use possessive quantifiers or atomic groups where available:
   a++b instead of a+b (prevents backtracking)

6. Compile and reuse regex objects instead of re-creating
```

## Additional Resources

- Regex101 (tester): https://regex101.com/
- Regexr (visual): https://regexr.com/
- MDN RegExp: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/RegExp
- Python re module: https://docs.python.org/3/library/re.html
