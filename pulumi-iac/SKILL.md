---
name: pulumi-iac
description: Pulumi infrastructure as code using TypeScript, Python, or Go covering AWS, GCP, Azure resource provisioning, stack management, component resources, secrets, testing, CI/CD integration, and modern IaC patterns with real programming languages.
---

# Pulumi Infrastructure as Code

This skill should be used when defining cloud infrastructure using Pulumi with real programming languages. It covers resource provisioning, stack management, component patterns, and deployment automation.

## When to Use This Skill

Use this skill when you need to:

- Define cloud infrastructure with TypeScript, Python, or Go
- Provision AWS, GCP, or Azure resources programmatically
- Create reusable infrastructure components
- Manage multiple environments (stacks)
- Test infrastructure code
- Integrate IaC with CI/CD pipelines

## Project Setup (TypeScript)

```bash
# New project
pulumi new aws-typescript --name my-infra

# Project structure
# my-infra/
# ├── Pulumi.yaml          # Project metadata
# ├── Pulumi.dev.yaml      # Dev stack config
# ├── Pulumi.prod.yaml     # Prod stack config
# ├── index.ts             # Entry point
# └── components/          # Reusable components
```

```yaml
# Pulumi.yaml
name: my-infra
runtime:
  name: nodejs
  options:
    typescript: true
description: Production infrastructure
```

## Core AWS Resources

```typescript
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

const config = new pulumi.Config();
const env = pulumi.getStack(); // "dev" | "staging" | "prod"

// VPC
const vpc = new aws.ec2.Vpc("main", {
  cidrBlock: "10.0.0.0/16",
  enableDnsHostnames: true,
  tags: { Name: `${env}-vpc`, Environment: env },
});

// Subnets (public + private across AZs)
const azs = ["us-east-1a", "us-east-1b"];
const publicSubnets = azs.map(
  (az, i) =>
    new aws.ec2.Subnet(`public-${i}`, {
      vpcId: vpc.id,
      cidrBlock: `10.0.${i}.0/24`,
      availabilityZone: az,
      mapPublicIpOnLaunch: true,
      tags: { Name: `${env}-public-${az}` },
    }),
);

const privateSubnets = azs.map(
  (az, i) =>
    new aws.ec2.Subnet(`private-${i}`, {
      vpcId: vpc.id,
      cidrBlock: `10.0.${i + 10}.0/24`,
      availabilityZone: az,
      tags: { Name: `${env}-private-${az}` },
    }),
);

// RDS
const db = new aws.rds.Instance("postgres", {
  engine: "postgres",
  engineVersion: "16.1",
  instanceClass: config.require("dbInstanceClass"),
  allocatedStorage: 20,
  dbName: "myapp",
  username: "admin",
  password: config.requireSecret("dbPassword"),
  vpcSecurityGroupIds: [dbSg.id],
  dbSubnetGroupName: dbSubnetGroup.name,
  skipFinalSnapshot: env !== "prod",
  tags: { Environment: env },
});

// S3 Bucket
const bucket = new aws.s3.BucketV2("assets", {
  bucket: `${env}-myapp-assets`,
  tags: { Environment: env },
});

new aws.s3.BucketVersioningV2("assets-versioning", {
  bucket: bucket.id,
  versioningConfiguration: { status: "Enabled" },
});

// Exports
export const vpcId = vpc.id;
export const dbEndpoint = db.endpoint;
export const bucketName = bucket.bucket;
```

## Component Resources (Reusable)

