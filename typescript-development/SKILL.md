---
name: typescript-development
description: TypeScript development best practices covering strict mode configuration, advanced types, generics, utility types, decorators, module systems, type narrowing, and production-ready patterns for building type-safe applications.
---

# TypeScript Development

This skill should be used when writing, configuring, or improving TypeScript code. It covers tsconfig setup, advanced type patterns, generics, utility types, decorators, and production-grade TypeScript workflows.

## When to Use This Skill

Use this skill when you need to:

- Configure TypeScript projects with strict settings
- Write advanced generic types and utility types
- Apply type narrowing and discriminated unions
- Use decorators and metadata reflection
- Structure TypeScript modules and namespaces
- Work with declaration files and third-party types
- Migrate JavaScript projects to TypeScript
- Apply TypeScript patterns for React, Node.js, and APIs

## Project Setup

### tsconfig.json (Strict Mode)

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "exactOptionalPropertyTypes": true,
    "noPropertyAccessFromIndexSignature": true,
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

### tsconfig for React/Vite

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true
  },
  "include": ["src"]
}
```

## Core Type System

### Primitive Types and Annotations

```typescript
// Explicit types (prefer inference when obvious)
const name: string = "Alice";          // prefer: const name = "Alice"
const count: number = 42;              // prefer: const count = 42
const active: boolean = true;          // prefer: const active = true

// When annotations add value
function greet(name: string): string {
  return `Hello, ${name}`;
}

// Object types
type Point = {
  x: number;
  y: number;
  label?: string;  // optional
};

// readonly
type Config = {
  readonly apiUrl: string;
  readonly timeout: number;
};

// Index signatures
type StringMap = {
  [key: string]: string;
};

// With noPropertyAccessFromIndexSignature enabled:
const map: StringMap = {};
const value = map["key"]; // string | undefined with noUncheckedIndexedAccess
```

### Union and Intersection Types

```typescript
// Union types
type Status = "pending" | "active" | "inactive";
type ID = string | number;

// Intersection types
type Timestamped = {
  createdAt: Date;
  updatedAt: Date;
};

type User = {
  id: number;
  name: string;
  email: string;
} & Timestamped;

// Discriminated unions (exhaustive pattern matching)
type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "rectangle"; width: number; height: number }
  | { kind: "triangle"; base: number; height: number };

function area(shape: Shape): number {
  switch (shape.kind) {
    case "circle":
      return Math.PI * shape.radius ** 2;
    case "rectangle":
      return shape.width * shape.height;
    case "triangle":
      return (shape.base * shape.height) / 2;
    default:
      // Exhaustiveness check
      const _exhaustive: never = shape;
      throw new Error(`Unknown shape: ${_exhaustive}`);
  }
}
```

### Type Narrowing

```typescript
// typeof narrowing
function formatValue(value: string | number): string {
  if (typeof value === "string") {
    return value.toUpperCase();
  }
  return value.toFixed(2);
}

// instanceof narrowing
class HttpError extends Error {
  constructor(
    public statusCode: number,
    message: string
  ) {
    super(message);
  }
}

