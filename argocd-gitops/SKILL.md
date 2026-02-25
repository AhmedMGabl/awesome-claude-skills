---
name: argocd-gitops
description: Argo CD GitOps patterns covering application manifests, sync policies, Helm/Kustomize integration, ApplicationSets, multi-cluster deployment, and RBAC configuration.
---

# Argo CD GitOps

This skill should be used when implementing GitOps with Argo CD. It covers application manifests, sync policies, Helm/Kustomize integration, ApplicationSets, and multi-cluster deployment.

## When to Use This Skill

Use this skill when you need to:

- Implement GitOps continuous delivery with Argo CD
- Define Application and ApplicationSet resources
- Configure auto-sync and self-healing
- Deploy with Helm charts or Kustomize overlays
- Manage multi-cluster and multi-environment deployments

## Application Manifest

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/myapp-deploy.git
    targetRevision: main
    path: k8s/overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: myapp
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
      - PruneLast=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

## Helm Application

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp-helm
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/helm-charts.git
    targetRevision: main
    path: charts/myapp
    helm:
      releaseName: myapp
      valueFiles:
        - values.yaml
        - values-production.yaml
      parameters:
        - name: image.tag
          value: "v2.0.0"
        - name: replicaCount
          value: "3"
  destination:
    server: https://kubernetes.default.svc
    namespace: myapp
```

## Kustomize Application

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp-kustomize
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/myapp-deploy.git
    targetRevision: main
    path: k8s/overlays/staging
    kustomize:
      images:
        - myapp=myregistry/myapp:v2.0.0
      namePrefix: staging-
  destination:
    server: https://kubernetes.default.svc
    namespace: staging
```

## ApplicationSet (Multi-Environment)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: myapp-environments
  namespace: argocd
spec:
  generators:
    - list:
        elements:
          - environment: dev
            namespace: myapp-dev
            cluster: https://kubernetes.default.svc
            values_file: values-dev.yaml
          - environment: staging
            namespace: myapp-staging
            cluster: https://kubernetes.default.svc
            values_file: values-staging.yaml
          - environment: production
            namespace: myapp-prod
            cluster: https://prod-cluster.example.com
            values_file: values-prod.yaml
  template:
    metadata:
      name: "myapp-{{environment}}"
    spec:
      project: default
      source:
        repoURL: https://github.com/myorg/helm-charts.git
        targetRevision: main
        path: charts/myapp
        helm:
          valueFiles:
            - "{{values_file}}"
      destination:
        server: "{{cluster}}"
        namespace: "{{namespace}}"
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
```

## Git Generator (Directory-Based)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: microservices
  namespace: argocd
spec:
  generators:
    - git:
        repoURL: https://github.com/myorg/services.git
        revision: main
        directories:
          - path: "services/*"
  template:
    metadata:
      name: "{{path.basename}}"
    spec:
      project: default
      source:
        repoURL: https://github.com/myorg/services.git
        targetRevision: main
        path: "{{path}}"
      destination:
        server: https://kubernetes.default.svc
        namespace: "{{path.basename}}"
```

## Project RBAC

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: myteam
  namespace: argocd
spec:
  description: My team's applications
  sourceRepos:
    - "https://github.com/myorg/*"
  destinations:
    - namespace: "myapp-*"
      server: https://kubernetes.default.svc
  clusterResourceWhitelist:
    - group: ""
      kind: Namespace
  roles:
    - name: developer
      policies:
        - p, proj:myteam:developer, applications, get, myteam/*, allow
        - p, proj:myteam:developer, applications, sync, myteam/*, allow
```

## CLI Commands

```bash
argocd app create myapp -f app.yaml
argocd app sync myapp
argocd app get myapp
argocd app diff myapp
argocd app rollback myapp 1
argocd app delete myapp
argocd app list
```

## Additional Resources

- Argo CD: https://argo-cd.readthedocs.io/
- ApplicationSet: https://argo-cd.readthedocs.io/en/stable/operator-manual/applicationset/
- Best Practices: https://argo-cd.readthedocs.io/en/stable/user-guide/best_practices/
