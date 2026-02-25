---
name: pulumi-infrastructure
description: Pulumi infrastructure-as-code patterns covering TypeScript/Python programs, AWS/Azure/GCP resources, stacks, configuration, secrets, component resources, and testing.
---

# Pulumi Infrastructure

This skill should be used when provisioning cloud infrastructure with Pulumi. It covers TypeScript/Python programs, cloud resources, stacks, configuration, and testing.

## When to Use This Skill

Use this skill when you need to:

- Provision cloud infrastructure with real programming languages
- Manage AWS, Azure, or GCP resources with Pulumi
- Use stacks for multi-environment deployments
- Create reusable component resources
- Test infrastructure code

## Setup

```bash
curl -fsSL https://get.pulumi.com | sh
pulumi new aws-typescript  # or aws-python, azure-typescript, gcp-typescript
```

## Basic AWS Program (TypeScript)

```typescript
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

const config = new pulumi.Config();
const environment = pulumi.getStack();

// VPC
const vpc = new aws.ec2.Vpc("main", {
    cidrBlock: "10.0.0.0/16",
    enableDnsHostnames: true,
    tags: { Name: `${environment}-vpc` },
});

// Subnets
const publicSubnet = new aws.ec2.Subnet("public", {
    vpcId: vpc.id,
    cidrBlock: "10.0.1.0/24",
    mapPublicIpOnLaunch: true,
    tags: { Name: `${environment}-public` },
});

// Security Group
const webSg = new aws.ec2.SecurityGroup("web", {
    vpcId: vpc.id,
    ingress: [
        { protocol: "tcp", fromPort: 80, toPort: 80, cidrBlocks: ["0.0.0.0/0"] },
        { protocol: "tcp", fromPort: 443, toPort: 443, cidrBlocks: ["0.0.0.0/0"] },
    ],
    egress: [
        { protocol: "-1", fromPort: 0, toPort: 0, cidrBlocks: ["0.0.0.0/0"] },
    ],
});

// S3 Bucket
const bucket = new aws.s3.Bucket("assets", {
    bucket: `${environment}-assets`,
    acl: "private",
});

// RDS
const db = new aws.rds.Instance("main", {
    engine: "postgres",
    engineVersion: "15",
    instanceClass: "db.t3.micro",
    allocatedStorage: 20,
    dbName: config.require("dbName"),
    username: config.require("dbUsername"),
    password: config.requireSecret("dbPassword"),
    skipFinalSnapshot: true,
    vpcSecurityGroupIds: [webSg.id],
});

// Exports
export const vpcId = vpc.id;
export const bucketName = bucket.id;
export const dbEndpoint = db.endpoint;
```

## Component Resources

```typescript
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

interface WebAppArgs {
    domain: string;
    instanceType: string;
    dbInstanceClass: string;
}

class WebApp extends pulumi.ComponentResource {
    public readonly url: pulumi.Output<string>;

    constructor(name: string, args: WebAppArgs, opts?: pulumi.ComponentResourceOptions) {
        super("custom:WebApp", name, {}, opts);

        const bucket = new aws.s3.Bucket(`${name}-assets`, {}, { parent: this });

        const instance = new aws.ec2.Instance(`${name}-server`, {
            instanceType: args.instanceType,
            ami: "ami-0c55b159cbfafe1f0",
            tags: { Name: `${name}-server` },
        }, { parent: this });

        this.url = pulumi.interpolate`http://${instance.publicIp}`;
        this.registerOutputs({ url: this.url });
    }
}

const app = new WebApp("myapp", {
    domain: "example.com",
    instanceType: "t3.micro",
    dbInstanceClass: "db.t3.micro",
});

export const appUrl = app.url;
```

## Configuration and Secrets

```bash
pulumi config set dbName mydb
pulumi config set dbUsername admin
pulumi config set --secret dbPassword supersecret
pulumi config set aws:region us-east-1
```

```typescript
const config = new pulumi.Config();
const dbName = config.require("dbName");
const dbPassword = config.requireSecret("dbPassword");
const port = config.getNumber("port") ?? 8080;
```

## Stacks

```bash
pulumi stack init dev
pulumi stack init staging
pulumi stack init prod

pulumi stack select dev
pulumi up
```

## Commands

```bash
pulumi new aws-typescript    # create project
pulumi up                    # deploy
pulumi preview               # preview changes
pulumi destroy               # tear down
pulumi stack output          # show outputs
```

## Additional Resources

- Pulumi: https://www.pulumi.com/docs/
- AWS Guide: https://www.pulumi.com/docs/clouds/aws/
- Examples: https://github.com/pulumi/examples
