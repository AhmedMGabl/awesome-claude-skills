---
name: kustomize-overlays
description: >
  This skill should be used when creating or reviewing Kustomize configurations
  covering base/overlay structure, strategic merge patches, JSON patches, config/secret
  generators, component reuse, and environment-specific Kubernetes configurations.
---

# Kustomize Overlay Patterns

Generate Kustomize configurations for managing Kubernetes manifests across environments with bases, overlays, patches, generators, and components.

## When to Use

- Structuring Kubernetes manifests with base/overlay separation for dev, staging, and production
- Writing strategic merge patches to modify resource fields per environment
- Applying JSON patches for precise array or field manipulations
- Generating ConfigMaps and Secrets from files or literals
- Creating reusable Kustomize components shared across overlays

## Example 1: Base/Overlay Directory Structure

```
app/
  base/
    kustomization.yaml
    deployment.yaml
    service.yaml
  overlays/
    dev/
      kustomization.yaml
      replica-patch.yaml
    production/
      kustomization.yaml
      replica-patch.yaml
      hpa.yaml
  components/
    monitoring/
      kustomization.yaml
      service-monitor.yaml
```

Base `kustomization.yaml`:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
  - service.yaml
commonLabels:
  app.kubernetes.io/name: myapp
```

## Example 2: Overlay with Strategic Merge Patches

```yaml
# overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../base
namespace: production
namePrefix: prod-
patches:
  - path: replica-patch.yaml
images:
  - name: myapp
    newName: registry.example.com/myapp
    newTag: v2.3.1
```

```yaml
# overlays/production/replica-patch.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 5
  template:
    spec:
      containers:
        - name: myapp
          resources:
            requests:
              cpu: 500m
              memory: 512Mi
            limits:
              cpu: "1"
              memory: 1Gi
```

## Example 3: JSON Patches

```yaml
# overlays/staging/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../base
namespace: staging
patches:
  - target:
      kind: Deployment
      name: myapp
    patch: |-
      - op: add
        path: /spec/template/spec/containers/-
        value:
          name: log-shipper
          image: fluent/fluent-bit:2.2
          volumeMounts:
            - name: logs
              mountPath: /var/log/app
      - op: add
        path: /spec/template/spec/volumes/-
        value:
          name: logs
          emptyDir: {}
```

## Example 4: ConfigMap and Secret Generators

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../base
configMapGenerator:
  - name: app-config
    behavior: merge
    literals:
      - DATABASE_HOST=dev-db.internal
      - CACHE_TTL=60
    files:
      - configs/feature-flags.json
secretGenerator:
  - name: app-secrets
    literals:
      - DB_PASSWORD=dev-password-123
generatorOptions:
  labels:
    app.kubernetes.io/part-of: myapp
```

## Example 5: Reusable Components

```yaml
# components/monitoring/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1alpha1
kind: Component
patches:
  - target:
      kind: Deployment
    patch: |-
      - op: add
        path: /spec/template/metadata/annotations/prometheus.io~1scrape
        value: "true"
      - op: add
        path: /spec/template/metadata/annotations/prometheus.io~1port
        value: "9090"
resources:
  - service-monitor.yaml
```

Reference in overlays:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../base
components:
  - ../../components/monitoring
```

## Example 6: Replacements

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../base
  - ingress.yaml
replacements:
  - source:
      kind: Service
      name: myapp
      fieldPath: metadata.name
    targets:
      - select:
          kind: Ingress
        fieldPaths:
          - spec.rules.0.http.paths.0.backend.service.name
```

Build and verify: `kustomize build overlays/production | kubectl apply -f -`
