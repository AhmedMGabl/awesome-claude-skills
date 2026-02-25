---
name: nodejs-api-development
description: Node.js API development covering Express and Fastify frameworks, REST API design, middleware patterns, authentication (JWT/sessions), WebSockets, rate limiting, input validation, error handling, and production deployment.
---

# Node.js API Development

This skill should be used when building Node.js backend APIs. It covers Express and Fastify setup, REST design principles, middleware, authentication, real-time communication, validation, error handling, and production-ready patterns.

## When to Use This Skill

Use this skill when you need to:

- Build REST APIs with Express or Fastify
- Implement JWT or session-based authentication
- Add middleware for logging, rate limiting, CORS, and compression
- Validate request input with Zod or Joi
- Handle real-time communication with WebSockets
- Structure Node.js projects for production
- Add observability with logging and health checks

## Project Setup

```bash
# Initialize project
npm init -y
npm install express zod bcryptjs jsonwebtoken cookie-parser cors helmet morgan
npm install -D typescript @types/node @types/express tsx nodemon

# Or use Fastify (faster, TypeScript-first)
npm install fastify @fastify/jwt @fastify/cors @fastify/helmet @fastify/rate-limit zod
npm install -D typescript @types/node tsx

# Project structure
src/
├── app.ts              # Express app factory
├── server.ts           # Server entry point
├── config/
│   └── index.ts        # Environment config
├── middleware/
│   ├── auth.ts         # Authentication middleware
│   ├── error.ts        # Error handler
│   └── validate.ts     # Request validation
├── routes/
│   ├── index.ts        # Route registry
│   ├── users.ts        # User routes
│   └── auth.ts         # Auth routes
├── controllers/
│   ├── users.ts        # Request handlers
│   └── auth.ts
├── services/
│   ├── user.service.ts # Business logic
│   └── auth.service.ts
├── models/
│   └── user.model.ts   # Data models
└── types/
    └── index.ts        # Shared types
```

## Express Setup

### Application Factory

```typescript
// src/app.ts
import express from "express";
import cors from "cors";
import helmet from "helmet";
import morgan from "morgan";
import cookieParser from "cookie-parser";
import { errorHandler } from "./middleware/error";
import { registerRoutes } from "./routes";

export function createApp() {
  const app = express();

  // Security
  app.use(helmet());
  app.use(cors({
    origin: process.env.CORS_ORIGIN?.split(",") ?? ["http://localhost:3000"],
    credentials: true,
  }));

  // Parsing
  app.use(express.json({ limit: "10mb" }));
  app.use(express.urlencoded({ extended: true }));
  app.use(cookieParser());

  // Logging
  app.use(morgan(process.env.NODE_ENV === "production" ? "combined" : "dev"));

  // Routes
  registerRoutes(app);

  // Health check
  app.get("/health", (req, res) => {
    res.json({ status: "ok", timestamp: new Date().toISOString() });
  });

  // 404 handler
  app.use((req, res) => {
    res.status(404).json({ error: "Route not found" });
  });

  // Error handler (must be last)
  app.use(errorHandler);

  return app;
}

// src/server.ts
import { createApp } from "./app";

const PORT = Number(process.env.PORT ?? 3000);
const app = createApp();

const server = app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

// Graceful shutdown
process.on("SIGTERM", () => {
  server.close(() => {
    console.log("Server closed");
    process.exit(0);
  });
});
```

### Routes and Controllers

```typescript
// src/routes/users.ts
import { Router } from "express";
import { authenticate } from "../middleware/auth";
import { validate } from "../middleware/validate";
import { CreateUserSchema, UpdateUserSchema } from "../schemas/user";
import * as controller from "../controllers/users";

const router = Router();

router.get("/", authenticate, controller.listUsers);
router.post("/", validate(CreateUserSchema), controller.createUser);
router.get("/:id", authenticate, controller.getUser);
router.put("/:id", authenticate, validate(UpdateUserSchema), controller.updateUser);
router.delete("/:id", authenticate, controller.deleteUser);

export default router;

// src/routes/index.ts
import { Express } from "express";
import usersRouter from "./users";
import authRouter from "./auth";

export function registerRoutes(app: Express) {
  app.use("/api/v1/users", usersRouter);
  app.use("/api/v1/auth", authRouter);
}

// src/controllers/users.ts
import { Request, Response, NextFunction } from "express";
import { UserService } from "../services/user.service";

const userService = new UserService();

export async function listUsers(req: Request, res: Response, next: NextFunction) {
  try {
    const page = Number(req.query.page ?? 1);
    const limit = Number(req.query.limit ?? 10);
    const users = await userService.findAll({ page, limit });
    res.json(users);
  } catch (err) {
    next(err);
  }
}

export async function createUser(req: Request, res: Response, next: NextFunction) {
  try {
    const user = await userService.create(req.body);
    res.status(201).json(user);
  } catch (err) {
    next(err);
  }
}

export async function getUser(req: Request, res: Response, next: NextFunction) {
  try {
    const user = await userService.findById(req.params.id);
    if (!user) return res.status(404).json({ error: "User not found" });
    res.json(user);
  } catch (err) {
    next(err);
  }
}
```