function handleError(error: unknown): string {
  if (error instanceof HttpError) {
    return `HTTP ${error.statusCode}: ${error.message}`;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return String(error);
}

// Type predicates (type guards)
interface Cat { kind: "cat"; meow(): void }
interface Dog { kind: "dog"; bark(): void }

function isCat(animal: Cat | Dog): animal is Cat {
  return animal.kind === "cat";
}

// Assertion functions
function assertDefined<T>(val: T | undefined | null, msg?: string): asserts val is T {
  if (val === undefined || val === null) {
    throw new Error(msg ?? "Expected defined value");
  }
}

// in narrowing
type ApiResponse =
  | { success: true; data: unknown }
  | { success: false; error: string };

function handleResponse(response: ApiResponse) {
  if (response.success) {
    console.log(response.data);
  } else {
    console.error(response.error);
  }
}
```

## Generics

### Generic Functions and Constraints

```typescript
// Basic generic
function identity<T>(value: T): T {
  return value;
}

// With constraints
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

// Multiple type parameters
function zip<A, B>(as: A[], bs: B[]): [A, B][] {
  return as.map((a, i) => [a, bs[i]]);
}

// Conditional types in generics
type NonNullable<T> = T extends null | undefined ? never : T;
type ReturnType<T extends (...args: any) => any> = T extends (...args: any) => infer R ? R : never;

// Constrained with default
function createArray<T extends object = Record<string, unknown>>(
  length: number,
  fill: T
): T[] {
  return Array.from({ length }, () => ({ ...fill }));
}

// Generic classes
class Repository<T extends { id: number }> {
  private items = new Map<number, T>();

  add(item: T): void {
    this.items.set(item.id, item);
  }

  get(id: number): T | undefined {
    return this.items.get(id);
  }

  getAll(): T[] {
    return Array.from(this.items.values());
  }

  remove(id: number): boolean {
    return this.items.delete(id);
  }
}

// Builder pattern with generics
class QueryBuilder<T extends Record<string, unknown>> {
  private filters: Partial<T> = {};
  private limitCount?: number;

  where(filter: Partial<T>): this {
    this.filters = { ...this.filters, ...filter };
    return this;
  }

  limit(n: number): this {
    this.limitCount = n;
    return this;
  }

  build(): { filters: Partial<T>; limit?: number } {
    return { filters: this.filters, limit: this.limitCount };
  }
}
```

### Advanced Generic Patterns

```typescript
// Mapped types
type Readonly<T> = {
  readonly [K in keyof T]: T[K];
};

type Partial<T> = {
  [K in keyof T]?: T[K];
};

type Required<T> = {
  [K in keyof T]-?: T[K];
};

// Template literal types
type EventName<T extends string> = `on${Capitalize<T>}`;
type ClickEvent = EventName<"click">;  // "onClick"

type ApiRoute<T extends string> = `/api/v1/${T}`;
type UserRoute = ApiRoute<"users">;  // "/api/v1/users"

// Conditional types
type IsArray<T> = T extends any[] ? true : false;
type Flatten<T> = T extends Array<infer Item> ? Item : T;

// Distributive conditional types
type ToArray<T> = T extends any ? T[] : never;
type StringOrNumber = string | number;
type StringOrNumberArray = ToArray<StringOrNumber>; // string[] | number[]

// Recursive types
type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K];
};

type DeepPartial<T> = {
  [K in keyof T]?: T[K] extends object ? DeepPartial<T[K]> : T[K];
};

// Extract keys by value type
type KeysOfType<T, V> = {
  [K in keyof T]: T[K] extends V ? K : never;
}[keyof T];

interface User {
  id: number;
  name: string;
  email: string;
  age: number;
}

type StringKeys = KeysOfType<User, string>; // "name" | "email"
type NumberKeys = KeysOfType<User, number>; // "id" | "age"
```

## Utility Types

```typescript
// Built-in utility types
interface User {
  id: number;
  name: string;
  email: string;
  password: string;
  role: "admin" | "user";
  createdAt: Date;
}

// Partial - all fields optional
type UserUpdate = Partial<User>;

// Required - all fields required (removes optional)
type CompleteUser = Required<User>;

// Pick - select fields
type UserPublic = Pick<User, "id" | "name" | "email" | "role">;

// Omit - exclude fields
type UserCreate = Omit<User, "id" | "createdAt">;

// Record - key-value map
type UserRoles = Record<User["role"], string[]>;
// { admin: string[]; user: string[] }

// Exclude and Extract (union operations)
type NonAdmin = Exclude<User["role"], "admin">;  // "user"
type AdminOnly = Extract<User["role"], "admin">; // "admin"

// Parameters and ReturnType
function createUser(name: string, email: string): User { /* ... */ }
type CreateUserParams = Parameters<typeof createUser>; // [string, string]
type CreateUserReturn = ReturnType<typeof createUser>;  // User

// Awaited (unwrap Promise)
type AsyncUser = Promise<User>;
type UnwrappedUser = Awaited<AsyncUser>; // User

// Custom utility types
type Nullable<T> = T | null;
type Maybe<T> = T | null | undefined;

type RequireAtLeastOne<T, Keys extends keyof T = keyof T> = Pick<T, Exclude<keyof T, Keys>> &
  { [K in Keys]-?: Required<Pick<T, K>> & Partial<Pick<T, Exclude<Keys, K>>> }[Keys];

// XOR - exactly one of two types
type XOR<T, U> = (T | U) extends object
  ? (Without<T, U> & U) | (Without<U, T> & T)
  : T | U;
