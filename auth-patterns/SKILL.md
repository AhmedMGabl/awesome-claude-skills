---
name: auth-patterns
description: Authentication and authorization patterns covering JWT tokens, OAuth 2.0 flows, session management, RBAC, passwordless auth, multi-factor authentication, API key management, and security best practices for web applications.
---

# Authentication & Authorization Patterns

This skill should be used when implementing authentication and authorization in applications. It covers JWT, OAuth 2.0, sessions, role-based access control, and security best practices.

## When to Use This Skill

Use this skill when you need to:

- Implement user authentication (login, signup, password reset)
- Set up OAuth 2.0 with social providers
- Manage JWT tokens (access/refresh token rotation)
- Build role-based access control (RBAC)
- Implement passwordless authentication (magic links, OTP)
- Secure APIs with authentication middleware
- Handle multi-factor authentication (MFA/2FA)

## JWT Authentication

### Token Generation and Verification

```typescript
import jwt from "jsonwebtoken";
import bcrypt from "bcryptjs";

const JWT_SECRET = process.env.JWT_SECRET!;
const JWT_REFRESH_SECRET = process.env.JWT_REFRESH_SECRET!;

interface TokenPayload {
  userId: string;
  email: string;
  role: string;
}

function generateTokens(payload: TokenPayload) {
  const accessToken = jwt.sign(payload, JWT_SECRET, { expiresIn: "15m" });
  const refreshToken = jwt.sign({ userId: payload.userId }, JWT_REFRESH_SECRET, {
    expiresIn: "7d",
  });
  return { accessToken, refreshToken };
}

function verifyAccessToken(token: string): TokenPayload {
  return jwt.verify(token, JWT_SECRET) as TokenPayload;
}

function verifyRefreshToken(token: string): { userId: string } {
  return jwt.verify(token, JWT_REFRESH_SECRET) as { userId: string };
}
```

### Login and Registration

```typescript
async function register(email: string, password: string, name: string) {
  // Check existing user
  const existing = await db.user.findUnique({ where: { email } });
  if (existing) throw new Error("Email already registered");

  // Hash password
  const hashedPassword = await bcrypt.hash(password, 12);

  const user = await db.user.create({
    data: { email, password: hashedPassword, name, role: "user" },
  });

  const tokens = generateTokens({
    userId: user.id,
    email: user.email,
    role: user.role,
  });

  // Store refresh token hash in DB
  await db.refreshToken.create({
    data: {
      token: await bcrypt.hash(tokens.refreshToken, 10),
      userId: user.id,
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
    },
  });

  return { user: { id: user.id, email: user.email, name: user.name }, ...tokens };
}

async function login(email: string, password: string) {
  const user = await db.user.findUnique({ where: { email } });
  if (!user) throw new Error("Invalid credentials");

  const valid = await bcrypt.compare(password, user.password);
  if (!valid) throw new Error("Invalid credentials");

  const tokens = generateTokens({
    userId: user.id,
    email: user.email,
    role: user.role,
  });

  await db.refreshToken.create({
    data: {
      token: await bcrypt.hash(tokens.refreshToken, 10),
      userId: user.id,
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
    },
  });

  return { user: { id: user.id, email: user.email, role: user.role }, ...tokens };
}
```

### Token Refresh with Rotation

```typescript
async function refreshAccessToken(refreshToken: string) {
  const payload = verifyRefreshToken(refreshToken);

  // Find stored refresh tokens for user
  const storedTokens = await db.refreshToken.findMany({
    where: { userId: payload.userId, expiresAt: { gt: new Date() } },
  });

  // Verify refresh token matches stored hash
  let validToken = null;
  for (const stored of storedTokens) {
    if (await bcrypt.compare(refreshToken, stored.token)) {
      validToken = stored;
      break;
    }
  }

  if (!validToken) {
    // Possible token reuse attack — revoke all tokens
    await db.refreshToken.deleteMany({ where: { userId: payload.userId } });
    throw new Error("Invalid refresh token");
  }

  // Rotate: delete old, create new
  await db.refreshToken.delete({ where: { id: validToken.id } });

  const user = await db.user.findUniqueOrThrow({ where: { id: payload.userId } });
  const tokens = generateTokens({
    userId: user.id,
    email: user.email,
    role: user.role,
  });

  await db.refreshToken.create({
    data: {
      token: await bcrypt.hash(tokens.refreshToken, 10),
      userId: user.id,
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
    },
  });

  return tokens;
}
```

### Auth Middleware

```typescript
// Express middleware
function authenticate(req: Request, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;
  if (!authHeader?.startsWith("Bearer ")) {
    return res.status(401).json({ error: "Missing token" });
  }

  try {
    const token = authHeader.slice(7);
    const payload = verifyAccessToken(token);
    req.user = payload;
    next();
  } catch (err) {
    return res.status(401).json({ error: "Invalid or expired token" });
  }
}

// Role-based authorization
function authorize(...roles: string[]) {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user || !roles.includes(req.user.role)) {
      return res.status(403).json({ error: "Insufficient permissions" });
    }
    next();
  };
}

// Usage
app.get("/api/admin/users", authenticate, authorize("admin"), getUsers);
app.get("/api/profile", authenticate, getProfile);
```