## Middleware

### Validation with Zod

```typescript
// src/middleware/validate.ts
import { Request, Response, NextFunction } from "express";
import { z, ZodSchema } from "zod";

export function validate(schema: ZodSchema) {
  return (req: Request, res: Response, next: NextFunction) => {
    const result = schema.safeParse({
      body: req.body,
      query: req.query,
      params: req.params,
    });

    if (!result.success) {
      return res.status(400).json({
        error: "Validation failed",
        details: result.error.flatten(),
      });
    }

    // Replace with parsed/coerced values
    req.body = result.data.body;
    next();
  };
}

// src/schemas/user.ts
import { z } from "zod";

export const CreateUserSchema = z.object({
  body: z.object({
    name: z.string().min(1).max(100),
    email: z.string().email(),
    password: z.string().min(8),
    role: z.enum(["admin", "user"]).default("user"),
  }),
});

export const UpdateUserSchema = z.object({
  params: z.object({ id: z.string().uuid() }),
  body: z.object({
    name: z.string().min(1).max(100).optional(),
    email: z.string().email().optional(),
  }),
});

export type CreateUserInput = z.infer<typeof CreateUserSchema>["body"];
```

### Authentication Middleware

```typescript
// src/middleware/auth.ts
import { Request, Response, NextFunction } from "express";
import jwt from "jsonwebtoken";

interface TokenPayload {
  userId: string;
  email: string;
  role: string;
}

// Augment Express Request type
declare global {
  namespace Express {
    interface Request {
      user?: TokenPayload;
    }
  }
}

export function authenticate(req: Request, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;
  const token = authHeader?.startsWith("Bearer ")
    ? authHeader.slice(7)
    : req.cookies?.access_token;

  if (!token) {
    return res.status(401).json({ error: "Authentication required" });
  }

  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET!) as TokenPayload;
    req.user = payload;
    next();
  } catch {
    return res.status(401).json({ error: "Invalid or expired token" });
  }
}

export function requireRole(role: string) {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({ error: "Authentication required" });
    }
    if (req.user.role !== role) {
      return res.status(403).json({ error: "Insufficient permissions" });
    }
    next();
  };
}
```

### Error Handler

```typescript
// src/middleware/error.ts
import { Request, Response, NextFunction } from "express";

export class AppError extends Error {
  constructor(
    public message: string,
    public statusCode: number = 500,
    public code?: string
  ) {
    super(message);
    this.name = "AppError";
  }
}

export function errorHandler(
  err: Error,
  req: Request,
  res: Response,
  _next: NextFunction
) {
  // Known application errors
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      error: err.message,
      code: err.code,
    });
  }

  // Prisma/DB errors
  if (err.name === "PrismaClientKnownRequestError") {
    const prismaErr = err as any;
    if (prismaErr.code === "P2002") {
      return res.status(409).json({ error: "Record already exists" });
    }
    if (prismaErr.code === "P2025") {
      return res.status(404).json({ error: "Record not found" });
    }
  }

  // Unexpected errors
  console.error("Unexpected error:", err);
  res.status(500).json({
    error: process.env.NODE_ENV === "production"
      ? "Internal server error"
      : err.message,
  });
}
```

### Rate Limiting

```typescript
// src/middleware/rateLimit.ts
import rateLimit from "express-rate-limit";
import { RedisStore } from "rate-limit-redis";
import Redis from "ioredis";

const redis = new Redis(process.env.REDIS_URL!);

// Global rate limit
export const globalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 minutes
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
  store: new RedisStore({ sendCommand: (...args) => redis.call(...args) }),
  message: { error: "Too many requests, please try again later" },
});

// Strict limit for auth endpoints
export const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,
  skipSuccessfulRequests: true,
  message: { error: "Too many login attempts, please try again in 15 minutes" },
});

// Usage
app.use(globalLimiter);
app.use("/api/v1/auth/login", authLimiter);
```

## Authentication Service

