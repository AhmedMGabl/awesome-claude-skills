---
name: cicd-pipelines
description: CI/CD pipeline configuration covering GitHub Actions, GitLab CI, Docker multi-stage builds, deployment strategies (blue-green, canary, rolling), secrets management, pipeline optimization, and production deployment automation.
---

# CI/CD Pipelines

This skill provides production-ready CI/CD pipeline configurations for GitHub Actions, GitLab CI, Docker builds, and deployment automation. To use this skill, describe the target platform, language/framework, and deployment environment.

---

## 1. GitHub Actions Workflows

### Complete CI Workflow (Node.js)

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npm run format:check

  test:
    name: Test (Node ${{ matrix.node-version }})
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        node-version: [18, 20, 22]
        exclude:
          - os: windows-latest
            node-version: 18
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: npm
      - run: npm ci
      - run: npm test -- --coverage
      - name: Upload coverage
        if: matrix.os == 'ubuntu-latest' && matrix.node-version == 20
        uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          files: ./coverage/lcov.info

  build:
    name: Build and Push Image
    runs-on: ubuntu-latest
    needs: [lint, test]
    permissions:
      contents: read
      packages: write
    outputs:
      image-digest: ${{ steps.build.outputs.digest }}
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,prefix=sha-,format=short
      - name: Build and push
        id: build
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.event_name \!= 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          platforms: linux/amd64,linux/arm64
```

### CD Workflow with Environment Promotion

```yaml
# .github/workflows/cd.yml
name: CD

on:
  workflow_run:
    workflows: [CI]
    types: [completed]
    branches: [main]

jobs:
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    environment:
      name: staging
      url: https://staging.example.com
    steps:
      - uses: actions/checkout@v4
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN_STAGING }}
          aws-region: ${{ vars.AWS_REGION }}
      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster staging-cluster \
            --service my-app-staging \
            --force-new-deployment
      - name: Wait for stability
        run: |
          aws ecs wait services-stable \
            --cluster staging-cluster \
            --services my-app-staging
      - run: npm run test:smoke -- --url https://staging.example.com

  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: deploy-staging
    environment:
      name: production
      url: https://example.com
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN_PROD }}
          aws-region: ${{ vars.AWS_REGION }}
      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster prod-cluster \
            --service my-app-prod \
            --force-new-deployment
      - name: Wait for stability
        run: |
          aws ecs wait services-stable \
            --cluster prod-cluster \
            --services my-app-prod
```

### Reusable Workflow

```yaml
# .github/workflows/reusable-deploy.yml
name: Reusable Deploy

on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
      image-tag:
        required: true
        type: string
      cluster-name:
        required: true
        type: string
    secrets:
      AWS_ROLE_ARN:
        required: true

jobs:
  deploy:
    name: Deploy to ${{ inputs.environment }}
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: us-east-1
      - name: Update ECS task definition
        run: |
          IMAGE="${{ inputs.image-tag }}"
          CLUSTER="${{ inputs.cluster-name }}"
          TASK=$(aws ecs describe-task-definition --task-definition my-app --query taskDefinition --output json)
          NEW=$(echo  | jq --arg I  '.containerDefinitions[0].image=$I')
          REV=$(aws ecs register-task-definition --cli-input-json  --query taskDefinition.taskDefinitionArn --output text)
          aws ecs update-service --cluster  --service my-app --task-definition 

# Caller example:
# jobs:
#   deploy-prod:
#     uses: ./.github/workflows/reusable-deploy.yml
#     with:
#       environment: production
#       image-tag: ghcr.io/org/app:sha-abc123
#       cluster-name: prod-cluster
#     secrets:
#       AWS_ROLE_ARN: ${{ secrets.AWS_ROLE_ARN_PROD }}
```

---

## 2. GitLab CI/CD

### Complete .gitlab-ci.yml

```yaml
# .gitlab-ci.yml
stages:
  - validate
  - build
  - test
  - security
  - package
  - deploy-staging
  - deploy-production

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: /certs
  IMAGE_TAG: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA
  LATEST_TAG: $CI_REGISTRY_IMAGE:latest

default:
  image: node:20-alpine
  cache:
    key:
      files: [package-lock.json]
    paths: [node_modules/]
    policy: pull-push

lint:
  stage: validate
  script: [npm ci, npm run lint, npm run format:check]
  rules:
    - if: $CI_PIPELINE_SOURCE == 'merge_request_event'
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

