---
name: helm-charts-advanced
description: >
  This skill should be used when developing or reviewing advanced Helm charts covering
  chart structure, values templating, hooks, dependencies, library charts, testing,
  OCI registries, and production chart best practices.
---

# Advanced Helm Chart Patterns

Generate Helm chart resources for packaging and deploying Kubernetes applications. Cover Chart.yaml, Go templating, helpers, lifecycle hooks, dependencies, testing, and OCI distribution.

## When to Use

- Scaffolding new Helm charts with proper metadata and dependencies
- Writing Go template logic with conditional blocks, loops, and helpers
- Configuring lifecycle hooks for migrations and cleanup
- Managing chart dependencies and library chart abstractions
- Writing Helm tests and publishing charts to OCI registries

## Example 1: Chart.yaml with Dependencies

```yaml
apiVersion: v2
name: myapp
description: A production web application chart
type: application
version: 1.4.0
appVersion: "2.3.1"
kubeVersion: ">=1.25.0"
maintainers:
  - name: Platform Team
    email: platform@example.com
dependencies:
  - name: postgresql
    version: "13.2.x"
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled
  - name: redis
    version: "18.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    condition: redis.enabled
```

Run `helm dependency update` to pull sub-charts into `charts/`.

## Example 2: Go Templating with Helpers

```yaml
# templates/_helpers.tpl
{{- define "myapp.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{- define "myapp.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}

{{- define "myapp.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "myapp.fullname" . }}
  labels: {{- include "myapp.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels: {{- include "myapp.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
      labels: {{- include "myapp.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          ports:
            - name: http
              containerPort: {{ .Values.service.targetPort }}
          {{- with .Values.resources }}
          resources: {{- toYaml . | nindent 12 }}
          {{- end }}
```

## Example 3: Lifecycle Hooks

```yaml
# templates/hooks/db-migrate.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "myapp.fullname" . }}-migrate
  annotations:
    "helm.sh/hook": pre-install,pre-upgrade
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
spec:
  backoffLimit: 3
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: migrate
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          command: ["./migrate", "--direction", "up"]
          envFrom:
            - secretRef:
                name: {{ include "myapp.fullname" . }}-db
```

## Example 4: Values.yaml Defaults

```yaml
replicaCount: 2
image:
  repository: registry.example.com/myapp
  tag: ""
  pullPolicy: IfNotPresent
service:
  type: ClusterIP
  port: 80
  targetPort: 8080
ingress:
  enabled: false
  className: nginx
  hosts:
    - host: myapp.example.com
      paths:
        - path: /
          pathType: Prefix
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
autoscaling:
  enabled: false
  minReplicas: 2
  maxReplicas: 10
postgresql:
  enabled: true
redis:
  enabled: false
```

## Example 5: Helm Test

```yaml
# templates/tests/test-connection.yaml
apiVersion: v1
kind: Pod
metadata:
  name: {{ include "myapp.fullname" . }}-test
  annotations:
    "helm.sh/hook": test
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
spec:
  restartPolicy: Never
  containers:
    - name: curl-test
      image: curlimages/curl:8.5.0
      command: ["sh", "-c", "curl -sf http://{{ include \"myapp.fullname\" . }}:{{ .Values.service.port }}/healthz"]
```

Run with `helm test <release-name> --logs`.

## Example 6: OCI Registry Publishing

```bash
helm registry login registry.example.com -u user -p token
helm package . --version 1.4.0 --app-version 2.3.1
helm push myapp-1.4.0.tgz oci://registry.example.com/charts
helm install myapp oci://registry.example.com/charts/myapp --version 1.4.0
```
