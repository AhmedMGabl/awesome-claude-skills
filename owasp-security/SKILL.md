---
name: owasp-security
description: OWASP security patterns covering Top 10 vulnerabilities, injection prevention, authentication hardening, XSS mitigation, CSRF protection, CSP headers, and security testing.
---

# OWASP Security

This skill should be used when implementing web application security. It covers OWASP Top 10 vulnerabilities, injection prevention, authentication hardening, XSS, CSRF, CSP, and security testing.

## When to Use This Skill

Use this skill when you need to:

- Prevent OWASP Top 10 vulnerabilities
- Implement input validation and sanitization
- Harden authentication and session management
- Configure security headers (CSP, CORS, etc.)
- Perform security testing and code review

## SQL Injection Prevention

```typescript
// VULNERABLE - never do this
const query = `SELECT * FROM users WHERE id = '${userId}'`;

// SAFE - parameterized queries
const result = await db.query("SELECT * FROM users WHERE id = $1", [userId]);

// SAFE - ORM with parameterized methods
const user = await prisma.user.findUnique({ where: { id: userId } });

// SAFE - prepared statements
const stmt = db.prepare("SELECT * FROM users WHERE email = ? AND status = ?");
const user = stmt.get(email, "active");
```

## XSS Prevention

```typescript
// Server-side: sanitize HTML input with DOMPurify
import DOMPurify from "isomorphic-dompurify";

const cleanHtml = DOMPurify.sanitize(userInput, {
  ALLOWED_TAGS: ["b", "i", "em", "strong", "a", "p"],
  ALLOWED_ATTR: ["href", "title"],
});

// Always sanitize before rendering user-generated HTML
// In React, prefer text content over raw HTML injection
// When raw HTML is unavoidable, always sanitize with DOMPurify first

// Escape utility for template contexts
function escapeHtml(str: string): string {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
```

## CSRF Protection

```typescript
// Express with csurf
import csrf from "csurf";

const csrfProtection = csrf({ cookie: true });
app.use(csrfProtection);

app.get("/form", (req, res) => {
  res.render("form", { csrfToken: req.csrfToken() });
});

// SameSite cookies
res.cookie("session", token, {
  httpOnly: true,
  secure: true,
  sameSite: "strict",
  maxAge: 3600000,
});
```

## Security Headers

```typescript
// Helmet.js for Express
import helmet from "helmet";

app.use(helmet());

// Content Security Policy
app.use(
  helmet.contentSecurityPolicy({
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'nonce-abc123'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:", "https:"],
      connectSrc: ["'self'", "https://api.example.com"],
      fontSrc: ["'self'", "https://fonts.gstatic.com"],
      frameSrc: ["'none'"],
      objectSrc: ["'none'"],
    },
  })
);

// Additional headers
app.use(helmet.hsts({ maxAge: 31536000, includeSubDomains: true }));
app.use(helmet.noSniff());
app.use(helmet.frameguard({ action: "deny" }));
```

## Authentication Hardening

```typescript
import bcrypt from "bcrypt";

// Password hashing
const SALT_ROUNDS = 12;
const hash = await bcrypt.hash(password, SALT_ROUNDS);
const isValid = await bcrypt.compare(password, hash);

// Rate limiting login attempts
import rateLimit from "express-rate-limit";

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5,
  message: "Too many login attempts, please try again later",
  standardHeaders: true,
  legacyHeaders: false,
});

app.post("/login", loginLimiter, loginHandler);

// Session configuration
app.use(session({
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: true,
    httpOnly: true,
    sameSite: "strict",
    maxAge: 1800000, // 30 minutes
  },
}));
```

## Input Validation

```typescript
import { z } from "zod";

const userSchema = z.object({
  email: z.string().email().max(254),
  password: z.string().min(8).max(128),
  name: z.string().min(1).max(100).regex(/^[a-zA-Z\s]+$/),
  age: z.number().int().min(13).max(150).optional(),
});

// Validate and reject invalid input
app.post("/users", (req, res) => {
  const result = userSchema.safeParse(req.body);
  if (!result.success) {
    return res.status(400).json({ errors: result.error.flatten() });
  }
  // Proceed with validated data
});
```

## Additional Resources

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- OWASP Cheat Sheets: https://cheatsheetseries.owasp.org/
- Security Headers: https://securityheaders.com/
