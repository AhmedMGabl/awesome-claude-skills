---
name: jsonnet-config
description: >
  Jsonnet configuration patterns covering data templating, functions, imports, object composition,
  hidden fields, array comprehensions, and Kubernetes manifest generation.
  This skill should be used when writing Jsonnet templates for configuration generation,
  composing objects with mixins and late binding, using the standard library for data
  transformation, generating Kubernetes manifests with Tanka or kubecfg, or structuring
  large configuration codebases with imports and parameterized functions.
---

# Jsonnet Configuration

## When to Use

- Generating JSON or YAML configuration from parameterized Jsonnet templates
- Composing configuration objects with mixins, late binding, and inheritance
- Writing reusable library functions for common configuration patterns
- Using `std` library functions for string formatting, array manipulation, and assertions
- Generating Kubernetes manifests with Grafana Tanka or kubecfg

## Examples

### 1. Objects, Functions, and Conditionals

```jsonnet
local defaults = { region: 'us-east-1', instanceType: 't3.micro', monitoring: true };

local makeInstance(name, env, overrides={}) =
  defaults + overrides + {
    name: name, environment: env,
    tags: { Name: name, Environment: env, ManagedBy: 'jsonnet' },
    alerting: if defaults.monitoring && env == 'prod' then true else false,
  };

{
  production: makeInstance('web-prod', 'prod', { instanceType: 't3.large' }),
  staging: makeInstance('web-staging', 'staging'),
  development: makeInstance('web-dev', 'dev', { monitoring: false }),
}
```

```bash
jsonnet config.jsonnet            # Evaluate to JSON
jsonnet -y config.jsonnet         # Evaluate to YAML
jsonnet --ext-str region=eu-west-1 config.jsonnet
```

### 2. Imports, Hidden Fields, and Library Structure

```jsonnet
// lib/conventions.libsonnet
{
  _config:: { namespace: 'default', domain: 'example.com',
    labels: { 'app.kubernetes.io/managed-by': 'jsonnet' } },

  withNamespace(ns):: self { _config+:: { namespace: ns } },
  withDomain(d):: self { _config+:: { domain: d } },
  nameFor(component):: '%s-%s' % [self._config.namespace, component],
  labelsFor(component):: self._config.labels + {
    'app.kubernetes.io/name': component,
    'app.kubernetes.io/part-of': self._config.namespace,
  },
}
```

```jsonnet
// environments/prod.jsonnet
local cfg = (import '../lib/conventions.libsonnet')
  .withNamespace('myapp').withDomain('prod.example.com');

{ serviceName: cfg.nameFor('api'), labels: cfg.labelsFor('api'), domain: cfg._config.domain }
```

### 3. Array and Object Comprehensions

```jsonnet
local services = ['api', 'worker', 'web'];
local ports = { api: 8080, worker: 9090, web: 3000 };
local envVars = { LOG_LEVEL: 'info', DB_HOST: 'postgres.svc.cluster.local' };

{
  containers: [
    { name: svc, image: 'registry/%s:latest' % svc, ports: [{ containerPort: ports[svc] }],
      env: [{ name: k, value: envVars[k] } for k in std.objectFields(envVars)] }
    for svc in services
  ],
  serviceConfigs: {
    [svc]: { replicas: if svc == 'web' then 3 else 2, port: ports[svc] }
    for svc in services
  },
}
```

### 4. Mixins and Object Composition

```jsonnet
// lib/mixins.libsonnet
{
  deploymentMixin:: {
    apiVersion: 'apps/v1', kind: 'Deployment',
    metadata: { labels: {} },
    spec: { replicas: 1, template: { metadata: { labels: {} }, spec: { containers: [] } } },
  },
  securityMixin:: {
    spec+: { template+: { spec+: {
      securityContext: { runAsNonRoot: true, fsGroup: 1000 },
      containers: [c + { securityContext: { readOnlyRootFilesystem: true } } for c in super.containers],
    } } },
  },
  resourcesMixin(cpu='100m', mem='128Mi'):: {
    spec+: { template+: { spec+: {
      containers: [c + { resources: { requests: { cpu: cpu, memory: mem } } } for c in super.containers],
    } } },
  },
}
```

```jsonnet
local m = import 'lib/mixins.libsonnet';
m.deploymentMixin + m.securityMixin + m.resourcesMixin('250m', '256Mi') + {
  metadata+: { name: 'my-api', labels+: { app: 'my-api' } },
  spec+: { replicas: 3, selector: { matchLabels: { app: 'my-api' } },
    template+: { metadata+: { labels+: { app: 'my-api' } },
      spec+: { containers: [{ name: 'api', image: 'my-api:v1.0', ports: [{ containerPort: 8080 }] }] } } },
}
```

### 5. Standard Library Usage

```jsonnet
local data = { users: [
  { name: 'alice', role: 'admin', active: true },
  { name: 'bob', role: 'viewer', active: true },
  { name: 'charlie', role: 'editor', active: false },
] };

{
  upperNames: [std.asciiUpper(u.name) for u in data.users],
  activeUsers: std.filter(function(u) u.active, data.users),
  summary: std.map(function(u) '%s (%s)' % [u.name, u.role], data.users),
  allRoles: std.set([u.role for u in data.users]),
  verified:
    assert std.length(data.users) > 0 : 'Users list must not be empty';
    true,
}
```

### 6. Kubernetes Manifests with Tanka

```jsonnet
local k = import 'github.com/grafana/jsonnet-libs/ksonnet-util/kausal.libsonnet';
local deploy = k.apps.v1.deployment;
local container = k.core.v1.container;
local port = k.core.v1.containerPort;

{
  _config:: { name: 'my-app', image: 'my-app:v2.1.0', port: 8080, replicas: 3 },
  local c = container.new($._config.name, $._config.image)
    + container.withPorts([port.new('http', $._config.port)])
    + k.util.resourcesRequests('200m', '256Mi'),
  deployment: deploy.new($._config.name, $._config.replicas, [c]),
  service: k.util.serviceFor(self.deployment),
}
```

```bash
tk init && tk env add environments/prod --namespace=production
tk show environments/prod    # Preview manifests
tk apply environments/prod   # Apply to cluster
```
