---
name: express-js
description: Express.js web framework development covering TypeScript setup, routing with Router and parameter handling, middleware integration (CORS, Helmet, Morgan, rate limiting), request validation with Zod, file uploads with Multer, JWT authentication, custom error handling patterns, graceful shutdown, testing with Supertest, and production project structure conventions.
---

# Express.js Development

This skill should be used when building web applications and REST APIs with the Express.js framework. It covers TypeScript-first project setup, routing patterns, middleware composition, validation, authentication, error handling, file uploads, graceful shutdown, and testing strategies for production-grade Express applications.

## When to Use This Skill

- Set up an Express.js application with TypeScript from scratch
- Define routes with Router, path parameters, and query strings
- Apply middleware for security, logging, CORS, and rate limiting
- Validate request bodies, params, and query strings with Zod
- Handle file uploads with Multer
- Implement JWT-based authentication and role-based authorization
- Build custom error classes and a global error handler
- Configure graceful shutdown for zero-downtime deployments
- Write integration tests with Supertest
- Structure an Express project for maintainability at scale

## Project Setup

### Initialize with TypeScript

```bash
mkdir my-api && cd my-api
npm init -y

# Runtime dependencies
npm install express cors helmet morgan cookie-parser compression
npm install express-rate-limit zod jsonwebtoken bcryptjs multer

# TypeScript and dev tooling
npm install -D typescript @types/node @types/express @types/cors \
  @types/morgan @types/cookie-parser @types/compression \
  @types/jsonwebtoken @types/bcryptjs @types/multer \
  tsx nodemon vitest supertest @types/supertest
```

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

### package.json Scripts

```json
{
  "scripts": {
    "dev": "nodemon --exec tsx src/server.ts",
    "build": "tsc",
    "start": "node dist/server.js",
    "test": "vitest run",
    "test:watch": "vitest",
    "lint": "eslint src/"
  }
}
```

### Project Structure

```
src/
├── app.ts                  # Express app factory
├── server.ts               # HTTP server entry point
├── config/
│   └── env.ts              # Environment variable validation
├── middleware/
│   ├── auth.ts             # JWT authentication
│   ├── errorHandler.ts     # Global error handler
│   ├── rateLimiter.ts      # Rate limiting configuration
│   ├── validate.ts         # Zod request validation
│   └── upload.ts           # Multer file upload configuration
├── routes/
│   ├── index.ts            # Route registry
│   ├── auth.routes.ts      # Authentication routes
│   ├── users.routes.ts     # User CRUD routes
│   └── files.routes.ts     # File upload routes
├── controllers/
│   ├── auth.controller.ts  # Auth request handlers
│   ├── users.controller.ts # User request handlers
│   └── files.controller.ts # File request handlers
├── services/
│   ├── auth.service.ts     # Authentication business logic
│   └── user.service.ts     # User business logic
├── errors/
│   └── AppError.ts         # Custom error classes
├── types/
│   └── index.ts            # Shared TypeScript types
└── utils/
    └── asyncHandler.ts     # Async route wrapper
tests/
├── setup.ts                # Test configuration
├── auth.test.ts            # Auth endpoint tests
├── users.test.ts           # User endpoint tests
└── helpers/
    └── testUtils.ts        # Shared test utilities
```

## Application Factory

```typescript
// src/app.ts
import express from "express";
import cors from "cors";
import helmet from "helmet";
import morgan from "morgan";
import cookieParser from "cookie-parser";
import compression from "compression";
import { config } from "./config/env";
import { registerRoutes } from "./routes";
import { errorHandler } from "./middleware/errorHandler";
import { AppError } from "./errors/AppError";

export function createApp() {
  const app = express();

  // Security headers
  app.use(helmet());

  // CORS
  app.use(
    cors({
      origin: config.CORS_ORIGINS,
      credentials: true,
      methods: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
      allowedHeaders: ["Content-Type", "Authorization"],
    })
  );

  // Response compression
  app.use(compression());

  // Body parsing
  app.use(express.json({ limit: "10mb" }));
  app.use(express.urlencoded({ extended: true, limit: "10mb" }));
  app.use(cookieParser());

  // Request logging
  app.use(morgan(config.NODE_ENV === "production" ? "combined" : "dev"));

  // Health check (before auth middleware)
  app.get("/health", (_req, res) => {
    res.json({
      status: "ok",
      environment: config.NODE_ENV,
      timestamp: new Date().toISOString(),
    });
  });

  // API routes
  registerRoutes(app);

  // 404 handler for unmatched routes
  app.use((_req, _res, next) => {
    next(new AppError("Route not found", 404));
  });

  // Global error handler (must be registered last)
  app.use(errorHandler);

  return app;
}
```

