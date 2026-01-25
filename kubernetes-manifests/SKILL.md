---
name: kubernetes-manifests
description: Kubernetes manifest creation and management including deployments, services, ingress, StatefulSets, ConfigMaps, secrets, RBAC, auto-scaling, and production-ready orchestration patterns.
---

# Kubernetes Manifests

This skill should be used when the user needs to create, manage, or deploy applications on Kubernetes. It covers writing manifests for various resource types, implementing production-ready patterns, configuring networking and storage, setting up RBAC, and deploying common application stacks.

## When to Use This Skill

Use this skill when you need to:

- Create Kubernetes manifests (Deployments, Services, Ingress, etc.)
- Deploy applications to Kubernetes clusters
- Configure production-ready Kubernetes resources
- Set up monitoring, auto-scaling, and high availability
- Implement RBAC and security policies
- Manage StatefulSets for databases or stateful applications
- Configure networking, load balancing, and ingress
- Deploy common stacks (MERN, microservices, etc.) on Kubernetes

## Core Kubernetes Resources

### Deployments

Deployments manage stateless applications with rolling updates and rollback capabilities.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  namespace: production
  labels:
    app: web-app
    version: v1
spec:
  replicas: 3
  revisionHistoryLimit: 10
  selector:
    matchLabels:
      app: web-app
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: web-app
        version: v1
    spec:
      containers:
      - name: web-app
        image: myapp:1.0.0
        ports:
        - containerPort: 3000
          name: http
          protocol: TCP
        env:
        - name: NODE_ENV
          value: production
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: url
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: cache
          mountPath: /app/.cache
      volumes:
      - name: tmp
        emptyDir: {}
      - name: cache
        emptyDir: {}
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - web-app
              topologyKey: kubernetes.io/hostname
```

### Services

Services provide stable networking endpoints for pods.

```yaml
# ClusterIP Service (internal only)
apiVersion: v1
kind: Service
metadata:
  name: web-app
  namespace: production
spec:
  type: ClusterIP
  selector:
    app: web-app
  ports:
  - name: http
    port: 80
    targetPort: 3000
    protocol: TCP
  sessionAffinity: None

---
# LoadBalancer Service (external access)
apiVersion: v1
kind: Service
metadata:
  name: web-app-lb
  namespace: production
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: nlb
spec:
  type: LoadBalancer
  selector:
    app: web-app
  ports:
  - name: http
    port: 80
    targetPort: 3000
    protocol: TCP
  - name: https
    port: 443
    targetPort: 3000
    protocol: TCP

---
# Headless Service (for StatefulSets)
apiVersion: v1
kind: Service
metadata:
  name: mongodb
  namespace: production
spec:
  clusterIP: None
  selector:
    app: mongodb
  ports:
  - name: mongodb
    port: 27017
    targetPort: 27017
```

### ConfigMaps and Secrets

Store configuration and sensitive data separately from application code.

```yaml
# ConfigMap for application configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: production
data:
  API_URL: "https://api.example.com"
  CACHE_TTL: "3600"
  LOG_LEVEL: "info"
  config.json: |
    {
      "feature_flags": {
        "new_ui": true,
        "beta_features": false
      },
      "limits": {
        "max_upload_size": "10MB",
        "rate_limit": 100
      }
    }

---
# Secret for sensitive data (base64 encoded)
apiVersion: v1
kind: Secret
metadata:
  name: database-credentials
  namespace: production
type: Opaque
data:
  username: cG9zdGdyZXM=  # base64 encoded
  password: c3VwZXJzZWNyZXQ=
  url: cG9zdGdyZXNxbDovL3Bvc3RncmVzOnN1cGVyc2VjcmV0QGRiOjU0MzIvbXlhcHA=

---
# TLS Secret for ingress
apiVersion: v1
kind: Secret
metadata:
  name: tls-certificate
  namespace: production
type: kubernetes.io/tls
data:
  tls.crt: <base64-encoded-certificate>
  tls.key: <base64-encoded-private-key>
```

Create secrets from files:
```bash
# From literal values
kubectl create secret generic database-credentials \
  --from-literal=username=postgres \
  --from-literal=password=supersecret \
  -n production

# From files
kubectl create secret generic app-secrets \
  --from-file=./api-key.txt \
  --from-file=./service-account.json \
  -n production

# TLS certificate
kubectl create secret tls tls-certificate \
  --cert=path/to/tls.crt \
  --key=path/to/tls.key \
  -n production
