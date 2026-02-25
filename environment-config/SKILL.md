---
name: environment-config
description: Environment configuration and secrets management covering dotenv patterns, environment variable validation (Zod/Envalid), 12-factor app config, secrets managers (AWS Secrets Manager, Vault), configuration hierarchies, feature flags, and secure configuration deployment.
---

# Environment Configuration & Secrets

This skill should be used when managing application configuration, environment variables, or secrets. It covers validation, 12-factor patterns, and secure config management.

## When to Use This Skill

Use this skill when you need to:

- Set up environment variable management
- Validate configuration at startup
- Integrate with secrets managers
- Implement feature flags
- Manage multi-environment configurations

## TypeScript Config Validation (Zod)

```typescript
// config.ts — validate all env vars at startup
import { z } from "zod";

const envSchema = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
  REDIS_URL: z.string().url().optional(),
  JWT_SECRET: z.string().min(32),
  JWT_EXPIRES_IN: z.string().default("7d"),
  CORS_ORIGINS: z.string().transform((s) => s.split(",")),
  LOG_LEVEL: z.enum(["debug", "info", "warn", "error"]).default("info"),
  SENTRY_DSN: z.string().url().optional(),
  STRIPE_SECRET_KEY: z.string().startsWith("sk_"),
  STRIPE_WEBHOOK_SECRET: z.string().startsWith("whsec_"),
  S3_BUCKET: z.string().min(1),
  S3_REGION: z.string().default("us-east-1"),
});

export type Env = z.infer<typeof envSchema>;

function validateEnv(): Env {
  const result = envSchema.safeParse(process.env);
  if (!result.success) {
    console.error("Invalid environment variables:");
    for (const issue of result.error.issues) {
      console.error(`  ${issue.path.join(".")}: ${issue.message}`);
    }
    process.exit(1);
  }
  return result.data;
}

export const env = validateEnv();

// Usage throughout app:
// import { env } from "./config";
// db.connect(env.DATABASE_URL);
```

## Python Config Validation (Pydantic)

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    environment: str = "development"
    debug: bool = False
    database_url: str
    redis_url: str | None = None
    secret_key: str
    cors_origins: list[str] = ["http://localhost:3000"]
    log_level: str = "info"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

## .env File Patterns

```bash
# .env.example (committed to git — no real values)
NODE_ENV=development
PORT=3000
DATABASE_URL=postgresql://user:pass@localhost:5432/myapp
REDIS_URL=redis://localhost:6379
JWT_SECRET=change-me-to-a-real-secret-at-least-32-chars
STRIPE_SECRET_KEY=sk_test_xxx

# .env.local (NOT committed — real values)
# .env.development (committed — dev defaults)
# .env.production (NOT committed — prod values)
# .env.test (committed — test overrides)
```

```gitignore
# .gitignore
.env
.env.local
.env.production
.env.*.local
```

## Feature Flags

```typescript
// Simple feature flag system
interface FeatureFlags {
  newDashboard: boolean;
  betaPayments: boolean;
  experimentalSearch: boolean;
}

const flags: FeatureFlags = {
  newDashboard: env.NODE_ENV === "development" || env.FEATURE_NEW_DASHBOARD === "true",
  betaPayments: env.FEATURE_BETA_PAYMENTS === "true",
  experimentalSearch: false,
};

export function isFeatureEnabled(flag: keyof FeatureFlags): boolean {
  return flags[flag] ?? false;
}

// Usage
if (isFeatureEnabled("newDashboard")) {
  return <NewDashboard />;
}
```

## Secrets Manager Integration

```typescript
// AWS Secrets Manager
import { SecretsManagerClient, GetSecretValueCommand } from "@aws-sdk/client-secrets-manager";

const client = new SecretsManagerClient({ region: "us-east-1" });

async function getSecret(secretName: string): Promise<Record<string, string>> {
  const command = new GetSecretValueCommand({ SecretId: secretName });
  const response = await client.send(command);
  return JSON.parse(response.SecretString!);
}

// Load secrets at startup
async function loadSecrets() {
  const dbSecrets = await getSecret("myapp/production/database");
  process.env.DATABASE_URL = `postgresql://${dbSecrets.username}:${dbSecrets.password}@${dbSecrets.host}:5432/${dbSecrets.dbname}`;
}
```

## 12-Factor App Config Rules

```
1. Store config in environment variables (not in code)
2. Strict separation between config and code
3. Config varies between deploys; code does not
4. Never store credentials in version control
5. Group related config by service (DB_, REDIS_, STRIPE_)
6. Validate ALL config at startup (fail fast)
7. Provide sensible defaults for development
8. Document every env var in .env.example
```

## Additional Resources

- 12-Factor App Config: https://12factor.net/config
- Zod: https://zod.dev/
- dotenv: https://github.com/motdotla/dotenv
- Pydantic Settings: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