## Server Entry Point with Graceful Shutdown

```typescript
// src/server.ts
import { createApp } from "./app";
import { config } from "./config/env";

const app = createApp();

const server = app.listen(config.PORT, () => {
  console.log(`Server running on port ${config.PORT} [${config.NODE_ENV}]`);
});

// Graceful shutdown handler
function shutdown(signal: string) {
  console.log(`${signal} received. Starting graceful shutdown...`);

  // Stop accepting new connections
  server.close((err) => {
    if (err) {
      console.error("Error during server close:", err);
      process.exit(1);
    }

    console.log("HTTP server closed.");

    // Close database connections, flush logs, etc.
    // await db.disconnect();
    // await redis.quit();

    console.log("Cleanup complete. Exiting.");
    process.exit(0);
  });

  // Force exit if shutdown takes too long
  setTimeout(() => {
    console.error("Graceful shutdown timed out. Forcing exit.");
    process.exit(1);
  }, 30_000);
}

process.on("SIGTERM", () => shutdown("SIGTERM"));
process.on("SIGINT", () => shutdown("SIGINT"));

// Handle unhandled rejections and uncaught exceptions
process.on("unhandledRejection", (reason) => {
  console.error("Unhandled Rejection:", reason);
  shutdown("unhandledRejection");
});

process.on("uncaughtException", (err) => {
  console.error("Uncaught Exception:", err);
  shutdown("uncaughtException");
});

export { server };
```

## Environment Configuration

```typescript
// src/config/env.ts
import { z } from "zod";

const EnvSchema = z.object({
  NODE_ENV: z.enum(["development", "production", "test"]).default("development"),
  PORT: z.coerce.number().default(3000),
  CORS_ORIGINS: z
    .string()
    .default("http://localhost:3000")
    .transform((val) => val.split(",")),
  JWT_SECRET: z.string().min(32),
  JWT_REFRESH_SECRET: z.string().min(32),
  JWT_ACCESS_EXPIRY: z.string().default("15m"),
  JWT_REFRESH_EXPIRY: z.string().default("7d"),
  DATABASE_URL: z.string().url(),
  UPLOAD_DIR: z.string().default("uploads"),
  MAX_FILE_SIZE_MB: z.coerce.number().default(5),
});

const parsed = EnvSchema.safeParse(process.env);

if (!parsed.success) {
  console.error("Invalid environment variables:");
  console.error(parsed.error.flatten().fieldErrors);
  process.exit(1);
}

export const config = parsed.data;
export type Config = z.infer<typeof EnvSchema>;
```

## Routing

### Route Registry

```typescript
// src/routes/index.ts
import { Express } from "express";
import { globalLimiter } from "../middleware/rateLimiter";
import authRoutes from "./auth.routes";
import usersRoutes from "./users.routes";
import filesRoutes from "./files.routes";

export function registerRoutes(app: Express) {
  // Apply global rate limiter to all API routes
  app.use("/api", globalLimiter);

  app.use("/api/v1/auth", authRoutes);
  app.use("/api/v1/users", usersRoutes);
  app.use("/api/v1/files", filesRoutes);
}
```

### Router with Params and Query Strings

```typescript
// src/routes/users.routes.ts
import { Router } from "express";
import { authenticate, requireRole } from "../middleware/auth";
import { validate } from "../middleware/validate";
import {
  CreateUserSchema,
  UpdateUserSchema,
  ListUsersQuerySchema,
  UserIdParamSchema,
} from "../schemas/user.schema";
import * as controller from "../controllers/users.controller";

const router = Router();

// GET /api/v1/users?page=1&limit=20&sort=createdAt&order=desc&search=alice
router.get(
  "/",
  authenticate,
  validate({ query: ListUsersQuerySchema }),
  controller.listUsers
);

// POST /api/v1/users
router.post(
  "/",
  authenticate,
  requireRole("admin"),
  validate({ body: CreateUserSchema }),
  controller.createUser
);

// GET /api/v1/users/:id
router.get(
  "/:id",
  authenticate,
  validate({ params: UserIdParamSchema }),
  controller.getUserById
);

// PATCH /api/v1/users/:id
router.patch(
  "/:id",
  authenticate,
  validate({ params: UserIdParamSchema, body: UpdateUserSchema }),
  controller.updateUser
);

// DELETE /api/v1/users/:id
router.delete(
  "/:id",
  authenticate,
  requireRole("admin"),
  validate({ params: UserIdParamSchema }),
  controller.deleteUser
);

export default router;
```

### Controller Pattern

