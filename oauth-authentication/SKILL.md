---
name: oauth-authentication
description: OAuth 2.0 and authentication implementation covering Authorization Code flow with PKCE, JWT token management, session handling, passport.js strategies, NextAuth.js/Auth.js configuration, social login providers, refresh token rotation, RBAC patterns, and secure cookie settings for web applications.
---

# OAuth & Authentication

This skill should be used when implementing authentication and authorization in web applications. It covers OAuth 2.0 flows, JWT management, session handling, and popular auth libraries.

## When to Use This Skill

Use this skill when you need to:

- Implement OAuth 2.0 / OpenID Connect flows
- Add social login (Google, GitHub, etc.)
- Manage JWTs and refresh tokens
- Set up session-based authentication
- Implement role-based access control (RBAC)
- Configure Auth.js (NextAuth) or Passport.js

## Auth.js (NextAuth.js) Setup

```typescript
// auth.ts — Auth.js v5
import NextAuth from "next-auth";
import GitHub from "next-auth/providers/github";
import Google from "next-auth/providers/google";
import Credentials from "next-auth/providers/credentials";
import { PrismaAdapter } from "@auth/prisma-adapter";
import { prisma } from "@/lib/prisma";
import bcrypt from "bcryptjs";

export const { handlers, auth, signIn, signOut } = NextAuth({
  adapter: PrismaAdapter(prisma),
  providers: [
    GitHub({ clientId: process.env.GITHUB_ID!, clientSecret: process.env.GITHUB_SECRET! }),
    Google({ clientId: process.env.GOOGLE_ID!, clientSecret: process.env.GOOGLE_SECRET! }),
    Credentials({
      credentials: { email: { type: "email" }, password: { type: "password" } },
      async authorize(credentials) {
        const user = await prisma.user.findUnique({ where: { email: credentials.email as string } });
        if (!user?.passwordHash) return null;
        const valid = await bcrypt.compare(credentials.password as string, user.passwordHash);
        return valid ? user : null;
      },
    }),
  ],
  callbacks: {
    async session({ session, token }) {
      if (token.sub) session.user.id = token.sub;
      if (token.role) session.user.role = token.role as string;
      return session;
    },
    async jwt({ token, user }) {
      if (user) token.role = (user as any).role;
      return token;
    },
  },
  pages: { signIn: "/login", error: "/auth/error" },
});
```

```typescript
// middleware.ts — Protect routes
import { auth } from "./auth";

export default auth((req) => {
  const isLoggedIn = !!req.auth;
  const isProtected = req.nextUrl.pathname.startsWith("/dashboard");

  if (isProtected && !isLoggedIn) {
    return Response.redirect(new URL("/login", req.nextUrl));
  }
});

export const config = { matcher: ["/dashboard/:path*", "/api/protected/:path*"] };
```

## JWT Token Management

```typescript
import jwt from "jsonwebtoken";

const ACCESS_SECRET = process.env.JWT_ACCESS_SECRET!;
const REFRESH_SECRET = process.env.JWT_REFRESH_SECRET!;

interface TokenPayload { userId: string; role: string; }

function generateTokens(payload: TokenPayload) {
  const accessToken = jwt.sign(payload, ACCESS_SECRET, { expiresIn: "15m" });
  const refreshToken = jwt.sign({ userId: payload.userId }, REFRESH_SECRET, { expiresIn: "7d" });
  return { accessToken, refreshToken };
}

function verifyAccess(token: string): TokenPayload {
  return jwt.verify(token, ACCESS_SECRET) as TokenPayload;
}

// Refresh token rotation — issue new refresh token on each use
async function rotateRefreshToken(oldRefreshToken: string) {
  const { userId } = jwt.verify(oldRefreshToken, REFRESH_SECRET) as { userId: string };

  // Invalidate old token in database
  const stored = await db.refreshToken.findUnique({ where: { token: oldRefreshToken } });
  if (!stored || stored.revoked) throw new Error("Invalid refresh token");

  await db.refreshToken.update({ where: { id: stored.id }, data: { revoked: true } });

  const user = await db.user.findUniqueOrThrow({ where: { id: userId } });
  const tokens = generateTokens({ userId: user.id, role: user.role });

  await db.refreshToken.create({ data: { token: tokens.refreshToken, userId: user.id } });
  return tokens;
}
```

## Express.js Auth Middleware

```typescript
import { Request, Response, NextFunction } from "express";

// JWT middleware
function authenticate(req: Request, res: Response, next: NextFunction) {
  const header = req.headers.authorization;
  if (!header?.startsWith("Bearer ")) return res.status(401).json({ error: "Missing token" });

  try {
    const payload = verifyAccess(header.slice(7));
    req.user = payload;
    next();
  } catch {
    return res.status(401).json({ error: "Invalid or expired token" });
  }
}

// RBAC middleware
function authorize(...roles: string[]) {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user || !roles.includes(req.user.role)) {
      return res.status(403).json({ error: "Insufficient permissions" });
    }
    next();
  };
}

// Usage
app.get("/admin/users", authenticate, authorize("admin"), (req, res) => {
  // Only admins reach here
});
```

## Secure Cookie Settings

```typescript
// Cookie configuration for tokens
const cookieOptions = {
  httpOnly: true,       // Not accessible via JavaScript
  secure: true,         // HTTPS only
  sameSite: "lax" as const,  // CSRF protection
  path: "/",
  maxAge: 7 * 24 * 60 * 60,  // 7 days (refresh token)
};

// Set refresh token as HTTP-only cookie
res.cookie("refresh_token", refreshToken, cookieOptions);

// Access token goes in response body (stored in memory, not localStorage)
res.json({ accessToken, expiresIn: 900 });
```

## OAuth 2.0 Authorization Code + PKCE

```typescript
import crypto from "crypto";

// Client-side: Generate PKCE challenge
function generatePKCE() {
  const verifier = crypto.randomBytes(32).toString("base64url");
  const challenge = crypto.createHash("sha256").update(verifier).digest("base64url");
  return { verifier, challenge };
}

// Step 1: Redirect to authorization endpoint
const { verifier, challenge } = generatePKCE();
// Store verifier in session
const authUrl = new URL("https://provider.com/authorize");
authUrl.searchParams.set("client_id", CLIENT_ID);
authUrl.searchParams.set("redirect_uri", REDIRECT_URI);
authUrl.searchParams.set("response_type", "code");
authUrl.searchParams.set("scope", "openid profile email");
authUrl.searchParams.set("code_challenge", challenge);
authUrl.searchParams.set("code_challenge_method", "S256");
authUrl.searchParams.set("state", crypto.randomBytes(16).toString("hex"));

// Step 2: Exchange code for tokens (server-side)
async function exchangeCode(code: string, codeVerifier: string) {
  const response = await fetch("https://provider.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "authorization_code",
      client_id: CLIENT_ID,
      code,
      redirect_uri: REDIRECT_URI,
      code_verifier: codeVerifier,
    }),
  });
  return response.json(); // { access_token, refresh_token, id_token }
}
```

## Python FastAPI Auth

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await get_user(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_role(*roles: str):
    async def check(user = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return check

@app.get("/admin/dashboard")
async def admin_dashboard(user = Depends(require_role("admin"))):
    return {"message": f"Welcome admin {user.name}"}
```

## Additional Resources

- Auth.js: https://authjs.dev/
- OAuth 2.0 RFC 6749: https://datatracker.ietf.org/doc/html/rfc6749
- PKCE RFC 7636: https://datatracker.ietf.org/doc/html/rfc7636
- JWT.io: https://jwt.io/
- OWASP Auth Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
