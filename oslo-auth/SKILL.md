---
name: oslo-auth
description: Oslo authentication utility patterns covering password hashing with Argon2/bcrypt/scrypt, TOTP/HOTP two-factor authentication, OAuth 2.0 helpers, JWT creation and verification, session token generation, and PKCE flow implementation.
---

# Oslo Auth

This skill should be used when implementing authentication utilities with the Oslo library. It covers password hashing, TOTP/HOTP, OAuth helpers, JWT, and session tokens.

## When to Use This Skill

Use this skill when you need to:

- Hash and verify passwords with Argon2, bcrypt, or scrypt
- Generate and verify TOTP/HOTP codes for 2FA
- Create and validate JWTs and session tokens
- Implement OAuth 2.0 authorization flows
- Generate PKCE code verifiers and challenges

## Password Hashing

```typescript
import { Argon2id } from "oslo/password";

const argon2id = new Argon2id();

// Hash password
async function hashPassword(password: string): Promise<string> {
  return await argon2id.hash(password);
}

// Verify password
async function verifyPassword(hash: string, password: string): Promise<boolean> {
  return await argon2id.verify(hash, password);
}

// With bcrypt
import { Bcrypt } from "oslo/password";
const bcrypt = new Bcrypt();
const hash = await bcrypt.hash(password);
const valid = await bcrypt.verify(hash, password);

// With scrypt
import { Scrypt } from "oslo/password";
const scrypt = new Scrypt();
const hash2 = await scrypt.hash(password);
```

## TOTP Two-Factor Authentication

```typescript
import { TOTPController } from "oslo/otp";
import { encodeHex, decodeHex } from "oslo/encoding";

const totp = new TOTPController({
  period: 30, // 30-second window
  digits: 6,
});

// Generate secret for user
function generateTOTPSecret(): string {
  const secret = crypto.getRandomValues(new Uint8Array(20));
  return encodeHex(secret);
}

// Generate OTP URI for QR code
function generateTOTPUri(secret: string, email: string): string {
  const issuer = "MyApp";
  const encoded = encodeHex(new TextEncoder().encode(secret));
  return `otpauth://totp/${issuer}:${email}?secret=${encoded}&issuer=${issuer}&digits=6&period=30`;
}

// Verify TOTP code
async function verifyTOTP(secret: string, code: string): Promise<boolean> {
  const secretBytes = decodeHex(secret);
  return await totp.verify(code, secretBytes);
}
```

## Session Tokens

```typescript
import { generateIdFromEntropySize } from "oslo/crypto";
import { sha256 } from "oslo/crypto";
import { encodeHex } from "oslo/encoding";

// Generate session token
function generateSessionToken(): string {
  return generateIdFromEntropySize(25); // 40-character string
}

// Hash token for storage
async function hashSessionToken(token: string): Promise<string> {
  const hash = await sha256(new TextEncoder().encode(token));
  return encodeHex(hash);
}

// Create session
async function createSession(userId: string) {
  const token = generateSessionToken();
  const hashedToken = await hashSessionToken(token);
  const expiresAt = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000); // 30 days

  await db.session.create({
    data: { id: hashedToken, userId, expiresAt },
  });

  return token; // Return unhashed token to client
}

// Validate session
async function validateSession(token: string) {
  const hashedToken = await hashSessionToken(token);
  const session = await db.session.findUnique({ where: { id: hashedToken } });

  if (!session || session.expiresAt < new Date()) {
    if (session) await db.session.delete({ where: { id: hashedToken } });
    return null;
  }

  return session;
}
```

## OAuth 2.0 Helpers

```typescript
import { OAuth2Client } from "oslo/oauth2";
import { generateState, generateCodeVerifier } from "oslo/oauth2";

const github = new OAuth2Client(
  process.env.GITHUB_CLIENT_ID!,
  "https://github.com/login/oauth/authorize",
  "https://github.com/login/oauth/access_token",
  { redirectURI: "http://localhost:3000/api/auth/callback/github" },
);

// Generate authorization URL
async function getAuthorizationUrl() {
  const state = generateState();
  const url = github.createAuthorizationURL({
    state,
    scopes: ["user:email"],
  });
  return { url: url.toString(), state };
}

// Exchange code for tokens
async function handleCallback(code: string) {
  const tokens = await github.validateAuthorizationCode(code);
  return tokens;
}

// PKCE flow
async function getPKCEAuthorizationUrl() {
  const state = generateState();
  const codeVerifier = generateCodeVerifier();
  const url = github.createAuthorizationURL({
    state,
    codeVerifier,
    scopes: ["user:email"],
  });
  return { url: url.toString(), state, codeVerifier };
}
```

## Additional Resources

- Oslo docs: https://oslo.js.org/
- GitHub: https://github.com/pilcrowOnPaper/oslo