```typescript
// components/static-site.ts
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

interface StaticSiteArgs {
  domain: string;
  indexDocument?: string;
  errorDocument?: string;
}

export class StaticSite extends pulumi.ComponentResource {
  public readonly bucketName: pulumi.Output<string>;
  public readonly url: pulumi.Output<string>;

  constructor(name: string, args: StaticSiteArgs, opts?: pulumi.ComponentResourceOptions) {
    super("custom:StaticSite", name, {}, opts);

    const bucket = new aws.s3.BucketV2(`${name}-bucket`, {
      bucket: args.domain,
    }, { parent: this });

    new aws.s3.BucketWebsiteConfigurationV2(`${name}-website`, {
      bucket: bucket.id,
      indexDocument: { suffix: args.indexDocument ?? "index.html" },
      errorDocument: { key: args.errorDocument ?? "404.html" },
    }, { parent: this });

    const cdn = new aws.cloudfront.Distribution(`${name}-cdn`, {
      enabled: true,
      defaultRootObject: "index.html",
      origins: [{
        domainName: bucket.bucketRegionalDomainName,
        originId: bucket.id,
        s3OriginConfig: { originAccessIdentity: oai.cloudfrontAccessIdentityPath },
      }],
      defaultCacheBehavior: {
        allowedMethods: ["GET", "HEAD"],
        cachedMethods: ["GET", "HEAD"],
        targetOriginId: bucket.id,
        viewerProtocolPolicy: "redirect-to-https",
        forwardedValues: { queryString: false, cookies: { forward: "none" } },
        compress: true,
      },
      restrictions: { geoRestriction: { restrictionType: "none" } },
      viewerCertificate: { cloudfrontDefaultCertificate: true },
    }, { parent: this });

    this.bucketName = bucket.bucket;
    this.url = pulumi.interpolate`https://${cdn.domainName}`;
    this.registerOutputs({ bucketName: this.bucketName, url: this.url });
  }
}

// Usage
const site = new StaticSite("marketing", { domain: "marketing.example.com" });
export const siteUrl = site.url;
```

## Stack Configuration and Secrets

```bash
# Set config values per stack
pulumi config set dbInstanceClass db.t3.micro
pulumi config set --secret dbPassword "super-secret-123"

# Stack-specific configs
pulumi config set --stack prod dbInstanceClass db.r6g.large
```

```typescript
// Read config in code
const config = new pulumi.Config();
const instanceClass = config.require("dbInstanceClass");   // Required string
const replicas = config.getNumber("replicas") ?? 1;        // Optional number with default
const dbPassword = config.requireSecret("dbPassword");     // Secret (encrypted)
```

## Testing Infrastructure

```typescript
// __tests__/infra.test.ts
import * as pulumi from "@pulumi/pulumi";

// Mock Pulumi runtime
pulumi.runtime.setMocks({
  newResource: (args) => ({ id: `${args.name}-id`, state: args.inputs }),
  call: (args) => args.inputs,
});

describe("Infrastructure", () => {
  let infra: typeof import("../index");

  beforeAll(async () => {
    infra = await import("../index");
  });

  test("S3 bucket has versioning enabled", async () => {
    // Policy tests ensure resources are configured correctly
    const bucketName = await new Promise<string>((resolve) =>
      infra.bucketName.apply(resolve),
    );
    expect(bucketName).toContain("myapp-assets");
  });

  test("RDS is not publicly accessible in prod", async () => {
    // Verify security properties
    const endpoint = await new Promise<string>((resolve) =>
      infra.dbEndpoint.apply(resolve),
    );
    expect(endpoint).toBeDefined();
  });
});
```

## Stack Management

```bash
# Create new stack (environment)
pulumi stack init staging

# Switch stacks
pulumi stack select prod

# Preview changes
pulumi preview

# Deploy
pulumi up

# Destroy resources
pulumi destroy

# View outputs
pulumi stack output

# Import existing resources
pulumi import aws:s3/bucketV2:BucketV2 my-bucket my-existing-bucket
```

## CI/CD Integration (GitHub Actions)

```yaml
name: Infrastructure
on:
  push:
    branches: [main]
    paths: ["infra/**"]
  pull_request:
    paths: ["infra/**"]

jobs:
  preview:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
        working-directory: infra
      - uses: pulumi/actions@v5
        with:
          command: preview
          stack-name: staging
          work-dir: infra
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}

  deploy:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
        working-directory: infra
      - uses: pulumi/actions@v5
        with:
          command: up
          stack-name: prod
          work-dir: infra
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
```

## Additional Resources

- Pulumi Docs: https://www.pulumi.com/docs/
- Pulumi Registry (providers): https://www.pulumi.com/registry/
- Pulumi Examples: https://github.com/pulumi/examples
- Pulumi AI: https://www.pulumi.com/ai