```typescript
// src/services/auth.service.ts
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import { AppError } from "../middleware/error";
import { UserRepository } from "../repositories/user.repository";

interface Tokens {
  accessToken: string;
  refreshToken: string;
}

export class AuthService {
  private userRepo = new UserRepository();
  private readonly ACCESS_TOKEN_TTL = "15m";
  private readonly REFRESH_TOKEN_TTL = "7d";

  async register(email: string, password: string, name: string) {
    const existing = await this.userRepo.findByEmail(email);
    if (existing) throw new AppError("Email already in use", 409);

    const passwordHash = await bcrypt.hash(password, 12);
    return this.userRepo.create({ email, passwordHash, name });
  }

  async login(email: string, password: string): Promise<Tokens> {
    const user = await this.userRepo.findByEmail(email);
    if (!user) throw new AppError("Invalid credentials", 401);

    const isValid = await bcrypt.compare(password, user.passwordHash);
    if (!isValid) throw new AppError("Invalid credentials", 401);

    return this.generateTokens(user);
  }

  async refreshTokens(refreshToken: string): Promise<Tokens> {
    try {
      const payload = jwt.verify(
        refreshToken,
        process.env.JWT_REFRESH_SECRET!
      ) as { userId: string };

      const user = await this.userRepo.findById(payload.userId);
      if (!user) throw new AppError("User not found", 404);

      return this.generateTokens(user);
    } catch {
      throw new AppError("Invalid refresh token", 401);
    }
  }

  private generateTokens(user: { id: string; email: string; role: string }): Tokens {
    const payload = { userId: user.id, email: user.email, role: user.role };

    const accessToken = jwt.sign(payload, process.env.JWT_SECRET!, {
      expiresIn: this.ACCESS_TOKEN_TTL,
    });

    const refreshToken = jwt.sign(
      { userId: user.id },
      process.env.JWT_REFRESH_SECRET!,
      { expiresIn: this.REFRESH_TOKEN_TTL }
    );

    return { accessToken, refreshToken };
  }
}
```

## Fastify Alternative

```typescript
// src/app.ts (Fastify)
import Fastify from "fastify";
import fastifyJWT from "@fastify/jwt";
import fastifyCors from "@fastify/cors";
import fastifyHelmet from "@fastify/helmet";
import fastifyRateLimit from "@fastify/rate-limit";

export async function buildApp() {
  const app = Fastify({
    logger: {
      transport: process.env.NODE_ENV !== "production"
        ? { target: "pino-pretty" }
        : undefined,
    },
  });

  // Security
  await app.register(fastifyHelmet);
  await app.register(fastifyCors, {
    origin: process.env.CORS_ORIGIN?.split(","),
    credentials: true,
  });

  // Rate limiting
  await app.register(fastifyRateLimit, {
    max: 100,
    timeWindow: "15 minutes",
  });

  // JWT
  await app.register(fastifyJWT, {
    secret: process.env.JWT_SECRET!,
  });

  // Decorate authenticate hook
  app.decorate("authenticate", async (request: any, reply: any) => {
    try {
      await request.jwtVerify();
    } catch {
      reply.status(401).send({ error: "Authentication required" });
    }
  });

  // Health check
  app.get("/health", async () => ({
    status: "ok",
    timestamp: new Date().toISOString(),
  }));

  // Register routes
  await app.register(import("./routes/users"), { prefix: "/api/v1/users" });
  await app.register(import("./routes/auth"), { prefix: "/api/v1/auth" });

  return app;
}

// src/routes/users.ts (Fastify)
import { FastifyPluginAsync } from "fastify";
import { z } from "zod";

const CreateUserBody = z.object({
  name: z.string().min(1),
  email: z.string().email(),
  password: z.string().min(8),
});

const plugin: FastifyPluginAsync = async (fastify) => {
  fastify.get("/", {
    onRequest: [fastify.authenticate],
    handler: async (request, reply) => {
      const page = Number(request.query.page ?? 1);
      const users = await userService.findAll({ page, limit: 10 });
      return users;
    },
  });

  fastify.post("/", {
    schema: {
      body: {
        type: "object",
        required: ["name", "email", "password"],
        properties: {
          name: { type: "string" },
          email: { type: "string", format: "email" },
          password: { type: "string", minLength: 8 },
        },
      },
    },
    handler: async (request, reply) => {
      const body = CreateUserBody.parse(request.body);
      const user = await userService.create(body);
      reply.status(201).send(user);
    },
  });
};

export default plugin;
```

## WebSockets

```typescript
// src/websocket.ts
import { WebSocketServer, WebSocket } from "ws";
import { IncomingMessage } from "http";
import { verify } from "jsonwebtoken";
import type { Server } from "http";

interface Client {
  ws: WebSocket;
  userId: string;
  rooms: Set<string>;
}

const clients = new Map<string, Client>();

export function setupWebSocket(server: Server) {
  const wss = new WebSocketServer({ server, path: "/ws" });

  wss.on("connection", (ws: WebSocket, req: IncomingMessage) => {
    // Authenticate via token in query string
    const url = new URL(req.url!, `http://${req.headers.host}`);
    const token = url.searchParams.get("token");

    if (!token) {
      ws.close(4001, "Authentication required");
      return;
    }

    let userId: string;
    try {
      const payload = verify(token, process.env.JWT_SECRET!) as { userId: string };
      userId = payload.userId;
    } catch {
      ws.close(4001, "Invalid token");
      return;
    }

    const clientId = crypto.randomUUID();
    clients.set(clientId, { ws, userId, rooms: new Set() });

    ws.send(JSON.stringify({ type: "connected", clientId }));

    ws.on("message", (data) => {
      try {
        const message = JSON.parse(data.toString());
        handleMessage(clientId, message);
      } catch {
        ws.send(JSON.stringify({ type: "error", message: "Invalid JSON" }));
      }
    });

    ws.on("close", () => {
      clients.delete(clientId);
    });
  });

  return wss;
}