type Without<T, U> = { [P in Exclude<keyof T, keyof U>]?: never };
```

## Interfaces vs Types

```typescript
// Interface - prefer for object shapes (extensible, better error messages)
interface Animal {
  name: string;
  speak(): string;
}

interface Dog extends Animal {
  breed: string;
}

// Declaration merging (interfaces only)
interface Window {
  myCustomProp: string;
}

// Type alias - prefer for unions, intersections, computed types
type StringOrNumber = string | number;
type Callback<T> = (error: Error | null, result: T) => void;

// Both work for objects - use interface for APIs, type for complex compositions
interface UserService {
  getUser(id: number): Promise<User>;
  createUser(data: UserCreate): Promise<User>;
  updateUser(id: number, data: UserUpdate): Promise<User>;
  deleteUser(id: number): Promise<void>;
}

// Implement interface
class UserServiceImpl implements UserService {
  async getUser(id: number): Promise<User> {
    return fetch(`/api/users/${id}`).then(r => r.json());
  }
  // ... other methods
}
```

## Decorators (TypeScript 5.x)

```typescript
// tsconfig: "experimentalDecorators": true (legacy) or target ES2022+

// Class decorator
function singleton<T extends { new(...args: any[]): object }>(constructor: T) {
  let instance: InstanceType<T>;
  return class extends constructor {
    constructor(...args: any[]) {
      super(...args);
      if (instance) return instance;
      instance = this as InstanceType<T>;
    }
  };
}

@singleton
class Database {
  connected = false;
  connect() { this.connected = true; }
}

// Method decorator
function log(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const original = descriptor.value;
  descriptor.value = function (...args: any[]) {
    console.log(`Calling ${propertyKey} with`, args);
    const result = original.apply(this, args);
    console.log(`${propertyKey} returned`, result);
    return result;
  };
  return descriptor;
}

// Property decorator with metadata
function validate(schema: Record<string, unknown>) {
  return function (target: any, key: string) {
    let value = target[key];
    Object.defineProperty(target, key, {
      get: () => value,
      set: (newVal) => {
        // Validate against schema
        value = newVal;
      },
    });
  };
}
```

## Module System

```typescript
// Named exports (preferred)
export interface Config {
  apiUrl: string;
  timeout: number;
}

export function createConfig(partial: Partial<Config>): Config {
  return {
    apiUrl: "https://api.example.com",
    timeout: 5000,
    ...partial,
  };
}

// Re-exports
export { UserService } from "./user-service";
export type { User, UserCreate, UserUpdate } from "./types";
export * from "./utils";

// Barrel file (index.ts) - group related exports
// src/index.ts
export * from "./config";
export * from "./types";
export * from "./services/user-service";
export * from "./services/auth-service";

// Type-only imports (erased at runtime)
import type { User } from "./types";
import { type Config, createConfig } from "./config";

// Dynamic imports
const { parseCSV } = await import("./csv-parser");

// Namespace imports
import * as validators from "./validators";
validators.isEmail("test@test.com");
```

## Error Handling Patterns

```typescript
// Custom error hierarchy
class AppError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode: number = 500
  ) {
    super(message);
    this.name = new.target.name;
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

class NotFoundError extends AppError {
  constructor(resource: string, id: string | number) {
    super(`${resource} with id ${id} not found`, "NOT_FOUND", 404);
  }
}

class ValidationError extends AppError {
  constructor(
    message: string,
    public readonly fields: Record<string, string>
  ) {
    super(message, "VALIDATION_ERROR", 400);
  }
}

// Result type pattern
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };

function ok<T>(value: T): Result<T> {
  return { ok: true, value };
}

function err<E extends Error>(error: E): Result<never, E> {
  return { ok: false, error };
}

async function fetchUser(id: number): Promise<Result<User, NotFoundError | AppError>> {
  try {
    const user = await db.users.findById(id);
    if (!user) return err(new NotFoundError("User", id));
    return ok(user);
  } catch (e) {
    return err(new AppError("Database error", "DB_ERROR"));
  }
}