```

### Ingress

Ingress manages external access to services with routing rules and TLS termination.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-app-ingress
  namespace: production
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
spec:
  tls:
  - hosts:
    - app.example.com
    - www.app.example.com
    secretName: tls-certificate
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-app
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8080
  - host: www.app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-app
            port:
              number: 80
```

## StatefulSets

StatefulSets manage stateful applications with stable network identities and persistent storage.

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mongodb
  namespace: production
spec:
  serviceName: mongodb
  replicas: 3
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo:6.0
        ports:
        - containerPort: 27017
          name: mongodb
        env:
        - name: MONGO_INITDB_ROOT_USERNAME
          valueFrom:
            secretKeyRef:
              name: mongodb-credentials
              key: username
        - name: MONGO_INITDB_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mongodb-credentials
              key: password
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        volumeMounts:
        - name: data
          mountPath: /data/db
        livenessProbe:
          tcpSocket:
            port: 27017
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          tcpSocket:
            port: 27017
          initialDelaySeconds: 10
          periodSeconds: 5
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 100Gi
```

## Jobs and CronJobs

Jobs run one-off tasks, while CronJobs run tasks on a schedule.

```yaml
# One-off Job
apiVersion: batch/v1
kind: Job
metadata:
  name: database-migration
  namespace: production