build:
  stage: build
  script: [npm ci, npm run build]
  artifacts:
    paths: [dist/]
    expire_in: 1 hour

unit-tests:
  stage: test
  script: [npm ci, npm run test:unit -- --coverage]
  coverage: '/Lines\s*:\s*(\d+\.?\d*)%/'
  artifacts:
    when: always
    reports:
      junit: test-results/junit.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
    paths: [coverage/]
    expire_in: 1 week

integration-tests:
  stage: test
  services:
    - name: postgres:15-alpine
      alias: postgres
  variables:
    POSTGRES_DB: testdb
    POSTGRES_USER: testuser
    POSTGRES_PASSWORD: $TEST_DB_PASSWORD
    DATABASE_URL: postgresql://testuser:$TEST_DB_PASSWORD@postgres:5432/testdb
  script: [npm ci, npm run test:integration]
  rules:
    - if: $CI_PIPELINE_SOURCE == 'merge_request_event'
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

sast:
  stage: security
  include:
    - template: Security/SAST.gitlab-ci.yml

dependency-scanning:
  stage: security
  include:
    - template: Security/Dependency-Scanning.gitlab-ci.yml

container-scanning:
  stage: security
  include:
    - template: Security/Container-Scanning.gitlab-ci.yml
  needs: [package]
  variables:
    CS_IMAGE: $IMAGE_TAG

package:
  stage: package
  image: docker:24
  services: [docker:24-dind]
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - |
      docker build \
        --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
        --build-arg VCS_REF=$CI_COMMIT_SHORT_SHA \
        --tag $IMAGE_TAG --tag $LATEST_TAG .
    - docker push $IMAGE_TAG && docker push $LATEST_TAG
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

deploy-staging:
  stage: deploy-staging
  image: bitnami/kubectl:latest
  environment:
    name: staging
    url: https://staging.example.com
    on_stop: stop-staging
  before_script:
    - kubectl config set-cluster k8s --server="$K8S_SERVER"
    - kubectl config set-credentials deployer --token="$K8S_TOKEN_STAGING"
    - kubectl config set-context default --cluster=k8s --user=deployer
    - kubectl config use-context default
  script:
    - kubectl set image deployment/my-app my-app=$IMAGE_TAG --namespace=staging
    - kubectl rollout status deployment/my-app --namespace=staging --timeout=5m
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

stop-staging:
  stage: deploy-staging
  environment:
    name: staging
    action: stop
  script: [echo 'Staging stopped']
  when: manual
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

deploy-production:
  stage: deploy-production
  image: bitnami/kubectl:latest
  environment:
    name: production
    url: https://example.com
  before_script:
    - kubectl config set-cluster k8s --server="$K8S_SERVER"
    - kubectl config set-credentials deployer --token="$K8S_TOKEN_PROD"
    - kubectl config set-context default --cluster=k8s --user=deployer
    - kubectl config use-context default
  script:
    - kubectl set image deployment/my-app my-app=$IMAGE_TAG --namespace=production
    - kubectl rollout status deployment/my-app --namespace=production --timeout=10m
  when: manual
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

---

## 3. Docker Multi-Stage Builds

### Node.js Production Image

```dockerfile
# Dockerfile - Node.js
# Stage 1: install dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production && \
    cp -R node_modules /tmp/prod_modules && \
    npm ci && \
    cp -R node_modules /tmp/dev_modules

# Stage 2: build
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /tmp/dev_modules ./node_modules
COPY . .
RUN npm run build

# Stage 3: production runtime
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production PORT=3000

RUN addgroup --system --gid 1001 nodejs && \
    adduser  --system --uid 1001 nextjs

COPY --from=builder --chown=nextjs:nodejs /app/dist    ./dist
COPY --from=builder --chown=nextjs:nodejs /app/public  ./public
COPY --from=deps    --chown=nextjs:nodejs /tmp/prod_modules ./node_modules
COPY --chown=nextjs:nodejs package.json ./

USER nextjs
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://localhost:3000/health || exit 1

CMD ["node", "dist/server.js"]
```

### Python Production Image (FastAPI)

```dockerfile
# Dockerfile - Python
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

FROM base AS deps
WORKDIR /tmp
RUN pip install uv
COPY requirements.txt ./
RUN uv pip install --system -r requirements.txt

FROM deps AS tester
WORKDIR /app
COPY . .
RUN python -m pytest tests/ -v --tb=short

FROM base AS runner
WORKDIR /app

RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --shell /bin/bash --create-home appuser

COPY --from=deps /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=deps /usr/local/bin             /usr/local/bin
COPY --chown=appuser:appgroup . .

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Go Minimal Scratch Image

```dockerfile
# Dockerfile - Go
FROM golang:1.23-alpine AS builder
WORKDIR /src

