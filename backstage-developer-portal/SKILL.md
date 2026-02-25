---
name: backstage-developer-portal
description: >
  This skill should be used when building or configuring Backstage developer portals
  covering catalog entities, software templates, TechDocs, plugins, search integration,
  authentication providers, and organizational modeling.
---

# Backstage Developer Portal Patterns

Generate Backstage configuration and catalog definitions for internal developer portals.

## When to Use

- Defining catalog-info.yaml entities for components, APIs, systems, and resources
- Creating software templates (scaffolder) for project bootstrapping
- Configuring TechDocs for documentation-as-code
- Setting up authentication providers and organizational entity hierarchies
- Configuring search integration with catalog and docs collators

## Example 1: Catalog Entity Definitions

```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: orders-service
  description: Handles order processing
  annotations:
    backstage.io/techdocs-ref: dir:.
    github.com/project-slug: org/orders-service
  tags: [java, grpc]
spec:
  type: service
  lifecycle: production
  owner: group:commerce-team
  system: commerce-platform
  providesApis: [orders-api]
  consumesApis: [payments-api]
---
apiVersion: backstage.io/v1alpha1
kind: API
metadata:
  name: orders-api
spec:
  type: grpc
  lifecycle: production
  owner: group:commerce-team
  definition:
    $text: ./api/orders.proto
```

## Example 2: Software Template (Scaffolder)

```yaml
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: microservice-template
  title: Create a Microservice
spec:
  owner: group:platform-team
  type: service
  parameters:
    - title: Service Details
      required: [name, owner]
      properties:
        name:
          title: Service Name
          type: string
          pattern: "^[a-z][a-z0-9-]*$"
        owner:
          title: Owner
          type: string
          ui:field: OwnerPicker
  steps:
    - id: fetch
      action: fetch:template
      input:
        url: ./skeleton
        values:
          name: ${{ parameters.name }}
    - id: publish
      action: publish:github
      input:
        repoUrl: github.com?owner=org&repo=${{ parameters.name }}
    - id: register
      action: catalog:register
      input:
        repoContentsUrl: ${{ steps.publish.output.repoContentsUrl }}
        catalogInfoPath: /catalog-info.yaml
```

## Example 3: TechDocs Configuration

```yaml
# mkdocs.yml
site_name: Orders Service
nav:
  - Home: index.md
  - Architecture: architecture.md
plugins:
  - techdocs-core
```

Backstage app-config:

```yaml
techdocs:
  builder: external
  publisher:
    type: awsS3
    awsS3:
      bucketName: backstage-techdocs
      region: us-east-1
```

## Example 4: Organizational Modeling

```yaml
apiVersion: backstage.io/v1alpha1
kind: Domain
metadata:
  name: commerce
spec:
  owner: group:commerce-leadership
---
apiVersion: backstage.io/v1alpha1
kind: System
metadata:
  name: commerce-platform
spec:
  owner: group:commerce-team
  domain: commerce
---
apiVersion: backstage.io/v1alpha1
kind: Group
metadata:
  name: commerce-team
spec:
  type: team
  parent: engineering
  members: [user:jane.smith, user:john.doe]
---
apiVersion: backstage.io/v1alpha1
kind: User
metadata:
  name: jane.smith
spec:
  memberOf: [commerce-team]
```

## Example 5: Authentication Configuration

```yaml
auth:
  providers:
    github:
      production:
        clientId: ${GITHUB_CLIENT_ID}
        clientSecret: ${GITHUB_CLIENT_SECRET}
        signIn:
          resolvers:
            - resolver: usernameMatchingUserEntityName
catalog:
  providers:
    github:
      mainOrg:
        organization: my-org
        catalogPath: /catalog-info.yaml
        filters:
          branch: main
        schedule:
          frequency: { minutes: 30 }
          timeout: { minutes: 3 }
```

Additional providers (Microsoft, Google) follow the same pattern with `clientId`, `clientSecret`, and `signIn.resolvers`.

## Example 6: Search Integration

```yaml
search:
  pg:
    highlightOptions:
      useHighlight: true
```

```typescript
indexBuilder.addCollator({
  schedule: env.scheduler.createScheduledTaskRunner({
    frequency: { minutes: 10 },
    timeout: { minutes: 15 },
  }),
  factory: DefaultCatalogCollatorFactory.fromConfig(env.config, {
    discovery: env.discovery, tokenManager: env.tokenManager,
  }),
});
```
