---
name: cdk8s-constructs
description: >
  CDK8s patterns covering Kubernetes manifest generation with TypeScript/Python, custom constructs,
  Helm chart imports, cdk8s-plus abstractions, and testing with snapshots.
  This skill should be used when generating Kubernetes YAML from TypeScript or Python using cdk8s,
  building reusable construct libraries, importing existing Helm charts, leveraging cdk8s-plus
  for high-level Deployment/Service/Ingress definitions, or writing snapshot tests for manifests.
---

# CDK8s Constructs

## When to Use

- Generating Kubernetes manifests programmatically with TypeScript or Python
- Building reusable constructs to encapsulate common deployment patterns
- Importing Helm charts into cdk8s applications for type-safe configuration
- Using cdk8s-plus abstractions for Deployments, Services, and Ingresses
- Writing snapshot tests to validate generated YAML output

## Examples

### 1. App, Chart, and Low-Level Constructs

```typescript
import { App, Chart, ChartProps } from "cdk8s";
import { KubeDeployment, KubeService, IntOrString } from "./imports/k8s";
import { Construct } from "constructs";

interface WebAppProps extends ChartProps { image: string; replicas?: number; port?: number }

class WebAppChart extends Chart {
  constructor(scope: Construct, id: string, props: WebAppProps) {
    super(scope, id, props);
    const label = { app: id };
    const port = props.port ?? 80;

    new KubeDeployment(this, "deployment", {
      spec: {
        replicas: props.replicas ?? 2,
        selector: { matchLabels: label },
        template: {
          metadata: { labels: label },
          spec: { containers: [{
            name: "app", image: props.image,
            ports: [{ containerPort: port }],
            resources: { requests: { cpu: "100m" as any, memory: "128Mi" as any } },
          }] },
        },
      },
    });

    new KubeService(this, "service", {
      spec: { type: "ClusterIP", ports: [{ port: 80, targetPort: IntOrString.fromNumber(port) }], selector: label },
    });
  }
}

const app = new App();
new WebAppChart(app, "my-web-app", { image: "nginx:1.25", replicas: 3 });
app.synth();
```

```bash
cdk8s init typescript-app && cdk8s import k8s && cdk8s synth
```

### 2. cdk8s-plus High-Level Constructs

```typescript
import { App, Chart } from "cdk8s";
import * as kplus from "cdk8s-plus-31";
import { Construct } from "constructs";

class ApiChart extends Chart {
  constructor(scope: Construct, id: string) {
    super(scope, id);
    const config = new kplus.ConfigMap(this, "config", {
      data: { LOG_LEVEL: "info", DB_HOST: "postgres.default.svc.cluster.local" },
    });
    const deploy = new kplus.Deployment(this, "api", {
      replicas: 3,
      containers: [{
        image: "my-api:v1.2.0", portNumber: 8080,
        envFrom: [kplus.Env.fromConfigMap(config)],
        liveness: kplus.Probe.fromHttpGet("/healthz", { port: 8080 }),
        readiness: kplus.Probe.fromHttpGet("/readyz", { port: 8080 }),
      }],
    });
    const svc = deploy.exposeViaService({ serviceType: kplus.ServiceType.CLUSTER_IP });
    new kplus.Ingress(this, "ingress", {
      rules: [{ host: "api.example.com", path: "/", backend: kplus.IngressBackend.fromService(svc) }],
    });
  }
}

const app = new App();
new ApiChart(app, "api");
app.synth();
```

### 3. Custom Reusable Construct

```typescript
import { Construct } from "constructs";
import * as kplus from "cdk8s-plus-31";

interface MicroserviceProps {
  image: string; port: number; replicas?: number;
  envVars?: Record<string, string>; ingressHost?: string;
}

class Microservice extends Construct {
  public readonly service: kplus.Service;
  constructor(scope: Construct, id: string, props: MicroserviceProps) {
    super(scope, id);
    const env: Record<string, kplus.EnvValue> = {};
    for (const [k, v] of Object.entries(props.envVars ?? {}))
      env[k] = kplus.EnvValue.fromValue(v);

    const deploy = new kplus.Deployment(this, "deploy", {
      replicas: props.replicas ?? 2,
      containers: [{ image: props.image, portNumber: props.port, envVariables: env }],
    });
    this.service = deploy.exposeViaService({ serviceType: kplus.ServiceType.CLUSTER_IP });
    if (props.ingressHost) {
      new kplus.Ingress(this, "ingress", {
        rules: [{ host: props.ingressHost, path: "/", backend: kplus.IngressBackend.fromService(this.service) }],
      });
    }
  }
}
```

### 4. Helm Chart Import

```bash
cdk8s import helm:https://charts.bitnami.com/bitnami/redis@19.0.0
```

```typescript
import { App, Chart } from "cdk8s";
import { Redis } from "./imports/redis";

class CacheChart extends Chart {
  constructor(scope: any, id: string) {
    super(scope, id);
    new Redis(this, "redis", {
      releaseName: "cache",
      values: {
        architecture: "replication",
        replica: { replicaCount: 3 },
        auth: { enabled: true, password: "change-me" },
      },
    });
  }
}
const app = new App();
new CacheChart(app, "cache");
app.synth();
```

### 5. Snapshot Testing with Jest

```typescript
import { Testing } from "cdk8s";
import { WebAppChart } from "../lib/web-app-chart";

describe("WebAppChart", () => {
  test("default config produces expected manifests", () => {
    const app = Testing.app();
    const chart = new WebAppChart(app, "test", { image: "nginx:1.25" });
    expect(Testing.synth(chart)).toMatchSnapshot();
  });

  test("custom replicas reflected in deployment", () => {
    const app = Testing.app();
    const chart = new WebAppChart(app, "test", { image: "nginx:1.25", replicas: 5 });
    const results = Testing.synth(chart);
    const deploy = results.find((r: any) => r.kind === "Deployment");
    expect(deploy.spec.replicas).toBe(5);
  });
});
```

```bash
npx jest --updateSnapshot
cdk8s synth && kubectl apply -f dist/
```