```typescript
// src/controllers/users.controller.ts
import { Request, Response, NextFunction } from "express";
import { UserService } from "../services/user.service";
import { AppError } from "../errors/AppError";

const userService = new UserService();

export async function listUsers(req: Request, res: Response, next: NextFunction) {
  try {
    const { page, limit, sort, order, search } = req.query as {
      page: string;
      limit: string;
      sort?: string;
      order?: string;
      search?: string;
    };

    const result = await userService.findAll({
      page: Number(page),
      limit: Number(limit),
      sort: sort as string | undefined,
      order: order as "asc" | "desc" | undefined,
      search: search as string | undefined,
    });

    res.json({
      data: result.users,
      meta: {
        page: result.page,
        limit: result.limit,
        total: result.total,
        totalPages: Math.ceil(result.total / result.limit),
      },
    });
  } catch (err) {
    next(err);
  }
}

export async function getUserById(req: Request, res: Response, next: NextFunction) {
  try {
    const user = await userService.findById(req.params.id);
    if (!user) {
      throw new AppError("User not found", 404, "USER_NOT_FOUND");
    }
    res.json({ data: user });
  } catch (err) {
    next(err);
  }
}

export async function createUser(req: Request, res: Response, next: NextFunction) {
  try {
    const user = await userService.create(req.body);
    res.status(201).json({ data: user });
  } catch (err) {
    next(err);
  }
}

export async function updateUser(req: Request, res: Response, next: NextFunction) {
  try {
    const user = await userService.update(req.params.id, req.body);
    if (!user) {
      throw new AppError("User not found", 404, "USER_NOT_FOUND");
    }
    res.json({ data: user });
  } catch (err) {
    next(err);
  }
}

export async function deleteUser(req: Request, res: Response, next: NextFunction) {
  try {
    await userService.delete(req.params.id);
    res.status(204).send();
  } catch (err) {
    next(err);
  }
}
```

### Async Handler Utility

To eliminate repetitive try/catch blocks in every controller, wrap async route handlers:

```typescript
// src/utils/asyncHandler.ts
import { Request, Response, NextFunction, RequestHandler } from "express";

export function asyncHandler(
  fn: (req: Request, res: Response, next: NextFunction) => Promise<void>
): RequestHandler {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
}

// Usage in controllers — no try/catch needed
import { asyncHandler } from "../utils/asyncHandler";

export const listUsers = asyncHandler(async (req, res) => {
  const users = await userService.findAll(req.query);
  res.json({ data: users });
});

export const createUser = asyncHandler(async (req, res) => {
  const user = await userService.create(req.body);
  res.status(201).json({ data: user });
});
```

## Middleware

### Request Validation with Zod

```typescript
// src/middleware/validate.ts
import { Request, Response, NextFunction } from "express";
import { ZodSchema, ZodError } from "zod";

interface ValidationSchemas {
  body?: ZodSchema;
  query?: ZodSchema;
  params?: ZodSchema;
}

export function validate(schemas: ValidationSchemas) {
  return (req: Request, res: Response, next: NextFunction) => {
    const errors: Record<string, unknown> = {};

    if (schemas.body) {
      const result = schemas.body.safeParse(req.body);
      if (!result.success) {
        errors.body = result.error.flatten().fieldErrors;
      } else {
        req.body = result.data;
      }
    }

    if (schemas.query) {
      const result = schemas.query.safeParse(req.query);
      if (!result.success) {
        errors.query = result.error.flatten().fieldErrors;
      } else {
        // Assign validated and coerced query values
        (req as any).validatedQuery = result.data;
      }
    }

    if (schemas.params) {
      const result = schemas.params.safeParse(req.params);
      if (!result.success) {
        errors.params = result.error.flatten().fieldErrors;
      }
    }

    if (Object.keys(errors).length > 0) {
      return res.status(400).json({
        error: "Validation failed",
        details: errors,
      });
    }

    next();
  };
}
```

### Zod Schemas

```typescript
// src/schemas/user.schema.ts
import { z } from "zod";

export const CreateUserSchema = z.object({
  name: z.string().min(1, "Name is required").max(100),
  email: z.string().email("Invalid email format"),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .regex(/[A-Z]/, "Password must contain an uppercase letter")
    .regex(/[0-9]/, "Password must contain a digit"),
  role: z.enum(["admin", "user", "moderator"]).default("user"),
});

export const UpdateUserSchema = z.object({
  name: z.string().min(1).max(100).optional(),
  email: z.string().email().optional(),
  role: z.enum(["admin", "user", "moderator"]).optional(),
});

export const UserIdParamSchema = z.object({
  id: z.string().uuid("Invalid user ID format"),
});

export const ListUsersQuerySchema = z.object({
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().min(1).max(100).default(20),
  sort: z.enum(["name", "email", "createdAt"]).default("createdAt"),
  order: z.enum(["asc", "desc"]).default("desc"),
  search: z.string().optional(),
});

export type CreateUserInput = z.infer<typeof CreateUserSchema>;
export type UpdateUserInput = z.infer<typeof UpdateUserSchema>;
export type ListUsersQuery = z.infer<typeof ListUsersQuerySchema>;
```