spec:
  backoffLimit: 3
  activeDeadlineSeconds: 600
  template:
    metadata:
      labels:
        app: migration
    spec:
      restartPolicy: OnFailure
      containers:
      - name: migrate
        image: myapp:1.0.0
        command: ["npm", "run", "migrate"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: url
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi

---
# CronJob for scheduled tasks
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup-database
  namespace: production
spec:
  schedule: "0 2 * * *"  # Every day at 2 AM
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      template:
        metadata:
          labels:
            app: backup
        spec:
          restartPolicy: OnFailure
          containers:
          - name: backup
            image: backup-tool:1.0.0
            command:
            - /bin/sh
            - -c
            - |
              pg_dump $DATABASE_URL > /backups/db-$(date +%Y%m%d-%H%M%S).sql
              aws s3 cp /backups/*.sql s3://my-backups/database/
            env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: database-credentials
                  key: url
            - name: AWS_ACCESS_KEY_ID
              valueFrom:
                secretKeyRef:
                  name: aws-credentials
                  key: access-key-id
            - name: AWS_SECRET_ACCESS_KEY
              valueFrom:
                secretKeyRef:
                  name: aws-credentials
                  key: secret-access-key
            volumeMounts:
            - name: backups
              mountPath: /backups
          volumes:
          - name: backups
            emptyDir: {}
```

## Persistent Storage

Persistent Volumes (PV) and Persistent Volume Claims (PVC) provide storage for stateful applications.

```yaml
# StorageClass definition
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
allowVolumeExpansion: true
reclaimPolicy: Retain

---
# Persistent Volume Claim
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-data
  namespace: production
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 50Gi
```

Using PVC in a pod:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-storage
spec:
  containers:
  - name: app
    image: myapp:1.0.0
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: app-data
```

## RBAC (Role-Based Access Control)

Control access to Kubernetes resources with ServiceAccounts, Roles, and RoleBindings.

```yaml
# ServiceAccount for application
apiVersion: v1
kind: ServiceAccount
metadata:
  name: web-app
  namespace: production

---
# Role with specific permissions
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: configmap-reader
  namespace: production
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["secrets"]
  resourceNames: ["app-secrets"]
  verbs: ["get"]

---
# RoleBinding to connect ServiceAccount with Role
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: web-app-configmap-reader
  namespace: production
subjects:
- kind: ServiceAccount
  name: web-app
  namespace: production
roleRef:
  kind: Role
  name: configmap-reader
  apiGroup: rbac.authorization.k8s.io

---
# ClusterRole for cluster-wide permissions
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]

---
# ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: read-pods-global
subjects:
- kind: ServiceAccount
  name: monitoring
  namespace: observability
roleRef:
  kind: ClusterRole
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

## Auto-Scaling

Horizontal Pod Autoscaler (HPA) automatically scales pods based on metrics.

```yaml
# HPA based on CPU and memory
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-app-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
      - type: Pods
        value: 4
        periodSeconds: 30
      selectPolicy: Max

---
# Vertical Pod Autoscaler (VPA)
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: web-app-vpa
  namespace: production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  updatePolicy:
    updateMode: Auto
  resourcePolicy:
    containerPolicies:
    - containerName: web-app
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 2000m
        memory: 2Gi
```

## NetworkPolicies

Control network traffic between pods for security.

```yaml
# Deny all ingress traffic by default
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress

---
# Allow specific traffic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-web-app
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: web-app
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: nginx-ingress
    ports:
    - protocol: TCP
      port: 3000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
  - to:  # Allow DNS
    - namespaceSelector:
        matchLabels:
          name: kube-system
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
```

## Complete MERN Stack Example

Full MERN (MongoDB, Express, React, Node.js) stack deployment on Kubernetes.

```yaml
# Namespace
apiVersion: v1
kind: Namespace
metadata:
  name: mern-app

---
# MongoDB StatefulSet
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mongodb
  namespace: mern-app
spec:
  serviceName: mongodb
  replicas: 1
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo:6.0
        ports:
        - containerPort: 27017
        env:
        - name: MONGO_INITDB_ROOT_USERNAME
          value: admin
        - name: MONGO_INITDB_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mongodb-secret
              key: password
        volumeMounts:
        - name: data
          mountPath: /data/db
        resources:
          requests:
            cpu: 250m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 2Gi
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi

---
# MongoDB Service
apiVersion: v1
kind: Service
metadata:
  name: mongodb
  namespace: mern-app
spec:
  clusterIP: None
  selector:
    app: mongodb
  ports:
  - port: 27017
    targetPort: 27017

---
# Backend Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: mern-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: mern-backend:1.0.0
        ports:
        - containerPort: 5000
        env:
        - name: MONGODB_URI
          value: mongodb://admin:$(MONGO_PASSWORD)@mongodb:27017/mernapp?authSource=admin
        - name: MONGO_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mongodb-secret
              key: password
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: jwt-secret
              key: secret
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 5

---
# Backend Service
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: mern-app
spec:
  selector:
    app: backend
  ports:
  - port: 5000
    targetPort: 5000

---
# Frontend Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: mern-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: mern-frontend:1.0.0
        ports:
        - containerPort: 80
        env:
        - name: REACT_APP_API_URL
          value: http://backend:5000
        resources:
          requests:
            cpu: 50m
            memory: 128Mi
          limits:
            cpu: 200m
            memory: 256Mi
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5

---
# Frontend Service
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: mern-app
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 80

---
# Ingress
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mern-ingress
  namespace: mern-app
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - mernapp.example.com
    secretName: mern-tls
  rules:
  - host: mernapp.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 5000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 80

---
# Secrets
apiVersion: v1
kind: Secret
metadata:
  name: mongodb-secret
  namespace: mern-app
type: Opaque
stringData:
  password: supersecret123

---
apiVersion: v1
kind: Secret
metadata:
  name: jwt-secret
  namespace: mern-app
type: Opaque
stringData:
  secret: jwt-super-secret-key

---
# HPA for backend
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: mern-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

Deploy the stack:
```bash
# Create namespace and deploy
kubectl apply -f mern-stack.yaml

# Check deployment status
kubectl get all -n mern-app

# View logs
kubectl logs -f deployment/backend -n mern-app
kubectl logs -f deployment/frontend -n mern-app

# Scale manually if needed
kubectl scale deployment/backend --replicas=5 -n mern-app
```

## Monitoring with Prometheus & Grafana

Deploy monitoring stack for observability.

```yaml
# Prometheus ServiceAccount
apiVersion: v1
kind: ServiceAccount
metadata:
  name: prometheus
  namespace: monitoring

---
# ClusterRole for Prometheus
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: prometheus
rules:
- apiGroups: [""]
  resources:
  - nodes
  - nodes/proxy
  - services
  - endpoints
  - pods
  verbs: ["get", "list", "watch"]
- apiGroups:
  - extensions
  resources:
  - ingresses
  verbs: ["get", "list", "watch"]

---
# ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: prometheus
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: prometheus
subjects:
- kind: ServiceAccount
  name: prometheus
  namespace: monitoring

---
# Prometheus ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s

    scrape_configs:
    - job_name: 'kubernetes-pods'
      kubernetes_sd_configs:
      - role: pod
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__

---
# Prometheus Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      serviceAccountName: prometheus
      containers:
      - name: prometheus
        image: prom/prometheus:v2.40.0
        args:
        - '--config.file=/etc/prometheus/prometheus.yml'
        - '--storage.tsdb.path=/prometheus'
        - '--storage.tsdb.retention.time=30d'
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: config
          mountPath: /etc/prometheus
        - name: storage
          mountPath: /prometheus
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 4Gi
      volumes:
      - name: config
        configMap:
          name: prometheus-config
      - name: storage
        persistentVolumeClaim:
          claimName: prometheus-storage

---
# Grafana Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:9.3.0
        ports:
        - containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          valueFrom:
            secretKeyRef:
              name: grafana-credentials
              key: password
        volumeMounts:
        - name: storage
          mountPath: /var/lib/grafana
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
      volumes:
      - name: storage
        persistentVolumeClaim:
          claimName: grafana-storage
```

## Common kubectl Commands

Essential commands for managing Kubernetes resources.

```bash
# Cluster information
kubectl cluster-info
kubectl get nodes
kubectl top nodes

# Namespace management
kubectl create namespace production
kubectl get namespaces
kubectl config set-context --current --namespace=production

# Deployment management
kubectl apply -f deployment.yaml
kubectl get deployments
kubectl describe deployment web-app
kubectl rollout status deployment/web-app
kubectl rollout history deployment/web-app
kubectl rollout undo deployment/web-app
kubectl rollout restart deployment/web-app

# Pod management
kubectl get pods
kubectl get pods -o wide
kubectl describe pod pod-name
kubectl logs pod-name
kubectl logs -f pod-name  # Follow logs
kubectl logs pod-name -c container-name  # Specific container
kubectl port-forward pod-name 8080:80
kubectl top pods

# Service management
kubectl get services
kubectl describe service web-app
kubectl expose deployment web-app --port=80 --target-port=8080

# ConfigMap and Secret management
kubectl create configmap app-config --from-file=config.json
kubectl get configmaps
kubectl describe configmap app-config
kubectl create secret generic db-creds --from-literal=password=secret
kubectl get secrets

# Scaling
kubectl scale deployment web-app --replicas=5
kubectl autoscale deployment web-app --min=2 --max=10 --cpu-percent=70

# Resource management
kubectl get all
kubectl get all -n production
kubectl delete -f deployment.yaml
kubectl delete deployment web-app
kubectl delete pod pod-name --force --grace-period=0

# Debug and troubleshooting
kubectl describe pod pod-name
kubectl logs pod-name --previous  # Previous container logs
kubectl events
kubectl get events --sort-by=.metadata.creationTimestamp

# Apply and manage manifests
kubectl apply -f ./manifests/
kubectl apply -k ./kustomize/
kubectl diff -f deployment.yaml

# Context and configuration
kubectl config get-contexts
kubectl config use-context production-cluster
kubectl config set-context --current --namespace=production
```

## Production Best Practices

### Resource Management

Always set resource requests and limits:

```yaml
resources:
  requests:
    cpu: 100m      # Minimum guaranteed
    memory: 128Mi
  limits:
    cpu: 500m      # Maximum allowed
    memory: 512Mi
```

### Health Checks

Implement liveness and readiness probes:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

### Security

- Run as non-root user
- Use read-only root filesystem
- Disable privilege escalation
- Use NetworkPolicies
- Implement RBAC
- Scan images for vulnerabilities
- Use Secrets for sensitive data
- Enable Pod Security Standards

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop:
    - ALL
```

### High Availability

- Use multiple replicas (minimum 2)
- Configure pod anti-affinity
- Use rolling updates with maxSurge and maxUnavailable
- Implement proper health checks
- Set pod disruption budgets

```yaml
podAntiAffinity:
  preferredDuringSchedulingIgnoredDuringExecution:
  - weight: 100
    podAffinityTerm:
      labelSelector:
        matchExpressions:
        - key: app
          operator: In
          values:
          - web-app
      topologyKey: kubernetes.io/hostname
```

### Labels and Annotations

Use consistent labels for organization:

```yaml
metadata:
  labels:
    app: web-app
    version: v1
    environment: production
    tier: frontend
    team: platform
  annotations:
    description: "Main web application"
    owner: "platform-team@example.com"
    monitoring: "enabled"
```

## Troubleshooting

Common issues and solutions:

**Pods not starting:**
```bash
kubectl describe pod pod-name
kubectl logs pod-name
kubectl get events --field-selector involvedObject.name=pod-name
```

**ImagePullBackOff:**
- Check image name and tag
- Verify image registry credentials
- Ensure image exists

**CrashLoopBackOff:**
- Check application logs
- Verify configuration (ConfigMaps, Secrets)
- Check resource limits
- Review health check configuration

**Service not accessible:**
- Verify service selector matches pod labels
- Check NetworkPolicies
- Verify ingress configuration
- Test with port-forward first

**Resource issues:**
```bash
kubectl top nodes
kubectl top pods
kubectl describe node node-name
```

## Additional Resources

- Official Kubernetes documentation: https://kubernetes.io/docs/
- kubectl cheat sheet: https://kubernetes.io/docs/reference/kubectl/cheatsheet/
- Best practices: https://kubernetes.io/docs/concepts/configuration/overview/
- Security: https://kubernetes.io/docs/concepts/security/
