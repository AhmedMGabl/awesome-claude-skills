---
name: gcp-cloud-run
description: Google Cloud Run patterns covering containerized services, Jobs, Pub/Sub triggers, Cloud SQL connections, Secret Manager, traffic splitting, and CI/CD deployment.
---

# GCP Cloud Run

This skill should be used when deploying containerized applications on Google Cloud Run. It covers services, Jobs, Pub/Sub, Cloud SQL, secrets, traffic splitting, and CI/CD.

## When to Use This Skill

Use this skill when you need to:

- Deploy containerized services on Cloud Run
- Process events with Pub/Sub triggers
- Connect to Cloud SQL databases
- Manage secrets with Secret Manager
- Configure traffic splitting and revisions

## Service Configuration

```yaml
# service.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: my-api
  annotations:
    run.googleapis.com/launch-stage: GA
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "1"
        autoscaling.knative.dev/maxScale: "100"
        run.googleapis.com/cpu-throttling: "false"
        run.googleapis.com/cloudsql-instances: PROJECT:REGION:INSTANCE
    spec:
      containerConcurrency: 80
      timeoutSeconds: 300
      containers:
        - image: gcr.io/PROJECT/my-api:latest
          ports:
            - containerPort: 8080
          resources:
            limits:
              cpu: "2"
              memory: 1Gi
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: database-url
                  key: latest
          startupProbe:
            httpGet:
              path: /healthz
            initialDelaySeconds: 0
            periodSeconds: 1
            failureThreshold: 30
```

## Dockerfile

```dockerfile
FROM node:20-slim AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-slim
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

ENV PORT=8080
EXPOSE 8080
USER node
CMD ["node", "dist/index.js"]
```

## Cloud SQL Connection

```typescript
import { Pool } from "pg";

const pool = new Pool({
  host: process.env.INSTANCE_UNIX_SOCKET
    ? undefined
    : process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  ...(process.env.INSTANCE_UNIX_SOCKET && {
    host: `/cloudsql/${process.env.INSTANCE_CONNECTION_NAME}`,
  }),
});
```

## Pub/Sub Push Handler

```typescript
import express from "express";

const app = express();
app.use(express.json());

app.post("/pubsub", async (req, res) => {
  const message = req.body.message;
  const data = JSON.parse(
    Buffer.from(message.data, "base64").toString()
  );

  try {
    await processEvent(data);
    res.status(200).send("OK");
  } catch (error) {
    console.error("Processing failed:", error);
    res.status(500).send("Error");  // triggers retry
  }
});

app.listen(process.env.PORT || 8080);
```

## Cloud Run Jobs

```bash
# Deploy a job
gcloud run jobs create data-migration \
  --image gcr.io/PROJECT/migration:latest \
  --tasks 10 \
  --max-retries 3 \
  --task-timeout 3600s \
  --set-env-vars DATABASE_URL=secret:database-url

# Execute the job
gcloud run jobs execute data-migration
```

## Deploy Commands

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT/my-api

# Deploy service
gcloud run deploy my-api \
  --image gcr.io/PROJECT/my-api \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars NODE_ENV=production \
  --set-secrets DATABASE_URL=database-url:latest \
  --add-cloudsql-instances PROJECT:REGION:INSTANCE \
  --min-instances 1 \
  --max-instances 100 \
  --cpu 2 \
  --memory 1Gi

# Traffic splitting
gcloud run services update-traffic my-api \
  --to-revisions my-api-v2=90,my-api-v1=10
```

## Cloud Build CI/CD

```yaml
# cloudbuild.yaml
steps:
  - name: "gcr.io/cloud-builders/docker"
    args: ["build", "-t", "gcr.io/$PROJECT_ID/my-api:$COMMIT_SHA", "."]
  - name: "gcr.io/cloud-builders/docker"
    args: ["push", "gcr.io/$PROJECT_ID/my-api:$COMMIT_SHA"]
  - name: "gcr.io/cloud-builders/gcloud"
    args:
      - "run"
      - "deploy"
      - "my-api"
      - "--image=gcr.io/$PROJECT_ID/my-api:$COMMIT_SHA"
      - "--region=us-central1"
```

## Additional Resources

- Cloud Run: https://cloud.google.com/run/docs
- Cloud SQL: https://cloud.google.com/sql/docs/postgres/connect-run
- Cloud Build: https://cloud.google.com/build/docs