### JWT Authentication Middleware

```typescript
// src/middleware/auth.ts
import { Request, Response, NextFunction } from "express";
import jwt from "jsonwebtoken";
import { config } from "../config/env";
import { AppError } from "../errors/AppError";

export interface TokenPayload {
  userId: string;
  email: string;
  role: string;
}

// Extend Express Request to include user
declare global {
  namespace Express {
    interface Request {
      user?: TokenPayload;
    }
  }
}

export function authenticate(req: Request, _res: Response, next: NextFunction) {
  // Extract token from Authorization header or cookie
  const authHeader = req.headers.authorization;
  const token = authHeader?.startsWith("Bearer ")
    ? authHeader.slice(7)
    : req.cookies?.access_token;

  if (!token) {
    return next(new AppError("Authentication required", 401, "AUTH_REQUIRED"));
  }

  try {
    const payload = jwt.verify(token, config.JWT_SECRET) as TokenPayload;
    req.user = payload;
    next();
  } catch (err) {
    if (err instanceof jwt.TokenExpiredError) {
      return next(new AppError("Token expired", 401, "TOKEN_EXPIRED"));
    }
    return next(new AppError("Invalid token", 401, "TOKEN_INVALID"));
  }
}

export function requireRole(...roles: string[]) {
  return (req: Request, _res: Response, next: NextFunction) => {
    if (!req.user) {
      return next(new AppError("Authentication required", 401, "AUTH_REQUIRED"));
    }

    if (!roles.includes(req.user.role)) {
      return next(
        new AppError("Insufficient permissions", 403, "FORBIDDEN")
      );
    }

    next();
  };
}

export function optionalAuth(req: Request, _res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;
  const token = authHeader?.startsWith("Bearer ")
    ? authHeader.slice(7)
    : req.cookies?.access_token;

  if (!token) {
    return next();
  }

  try {
    const payload = jwt.verify(token, config.JWT_SECRET) as TokenPayload;
    req.user = payload;
  } catch {
    // Token invalid but route is optional-auth, so continue without user
  }

  next();
}
```

### Rate Limiting

```typescript
// src/middleware/rateLimiter.ts
import rateLimit from "express-rate-limit";

// Global limiter: 100 requests per 15 minutes per IP
export const globalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
  message: {
    error: "Too many requests. Please try again later.",
    code: "RATE_LIMIT_EXCEEDED",
  },
});

// Strict limiter for auth endpoints: 5 attempts per 15 minutes
export const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,
  skipSuccessfulRequests: true,
  message: {
    error: "Too many login attempts. Please try again in 15 minutes.",
    code: "AUTH_RATE_LIMIT",
  },
});

// Per-route custom limiter factory
export function createLimiter(windowMs: number, max: number) {
  return rateLimit({
    windowMs,
    max,
    standardHeaders: true,
    legacyHeaders: false,
    message: {
      error: "Rate limit exceeded.",
      code: "RATE_LIMIT_EXCEEDED",
    },
  });
}

// Usage on specific routes
// router.post("/login", authLimiter, controller.login);
// router.post("/upload", createLimiter(60_000, 10), controller.upload);
```

## Error Handling

### Custom Error Classes

```typescript
// src/errors/AppError.ts
export class AppError extends Error {
  public readonly statusCode: number;
  public readonly code: string;
  public readonly isOperational: boolean;

  constructor(
    message: string,
    statusCode: number = 500,
    code: string = "INTERNAL_ERROR",
    isOperational: boolean = true
  ) {
    super(message);
    this.statusCode = statusCode;
    this.code = code;
    this.isOperational = isOperational;
    Object.setPrototypeOf(this, new.target.prototype);
    Error.captureStackTrace(this, this.constructor);
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string = "Resource") {
    super(`${resource} not found`, 404, "NOT_FOUND");
  }
}

export class ConflictError extends AppError {
  constructor(message: string = "Resource already exists") {
    super(message, 409, "CONFLICT");
  }
}

export class ValidationError extends AppError {
  public readonly details: Record<string, unknown>;

  constructor(message: string, details: Record<string, unknown> = {}) {
    super(message, 400, "VALIDATION_ERROR");
    this.details = details;
  }
}

export class UnauthorizedError extends AppError {
  constructor(message: string = "Authentication required") {
    super(message, 401, "UNAUTHORIZED");
  }
}

export class ForbiddenError extends AppError {
  constructor(message: string = "Insufficient permissions") {
    super(message, 403, "FORBIDDEN");
  }
}
```