// Usage with exhaustive handling
const result = await fetchUser(42);
if (result.ok) {
  console.log(result.value.name);
} else {
  if (result.error instanceof NotFoundError) {
    return res.status(404).json({ error: result.error.message });
  }
  return res.status(500).json({ error: "Internal error" });
}
```

## Declaration Files

```typescript
// Custom type augmentation for Express
// types/express/index.d.ts
import "express";

declare module "express" {
  interface Request {
    user?: {
      id: number;
      email: string;
      role: "admin" | "user";
    };
    requestId?: string;
  }
}

// Ambient module declarations
// types/svg.d.ts
declare module "*.svg" {
  const url: string;
  export default url;
}

declare module "*.png" {
  const url: string;
  export default url;
}

// Global augmentation
declare global {
  interface Window {
    analytics: {
      track(event: string, properties?: Record<string, unknown>): void;
    };
  }

  namespace NodeJS {
    interface ProcessEnv {
      NODE_ENV: "development" | "production" | "test";
      DATABASE_URL: string;
      JWT_SECRET: string;
      PORT?: string;
    }
  }
}

export {};  // Make this a module (required for global augmentation)
```

## Advanced Patterns

### Branded Types (Nominal Typing)

```typescript
// Prevent mixing semantically different string/number types
type Brand<T, B extends string> = T & { readonly _brand: B };

type UserId = Brand<number, "UserId">;
type OrderId = Brand<number, "OrderId">;
type Email = Brand<string, "Email">;

function createUserId(id: number): UserId {
  return id as UserId;
}

function createEmail(email: string): Email {
  if (!email.includes("@")) throw new Error("Invalid email");
  return email as Email;
}

function getUser(id: UserId): User { /* ... */ }

const userId = createUserId(1);
const orderId = 1 as OrderId;

getUser(userId);  // OK
// getUser(orderId);  // Error: Type 'OrderId' is not assignable to type 'UserId'
// getUser(1);         // Error: Type 'number' is not assignable to type 'UserId'
```

### Builder Pattern with Method Chaining

```typescript
class HttpRequestBuilder {
  private url = "";
  private method: "GET" | "POST" | "PUT" | "DELETE" = "GET";
  private headers: Record<string, string> = {};
  private body?: unknown;

  setUrl(url: string): this {
    this.url = url;
    return this;
  }

  setMethod(method: typeof this.method): this {
    this.method = method;
    return this;
  }

  addHeader(key: string, value: string): this {
    this.headers[key] = value;
    return this;
  }

  setBody(body: unknown): this {
    this.body = body;
    return this;
  }

  async send<T>(): Promise<T> {
    const response = await fetch(this.url, {
      method: this.method,
      headers: this.headers,
      body: this.body ? JSON.stringify(this.body) : undefined,
    });
    return response.json() as Promise<T>;
  }
}

const user = await new HttpRequestBuilder()
  .setUrl("/api/users/1")
  .setMethod("GET")
  .addHeader("Authorization", "Bearer token")
  .send<User>();
```

### Satisfies Operator (TypeScript 4.9+)

```typescript
// satisfies checks type but preserves literal types
type Colors = "red" | "green" | "blue";
type RGB = [number, number, number];

const palette = {
  red: [255, 0, 0],
  green: "#00ff00",
  blue: [0, 0, 255],
} satisfies Record<Colors, RGB | string>;

// palette.red is inferred as [number, number, number] (not RGB | string)
const [r, g, b] = palette.red;  // Works!
const greenHex = palette.green.toUpperCase();  // Works (it's string)
```

## Code Quality

```bash
# Install tools
npm install -D typescript ts-node @types/node
npm install -D @typescript-eslint/parser @typescript-eslint/eslint-plugin
npm install -D prettier eslint-config-prettier

# Type check
npx tsc --noEmit

# Watch mode
npx tsc --noEmit --watch

# Build
npx tsc

# ESLint with TypeScript
# .eslintrc.cjs
module.exports = {
  parser: "@typescript-eslint/parser",
  plugins: ["@typescript-eslint"],
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/strict-type-checked",
    "prettier",
  ],
  parserOptions: {
    project: true,
  },
};
```

## Additional Resources

- TypeScript Handbook: https://www.typescriptlang.org/docs/handbook/
- TypeScript Playground: https://www.typescriptlang.org/play
- Total TypeScript: https://www.totaltypescript.com/
- type-fest (utility types): https://github.com/sindresorhus/type-fest
