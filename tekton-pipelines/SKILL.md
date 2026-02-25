---
name: tekton-pipelines
description: >
  Tekton CI/CD patterns covering Tasks, Pipelines, PipelineRuns, workspaces, triggers, results,
  custom steps, and Kubernetes-native build automation.
  This skill should be used when defining Tekton Tasks and Pipelines for cloud-native CI/CD,
  configuring workspaces for shared storage between steps, setting up triggers for event-driven
  builds, passing results between tasks, or integrating Tekton Hub community tasks.
---

# Tekton Pipelines

## When to Use

- Defining Tekton Tasks with multi-step container-based build logic
- Creating Pipelines that orchestrate multiple Tasks with dependencies
- Configuring workspaces for sharing data between steps and tasks
- Setting up EventListeners, TriggerBindings, and TriggerTemplates for webhook-driven builds
- Passing results between tasks for dynamic pipeline behavior
- Integrating community tasks from Tekton Hub (git-clone, buildah, kaniko)

## Examples

### 1. Task with Parameters, Steps, and Results

```yaml
apiVersion: tekton.dev/v1
kind: Task
metadata:
  name: build-and-test
spec:
  params:
    - name: image
      type: string
    - name: context
      type: string
      default: "."
  workspaces:
    - name: source
  results:
    - name: image-digest
    - name: test-status
  steps:
    - name: run-tests
      image: node:20-slim
      workingDir: $(workspaces.source.path)
      script: |
        #!/usr/bin/env bash
        npm ci && npm test \
          && echo "pass" > $(results.test-status.path) \
          || echo "fail" > $(results.test-status.path)
    - name: build-image
      image: gcr.io/kaniko-project/executor:latest
      args:
        - --context=$(workspaces.source.path)/$(params.context)
        - --destination=$(params.image)
        - --digest-file=$(results.image-digest.path)
```

### 2. Pipeline with Task Dependencies and Result Passing

```yaml
apiVersion: tekton.dev/v1
kind: Pipeline
metadata:
  name: ci-pipeline
spec:
  params:
    - { name: repo-url, type: string }
    - { name: revision, type: string, default: main }
    - { name: image, type: string }
  workspaces:
    - name: shared-workspace
  tasks:
    - name: fetch-source
      taskRef: { name: git-clone }
      workspaces: [{ name: output, workspace: shared-workspace }]
      params: [{ name: url, value: "$(params.repo-url)" }, { name: revision, value: "$(params.revision)" }]
    - name: build-and-test
      taskRef: { name: build-and-test }
      runAfter: [fetch-source]
      workspaces: [{ name: source, workspace: shared-workspace }]
      params: [{ name: image, value: "$(params.image)" }]
    - name: deploy
      taskRef: { name: kubernetes-deploy }
      runAfter: [build-and-test]
      when: [{ input: "$(tasks.build-and-test.results.test-status)", operator: in, values: ["pass"] }]
      params: [{ name: image, value: "$(params.image)@$(tasks.build-and-test.results.image-digest)" }]
  finally:
    - name: notify
      taskRef: { name: send-notification }
      params: [{ name: message, value: "Pipeline done for $(params.repo-url)" }]
```

### 3. PipelineRun with Workspaces

```yaml
apiVersion: tekton.dev/v1
kind: PipelineRun
metadata:
  generateName: ci-run-
spec:
  pipelineRef: { name: ci-pipeline }
  params:
    - { name: repo-url, value: "https://github.com/myorg/myapp.git" }
    - { name: revision, value: feature-branch }
    - { name: image, value: "registry.example.com/myapp:latest" }
  workspaces:
    - name: shared-workspace
      volumeClaimTemplate:
        spec:
          accessModes: [ReadWriteOnce]
          resources: { requests: { storage: 1Gi } }
  taskRunTemplate:
    serviceAccountName: pipeline-sa
  timeouts: { pipeline: "1h", tasks: "30m" }
```

### 4. Triggers (EventListener, TriggerBinding, TriggerTemplate)

```yaml
apiVersion: triggers.tekton.dev/v1beta1
kind: TriggerBinding
metadata: { name: github-push-binding }
spec:
  params:
    - { name: repo-url, value: "$(body.repository.clone_url)" }
    - { name: revision, value: "$(body.after)" }
---
apiVersion: triggers.tekton.dev/v1beta1
kind: TriggerTemplate
metadata: { name: ci-trigger-template }
spec:
  params: [{ name: repo-url }, { name: revision }]
  resourcetemplates:
    - apiVersion: tekton.dev/v1
      kind: PipelineRun
      metadata: { generateName: ci-run- }
      spec:
        pipelineRef: { name: ci-pipeline }
        params:
          - { name: repo-url, value: "$(tt.params.repo-url)" }
          - { name: revision, value: "$(tt.params.revision)" }
        workspaces:
          - name: shared-workspace
            volumeClaimTemplate:
              spec: { accessModes: [ReadWriteOnce], resources: { requests: { storage: 1Gi } } }
---
apiVersion: triggers.tekton.dev/v1beta1
kind: EventListener
metadata: { name: github-listener }
spec:
  serviceAccountName: tekton-triggers-sa
  triggers:
    - name: github-push
      interceptors:
        - ref: { name: github }
          params: [{ name: eventTypes, value: ["push"] }]
      bindings: [{ ref: github-push-binding }]
      template: { ref: ci-trigger-template }
```

### 5. Task with Sidecar

```yaml
apiVersion: tekton.dev/v1
kind: Task
metadata: { name: integration-test }
spec:
  workspaces: [{ name: source }]
  sidecars:
    - name: postgres
      image: postgres:16
      env:
        - { name: POSTGRES_DB, value: testdb }
        - { name: POSTGRES_USER, value: testuser }
        - { name: POSTGRES_PASSWORD, value: testpass }
  steps:
    - name: wait-for-db
      image: postgres:16
      script: |
        until pg_isready -h localhost -U testuser; do sleep 2; done
    - name: run-tests
      image: golang:1.22
      workingDir: $(workspaces.source.path)
      script: go test -v -tags=integration ./tests/...
```

### 6. CLI and Tekton Hub

```bash
tkn hub install task git-clone   # Install community tasks
tkn hub install task buildah
tkn hub install task kaniko
tkn pipeline start ci-pipeline \
  --param repo-url=https://github.com/myorg/myapp.git \
  --param revision=main --showlog
tkn pipelinerun list             # Monitor runs
```