### Global Error Handler

```typescript
// src/middleware/errorHandler.ts
import { Request, Response, NextFunction } from "express";
import { AppError, ValidationError } from "../errors/AppError";
import { config } from "../config/env";

export function errorHandler(
  err: Error,
  _req: Request,
  res: Response,
  _next: NextFunction
) {
  // Handle known application errors
  if (err instanceof ValidationError) {
    return res.status(err.statusCode).json({
      error: err.message,
      code: err.code,
      details: err.details,
    });
  }

  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      error: err.message,
      code: err.code,
    });
  }

  // Handle Prisma/ORM duplicate key errors
  if (err.name === "PrismaClientKnownRequestError") {
    const prismaErr = err as any;
    if (prismaErr.code === "P2002") {
      return res.status(409).json({
        error: "A record with that value already exists",
        code: "DUPLICATE_ENTRY",
      });
    }
    if (prismaErr.code === "P2025") {
      return res.status(404).json({
        error: "Record not found",
        code: "NOT_FOUND",
      });
    }
  }

  // Handle JSON parse errors
  if (err.type === "entity.parse.failed") {
    return res.status(400).json({
      error: "Invalid JSON in request body",
      code: "INVALID_JSON",
    });
  }

  // Handle payload too large
  if (err.type === "entity.too.large") {
    return res.status(413).json({
      error: "Request body too large",
      code: "PAYLOAD_TOO_LARGE",
    });
  }

  // Unhandled errors
  console.error("Unhandled error:", err);
  res.status(500).json({
    error:
      config.NODE_ENV === "production"
        ? "Internal server error"
        : err.message,
    code: "INTERNAL_ERROR",
    ...(config.NODE_ENV !== "production" && { stack: err.stack }),
  });
}
```

## File Upload with Multer

```typescript
// src/middleware/upload.ts
import multer, { FileFilterCallback } from "multer";
import path from "path";
import crypto from "crypto";
import { Request } from "express";
import { config } from "../config/env";
import { AppError } from "../errors/AppError";

const ALLOWED_MIME_TYPES: Record<string, string[]> = {
  image: ["image/jpeg", "image/png", "image/webp", "image/gif"],
  document: ["application/pdf", "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
};

const ALL_ALLOWED = Object.values(ALLOWED_MIME_TYPES).flat();

const storage = multer.diskStorage({
  destination: (_req, _file, cb) => {
    cb(null, config.UPLOAD_DIR);
  },
  filename: (_req, file, cb) => {
    const uniqueId = crypto.randomUUID();
    const ext = path.extname(file.originalname).toLowerCase();
    cb(null, `${uniqueId}${ext}`);
  },
});

function fileFilter(_req: Request, file: Express.Multer.File, cb: FileFilterCallback) {
  if (ALL_ALLOWED.includes(file.mimetype)) {
    cb(null, true);
  } else {
    cb(new AppError(`File type ${file.mimetype} is not allowed`, 400, "INVALID_FILE_TYPE"));
  }
}

// Single file upload (field name: "file")
export const uploadSingle = multer({
  storage,
  fileFilter,
  limits: {
    fileSize: config.MAX_FILE_SIZE_MB * 1024 * 1024,
  },
}).single("file");

// Multiple files upload (field name: "files", max 5)
export const uploadMultiple = multer({
  storage,
  fileFilter,
  limits: {
    fileSize: config.MAX_FILE_SIZE_MB * 1024 * 1024,
    files: 5,
  },
}).array("files", 5);

// Upload with specific fields
export const uploadFields = multer({
  storage,
  fileFilter,
  limits: {
    fileSize: config.MAX_FILE_SIZE_MB * 1024 * 1024,
  },
}).fields([
  { name: "avatar", maxCount: 1 },
  { name: "documents", maxCount: 3 },
]);
```

### File Upload Routes and Controller

```typescript
// src/routes/files.routes.ts
import { Router } from "express";
import { authenticate } from "../middleware/auth";
import { uploadSingle, uploadMultiple } from "../middleware/upload";
import * as controller from "../controllers/files.controller";

const router = Router();

router.post("/upload", authenticate, uploadSingle, controller.uploadFile);
router.post("/upload/batch", authenticate, uploadMultiple, controller.uploadFiles);

export default router;

// src/controllers/files.controller.ts
import { Request, Response, NextFunction } from "express";
import { AppError } from "../errors/AppError";

export async function uploadFile(req: Request, res: Response, next: NextFunction) {
  try {
    if (!req.file) {
      throw new AppError("No file provided", 400, "NO_FILE");
    }

    res.status(201).json({
      data: {
        filename: req.file.filename,
        originalName: req.file.originalname,
        mimetype: req.file.mimetype,
        size: req.file.size,
        url: `/uploads/${req.file.filename}`,
      },
    });
  } catch (err) {
    next(err);
  }
}

export async function uploadFiles(req: Request, res: Response, next: NextFunction) {
  try {
    const files = req.files as Express.Multer.File[];
    if (!files || files.length === 0) {
      throw new AppError("No files provided", 400, "NO_FILES");
    }

    const uploaded = files.map((file) => ({
      filename: file.filename,
      originalName: file.originalname,
      mimetype: file.mimetype,
      size: file.size,
      url: `/uploads/${file.filename}`,
    }));

    res.status(201).json({ data: uploaded });
  } catch (err) {
    next(err);
  }
}
```