## OAuth 2.0

### Google OAuth with Passport.js

```typescript
import passport from "passport";
import { Strategy as GoogleStrategy } from "passport-google-oauth20";

passport.use(
  new GoogleStrategy(
    {
      clientID: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      callbackURL: "/auth/google/callback",
    },
    async (accessToken, refreshToken, profile, done) => {
      let user = await db.user.findUnique({
        where: { providerId: profile.id },
      });

      if (!user) {
        user = await db.user.create({
          data: {
            email: profile.emails?.[0]?.value ?? "",
            name: profile.displayName,
            provider: "google",
            providerId: profile.id,
            avatar: profile.photos?.[0]?.value,
          },
        });
      }

      done(null, user);
    }
  )
);

// Routes
app.get("/auth/google", passport.authenticate("google", { scope: ["profile", "email"] }));

app.get(
  "/auth/google/callback",
  passport.authenticate("google", { session: false }),
  (req, res) => {
    const tokens = generateTokens({
      userId: req.user.id,
      email: req.user.email,
      role: req.user.role,
    });
    // Redirect with tokens (use httpOnly cookies in production)
    res.redirect(`${process.env.CLIENT_URL}/auth/callback?token=${tokens.accessToken}`);
  }
);
```

## Session-Based Auth (Cookie)

```typescript
// HTTP-only cookie approach (more secure than localStorage)
function setAuthCookies(res: Response, tokens: { accessToken: string; refreshToken: string }) {
  res.cookie("access_token", tokens.accessToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    maxAge: 15 * 60 * 1000, // 15 minutes
    path: "/",
  });

  res.cookie("refresh_token", tokens.refreshToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
    path: "/api/auth/refresh",
  });
}

function clearAuthCookies(res: Response) {
  res.clearCookie("access_token");
  res.clearCookie("refresh_token");
}
```

## Passwordless Authentication

```typescript
// Magic link
async function sendMagicLink(email: string) {
  const token = crypto.randomBytes(32).toString("hex");
  const hashedToken = await bcrypt.hash(token, 10);

  await db.magicLink.create({
    data: {
      email,
      token: hashedToken,
      expiresAt: new Date(Date.now() + 15 * 60 * 1000), // 15 min
    },
  });

  const url = `${process.env.APP_URL}/auth/verify?token=${token}&email=${encodeURIComponent(email)}`;
  await sendEmail(email, "Your login link", `Click here to log in: ${url}`);
}

// OTP (Time-based One-Time Password) for 2FA
import { authenticator } from "otplib";
import QRCode from "qrcode";

async function setup2FA(userId: string) {
  const secret = authenticator.generateSecret();
  await db.user.update({ where: { id: userId }, data: { totpSecret: secret } });

  const otpauthUrl = authenticator.keyuri(userId, "MyApp", secret);
  const qrCodeUrl = await QRCode.toDataURL(otpauthUrl);
  return { secret, qrCodeUrl };
}

function verify2FA(secret: string, token: string): boolean {
  return authenticator.verify({ token, secret });
}
```

## RBAC (Role-Based Access Control)

```typescript
// Permission-based RBAC
const PERMISSIONS = {
  admin: ["users:read", "users:write", "users:delete", "posts:read", "posts:write", "posts:delete", "settings:manage"],
  editor: ["posts:read", "posts:write", "posts:delete", "users:read"],
  viewer: ["posts:read", "users:read"],
} as const;

type Role = keyof typeof PERMISSIONS;

function hasPermission(role: Role, permission: string): boolean {
  return (PERMISSIONS[role] as readonly string[]).includes(permission);
}

// Middleware
function requirePermission(permission: string) {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user || !hasPermission(req.user.role as Role, permission)) {
      return res.status(403).json({ error: "Forbidden" });
    }
    next();
  };
}

// Usage
app.delete("/api/users/:id", authenticate, requirePermission("users:delete"), deleteUser);
```

## Security Best Practices

```typescript
// Rate limiting for auth endpoints
import rateLimit from "express-rate-limit";

const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10, // 10 attempts per 15 minutes
  message: { error: "Too many attempts, try again later" },
  standardHeaders: true,
});

app.use("/api/auth/login", authLimiter);
app.use("/api/auth/register", authLimiter);

// Password validation
function validatePassword(password: string): string[] {
  const errors: string[] = [];
  if (password.length < 8) errors.push("At least 8 characters");
  if (!/[A-Z]/.test(password)) errors.push("At least one uppercase letter");
  if (!/[a-z]/.test(password)) errors.push("At least one lowercase letter");
  if (!/[0-9]/.test(password)) errors.push("At least one number");
  return errors;
}

// CSRF protection for cookie-based auth
import csrf from "csurf";
app.use(csrf({ cookie: { httpOnly: true, sameSite: "strict" } }));
```

## Additional Resources

- OWASP Authentication Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- JWT.io: https://jwt.io/
- Passport.js: https://www.passportjs.org/
- Auth.js (NextAuth): https://authjs.dev/
