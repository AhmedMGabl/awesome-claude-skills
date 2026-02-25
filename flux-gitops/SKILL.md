---
name: flux-gitops
description: >
  This skill should be used when setting up or reviewing Flux CD GitOps workflows
  covering source controllers, kustomization resources, Helm releases, image automation,
  notifications, multi-tenancy, and progressive delivery patterns.
---

# Flux CD GitOps Patterns

Generate Flux v2 resources for continuous delivery through GitOps.

## When to Use

- Defining GitRepository or HelmRepository sources
- Creating Flux Kustomization resources with dependency ordering
- Managing HelmRelease resources with remediation
- Setting up image automation to detect new tags and update Git
- Configuring Alerts for Slack or webhooks
- Designing multi-tenant Flux architectures

## Example 1: Source Definitions

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: app-repo
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/org/app-manifests
  ref:
    branch: main
  secretRef:
    name: git-credentials
---
apiVersion: source.toolkit.fluxcd.io/v1
kind: HelmRepository
metadata:
  name: bitnami
  namespace: flux-system
spec:
  interval: 30m
  url: https://charts.bitnami.com/bitnami
```

## Example 2: Flux Kustomization with Dependencies

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: infrastructure
  namespace: flux-system
spec:
  interval: 10m
  sourceRef:
    kind: GitRepository
    name: app-repo
  path: ./infrastructure/controllers
  prune: true
  wait: true
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: apps
  namespace: flux-system
spec:
  interval: 5m
  sourceRef:
    kind: GitRepository
    name: app-repo
  path: ./apps/production
  prune: true
  dependsOn:
    - name: infrastructure
  postBuild:
    substituteFrom:
      - kind: ConfigMap
        name: cluster-settings
```

## Example 3: HelmRelease with Remediation

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: myapp
  namespace: production
spec:
  interval: 15m
  chart:
    spec:
      chart: myapp
      version: "1.4.x"
      sourceRef:
        kind: HelmRepository
        name: internal-charts
        namespace: flux-system
  values:
    replicaCount: 3
  upgrade:
    remediation:
      retries: 3
    cleanupOnFail: true
```

## Example 4: Image Automation Pipeline

```yaml
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImageRepository
metadata:
  name: myapp
  namespace: flux-system
spec:
  image: registry.example.com/myapp
  interval: 5m
---
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImagePolicy
metadata:
  name: myapp
  namespace: flux-system
spec:
  imageRepositoryRef:
    name: myapp
  policy:
    semver:
      range: ">=1.0.0 <2.0.0"
---
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImageUpdateAutomation
metadata:
  name: myapp
  namespace: flux-system
spec:
  interval: 30m
  sourceRef:
    kind: GitRepository
    name: app-repo
  git:
    commit:
      author:
        name: fluxbot
        email: flux@example.com
    push:
      branch: main
  update:
    path: ./apps
    strategy: Setters
```

Mark images with setter comments: `image: registry.example.com/myapp:1.3.2 # {"$imagepolicy": "flux-system:myapp"}`

## Example 5: Notifications

```yaml
apiVersion: notification.toolkit.fluxcd.io/v1beta3
kind: Provider
metadata:
  name: slack
  namespace: flux-system
spec:
  type: slack
  channel: deployments
  secretRef:
    name: slack-bot-token
---
apiVersion: notification.toolkit.fluxcd.io/v1beta3
kind: Alert
metadata:
  name: deployment-alerts
  namespace: flux-system
spec:
  providerRef:
    name: slack
  eventSeverity: info
  eventSources:
    - kind: Kustomization
      name: "*"
    - kind: HelmRelease
      name: "*"
```

## Example 6: Multi-Tenant Repository Structure

```
clusters/prod-us-east-1/{flux-system/,infrastructure.yaml,apps.yaml}
infrastructure/controllers/
apps/base/myapp/release.yaml
tenants/team-alpha/{rbac.yaml,namespace.yaml,git-source.yaml}
```

Each tenant gets a namespace, RBAC, and Flux source for isolation.