## Authentication Service

```typescript
// src/services/auth.service.ts
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import { config } from "../config/env";
import { AppError } from "../errors/AppError";
import { TokenPayload } from "../middleware/auth";

interface TokenPair {
  accessToken: string;
  refreshToken: string;
}

export class AuthService {
  async hashPassword(password: string): Promise<string> {
    return bcrypt.hash(password, 12);
  }

  async comparePasswords(plain: string, hash: string): Promise<boolean> {
    return bcrypt.compare(plain, hash);
  }

  generateTokens(payload: TokenPayload): TokenPair {
    const accessToken = jwt.sign(payload, config.JWT_SECRET, {
      expiresIn: config.JWT_ACCESS_EXPIRY,
    });

    const refreshToken = jwt.sign(
      { userId: payload.userId },
      config.JWT_REFRESH_SECRET,
      { expiresIn: config.JWT_REFRESH_EXPIRY }
    );

    return { accessToken, refreshToken };
  }

  verifyRefreshToken(token: string): { userId: string } {
    try {
      return jwt.verify(token, config.JWT_REFRESH_SECRET) as { userId: string };
    } catch {
      throw new AppError("Invalid or expired refresh token", 401, "INVALID_REFRESH_TOKEN");
    }
  }

  setTokenCookies(res: import("express").Response, tokens: TokenPair) {
    res.cookie("access_token", tokens.accessToken, {
      httpOnly: true,
      secure: config.NODE_ENV === "production",
      sameSite: "strict",
      maxAge: 15 * 60 * 1000, // 15 minutes
    });

    res.cookie("refresh_token", tokens.refreshToken, {
      httpOnly: true,
      secure: config.NODE_ENV === "production",
      sameSite: "strict",
      path: "/api/v1/auth/refresh",
      maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
    });
  }

  clearTokenCookies(res: import("express").Response) {
    res.clearCookie("access_token");
    res.clearCookie("refresh_token", { path: "/api/v1/auth/refresh" });
  }
}
```

### Auth Routes and Controller

```typescript
// src/routes/auth.routes.ts
import { Router } from "express";
import { authLimiter } from "../middleware/rateLimiter";
import { validate } from "../middleware/validate";
import { LoginSchema, RegisterSchema } from "../schemas/auth.schema";
import * as controller from "../controllers/auth.controller";

const router = Router();

router.post("/register", validate({ body: RegisterSchema }), controller.register);
router.post("/login", authLimiter, validate({ body: LoginSchema }), controller.login);
router.post("/refresh", controller.refresh);
router.post("/logout", controller.logout);

export default router;

// src/schemas/auth.schema.ts
import { z } from "zod";

export const RegisterSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
  password: z.string().min(8).regex(/[A-Z]/).regex(/[0-9]/),
});

export const LoginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(1),
});

// src/controllers/auth.controller.ts
import { Request, Response, NextFunction } from "express";
import { AuthService } from "../services/auth.service";
import { AppError } from "../errors/AppError";

const authService = new AuthService();

export async function register(req: Request, res: Response, next: NextFunction) {
  try {
    const { name, email, password } = req.body;
    const hashedPassword = await authService.hashPassword(password);

    // Create user in database (replace with actual DB call)
    const user = { id: crypto.randomUUID(), name, email, role: "user" };

    const tokens = authService.generateTokens({
      userId: user.id,
      email: user.email,
      role: user.role,
    });

    authService.setTokenCookies(res, tokens);

    res.status(201).json({
      data: { user: { id: user.id, name: user.name, email: user.email, role: user.role } },
      accessToken: tokens.accessToken,
    });
  } catch (err) {
    next(err);
  }
}

export async function login(req: Request, res: Response, next: NextFunction) {
  try {
    const { email, password } = req.body;

    // Fetch user from database (replace with actual DB call)
    const user = await findUserByEmail(email);
    if (!user) {
      throw new AppError("Invalid credentials", 401, "INVALID_CREDENTIALS");
    }

    const isValid = await authService.comparePasswords(password, user.hashedPassword);
    if (!isValid) {
      throw new AppError("Invalid credentials", 401, "INVALID_CREDENTIALS");
    }

    const tokens = authService.generateTokens({
      userId: user.id,
      email: user.email,
      role: user.role,
    });

    authService.setTokenCookies(res, tokens);

    res.json({
      data: { user: { id: user.id, name: user.name, email: user.email, role: user.role } },
      accessToken: tokens.accessToken,
    });
  } catch (err) {
    next(err);
  }
}

export async function refresh(req: Request, res: Response, next: NextFunction) {
  try {
    const refreshToken = req.cookies?.refresh_token;
    if (!refreshToken) {
      throw new AppError("Refresh token required", 401, "NO_REFRESH_TOKEN");
    }

    const { userId } = authService.verifyRefreshToken(refreshToken);

    // Fetch user from database (replace with actual DB call)
    const user = await findUserById(userId);
    if (!user) {
      throw new AppError("User not found", 404, "USER_NOT_FOUND");
    }

    const tokens = authService.generateTokens({
      userId: user.id,
      email: user.email,
      role: user.role,
    });

    authService.setTokenCookies(res, tokens);
    res.json({ accessToken: tokens.accessToken });
  } catch (err) {
    next(err);
  }
}

export function logout(_req: Request, res: Response) {
  authService.clearTokenCookies(res);
  res.json({ message: "Logged out successfully" });
}
```