RUN apk add --no-cache git ca-certificates tzdata

COPY go.mod go.sum ./
RUN go mod download && go mod verify

COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build \
    -ldflags="-w -s -X main.version=$(git describe --tags --always)" \
FROM scratch AS runner
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /usr/share/zoneinfo                 /usr/share/zoneinfo
COPY --from=builder /app/server                         /server

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s \
  CMD ["/server", "healthcheck"]

ENTRYPOINT ["/server"]
```

---

## 4. Deployment Strategies

### Blue-Green Deployment (Kubernetes)

```bash
# Blue-green switch script (run in a GitHub Actions step)
CURRENT=$(kubectl get service my-app -o jsonpath='{.spec.selector.slot}' --namespace=production)

if [ "$CURRENT" = "blue" ]; then NEW_SLOT="green"; else NEW_SLOT="blue"; fi

# Deploy new image to inactive slot
kubectl set image deployment/my-app-${NEW_SLOT} \
  app=${IMAGE_TAG} --namespace=production

kubectl rollout status deployment/my-app-${NEW_SLOT} \
  --namespace=production --timeout=5m

# Smoke-test before switching live traffic
NEW_HOST=$(kubectl get service my-app-${NEW_SLOT}-internal \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

curl --fail --retry 5 --retry-delay 5 "http://${NEW_HOST}/health"

# Atomically switch traffic to the new slot
kubectl patch service my-app --namespace=production \
  --type=json \
  -p='[{"op":"replace","path":"/spec/selector/slot","value":"'${NEW_SLOT}"}\]'

echo "Traffic switched to ${NEW_SLOT}"
```

### Canary Deployment (Argo Rollouts)

```yaml
# rollout.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-app
  namespace: production
spec:
  replicas: 10
  strategy:
    canary:
      steps:
        - setWeight: 10
        - pause: { duration: 5m }
        - analysis:
            templates:
              - templateName: success-rate
        - setWeight: 30
        - pause: { duration: 5m }
        - setWeight: 60
        - pause: { duration: 5m }
        - setWeight: 100
      canaryService: my-app-canary
      stableService: my-app-stable
      trafficRouting:
        nginx:
          stableIngress: my-app-ingress
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: my-app
          image: ghcr.io/org/my-app:latest
          ports:
            - containerPort: 3000
```

### Rolling Update (Kubernetes Deployment)

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  namespace: production
spec:
  replicas: 6
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2
      maxUnavailable: 1
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: my-app
          image: ghcr.io/org/my-app:latest
          readinessProbe:
            httpGet:
              path: /ready
              port: 3000
            initialDelaySeconds: 10
            periodSeconds: 5
            failureThreshold: 3
          livenessProbe:
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 30
            periodSeconds: 10
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 15"]
      terminationGracePeriodSeconds: 60
```

---

## 5. Secrets Management

### OIDC Keyless Authentication (AWS)

```yaml
# .github/workflows/oidc-deploy.yml
name: Deploy with OIDC

on:
  push:
    branches: [main]

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Configure AWS credentials via OIDC
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{ vars.AWS_ACCOUNT_ID }}:role/GitHubActionsDeployRole
          role-session-name: github-actions-${{ github.run_id }}
          aws-region: ${{ vars.AWS_REGION }}
          # No static access keys -- OIDC token exchanged at runtime
      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster ${{ vars.ECS_CLUSTER }} \
            --service ${{ vars.ECS_SERVICE }} \
            --force-new-deployment
```

### Environment-Scoped Secrets

```yaml
# Three-tier scoping: narrowest environment wins
jobs:
  deploy-dev:
    environment: development
    env:
      API_KEY: ${{ secrets.DEV_API_KEY }}
      DATABASE_URL: ${{ secrets.DEV_DATABASE_URL }}
    steps:
      - run: ./scripts/deploy.sh

  deploy-staging:
    environment: staging
    env:
      API_KEY: ${{ secrets.STAGING_API_KEY }}
      DATABASE_URL: ${{ secrets.STAGING_DATABASE_URL }}
    steps:
      - run: ./scripts/deploy.sh

  deploy-production:
    environment: production
    env:
      API_KEY: ${{ secrets.PROD_API_KEY }}
      DATABASE_URL: ${{ secrets.PROD_DATABASE_URL }}
    steps:
      - run: ./scripts/deploy.sh
```

### HashiCorp Vault Integration

```yaml
- name: Import secrets from Vault
  uses: hashicorp/vault-action@v3
  with:
    url: ${{ secrets.VAULT_ADDR }}
    method: jwt
    role: github-actions
    jwtGithubAudience: sigstore
    secrets: |
      secret/data/myapp/prod api_key    | APP_API_KEY ;
      secret/data/myapp/prod db_url     | DATABASE_URL ;
      secret/data/myapp/prod jwt_secret | JWT_SECRET

- name: Deploy using Vault-sourced secrets
  run: |
    # APP_API_KEY, DATABASE_URL, JWT_SECRET available as env vars
    # Values are masked in logs automatically
    ./scripts/deploy.sh
```

---

## 6. Pipeline Optimization

### Dependency Caching

```yaml
# npm
- name: Cache Node modules
  uses: actions/cache@v4
  with:
    path: |
      ~/.npm
      node_modules
    key: npm-${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}
    restore-keys: npm-${{ runner.os }}-

# pip
- name: Cache pip packages
  uses: actions/cache@v4
  with:
    path: |
      ~/.cache/pip
      .venv
    key: pip-${{ runner.os }}-${{ hashFiles('**/requirements*.txt') }}
    restore-keys: pip-${{ runner.os }}-

# Gradle
- name: Cache Gradle
  uses: actions/cache@v4
  with:
    path: |
      ~/.gradle/caches
      ~/.gradle/wrapper
    key: gradle-${{ runner.os }}-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}

# Docker BuildKit layer cache
- name: Build and push with layer cache
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: ghcr.io/org/app:latest
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

### Parallel Jobs with Fan-Out / Fan-In

```yaml
jobs:
  # Fan-out: all three test suites run simultaneously
  test-unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm run test:unit

  test-integration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm run test:integration

  test-e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm run test:e2e

  # Fan-in: deploy only after all test jobs pass
  deploy:
    needs: [test-unit, test-integration, test-e2e]
    runs-on: ubuntu-latest
    steps:
      - run: echo "All tests passed - deploying"
```

### Conditional Steps and Path Filtering

```yaml
on:
  push:
    paths:
      - 'src/**'
      - 'tests/**'
      - 'Dockerfile'
    paths-ignore:
      - 'docs/**'
      - '**.md'

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      backend:  ${{ steps.filter.outputs.backend }}
      frontend: ${{ steps.filter.outputs.frontend }}
      infra:    ${{ steps.filter.outputs.infra }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            backend:
              - 'backend/**'
              - 'Dockerfile'
            frontend:
              - 'frontend/**'
            infra:
              - 'terraform/**'
              - 'k8s/**'

  build-backend:
    needs: detect-changes
    if: needs.detect-changes.outputs.backend == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: echo "Building backend"

  build-frontend:
    needs: detect-changes
    if: needs.detect-changes.outputs.frontend == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: echo "Building frontend"

  apply-infra:
    needs: detect-changes
    if: needs.detect-changes.outputs.infra == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: echo "Applying infra changes"
```

---

## 7. Release Automation

### Semantic Release Workflow

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    branches: [main]

permissions:
  contents: write
  issues: write
  pull-requests: write
  packages: write

jobs:
  release:
    name: Semantic Release
    runs-on: ubuntu-latest
    outputs:
      published: ${{ steps.release.outputs.new_release_published }}
      version:   ${{ steps.release.outputs.new_release_version }}
      git-tag:   ${{ steps.release.outputs.new_release_git_tag }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          persist-credentials: false
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - name: Install semantic-release
        run: |
          npm install -g \
            semantic-release \
            @semantic-release/changelog \
            @semantic-release/git \
            @semantic-release/github \
            conventional-changelog-conventionalcommits
      - name: Run semantic-release
        id: release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
        run: semantic-release

  publish-image:
    name: Publish Release Image
    needs: release
    if: needs.release.outputs.published == 'true'
    runs-on: ubuntu-latest
    permissions:
      packages: write
      contents: read
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ needs.release.outputs.git-tag }}
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:${{ needs.release.outputs.version }}
            ghcr.io/${{ github.repository }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### .releaserc.json

```json
{
  "branches": ["main", {"name": "beta", "prerelease": true}],
  "plugins": [
    ["@semantic-release/commit-analyzer", {
      "preset": "conventionalcommits",
      "releaseRules": [
        {"type": "feat",   "release": "minor"},
        {"type": "fix",    "release": "patch"},
        {"type": "perf",   "release": "patch"},
        {"breaking": true, "release": "major"}
      ]
    }],
    ["@semantic-release/release-notes-generator", {
      "preset": "conventionalcommits"
    }],
    ["@semantic-release/changelog", {"changelogFile": "CHANGELOG.md"}],
    ["@semantic-release/npm", {"npmPublish": true}],
    ["@semantic-release/git", {
      "assets": ["CHANGELOG.md", "package.json"],
      "message": "chore(release): ${nextRelease.version} [skip ci]"
    }],
    "@semantic-release/github"
  ]
}
```

---

## 8. Environment-Specific Deployments

### Promotion Pipeline (Dev to Staging to Prod)

```yaml
# .github/workflows/promote.yml
name: Promote

on:
  workflow_dispatch:
    inputs:
      source-env:
        description: Source environment
        required: true
        type: choice
        options: [development, staging]
      target-env:
        description: Target environment
        required: true
        type: choice
        options: [staging, production]
      image-tag:
        description: Verified image tag to promote
        required: true
        type: string

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Enforce promotion order
        run: |
          SRC="${{ inputs.source-env }}"
          TGT="${{ inputs.target-env }}"
          if [ "$SRC" = "development" ] && [ "$TGT" \!= "staging" ]; then
            echo "Error: development can only promote to staging" && exit 1
          fi
          if [ "$SRC" = "staging" ] && [ "$TGT" \!= "production" ]; then
            echo "Error: staging can only promote to production" && exit 1
          fi
          echo "Promotion path valid: $SRC -> $TGT"

  promote:
    needs: validate
    runs-on: ubuntu-latest
    environment: ${{ inputs.target-env }}
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}
      - name: Retag and push promoted image
        run: |
          REPO="${{ vars.ECR_REGISTRY }}/${{ vars.APP_NAME }}"
          TAG="${{ inputs.target-env }}-latest"
          aws ecr get-login-password | docker login --username AWS --password-stdin ${{ vars.ECR_REGISTRY }}
          docker pull  "$REPO:${{ inputs.image-tag }}"
          docker tag   "$REPO:${{ inputs.image-tag }}" "$REPO:$TAG"
          docker push  "$REPO:$TAG"
      - name: Update running service
        run: |
          aws ecs update-service \
            --cluster ${{ vars.ECS_CLUSTER }} \
            --service ${{ vars.ECS_SERVICE }} \
            --force-new-deployment
```

---

## 9. Security Scanning in Pipelines

### Comprehensive Security Scan Workflow

```yaml
# .github/workflows/security.yml
name: Security Scans

on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '0 6 * * 1'

jobs:
  sast:
    name: SAST with CodeQL
    runs-on: ubuntu-latest
    permissions:
      actions: read
      contents: read
      security-events: write
    strategy:
      matrix:
        language: [javascript, python]
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: ${{ matrix.language }}
          queries: security-and-quality
      - uses: github/codeql-action/autobuild@v3
      - uses: github/codeql-action/analyze@v3
        with:
          category: /language:${{ matrix.language }}

  dependency-audit:
    name: Dependency Vulnerability Audit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm audit --audit-level=high
      - name: Trivy filesystem scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: fs
          scan-ref: .
          format: sarif
          output: trivy-fs.sarif
          severity: HIGH,CRITICAL
          exit-code: 1
      - uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: trivy-fs.sarif

  container-scan:
    name: Container Image Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build image for scanning
        uses: docker/build-push-action@v5
        with:
          context: .
          push: false
          load: true
          tags: scan-target:${{ github.sha }}
      - name: Trivy image scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: scan-target:${{ github.sha }}
          format: sarif
          output: trivy-image.sarif
          severity: HIGH,CRITICAL
          exit-code: 1
          ignore-unfixed: true
      - uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: trivy-image.sarif

  secret-detection:
    name: Secret Detection
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Detect secrets with Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  sbom:
    name: Generate SBOM
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - uses: anchore/sbom-action@v0
        with:
          image: ghcr.io/${{ github.repository }}:latest
          artifact-name: sbom.spdx.json
          output-file: sbom.spdx.json
          format: spdx-json
```

---

## 10. Notifications

### Slack Notifications (GitHub Actions)

```yaml
      - name: Notify Slack on failure
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          channel-id: ${{ vars.SLACK_CHANNEL_ALERTS }}
          payload: |
            {
              "text": "Pipeline failed",
              "attachments": [{
                "color": "#FF0000",
                "fields": [
                  {"title": "Repository", "value": "${{ github.repository }}", "short": true},
                  {"title": "Branch",     "value": "${{ github.ref_name }}",   "short": true},
                  {"title": "Commit",     "value": "${{ github.sha }}",        "short": true},
                  {"title": "Author",     "value": "${{ github.actor }}",      "short": true},
                  {"title": "Run URL",
                   "value": "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}",
                   "short": false}
                ]
              }]
            }
        env:
          SLACK_BOT_TOKEN: ${{ secrets.SLACK_BOT_TOKEN }}

      - name: Notify Slack on deploy success
        if: success()
        uses: slackapi/slack-github-action@v1
        with:
          channel-id: ${{ vars.SLACK_CHANNEL_DEPLOYS }}
          payload: |
            {
              "text": "Deployment successful",
              "attachments": [{
                "color": "#36A64F",
                "fields": [
                  {"title": "Repository",  "value": "${{ github.repository }}", "short": true},
                  {"title": "Environment", "value": "production",               "short": true},
                  {"title": "Version",     "value": "${{ github.ref_name }}",   "short": true},
                  {"title": "Deployed by", "value": "${{ github.actor }}",      "short": true}
                ]
              }]
            }
        env:
          SLACK_BOT_TOKEN: ${{ secrets.SLACK_BOT_TOKEN }}
```

### Email Notification via SendGrid

```yaml
  notify-email:
    if: failure()
    needs: [deploy]
    runs-on: ubuntu-latest
    steps:
      - name: Send failure email
        uses: dawidd6/action-send-mail@v3
        with:
          server_address: smtp.sendgrid.net
          server_port: 587
          username: apikey
          password: ${{ secrets.SENDGRID_API_KEY }}
          subject: "Pipeline Failed: ${{ github.repository }} (${{ github.ref_name }})"
          to: ${{ vars.ONCALL_EMAIL }}
          from: ci-bot@example.com
          body: |
            The CI/CD pipeline failed for ${{ github.repository }}.

            Branch:  ${{ github.ref_name }}
            Commit:  ${{ github.sha }}
            Author:  ${{ github.actor }}
            Run URL: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}

            Please investigate and resolve.
