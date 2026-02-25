---
name: pulumi-infra
description: >
  Pulumi infrastructure patterns covering TypeScript/Python resource definitions, stack management,
  component resources, automation API, policy-as-code, and cloud provider integration.
  This skill should be used when creating infrastructure with Pulumi using general-purpose languages,
  building reusable component resources, managing multi-stack deployments, writing policy packs
  with CrossGuard, or automating infrastructure workflows via the Automation API.
---

# Pulumi Infrastructure

## When to Use

- Defining cloud infrastructure using TypeScript, Python, or other general-purpose languages
- Creating reusable component resources for organizational standards
- Managing stack configuration, secrets, and stack references across environments
- Automating `pulumi up`/`destroy` workflows with the Automation API
- Enforcing compliance rules with CrossGuard policy packs

## Examples

### 1. Stack Configuration and Resource Creation (TypeScript)

```typescript
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

const config = new pulumi.Config();
const environment = config.require("environment");

const vpc = new aws.ec2.Vpc("main-vpc", {
  cidrBlock: "10.0.0.0/16",
  enableDnsSupport: true,
  tags: { Name: `${environment}-vpc`, Environment: environment },
});

const subnet = new aws.ec2.Subnet("public-subnet", {
  vpcId: vpc.id,
  cidrBlock: "10.0.1.0/24",
  mapPublicIpOnLaunch: true,
});

export const vpcId = vpc.id;
```

```bash
pulumi config set environment staging
pulumi config set --secret dbPassword "s3cret!"
```

### 2. Component Resources (TypeScript)

```typescript
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

interface StaticSiteArgs { indexDocument?: string; tags?: Record<string, string> }

class StaticSite extends pulumi.ComponentResource {
  public readonly websiteUrl: pulumi.Output<string>;

  constructor(name: string, args: StaticSiteArgs, opts?: pulumi.ComponentResourceOptions) {
    super("custom:aws:StaticSite", name, {}, opts);
    const bucket = new aws.s3.BucketV2(`${name}-bucket`, { tags: args.tags }, { parent: this });
    const website = new aws.s3.BucketWebsiteConfigurationV2(`${name}-web`, {
      bucket: bucket.id,
      indexDocument: { suffix: args.indexDocument || "index.html" },
    }, { parent: this });
    this.websiteUrl = website.websiteEndpoint;
    this.registerOutputs({ websiteUrl: this.websiteUrl });
  }
}

const site = new StaticSite("my-site", { tags: { Project: "marketing" } });
export const url = site.websiteUrl;
```

### 3. Multi-Cloud with Python

```python
import pulumi
import pulumi_aws as aws
import pulumi_azure_native as azure

config = pulumi.Config()
env = config.require("environment")

bucket = aws.s3.BucketV2("data", tags={"Environment": env})
rg = azure.resources.ResourceGroup("rg", resource_group_name=f"{env}-rg", location="eastus")
storage = azure.storage.StorageAccount("storage",
    resource_group_name=rg.name, location=rg.location,
    sku=azure.storage.SkuArgs(name="Standard_LRS"), kind="StorageV2")

pulumi.export("aws_bucket", bucket.bucket)
pulumi.export("azure_storage", storage.name)
```

### 4. Stack References

```typescript
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

const networkStack = new pulumi.StackReference("myorg/networking/prod");
const subnetIds = networkStack.getOutput("privateSubnetIds");

const cluster = new aws.ecs.Cluster("app-cluster", {
  settings: [{ name: "containerInsights", value: "enabled" }],
});
const service = new aws.ecs.Service("app-svc", {
  cluster: cluster.arn, desiredCount: 2,
  networkConfiguration: { subnets: subnetIds.apply(ids => ids as string[]), assignPublicIp: false },
});
export const clusterArn = cluster.arn;
```

### 5. Automation API

```typescript
import { LocalWorkspace } from "@pulumi/pulumi/automation";

async function deploy() {
  const stack = await LocalWorkspace.createOrSelectStack({ stackName: "staging", workDir: "./infra" });
  await stack.setConfig("environment", { value: "staging" });
  await stack.setConfig("dbPassword", { value: "s3cret!", secret: true });
  await stack.refresh({ onOutput: console.info });
  const result = await stack.up({ onOutput: console.info });
  console.log(`VPC ID: ${result.outputs.vpcId.value}`);
}
deploy().catch(console.error);
```

### 6. CrossGuard Policy Pack

```typescript
import * as policy from "@pulumi/policy";

new policy.PolicyPack("compliance", {
  policies: [
    {
      name: "required-tags",
      description: "All resources must have Environment and Owner tags",
      enforcementLevel: "mandatory",
      validateResource: (args, reportViolation) => {
        const tags = (args.props as any).tags;
        if (tags && typeof tags === "object") {
          for (const tag of ["Environment", "Owner"]) {
            if (!(tag in tags)) reportViolation(`Missing required tag: ${tag}`);
          }
        }
      },
    },
    {
      name: "restrict-instance-types",
      description: "Only allow approved EC2 instance types",
      enforcementLevel: "advisory",
      validateResource: policy.validateResourceOfType(
        "aws:ec2/instance:Instance",
        (inst, _args, report) => {
          const allowed = ["t3.micro", "t3.small", "t3.medium"];
          if (!allowed.includes(inst.instanceType)) report(`Unapproved type: ${inst.instanceType}`);
        },
      ),
    },
  ],
});
```

```bash
pulumi preview --policy-pack ./policy-pack
```