## Testing with Supertest

### Test Setup

```typescript
// tests/setup.ts
import { beforeAll, afterAll } from "vitest";

// Global test setup (database seeding, etc.)
beforeAll(async () => {
  // Set test environment variables
  process.env.NODE_ENV = "test";
  process.env.JWT_SECRET = "test-secret-that-is-at-least-32-chars-long";
  process.env.JWT_REFRESH_SECRET = "test-refresh-secret-at-least-32-chars";
  process.env.DATABASE_URL = "postgresql://localhost:5432/test_db";
});

afterAll(async () => {
  // Clean up database, close connections
});
```

### Test Utilities

```typescript
// tests/helpers/testUtils.ts
import jwt from "jsonwebtoken";

export function generateTestToken(payload: {
  userId: string;
  email: string;
  role: string;
}): string {
  return jwt.sign(payload, process.env.JWT_SECRET!, { expiresIn: "1h" });
}

export const testUser = {
  userId: "550e8400-e29b-41d4-a716-446655440000",
  email: "test@example.com",
  role: "user",
};

export const testAdmin = {
  userId: "550e8400-e29b-41d4-a716-446655440001",
  email: "admin@example.com",
  role: "admin",
};
```

### Integration Tests

```typescript
// tests/auth.test.ts
import { describe, it, expect } from "vitest";
import supertest from "supertest";
import { createApp } from "../src/app";

const app = createApp();
const request = supertest(app);

describe("POST /api/v1/auth/register", () => {
  it("registers a new user with valid data", async () => {
    const res = await request
      .post("/api/v1/auth/register")
      .send({
        name: "Alice Smith",
        email: "alice@example.com",
        password: "Secure123",
      });

    expect(res.status).toBe(201);
    expect(res.body.data.user).toMatchObject({
      name: "Alice Smith",
      email: "alice@example.com",
      role: "user",
    });
    expect(res.body.accessToken).toBeDefined();
    expect(res.body.data.user.password).toBeUndefined();
  });

  it("returns 400 for invalid email", async () => {
    const res = await request
      .post("/api/v1/auth/register")
      .send({
        name: "Bob",
        email: "not-an-email",
        password: "Secure123",
      });

    expect(res.status).toBe(400);
    expect(res.body.error).toBe("Validation failed");
  });

  it("returns 400 for weak password", async () => {
    const res = await request
      .post("/api/v1/auth/register")
      .send({
        name: "Charlie",
        email: "charlie@example.com",
        password: "weak",
      });

    expect(res.status).toBe(400);
  });
});

describe("POST /api/v1/auth/login", () => {
  it("returns tokens for valid credentials", async () => {
    const res = await request
      .post("/api/v1/auth/login")
      .send({
        email: "alice@example.com",
        password: "Secure123",
      });

    expect(res.status).toBe(200);
    expect(res.body.accessToken).toBeDefined();
    expect(res.headers["set-cookie"]).toBeDefined();
  });

  it("returns 401 for invalid credentials", async () => {
    const res = await request
      .post("/api/v1/auth/login")
      .send({
        email: "alice@example.com",
        password: "WrongPassword1",
      });

    expect(res.status).toBe(401);
    expect(res.body.code).toBe("INVALID_CREDENTIALS");
  });
});

// tests/users.test.ts
import { describe, it, expect } from "vitest";
import supertest from "supertest";
import { createApp } from "../src/app";
import { generateTestToken, testUser, testAdmin } from "./helpers/testUtils";

const app = createApp();
const request = supertest(app);

describe("GET /api/v1/users", () => {
  it("returns 401 without authentication", async () => {
    const res = await request.get("/api/v1/users");
    expect(res.status).toBe(401);
  });

  it("returns paginated users with valid token", async () => {
    const token = generateTestToken(testUser);
    const res = await request
      .get("/api/v1/users")
      .set("Authorization", `Bearer ${token}`)
      .query({ page: 1, limit: 10 });

    expect(res.status).toBe(200);
    expect(res.body.data).toBeInstanceOf(Array);
    expect(res.body.meta).toMatchObject({
      page: 1,
      limit: 10,
    });
  });

  it("supports search query parameter", async () => {
    const token = generateTestToken(testUser);
    const res = await request
      .get("/api/v1/users")
      .set("Authorization", `Bearer ${token}`)
      .query({ search: "alice" });

    expect(res.status).toBe(200);
  });
});

describe("DELETE /api/v1/users/:id", () => {
  it("returns 403 for non-admin users", async () => {
    const token = generateTestToken(testUser);
    const res = await request
      .delete("/api/v1/users/550e8400-e29b-41d4-a716-446655440000")
      .set("Authorization", `Bearer ${token}`);

    expect(res.status).toBe(403);
  });

  it("returns 204 for admin users", async () => {
    const token = generateTestToken(testAdmin);
    const res = await request
      .delete("/api/v1/users/550e8400-e29b-41d4-a716-446655440000")
      .set("Authorization", `Bearer ${token}`);

    expect(res.status).toBe(204);
  });
});

describe("GET /health", () => {
  it("returns health status", async () => {
    const res = await request.get("/health");
    expect(res.status).toBe(200);
    expect(res.body.status).toBe("ok");
    expect(res.body.timestamp).toBeDefined();
  });
});

describe("404 handling", () => {
  it("returns 404 for unknown routes", async () => {
    const res = await request.get("/api/v1/nonexistent");
    expect(res.status).toBe(404);
    expect(res.body.error).toBe("Route not found");
  });
});
```