function handleMessage(clientId: string, message: { type: string; room?: string; data?: unknown }) {
  const client = clients.get(clientId);
  if (!client) return;

  switch (message.type) {
    case "join_room":
      if (message.room) client.rooms.add(message.room);
      break;
    case "leave_room":
      if (message.room) client.rooms.delete(message.room);
      break;
    case "broadcast":
      broadcastToRoom(message.room!, message.data, clientId);
      break;
  }
}

export function broadcastToRoom(room: string, data: unknown, excludeClientId?: string) {
  const payload = JSON.stringify({ type: "message", room, data });
  for (const [id, client] of clients) {
    if (id !== excludeClientId && client.rooms.has(room) && client.ws.readyState === WebSocket.OPEN) {
      client.ws.send(payload);
    }
  }
}
```

## File Uploads

```typescript
// src/middleware/upload.ts
import multer from "multer";
import path from "path";
import { v4 as uuidv4 } from "uuid";
import { AppError } from "./error";

const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp", "image/gif"];
const MAX_SIZE = 5 * 1024 * 1024; // 5MB

export const upload = multer({
  storage: multer.diskStorage({
    destination: "uploads/",
    filename: (_req, file, cb) => {
      const ext = path.extname(file.originalname);
      cb(null, `${uuidv4()}${ext}`);
    },
  }),
  limits: { fileSize: MAX_SIZE },
  fileFilter: (_req, file, cb) => {
    if (ALLOWED_TYPES.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new AppError("Invalid file type", 400) as any, false);
    }
  },
});

// Route
router.post("/avatar", authenticate, upload.single("avatar"), async (req, res) => {
  if (!req.file) return res.status(400).json({ error: "No file uploaded" });
  const url = `/uploads/${req.file.filename}`;
  await userService.updateAvatar(req.user!.userId, url);
  res.json({ url });
});
```

## Environment Configuration

```typescript
// src/config/index.ts
import { z } from "zod";

const EnvSchema = z.object({
  NODE_ENV: z.enum(["development", "production", "test"]).default("development"),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
  JWT_REFRESH_SECRET: z.string().min(32),
  REDIS_URL: z.string().url().optional(),
  CORS_ORIGIN: z.string().default("http://localhost:3000"),
});

const result = EnvSchema.safeParse(process.env);
if (!result.success) {
  console.error("Invalid environment variables:", result.error.flatten());
  process.exit(1);
}

export const config = result.data;
```

## Testing

```typescript
// tests/users.test.ts
import supertest from "supertest";
import { createApp } from "../src/app";

const app = createApp();
const request = supertest(app);

describe("POST /api/v1/users", () => {
  it("creates a user with valid data", async () => {
    const res = await request
      .post("/api/v1/users")
      .send({ name: "Alice", email: "alice@test.com", password: "secure123" });

    expect(res.status).toBe(201);
    expect(res.body).toMatchObject({ name: "Alice", email: "alice@test.com" });
    expect(res.body.password).toBeUndefined();
  });

  it("rejects invalid email", async () => {
    const res = await request
      .post("/api/v1/users")
      .send({ name: "Bob", email: "not-email", password: "secure123" });

    expect(res.status).toBe(400);
    expect(res.body.error).toBe("Validation failed");
  });
});

describe("GET /api/v1/users (authenticated)", () => {
  it("requires authentication", async () => {
    const res = await request.get("/api/v1/users");
    expect(res.status).toBe(401);
  });

  it("returns users with valid token", async () => {
    const token = generateTestToken({ userId: "1", role: "admin" });
    const res = await request
      .get("/api/v1/users")
      .set("Authorization", `Bearer ${token}`);

    expect(res.status).toBe(200);
    expect(Array.isArray(res.body.users)).toBe(true);
  });
});
```

## Additional Resources

- Express.js: https://expressjs.com/
- Fastify: https://www.fastify.io/
- node-jsonwebtoken: https://github.com/auth0/node-jsonwebtoken
- Zod: https://zod.dev/
- Supertest: https://github.com/ladjs/supertest
- ws (WebSockets): https://github.com/websockets/ws