```

### GitLab CI Slack Notifications

```yaml
# .gitlab-ci.yml reusable YAML anchor
.notify-slack: &notify-slack
  image: curlimages/curl:latest
  script:
    - |
      STATUS="${NOTIFICATION_STATUS:-unknown}"
      COLOR=$([ "$STATUS" = "success" ] && echo "good" || echo "danger")
      curl -s -X POST "$SLACK_WEBHOOK_URL" \
        -H 'Content-type: application/json' \
        --data "{...attachment payload...}"

notify-success:
  <<: *notify-slack
  stage: .post
  variables:
    NOTIFICATION_STATUS: success
  when: on_success
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

notify-failure:
  <<: *notify-slack
  stage: .post
  variables:
    NOTIFICATION_STATUS: failure
  when: on_failure
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

---

## Quick Reference

| Pattern | Use Case | Key Point |
|---|---|---|
| ```needs:``` | Job dependency chain | Fan-in / fan-out |
| ```environment:``` | Deployment gates | Approval and secrets scoping |
| ```concurrency:``` | Cancel stale runs | Cost and conflict avoidance |
| ```cache:``` | Speed up installs | Hash key on lockfile |
| ```matrix:``` | Cross-platform tests | Permutation builds |
| ```workflow_call:``` | Reusable workflows | DRY across repositories |
| ```paths-ignore:``` | Skip docs-only PRs | Efficient triggers |
| ```if: failure()``` | Alerting | Never miss a breakage |
| OIDC ```id-token: write``` | Keyless cloud auth | No long-lived credentials |
| ```artifacts:``` (GitLab) | Pass data between jobs | Build once, deploy many |

## Secrets Management Rules

1. Never hardcode credentials -- always reference ```${{ secrets.NAME }}``` or ```$VARIABLE```.
2. Scope secrets to the narrowest environment (environment-level over repository-level for production).
3. Prefer OIDC / workload identity over long-lived cloud access keys.
4. Rotate secrets on a schedule using a dedicated automation workflow.
5. Use ```vars``` for non-sensitive configuration and ```secrets``` for sensitive values to improve auditability.
6. Enable secret scanning alerts on all repositories and enforce Gitleaks in CI and pre-commit hooks.