### Vitest Configuration

```typescript
// vitest.config.ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    environment: "node",
    setupFiles: ["./tests/setup.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "html"],
      include: ["src/**/*.ts"],
      exclude: ["src/server.ts", "src/types/**"],
    },
    testTimeout: 10_000,
  },
});
```

## Project Structure Conventions

### Naming Conventions

| Item | Convention | Example |
|---|---|---|
| Files | kebab-case | `user.service.ts`, `auth.routes.ts` |
| Classes | PascalCase | `UserService`, `AppError` |
| Functions | camelCase | `createUser`, `authenticate` |
| Constants | UPPER_SNAKE_CASE | `MAX_FILE_SIZE`, `JWT_SECRET` |
| Interfaces | PascalCase (no `I` prefix) | `TokenPayload`, `UserInput` |
| Route files | `*.routes.ts` | `users.routes.ts` |
| Controller files | `*.controller.ts` | `users.controller.ts` |
| Service files | `*.service.ts` | `user.service.ts` |
| Schema files | `*.schema.ts` | `user.schema.ts` |
| Test files | `*.test.ts` | `users.test.ts` |

### Layered Architecture

Each layer has a single responsibility:

- **Routes** - HTTP method mapping, middleware composition, no business logic
- **Controllers** - Parse request, call service, format response
- **Services** - Business logic, orchestration, throws domain errors
- **Repositories** - Data access only, no business rules
- **Middleware** - Cross-cutting concerns (auth, validation, logging, errors)
- **Schemas** - Input validation and type definitions

### Response Format

Maintain a consistent response envelope across all endpoints:

```typescript
// Success responses
{ "data": { ... } }
{ "data": [...], "meta": { "page": 1, "limit": 20, "total": 100 } }

// Error responses
{ "error": "Human-readable message", "code": "MACHINE_READABLE_CODE" }
{ "error": "Validation failed", "code": "VALIDATION_ERROR", "details": { ... } }
```

## Additional Resources

- Express.js: https://expressjs.com/
- Zod: https://zod.dev/
- jsonwebtoken: https://github.com/auth0/node-jsonwebtoken
- Multer: https://github.com/expressjs/multer
- express-rate-limit: https://github.com/express-rate-limit/express-rate-limit
- Helmet: https://helmetjs.github.io/
- Supertest: https://github.com/ladjs/supertest
- Vitest: https://vitest.dev/
- Morgan: https://github.com/expressjs/morgan
