---
name: dagger-ci
description: Dagger CI/CD pipelines covering programmable pipelines in TypeScript/Python/Go, container operations, caching, secrets management, multi-platform builds, and local/CI execution.
---

# Dagger CI/CD

This skill should be used when building programmable CI/CD pipelines with Dagger. It covers pipeline definition, container operations, caching, and multi-platform builds.

## When to Use This Skill

Use this skill when you need to:

- Write CI/CD pipelines as code (TypeScript/Python/Go)
- Run identical pipelines locally and in CI
- Cache build steps for faster execution
- Build multi-platform container images
- Compose complex build workflows

## Setup

```bash
# Install Dagger CLI
curl -fsSL https://dl.dagger.io/dagger/install.sh | sh

# Initialize Dagger module
dagger init --sdk=typescript
```

## Basic Pipeline (TypeScript)

```typescript
// dagger/src/index.ts
import { dag, Container, Directory, object, func } from "@dagger.io/dagger";

@object()
class MyPipeline {
  @func()
  async test(source: Directory): Promise<string> {
    return dag
      .container()
      .from("node:20-slim")
      .withDirectory("/app", source)
      .withWorkdir("/app")
      .withExec(["npm", "ci"])
      .withExec(["npm", "test"])
      .stdout();
  }

  @func()
  async lint(source: Directory): Promise<string> {
    return dag
      .container()
      .from("node:20-slim")
      .withDirectory("/app", source)
      .withWorkdir("/app")
      .withExec(["npm", "ci"])
      .withExec(["npm", "run", "lint"])
      .stdout();
  }

  @func()
  async build(source: Directory): Promise<Container> {
    // Build and return the container
    return dag
      .container()
      .from("node:20-slim")
      .withDirectory("/app", source)
      .withWorkdir("/app")
      .withExec(["npm", "ci"])
      .withExec(["npm", "run", "build"]);
  }
}
```

## Caching

```typescript
@func()
async buildWithCache(source: Directory): Promise<Container> {
  const nodeCache = dag.cacheVolume("node-modules");
  const buildCache = dag.cacheVolume("build-cache");

  return dag
    .container()
    .from("node:20-slim")
    .withDirectory("/app", source)
    .withWorkdir("/app")
    .withMountedCache("/app/node_modules", nodeCache)
    .withMountedCache("/app/.next/cache", buildCache)
    .withExec(["npm", "ci"])
    .withExec(["npm", "run", "build"]);
}
```

## Multi-Platform Build

```typescript
@func()
async buildMultiPlatform(source: Directory): Promise<void> {
  const platforms = ["linux/amd64", "linux/arm64"];

  const variants = platforms.map((platform) =>
    dag
      .container({ platform })
      .from("node:20-slim")
      .withDirectory("/app", source)
      .withWorkdir("/app")
      .withExec(["npm", "ci", "--production"])
      .withExec(["npm", "run", "build"])
      .withEntrypoint(["node", "dist/index.js"]),
  );

  await dag
    .container()
    .publish("ghcr.io/myorg/myapp:latest", { platformVariants: variants });
}
```

## Secrets

```typescript
@func()
async deploy(source: Directory, token: Secret): Promise<string> {
  return dag
    .container()
    .from("node:20-slim")
    .withDirectory("/app", source)
    .withWorkdir("/app")
    .withSecretVariable("DEPLOY_TOKEN", token)
    .withExec(["npm", "ci"])
    .withExec(["npm", "run", "deploy"])
    .stdout();
}
```

## Running Pipelines

```bash
# Run locally
dagger call test --source=.
dagger call build --source=. export --path=./dist

# Run in GitHub Actions
# .github/workflows/ci.yml
# - uses: dagger/dagger-for-github@v6
#   with:
#     verb: call
#     args: test --source=.
```

## Additional Resources

- Dagger docs: https://docs.dagger.io/
- TypeScript SDK: https://docs.dagger.io/sdk/typescript
- Quickstart: https://docs.dagger.io/quickstart
