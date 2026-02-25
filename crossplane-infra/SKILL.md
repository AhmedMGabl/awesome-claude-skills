---
name: crossplane-infra
description: >
  This skill should be used when generating or reviewing Crossplane infrastructure
  resources including composite resources, compositions, XRDs, provider configurations,
  claims, EnvironmentConfigs, and GitOps workflows for declarative cloud provisioning.
---

# Crossplane Infrastructure Patterns

Generate Crossplane resource definitions for managing cloud infrastructure declaratively through Kubernetes.

## When to Use

- Defining CompositeResourceDefinitions (XRDs) for cloud infrastructure abstractions
- Writing Compositions that map claims to managed resources across AWS, GCP, or Azure
- Configuring Crossplane providers with authentication
- Creating Claims to request infrastructure
- Setting up EnvironmentConfigs for environment-specific values
- Structuring GitOps repositories for Crossplane resources

## Example 1: CompositeResourceDefinition (XRD)

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xdatabases.infra.example.com
spec:
  group: infra.example.com
  names:
    kind: XDatabase
    plural: xdatabases
  claimNames:
    kind: Database
    plural: databases
  versions:
    - name: v1alpha1
      served: true
      referenceable: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                parameters:
                  type: object
                  properties:
                    engine:
                      type: string
                      enum: [postgres, mysql]
                    storageGB:
                      type: integer
                      default: 20
                  required: [engine]
              required: [parameters]
```

## Example 2: Composition for AWS RDS

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: xdatabases.aws.infra.example.com
  labels:
    provider: aws
spec:
  compositeTypeRef:
    apiVersion: infra.example.com/v1alpha1
    kind: XDatabase
  resources:
    - name: rds-instance
      base:
        apiVersion: rds.aws.upbound.io/v1beta1
        kind: Instance
        spec:
          forProvider:
            region: us-east-1
            instanceClass: db.t3.micro
            allocatedStorage: 20
            skipFinalSnapshot: true
      patches:
        - type: FromCompositeFieldPath
          fromFieldPath: spec.parameters.engine
          toFieldPath: spec.forProvider.engine
        - type: FromCompositeFieldPath
          fromFieldPath: spec.parameters.storageGB
          toFieldPath: spec.forProvider.allocatedStorage
```

## Example 3: Provider Configuration with IRSA

```yaml
apiVersion: aws.upbound.io/v1beta1
kind: ProviderConfig
metadata:
  name: aws-prod
spec:
  credentials:
    source: IRSA
---
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws-rds
spec:
  package: xpkg.upbound.io/upbound/provider-aws-rds:v1.1.0
  controllerConfigRef:
    name: aws-irsa-config
---
apiVersion: pkg.crossplane.io/v1alpha1
kind: ControllerConfig
metadata:
  name: aws-irsa-config
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/crossplane
spec:
  serviceAccountName: crossplane-provider-aws
```

## Example 4: Claim for Requesting Infrastructure

```yaml
apiVersion: infra.example.com/v1alpha1
kind: Database
metadata:
  name: orders-db
  namespace: orders-team
spec:
  parameters:
    engine: postgres
    storageGB: 50
  compositionSelector:
    matchLabels:
      provider: aws
  writeConnectionSecretToRef:
    name: orders-db-creds
```

## Example 5: EnvironmentConfig

```yaml
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: EnvironmentConfig
metadata:
  name: production
  labels:
    environment: production
data:
  region: us-east-1
  vpcId: vpc-0abc123def456
  instanceClass: db.r6g.large
```

Reference in a Composition via `spec.environment.environmentConfigs`:

```yaml
spec:
  environment:
    environmentConfigs:
      - type: Selector
        selector:
          matchLabels:
            - key: environment
              type: FromCompositeFieldPath
              valueFromFieldPath: spec.parameters.environment
  resources:
    - name: rds-instance
      patches:
        - type: FromEnvironmentFieldPath
          fromFieldPath: instanceClass
          toFieldPath: spec.forProvider.instanceClass
```

## Example 6: GitOps Repository Structure

```
infrastructure/
  crossplane/
    providers/
      aws-provider.yaml
      provider-config.yaml
    apis/
      database/
        definition.yaml       # XRD
        composition-aws.yaml   # AWS Composition
        composition-gcp.yaml   # GCP Composition
    environment-configs/
      production.yaml
      staging.yaml
    claims/
      team-orders/database.yaml
      team-payments/database.yaml
```

Apply in order: providers first, then XRDs and Compositions, then Claims. Use Flux or ArgoCD with `dependsOn` to enforce ordering.
