<h1 align="center">Awesome Claude Skills</h1>

<p align="center">
<a href="https://platform.composio.dev/?utm_source=Github&utm_medium=Youtube&utm_campaign=2025-11&utm_content=AwesomeSkills">
  <img width="1280" height="640" alt="Composio banner" src="https://github.com/user-attachments/assets/adb3f57a-2706-4329-856f-059a32059d48">
</a>


</p>

<p align="center">
  <a href="https://awesome.re">
    <img src="https://awesome.re/badge.svg" alt="Awesome" />
  </a>
  <a href="https://makeapullrequest.com">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square" alt="PRs Welcome" />
  </a>
  <a href="https://www.apache.org/licenses/LICENSE-2.0">
    <img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg?style=flat-square" alt="License: Apache-2.0" />
  </a>
</p>
<div>
<p align="center">
  <a href="https://twitter.com/composio">
    <img src="https://img.shields.io/badge/Follow on X-000000?style=for-the-badge&logo=x&logoColor=white" alt="Follow on X" />
  </a>
  <a href="https://www.linkedin.com/company/composiohq/">
    <img src="https://img.shields.io/badge/Follow on LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="Follow on LinkedIn" />
  </a>
  <a href="https://discord.com/invite/composio">
    <img src="https://img.shields.io/badge/Join our Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Join our Discord" />
  </a>
  </p>
</div>

A curated list of practical Claude Skills for enhancing productivity across Claude.ai, Claude Code, and the Claude API.


> If you want your skills to take actions across 500+ apps, wire them up with [Composio](https://platform.composio.dev/?utm_source=Github&utm_medium=Youtube&utm_campaign=2025-11&utm_content=AwesomeSkills)


## Contents

- [What Are Claude Skills?](#what-are-claude-skills)
- [Skills](#skills)
  - [Document Processing](#document-processing)
  - [Development & Code Tools](#development--code-tools)
  - [Data & Analysis](#data--analysis)
  - [Business & Marketing](#business--marketing)
  - [Communication & Writing](#communication--writing)
  - [Creative & Media](#creative--media)
  - [Productivity & Organization](#productivity--organization)
  - [Collaboration & Project Management](#collaboration--project-management)
  - [Security & Systems](#security--systems)
- [Getting Started](#getting-started)
- [Creating Skills](#creating-skills)
- [Contributing](#contributing)
- [Resources](#resources)
- [License](#license)

## What Are Claude Skills?

Claude Skills are customizable workflows that teach Claude how to perform specific tasks according to your unique requirements. Skills enable Claude to execute tasks in a repeatable, standardized manner across all Claude platforms.

## Skills

### Document Processing

- [docx](https://github.com/anthropics/skills/tree/main/skills/docx) - Create, edit, analyze Word docs with tracked changes, comments, formatting.
- [pdf](https://github.com/anthropics/skills/tree/main/skills/pdf) - Extract text, tables, metadata, merge & annotate PDFs.
- [pptx](https://github.com/anthropics/skills/tree/main/skills/pptx) - Read, generate, and adjust slides, layouts, templates.
- [xlsx](https://github.com/anthropics/skills/tree/main/skills/xlsx) - Spreadsheet manipulation: formulas, charts, data transformations.
- [Markdown to EPUB Converter](https://github.com/smerchek/claude-epub-skill) - Converts markdown documents and chat summaries into professional EPUB ebook files. *By [@smerchek](https://github.com/smerchek)*

### Development & Code Tools

- [Accessibility Testing](./accessibility-testing/) - Accessibility testing automation with axe-core, Playwright audits, keyboard navigation testing, ARIA validation, and a11y CI pipelines.
- [Accessibility & WCAG Compliance](./accessibility-wcag/) - Web accessibility and WCAG compliance covering semantic HTML, ARIA attributes, keyboard navigation, color contrast, accessible forms, and testing with axe-core and Lighthouse.
- [Algorithmic Art](./algorithmic-art/) - Creates algorithmic art and generative designs using computational creativity techniques.
- [Android Kotlin Development](./android-kotlin/) - Android development with Jetpack Compose, ViewModel, Room, Retrofit, Hilt DI, Navigation Compose, and Material 3.
- [Angular Development](./angular-development/) - Angular 18+ development with signals, standalone components, new control flow syntax, defer blocks, SSR, NgRx signal store, and reactive forms.
- [Ansible Automation](./ansible-automation/) - Ansible automation covering playbooks, roles, inventory management, Vault secrets, Galaxy collections, and CI/CD integration.
- [AI-Assisted Development](./github-copilot-patterns/) - AI coding assistant patterns with effective prompting, context management, code review, test generation, and team guidelines.
- [API Design Best Practices](./api-design/) - REST API design covering resource naming, HTTP status codes, pagination, filtering, versioning, error formats, and OpenAPI specs.
- [API Gateway](./api-gateway/) - API gateway patterns with request routing, rate limiting, auth middleware, BFF pattern, and AWS/Kong configuration.
- [API Documentation Generator](./api-documentation-generator/) - Generate OpenAPI/Swagger specs, create interactive API documentation, and implement API documentation best practices.
- [AI SDK (Vercel)](./ai-sdk-vercel/) - Vercel AI SDK with streaming chat, tool calling, structured output, multi-provider support, RAG, and useChat hooks.
- [API Mocking](./api-mocking/) - API mocking with MSW, Nock, JSON Server, test data factories with Faker, and contract testing with Pact.
- [Autonomous Task Execution](./autonomous-task-execution/) - Autonomous task execution patterns for AI assistants covering goal decomposition, self-directed research, proactive tool usage, and error recovery.
- [Artifacts Builder](./artifacts-builder/) - Suite of tools for creating elaborate, multi-component Claude.ai HTML artifacts using modern frontend web technologies (React, Tailwind CSS, shadcn/ui).
- [Auth Patterns](./auth-patterns/) - Authentication and authorization patterns covering JWT, OAuth 2.0, session management, RBAC, passwordless auth, MFA, and security best practices.
- [Auth0 Integration](./auth0-integration/) - Auth0 with Universal Login, social connections, RBAC, organizations, M2M tokens, Next.js SDK, and Express middleware.
- [AWS CDK](./aws-cdk/) - AWS CDK infrastructure as code covering constructs, stacks, Lambda, API Gateway, DynamoDB, S3, CloudFront, testing, and CI/CD pipelines.
- [AWS Lambda](./aws-lambda/) - Serverless functions with API Gateway, S3/SQS/DynamoDB event sources, SAM/CDK deployment, and cold start optimization.
- [aws-skills](https://github.com/zxkane/aws-skills) - AWS development with CDK best practices, cost optimization MCP servers, and serverless/event-driven architecture patterns.
- [Astro Framework](./astro-framework/) - Astro with content collections, island architecture, partial hydration, View Transitions, and MDX integration.
- [AWS S3 & CloudFront](./aws-s3-cloudfront/) - S3 file operations, presigned URLs, multipart uploads, CloudFront CDN, cache invalidation, and CDK infrastructure.
- [AWS Serverless](./aws-serverless/) - AWS serverless development with Lambda, API Gateway, DynamoDB, Step Functions, EventBridge, CDK/SAM, and production-ready patterns.
- [Browser Extensions](./browser-extensions/) - Browser extension development with Manifest V3, content scripts, service workers, popup UI, and cross-browser patterns.
- [Biome Linting](./biome-linting/) - Biome toolchain covering linting, formatting, import sorting, migration from ESLint/Prettier, and CI integration.
- [Bun Runtime](./bun-runtime/) - Bun runtime with Bun.serve, built-in SQLite, bun:test, bundling, fast package management, and Node.js compatibility.
- [Changelog Generator](./changelog-generator/) - Automatically creates user-facing changelogs from git commits by analyzing history and transforming technical commits into customer-friendly release notes.
- [CLI Development](./cli-development/) - CLI application development with Commander.js, Click, Cobra, interactive prompts, colored output, and distribution patterns.
- [Callstack React Native Performance](https://github.com/callstackincubator/agent-skills) - React Native performance optimization skills from Callstack covering JS/React, Native, and bundling optimizations. *By [@callstackincubator](https://github.com/callstackincubator)*
- [Chaos Engineering](./chaos-engineering/) - Chaos engineering and resilience testing with LitmusChaos, Toxiproxy, circuit breakers, fault injection, and gameday planning.
- [Cloudflare Workers](./cloudflare-workers/) - Cloudflare Workers edge computing with Hono, D1, R2, KV, Durable Objects, Cron Triggers, and Wrangler deployment.
- [CI/CD Pipelines](./cicd-pipelines/) - CI/CD pipeline configuration covering GitHub Actions, GitLab CI, Docker multi-stage builds, deployment strategies, secrets management, and production deployment automation.
- [Claude API](./claude-api/) - Anthropic Claude API integration covering messages API, streaming, tool use, vision, prompt caching, extended thinking, and SDK patterns.
- [Clerk Authentication](./clerk-authentication/) - Clerk auth with sign-in components, organizations, RBAC, webhook sync, and Next.js App Router integration.
- [Concurrency Patterns](./concurrency-patterns/) - Concurrency with Promise.all, Web Workers, async iterators, semaphores, Go goroutines, and Python asyncio.
- [Context Management](./context-management/) - Context management patterns for Claude Code sessions covering codebase navigation, progressive exploration, dependency tracing, and avoiding context drift.
- [CSS Grid & Flexbox](./css-grid-flexbox/) - CSS Grid and Flexbox with auto-fill, subgrid, container queries, responsive patterns, and layout decision guide.
- [CSS Architecture](./css-architecture/) - CSS architecture with CSS Modules, custom properties, cascade layers, nesting, :has() selector, and scalable patterns.
- [Deno Development](./deno-development/) - Deno runtime with permissions, HTTP servers, built-in TypeScript, npm compatibility, Fresh framework, Deploy, and KV store.
- [Dependency Injection](./dependency-injection/) - DI patterns with tsyringe, InversifyJS, Python dependency-injector, constructor injection, and testing strategies.
- [Design System & Components](./design-system/) - Design system patterns with design tokens, CVA variants, accessible components, Storybook docs, and theming.
- [Developer Growth Analysis](./developer-growth-analysis/) - Analyzes Claude Code chat history to identify coding patterns, development gaps, curates HackerNews resources, and sends personalized growth reports to Slack.
- [Django Development](./django-development/) - Django web development with models, DRF, authentication, Celery background tasks, query optimization, and production deployment patterns.
- [DNS & Networking](./dns-networking/) - DNS records, domain configuration, Cloudflare/Route 53, SSL/TLS, CDN setup, and network troubleshooting.
- [Discord Bot](./discord-bot/) - Discord bot development with Discord.js v14 covering slash commands, event handling, embeds, buttons, select menus, modals, and permissions.
- [Docker Compose Orchestration](./docker-compose-orchestration/) - Multi-container Docker orchestration with service dependencies, development environments, production deployments, and complete stack configurations.
- [Docker & Kubernetes Production](./docker-kubernetes/) - Docker multi-stage builds, Docker Compose, Kubernetes Deployments, Helm charts, autoscaling, and CI/CD pipelines.
- [Docker Development](./docker-development/) - Dockerfile best practices, multi-stage builds, layer caching, health checks, security hardening, and debugging containers.
- [Drizzle ORM Advanced](./drizzle-studio/) - Drizzle ORM with relational queries, prepared statements, migrations, Drizzle Studio, and framework integration.
- [Drizzle ORM](./drizzle-orm/) - Drizzle ORM for TypeScript with schema definition, migrations, type-safe queries, joins, transactions, and multi-database support.
- [DynamoDB Operations](./dynamodb-operations/) - Amazon DynamoDB operations with single-table design, SDK v3 CRUD, GSIs, batch operations, transactions, and streams.
- [Event Sourcing & CQRS](./event-sourcing/) - Event sourcing with event stores, aggregate roots, command handlers, projections, and saga orchestration.
- [Elasticsearch](./elasticsearch/) - Elasticsearch integration covering index management, full-text search, aggregations, mappings, bulk operations, and query DSL.
- [Electron Desktop Apps](./electron-desktop/) - Electron with main/renderer processes, IPC, auto-updates, native menus, system tray, and cross-platform packaging.
- [Express.js](./express-js/) - Express.js with routing, middleware, Zod validation, JWT auth, error handling patterns, graceful shutdown, and supertest testing.
- [ESLint & Biome](./eslint-biome/) - Code linting and formatting with ESLint flat config, Biome, Prettier, lint-staged, and CI enforcement.
- [Error Handling Patterns](./error-handling/) - Error handling strategies with custom errors, Result types, retry logic, circuit breakers, and error boundaries across TypeScript, Python, and Go.
- [Email Sending](./email-sending/) - Transactional email with Resend, SendGrid, SES, queue management, SPF/DKIM/DMARC, and deliverability.
- [Email Templates](./email-templates/) - Email template development with React Email, MJML, responsive HTML, dark mode, deliverability, and Resend/SendGrid.
- [Environment Config & Secrets](./environment-config/) - Environment configuration with Zod/Pydantic validation, 12-factor patterns, feature flags, and secrets managers.
- [Elasticsearch & Search](./elasticsearch-search/) - Elasticsearch and search engine patterns covering index management, full-text search, aggregations, autocomplete, fuzzy matching, and production search architecture.
- [Claude Code Terminal Title](https://github.com/bluzername/claude-code-terminal-title) - Gives each Claud-Code terminal window a dynamic title that describes the work being done so you don't lose track of what window is doing what.
- [Caching Strategies](./caching-strategies/) - Caching with HTTP headers, CDN, Redis, React Query/SWR, invalidation patterns, and stampede prevention.
- [Capacitor Mobile](./capacitor-mobile/) - Capacitor cross-platform mobile development with native plugins, deep linking, push notifications, and app store deployment.
- [Contentful CMS](./contentful-cms/) - Contentful CMS integration covering content modeling, Delivery and Management APIs, rich text rendering, image optimization, and Next.js integration.
- [Coolify Self-Hosted](./coolify-selfhost/) - Coolify self-hosted PaaS covering server setup, GitHub deployment, database provisioning, custom domains, and Docker Compose.
- [Convex Backend](./convex-backend/) - Convex BaaS with reactive queries, mutations, actions, real-time data, scheduled functions, and Clerk auth.
- [Cron Jobs & Scheduling](./cron-jobs/) - Task scheduling with node-cron, BullMQ repeatable jobs, pg-boss, distributed locking, and serverless cron triggers.
- [Cypress Testing](./cypress-testing/) - Cypress E2E testing with custom commands, API interception, authentication flows, CI configuration, and retry strategies.
- [Cron & Job Scheduling](./cron-scheduling/) - Job scheduling with cron expressions, BullMQ, Celery, distributed queues, idempotent jobs, and production patterns.
- [Code Refactoring](./code-refactoring/) - Code refactoring and technical debt management covering code smell detection, safe refactoring techniques, architecture improvement, and legacy code strategies.
- [Data Engineering & ETL](./data-engineering/) - Data engineering and ETL pipeline patterns with Kafka, dbt, Airflow, data validation, and modern Python data stack.
- [Data Visualization](./data-visualization/) - Data visualization with Chart.js, Recharts, D3.js, dashboard layouts, responsive charts, and real-time data updates.
- [Database Migrations](./database-migrations/) - Database migration strategies covering zero-downtime migrations, rollback patterns, and ORM-specific workflows with Prisma, Drizzle, Knex, and Alembic.
- [Database Seeding](./database-seeding/) - Database seed scripts with Prisma, Drizzle, SQLAlchemy, factory patterns, Faker, and deterministic test data.
- [Date Handling](./date-handling/) - Date and time handling with date-fns, dayjs, Temporal API, Luxon timezone management, duration calculations, relative time, and Intl.DateTimeFormat internationalization.
- [D3.js Visualization](https://github.com/chrisvoncsefalvay/claude-d3js-skill) - Teaches Claude to produce D3 charts and interactive data visualizations. *By [@chrisvoncsefalvay](https://github.com/chrisvoncsefalvay)*
- [Feature Flags](./feature-flags/) - Feature flags with LaunchDarkly, percentage rollouts, A/B testing, user targeting, and flag lifecycle management.
- [Firebase Development](./firebase-development/) - Firebase with Firestore, Authentication, Cloud Storage, Cloud Functions, security rules, and Admin SDK.
- [Figma to Code](./figma-to-code/) - Figma-to-code translation with design tokens, auto-layout to flexbox/grid, variant-to-prop mapping, and responsive conversion.
- [File Upload](./file-upload/) - File uploads with Multer, presigned S3 URLs, chunked uploads, validation, image processing, and drag-and-drop UI.
- [Framer Motion](./framer-motion/) - Framer Motion animations with variants, gestures, layout animations, scroll effects, AnimatePresence, and spring physics.
- [Form Validation](./form-validation/) - Form validation with Zod, React Hook Form, server-side validation, accessible errors, and multi-step wizards.
- [FFUF Web Fuzzing](https://github.com/jthack/ffuf_claude_skill) - Integrates the ffuf web fuzzer so Claude can run fuzzing tasks and analyze results for vulnerabilities. *By [@jthack](https://github.com/jthack)*
- [finishing-a-development-branch](https://github.com/obra/superpowers/tree/main/skills/finishing-a-development-branch) - Guides completion of development work by presenting clear options and handling chosen workflow.
- [FastAPI Development](./fastapi-development/) - FastAPI development with async/await, Pydantic v2, dependency injection, SQLAlchemy async, JWT auth, WebSockets, and testing with httpx/pytest.
- [Feishu Automation](./feishu-automation/) - Automate Feishu workflows with bulk document operations, scheduled reports, document templates, data synchronization between bases, and smart notifications.
- [Flask Development](./flask-development/) - Flask web development covering blueprints, SQLAlchemy models, Flask-Login authentication, REST APIs, Celery tasks, and pytest testing.
- [Fly.io Deployment](./fly-io-deployment/) - Fly.io deployment covering multi-region deployment, Postgres clusters, Redis, volumes, autoscaling, and CI/CD with GitHub Actions.
- [Flutter Development](./flutter-development/) - Flutter mobile and web development covering Dart fundamentals, widgets, state management (Riverpod/Bloc), navigation (GoRouter), animations, testing, and production deployment to iOS and Android.
- [Feishu Direct API](./feishu-direct-api/) - Search, read, modify, and manage Feishu documents, bases, wikis, and chats using direct API calls without requiring MCP server setup.
- [Feishu MCP](./feishu-mcp/) - Comprehensive Feishu (Lark) integration with document search, Feishu Docs/Bases modification, wiki access, messaging, and data correction capabilities.
- [gRPC APIs](./grpc-apis/) - gRPC API development with Connect protocol, streaming RPCs, interceptors, error handling, and gRPC-Web browser support.
- [gRPC & Protocol Buffers](./grpc-protobuf/) - gRPC and Protocol Buffers with proto3 schemas, code generation, streaming RPCs, interceptors, and Node.js/Go/Python patterns.
- [GitHub Actions](./github-actions/) - GitHub Actions CI/CD covering workflow syntax, reusable workflows, composite actions, matrix strategies, caching, and deployments.
- [GitHub API Integration](./github-api/) - GitHub API with Octokit, REST/GraphQL, PR automation, webhooks, GitHub Apps, and release management.
- [Go Development](./golang-development/) - Go development with error handling, goroutines, channels, HTTP servers, generics, interfaces, testing, and production-ready patterns.
- [Git Hooks & Automation](./git-hooks-automation/) - Git hooks with Husky, lint-staged, conventional commits, semantic release, changesets, and developer experience tooling.
- [Git Workflows](./git-workflows/) - Git branching strategies (GitFlow, trunk-based), merge vs rebase, conflict resolution, cherry-pick, bisect, worktrees, hooks, and monorepo management.
- [GitHub Actions Advanced](./github-actions-advanced/) - Advanced GitHub Actions with reusable workflows, composite actions, matrix strategies, OIDC, and caching optimization.
- [GitHub Actions CI/CD](./github-actions-cicd/) - GitHub Actions with reusable workflows, composite actions, OIDC, environment gates, and monorepo change detection.
- [GitHub Copilot Setup](./github-copilot-setup/) - GitHub Copilot configuration with custom instructions, Copilot Chat, context variables, and team productivity patterns.
- [GitHub Actions Generator](./github-actions-generator/) - Generates production-ready GitHub Actions workflows for CI/CD, testing, deployment, and automation following best practices.
- [GraphQL Code Generator](./graphql-codegen/) - GraphQL Code Generator covering TypeScript type generation, typed document nodes, React Query and Apollo hooks, and fragment colocation.
- [GraphQL Development](./graphql-development/) - GraphQL API development with schema design, Apollo Server/Client, subscriptions, type safety, authentication, and real-time capabilities.
- [GraphQL Subscriptions](./graphql-subscriptions/) - Real-time GraphQL subscriptions with WebSocket transport, pub/sub patterns, Redis scaling, filtering, and authentication.
- [Hono Framework](./hono-framework/) - Hono web framework with routing, middleware, Zod OpenAPI, multi-runtime (Cloudflare, Bun, Node.js, Deno), and RPC client.
- [HTMX & Hypermedia](./htmx-hypermedia/) - HTMX with server-rendered HTML, partial updates, infinite scroll, active search, and progressive enhancement.
- [Image Optimization](./image-optimization/) - Image optimization with Next.js Image, sharp, responsive srcset, WebP/AVIF, lazy loading, and LCP improvement.
- [i18n & Localization](./i18n-localization/) - Internationalization with react-intl, next-intl, i18next, ICU message format, Intl API, RTL layout, and translation workflows.
- [Jest Testing](./jest-testing/) - Write and configure JavaScript/TypeScript tests using Jest or Vitest with unit tests, integration tests, mocking, and coverage.
- [Incident Response & SRE](./incident-response/) - Incident response and SRE patterns covering classification, triage, runbooks, postmortems, SLOs, error budgets, and production reliability.
- [iOS Simulator](https://github.com/conorluddy/ios-simulator-skill) - Enables Claude to interact with iOS Simulator for testing and debugging iOS applications. *By [@conorluddy](https://github.com/conorluddy)*
- [Kafka Streaming](./kafka-streaming/) - Apache Kafka event streaming covering producers, consumers, consumer groups, topics, partitions, and exactly-once semantics.
- [Kubernetes Manifests](./kubernetes-manifests/) - Kubernetes manifest creation and management including deployments, services, ingress, StatefulSets, auto-scaling, and production-ready orchestration.
- [Laravel Development](./laravel-development/) - Laravel PHP development covering Eloquent ORM, Sanctum authentication, queues, event broadcasting, and testing with Pest.
- [Linux Commands Reference](./linux-commands/) - Essential Linux/Unix commands for file operations, text processing, networking, systemd, SSH, and shell scripting.
- [Load Testing](./load-testing/) - Load testing with k6, Autocannon, stress/spike tests, threshold-based pass/fail, and CI integration.
- [Logging & Structured Logging](./logging-structured/) - Structured JSON logging with Pino/Winston, correlation IDs, request tracing, and production logging patterns.
- [Lucia Authentication](./lucia-auth/) - Lucia session auth with Prisma/Drizzle adapters, OAuth via Arctic, password hashing, and email verification.
- [LLM Integration](./llm-integration/) - LLM and AI integration patterns covering Claude API, OpenAI API, structured outputs, function calling, RAG pipelines, embeddings, vector search, and production AI application patterns.
- [MCP Builder](./mcp-builder/) - Guides creation of high-quality MCP (Model Context Protocol) servers for integrating external APIs and services with LLMs using Python or TypeScript.
- [Message Queues & Events](./message-queues/) - Message queue and event-driven patterns with RabbitMQ, BullMQ, SQS, Kafka, dead letter queues, and idempotency.
- [Markdown & Documentation](./markdown-documentation/) - Technical docs with README templates, JSDoc/TSDoc, Docusaurus, VitePress, ADRs, and changelog conventions.
- [Microservices Architecture](./microservices-architecture/) - Microservices patterns with API gateways, service mesh, event-driven architecture, Saga pattern, circuit breakers, and distributed systems.
- [MongoDB](./mongodb/) - MongoDB with Mongoose schemas, aggregation pipeline, transactions, change streams, population, and connection management.
- [MongoDB Operations](./mongodb-operations/) - MongoDB database operations including schema design, query optimization, aggregation pipelines, indexing strategies, and best practices.
- [Migration Patterns](./migration-patterns/) - Framework migration (CRA to Vite/Next.js), API versioning, gradual TypeScript adoption, and zero-downtime strategies.
- [Material UI](./material-ui/) - MUI component library with theme customization, sx prop, DataGrid, form components, dark mode, and responsive design.
- [Monorepo Management](./monorepo-management/) - Monorepo management with Turborepo, Nx, and pnpm workspaces covering task pipelines, remote caching, and shared configurations.
- [Multi-Tenant SaaS](./multi-tenant-saas/) - Multi-tenant architecture with row-level security, subdomain routing, tenant-scoped queries, Stripe billing, and isolation strategies.
- [Monitoring & Observability](./monitoring-observability/) - Monitoring, logging, metrics, distributed tracing, alerting, and observability best practices for production applications.
- [MySQL Operations](./mysql-operations/) - MySQL/MariaDB database operations including schema design, SQL queries, optimization, indexing, transactions, and best practices.
- [Nuxt Development](./nuxt-development/) - Nuxt 3 with auto-imports, server routes, composables, useFetch, Nitro, Pinia, and multi-platform deployment.
- [Neon Database](./neon-database/) - Neon serverless Postgres covering branching, connection pooling, edge access, Drizzle ORM integration, and preview deployment workflows.
- [NestJS Framework](./nestjs-framework/) - NestJS with module architecture, dependency injection, guards, interceptors, pipes, TypeORM, Swagger, and testing.
- [Netlify Deployment](./netlify-deployment/) - Netlify deployment covering build configuration, serverless functions, edge functions, environment variables, redirects, forms, and CI/CD.
- [Notion API](./notion-api/) - Notion API integration covering database queries, page creation, block manipulation, property types, pagination, and OAuth authentication.
- [Nginx Configuration](./nginx-configuration/) - Nginx reverse proxy, SSL/TLS, load balancing, caching, security headers, WebSocket proxying, and Docker deployment.
- [NextAuth.js Authentication](./nextauth-authentication/) - Auth.js v5 authentication with OAuth providers, credentials, JWT sessions, RBAC, middleware protection, and Prisma adapter.
- [Next.js Development](./nextjs-development/) - Next.js development covering App Router, Server/Client Components, SSR/SSG/ISR, API routes, middleware, authentication, and production deployment.
- [OAuth & Authentication](./oauth-authentication/) - OAuth 2.0, JWT management, Auth.js/NextAuth, PKCE flow, social login, refresh token rotation, and RBAC patterns.
- [OpenAPI Specification](./openapi-spec/) - OpenAPI 3.1 authoring, schema design, code generation with openapi-typescript, Zod validation, and API-first development.
- [OpenAI API](./openai-api/) - OpenAI API integration covering chat completions, function calling, structured outputs, streaming, embeddings, and image generation.
- [OpenTelemetry](./opentelemetry/) - OpenTelemetry observability covering traces, metrics, and logs instrumentation for Node.js and Python, SDK configuration, exporters, and auto-instrumentation.
- [Node.js API Development](./nodejs-api-development/) - Node.js API development with Express and Fastify, JWT authentication, rate limiting, WebSockets, input validation, and production patterns.
- [Payment Processing](./payment-processing/) - Payment flows with Stripe Checkout, subscriptions, metered billing, refunds, webhooks, and PCI compliance.
- [Payload CMS](./payload-cms/) - Payload CMS with collections, access control, hooks, Lexical rich text, file uploads, and Next.js integration.
- [PDF Generation](./pdf-generation/) - PDF generation with Playwright HTML-to-PDF, pdf-lib, invoice templates, watermarks, and Python ReportLab.
- [Performance Optimization](./performance-optimization/) - Application performance optimization with Core Web Vitals, bundle analysis, caching strategies, database tuning, and React/Next.js optimizations.
- [pnpm Workspaces](./pnpm-workspaces/) - pnpm workspace management with workspace protocol, filtering, catalogs, .npmrc config, and dependency alignment.
- [Playwright E2E Testing](./playwright-testing/) - End-to-end testing with Playwright covering page objects, visual regression, API testing, network interception, and CI integration.
- [PostgreSQL Operations](./postgresql-operations/) - PostgreSQL operations including schema design, complex queries, window functions, CTEs, JSONB, full-text search, indexing strategies, and performance tuning.
- [Prompt Improver Hook](https://github.com/severity1/claude-code-prompt-improver) - Intelligent hook that intercepts and refines vague prompts into precise, actionable instructions. *By [@severity1](https://github.com/severity1)*
- [Prompt Engineering](./prompt-engineering/) - Prompt engineering patterns with structured prompting, chain-of-thought, few-shot examples, tool use design, and evaluation strategies.
- [PWA Development](./pwa-development/) - Progressive Web Apps with service workers, Workbox, offline caching strategies, push notifications, and install prompts.
- [Qwik Framework](./qwik-framework/) - Qwik framework covering resumability, signals, routeLoader$/routeAction$, server$ functions, and Qwik City deployment.
- [RabbitMQ](./rabbitmq/) - RabbitMQ message broker covering exchanges, queues, routing, pub/sub, work queues, RPC, and dead letter handling.
- [Prisma ORM](./prisma-orm/) - Prisma ORM for TypeScript covering schema design, migrations, relations, CRUD, transactions, raw queries, middleware, and production database patterns.
- [move-code-quality-skill](https://github.com/1NickPappas/move-code-quality-skill) - Analyzes Move language packages against the official Move Book Code Quality Checklist for Move 2024 Edition compliance and best practices.
- [Radix UI](./radix-ui/) - Radix UI headless components with accessible dialogs, dropdowns, tabs, tooltips, Tailwind styling, and ARIA compliance.
- [Railway Deployment](./railway-deployment/) - Railway deployment covering Postgres/Redis provisioning, Nixpacks builds, custom domains, cron jobs, and GitHub integration.
- [Rate Limiting & Throttling](./rate-limiting/) - Rate limiting with token bucket, sliding window, Redis distributed limits, Express middleware, and tiered API quotas.
- [React Hook Form](./react-hook-form/) - React Hook Form with Zod validation, useFieldArray, Controller, multi-step wizards, and performance optimization.
- [React Router](./react-router/) - React Router v7 with file-based routing, nested layouts, loaders, actions, route protection, and search params.
- [React Server Components](./react-server-components/) - React Server Components covering server vs client component patterns, data fetching, streaming with Suspense, server actions, and composition patterns.
- [React Development](./react-development/) - React development with hooks, component patterns, state management (Zustand/Context), performance optimization, testing with React Testing Library, and modern React 18+ best practices.
- [React Email](./react-email/) - React Email templates with @react-email/components, responsive layouts, preview server, and sending with Resend or Nodemailer.
- [React Native Mobile](./react-native-mobile/) - React Native mobile development with Expo, React Navigation, Reanimated animations, push notifications, and cross-platform deployment patterns.
- [Regex Patterns](./regex-patterns/) - Regular expression patterns for validation, extraction, lookaheads/lookbehinds, named groups, and performance optimization.
- [Redux Toolkit](./redux-toolkit/) - Redux Toolkit with configureStore, createSlice, createAsyncThunk, RTK Query, entity adapters, and TypeScript typing.
- [Redis Caching](./redis-caching/) - Redis caching strategies, session management, rate limiting, real-time features, and performance optimization with in-memory data store.
- [Redis Patterns](./redis-patterns/) - Advanced Redis patterns covering pub/sub, Streams, Lua scripting, RedisJSON, RediSearch, TimeSeries, and cluster configuration.
- [Remix Development](./remix-development/) - Remix with nested routes, loaders, actions, form handling, error boundaries, streaming SSR, and progressive enhancement.
- [Research & Analysis](./research-and-analysis/) - Deep research and analysis patterns covering systematic exploration, technology comparison, architecture analysis, and thorough investigation before implementation.
- [Responsive Design](./responsive-design/) - Responsive web design with mobile-first CSS, Grid/Flexbox, container queries, fluid typography, and touch target optimization.
- [S3 & Object Storage](./s3-storage/) - AWS S3 and object storage with presigned URLs, multipart uploads, lifecycle policies, CloudFront CDN, and R2/MinIO.
- [Playwright Browser Automation](https://github.com/lackeyjb/playwright-skill) - Model-invoked Playwright automation for testing and validating web applications. *By [@lackeyjb](https://github.com/lackeyjb)*
- [prompt-engineering](https://github.com/NeoLabHQ/context-engineering-kit/tree/master/plugins/customaize-agent/skills/prompt-engineering) - Teaches well-known prompt engineering techniques and patterns, including Anthropic best practices and agent persuasion principles.
- [pypict-claude-skill](https://github.com/omkamal/pypict-claude-skill) - Design comprehensive test cases using PICT (Pairwise Independent Combinatorial Testing) for requirements or code, generating optimized test suites with pairwise coverage.
- [Pulumi Infrastructure as Code](./pulumi-iac/) - Pulumi IaC with TypeScript covering AWS/GCP/Azure, stack management, component resources, testing, and CI/CD integration.
- [Puppeteer Scraping](./puppeteer-scraping/) - Puppeteer browser automation covering page navigation, form filling, screenshots, PDF generation, network interception, and stealth mode.
- [Python Development](./python-development/) - Python development best practices including virtual environments, type hints, dataclasses, async/await, pytest testing, packaging, and modern Python patterns.
- [Ruby on Rails](./ruby-on-rails/) - Ruby on Rails development covering MVC architecture, Active Record, Hotwire/Turbo, background jobs, and RSpec testing.
- [Rust Development](./rust-development/) - Rust systems programming with ownership/borrowing, lifetimes, traits, async Tokio, Axum web framework, error handling, and production patterns.
- [Security Audit Skills (Trail of Bits)](https://github.com/trailofbits/skills) - Professional security research skills with CodeQL, Semgrep, variant analysis, and smart contract auditing across 6 blockchain platforms. *By [@trailofbits](https://github.com/trailofbits)*
- [Security Scanning](./security-scanning/) - Security scanning for dependencies, SAST, secrets detection, vulnerability management, and security best practices in CI/CD pipelines.
- [Serverless Patterns](./serverless-patterns/) - Serverless architecture with Lambda, cold start optimization, Step Functions, DynamoDB, and Vercel functions.
- [shadcn/ui](./shadcn-ui/) - shadcn/ui components with forms, data tables, theming, dark mode, and React Hook Form + Zod validation.
- [Skill Creator](./skill-creator/) - Provides guidance for creating effective Claude Skills that extend capabilities with specialized knowledge, workflows, and tool integrations.
- [Supabase Development](./supabase-development/) - Supabase backend-as-a-service covering PostgreSQL database, authentication, real-time subscriptions, storage, edge functions, and Row Level Security policies.
- [Skill Share](./skill-share/) - Creates new Claude skills and automatically shares them on Slack using Rube for seamless team collaboration and skill discovery.
- [Socket.IO](./socket-io/) - Socket.IO real-time communication with rooms, namespaces, typed events, auth middleware, React hooks, and Redis adapter scaling.
- [SolidJS](./solid-js/) - SolidJS reactive UI framework covering signals, effects, stores, control flow, resource fetching, routing, and SolidStart SSR.
- [Skill Seekers](https://github.com/yusufkaraaslan/Skill_Seekers) - Automatically converts any documentation website into a Claude AI skill in minutes. *By [@yusufkaraaslan](https://github.com/yusufkaraaslan)*
- [State Machines & XState](./state-machines/) - State machine patterns with XState v5 for complex UI workflows, business processes, and parallel state management.
- [Storybook Documentation](./storybook-docs/) - Storybook with CSF3 stories, controls, interaction testing, visual regression, and component documentation.
- [SWR Data Fetching](./swr-data-fetching/) - SWR with stale-while-revalidate caching, optimistic mutations, useSWRInfinite pagination, and prefetching.
- [Strapi CMS](./strapi-cms/) - Strapi headless CMS covering content types, REST and GraphQL APIs, lifecycle hooks, authentication, custom plugins, and deployment.
- [Stripe Billing](./stripe-billing/) - Stripe billing covering subscriptions, usage-based metering, customer portal, invoicing, webhooks, and SaaS pricing patterns.
- [Stripe Connect](./stripe-connect/) - Marketplace payments with connected account onboarding, destination/direct charges, transfer splits, and platform fees.
- [SQL Optimization](./sql-optimization/) - SQL query optimization with EXPLAIN ANALYZE, index strategies, N+1 detection, materialized views, partitioning, and connection pooling.
- [SSE Streaming](./sse-streaming/) - Server-Sent Events covering event stream protocol, Express/Node.js implementations, AI token streaming, reconnection, and React hooks.
- [SQLite & LibSQL](./sqlite-libsql/) - SQLite and Turso with better-sqlite3, LibSQL client, FTS5 full-text search, JSON functions, and Drizzle integration.
- [Spring Boot](./spring-boot/) - Spring Boot development with REST APIs, Spring Data JPA, Spring Security, JWT/OAuth2, MockMvc testing, and production deployment patterns.
- [Sanity CMS](./sanity-cms/) - Sanity headless CMS with GROQ queries, schema definition, image handling, portable text, and Next.js integration.
- [Semantic Release](./semantic-release/) - Automated versioning with semantic-release, conventional commits, commitlint, changesets, and GitHub Actions workflows.
- [SEO Optimization](./seo-optimization/) - SEO technical optimization covering meta tags, structured data (JSON-LD), Open Graph, sitemaps, Core Web Vitals, and search engine visibility.
- [Sharp Image Processing](./sharp-image-processing/) - Sharp image processing covering resizing, format conversion, watermarks, metadata, batch processing, and upload pipelines.
- [Stripe Payments](./stripe-payments/) - Stripe payment integration covering Checkout Sessions, Payment Intents, subscriptions, webhooks, Connect for marketplaces, and production payment patterns.
- [SwiftUI Development](./swiftui-development/) - SwiftUI for iOS/macOS with views, @Observable state, NavigationStack, async/await, SwiftData, MVVM, and accessibility.
- [SvelteKit Development](./sveltekit-development/) - SvelteKit full-stack development with Svelte 5 runes, load functions, form actions, API routes, authentication, and deployment adapters.
- [software-architecture](https://github.com/NeoLabHQ/context-engineering-kit/tree/master/plugins/ddd/skills/software-architecture) - Implements design patterns including Clean Architecture, SOLID principles, and comprehensive software design best practices.
- [subagent-driven-development](https://github.com/NeoLabHQ/context-engineering-kit/tree/master/plugins/sadd/skills/subagent-driven-development) - Dispatches independent subagents for individual tasks with code review checkpoints between iterations for rapid, controlled development.
- [Tailwind CSS Styling](./tailwindcss-styling/) - Tailwind CSS utility-first styling with responsive design, dark mode, custom themes, component patterns, animations, and production optimization.
- [TanStack Query](./tanstack-query/) - TanStack Query (React Query) with queries, mutations, optimistic updates, infinite scrolling, prefetching, and cache management.
- [Tauri Desktop Apps](./tauri-desktop/) - Tauri with Rust backend commands, IPC, system tray, auto-updates, and cross-platform packaging.
- [Terraform Infrastructure](./terraform-infrastructure/) - Terraform infrastructure as code covering providers, modules, state management, workspaces, AWS/GCP/Azure resources, remote backends, and production-ready IaC patterns.
- [Testing Strategies](./testing-strategies/) - Testing pyramid, integration tests, contract testing with Pact, database testing with Testcontainers, and CI optimization.
- [Test-Driven Development](./test-driven-development/) - TDD methodology covering red-green-refactor cycle, test design patterns, BDD, and maintaining test quality across TypeScript, Python, and Go.
- [Tailwind CSS](./tailwind-css/) - Tailwind CSS with utility classes, responsive design, dark mode, custom themes, component patterns, and animations.
- [Three.js 3D Graphics](./three-js/) - Three.js with scene setup, GLTF models, React Three Fiber, Rapier physics, animations, and performance optimization.
- [Testing Library](./testing-library/) - React Testing Library with accessibility-first queries, userEvent, async patterns, custom render wrappers, and hook testing.
- [tRPC](./trpc-api/) - tRPC type-safe APIs with routers, procedures, Zod validation, middleware, React Query integration, and SSR prefetching.
- [Turborepo Monorepo](./turborepo-monorepo/)
- [Turborepo Pipelines](./turborepo-pipelines/) - Turborepo build orchestration with task pipelines, remote caching, pruned Docker builds, and GitHub Actions CI.
- [Turborepo v2](./turborepo-v2/) - Turborepo v2 covering task configuration, watch mode, boundary enforcement, remote caching, and migration from v1.
- [Twilio Communication](./twilio-communication/) - Twilio APIs covering SMS, voice calls with TwiML, WhatsApp messaging, Verify OTP, webhooks, and Node.js SDK integration.
- [TypeScript Development](./typescript-development/) - TypeScript development with strict mode, advanced generics, utility types, type narrowing, decorators, module systems, and production-ready type-safe patterns.
- [Vitest Testing](./vitest-testing/) - Vitest with mocking, snapshots, coverage, workspace mode for monorepos, browser mode, and Jest migration.
- [Vue.js Development](./vuejs-development/) - Vue.js development covering Composition API, reactive state, Pinia store, Vue Router, TypeScript integration, component patterns, composables, testing with Vitest, and production-ready patterns with Nuxt.js.
- [test-driven-development](https://github.com/obra/superpowers/tree/main/skills/test-driven-development) - Use when implementing any feature or bugfix, before writing implementation code.
- [Unit Testing Patterns](./unit-testing-patterns/) - Unit testing with AAA pattern, mocking, parameterized tests, async testing, and coverage strategies across TypeScript and Python.
- [Upstash Serverless](./upstash-serverless/) - Upstash serverless data services covering Redis REST API, QStash queues, Vector search, rate limiting, and caching.
- [Vercel Deployment](./vercel-deployment/) - Vercel deployment with serverless/edge functions, preview deployments, monorepo support, and custom domains.
- [Vite Build Tool](./vite-build-tool/) - Vite configuration with path aliases, environment variables, library mode, SSR, plugin development, and chunk splitting.
- [using-git-worktrees](https://github.com/obra/superpowers/blob/main/skills/using-git-worktrees/) - Creates isolated git worktrees with smart directory selection and safety verification.
- [Webapp Testing](./webapp-testing/) - Tests local web applications using Playwright for verifying frontend functionality, debugging UI behavior, and capturing screenshots.
- [WebAssembly](./webassembly/) - WebAssembly (Wasm) development covering Rust-to-Wasm with wasm-pack, AssemblyScript, JavaScript interop, memory management, and WASI.
- [Webpack Configuration](./webpack-config/) - Webpack 5 with loaders, code splitting, Module Federation, production optimization, and bundle analysis.
- [Web Components](./web-components/) - Web Components with Custom Elements, Shadow DOM, Lit framework, slots, form-associated elements, and framework interop.
- [Web Workers](./web-workers/) - Web Workers for parallel processing covering dedicated workers, worker pools, Comlink RPC, transferable objects, and OffscreenCanvas.
- [Web Accessibility](./web-accessibility/) - Web accessibility (a11y) covering WCAG 2.2 compliance, ARIA attributes, keyboard navigation, screen reader optimization, focus management, and automated testing with axe-core.
- [Web Animation](./web-animation/) - Web animation with Framer Motion, GSAP, CSS transitions, scroll effects, spring physics, and reduced-motion accessibility.
- [Web Scraping](./web-scraping/) - Web scraping with Cheerio, Playwright, Beautiful Soup, rate limiting, structured data extraction, and ethical practices.
- [Vercel Agent Skills](https://github.com/vercel-labs/agent-skills) - One-command Vercel deployment, React/Next.js performance optimization (40+ rules), and code auditing for 100+ accessibility/UX rules. *By [@vercel-labs](https://github.com/vercel-labs)*
- [WebRTC Communication](./webrtc-communication/) - WebRTC real-time communication covering peer connections, media streams, data channels, signaling with WebSocket, and screen sharing.
- [Webhooks Integration](./webhooks-integration/) - Webhook implementation with HMAC-SHA256 verification, idempotent processing, Stripe/GitHub patterns, and delivery systems.
- [Zod Validation](./zod-validation/) - Zod schema validation with transforms, refinements, discriminated unions, React Hook Form integration, and shared client/server schemas.
- [Zustand State Management](./zustand-state/) - Zustand with stores, selectors, persist/devtools/immer middleware, async actions, store composition, and testing.
- [WebSocket & Real-time](./websocket-realtime/) - WebSocket and real-time communication with Socket.IO, native WebSocket API, Server-Sent Events, pub/sub, presence tracking, and scalable architecture.

### Data & Analysis

- [AltimateAI Data Engineering](https://github.com/AltimateAI/data-engineering-skills) - dbt task automation, SQL optimization (+22% faster queries on TPC-H 1TB), query profiling, and anti-pattern detection. *By [@AltimateAI](https://github.com/AltimateAI)*
- [CSV Data Summarizer](https://github.com/coffeefuelbump/csv-data-summarizer-claude-skill) - Automatically analyzes CSV files and generates comprehensive insights with visualizations without requiring user prompts. *By [@coffeefuelbump](https://github.com/coffeefuelbump)*
- [postgres](https://github.com/sanjay3290/ai-skills/tree/main/skills/postgres) - Execute safe read-only SQL queries against PostgreSQL databases with multi-connection support and defense-in-depth security. *By [@sanjay3290](https://github.com/sanjay3290)*
- [root-cause-tracing](https://github.com/obra/superpowers/tree/main/skills/root-cause-tracing) - Use when errors occur deep in execution and you need to trace back to find the original trigger.

### Business & Marketing

- [Brand Guidelines](./brand-guidelines/) - Applies Anthropic's official brand colors and typography to artifacts for consistent visual identity and professional design standards.
- [Competitive Ads Extractor](./competitive-ads-extractor/) - Extracts and analyzes competitors' ads from ad libraries to understand messaging and creative approaches that resonate.
- [Domain Name Brainstormer](./domain-name-brainstormer/) - Generates creative domain name ideas and checks availability across multiple TLDs including .com, .io, .dev, and .ai extensions.
- [Internal Comms](./internal-comms/) - Helps write internal communications including 3P updates, company newsletters, FAQs, status reports, and project updates using company-specific formats.
- [Lead Research Assistant](./lead-research-assistant/) - Identifies and qualifies high-quality leads by analyzing your product, searching for target companies, and providing actionable outreach strategies.

### Communication & Writing

- [article-extractor](https://github.com/michalparkola/tapestry-skills-for-claude-code/tree/main/article-extractor) - Extract full article text and metadata from web pages.
- [brainstorming](https://github.com/obra/superpowers/tree/main/skills/brainstorming) - Transform rough ideas into fully-formed designs through structured questioning and alternative exploration.
- [Content Research Writer](./content-research-writer/) - Assists in writing high-quality content by conducting research, adding citations, improving hooks, and providing section-by-section feedback.
- [family-history-research](https://github.com/emaynard/claude-family-history-research-skill) - Provides assistance with planning family history and genealogy research projects.
- [Meeting Insights Analyzer](./meeting-insights-analyzer/) - Analyzes meeting transcripts to uncover behavioral patterns including conflict avoidance, speaking ratios, filler words, and leadership style.
- [NotebookLM Integration](https://github.com/PleasePrompto/notebooklm-skill) - Lets Claude Code chat directly with NotebookLM for source-grounded answers based exclusively on uploaded documents. *By [@PleasePrompto](https://github.com/PleasePrompto)*

### Creative & Media

- [Algorithmic Art](./algorithmic-art/) - Creates algorithmic art and generative designs using computational creativity techniques.
- [Canvas Design](./canvas-design/) - Creates beautiful visual art in PNG and PDF documents using design philosophy and aesthetic principles for posters, designs, and static pieces.
- [imagen](https://github.com/sanjay3290/ai-skills/tree/main/skills/imagen) - Generate images using Google Gemini's image generation API for UI mockups, icons, illustrations, and visual assets. *By [@sanjay3290](https://github.com/sanjay3290)*
- [Image Enhancer](./image-enhancer/) - Improves image and screenshot quality by enhancing resolution, sharpness, and clarity for professional presentations and documentation.
- [Slack GIF Creator](./slack-gif-creator/) - Creates animated GIFs optimized for Slack with validators for size constraints and composable animation primitives.
- [Theme Factory](./theme-factory/) - Applies professional font and color themes to artifacts including slides, docs, reports, and HTML landing pages with 10 pre-set themes.
- [Video Downloader](./video-downloader/) - Downloads videos from YouTube and other platforms for offline viewing, editing, or archival with support for various formats and quality options.
- [youtube-transcript](https://github.com/michalparkola/tapestry-skills-for-claude-code/tree/main/youtube-transcript) - Fetch transcripts from YouTube videos and prepare summaries.

### Productivity & Organization

- [File Organizer](./file-organizer/) - Intelligently organizes files and folders by understanding context, finding duplicates, and suggesting better organizational structures.
- [Invoice Organizer](./invoice-organizer/) - Automatically organizes invoices and receipts for tax preparation by reading files, extracting information, and renaming consistently.
- [kaizen](https://github.com/NeoLabHQ/context-engineering-kit/tree/master/plugins/kaizen/skills/kaizen) - Applies continuous improvement methodology with multiple analytical approaches, based on Japanese Kaizen philosophy and Lean methodology.
- [n8n-skills](https://github.com/haunchen/n8n-skills) - Enables AI assistants to directly understand and operate n8n workflows.
- [Raffle Winner Picker](./raffle-winner-picker/) - Randomly selects winners from lists, spreadsheets, or Google Sheets for giveaways and contests with cryptographically secure randomness.
- [ship-learn-next](https://github.com/michalparkola/tapestry-skills-for-claude-code/tree/main/ship-learn-next) - Skill to help iterate on what to build or learn next, based on feedback loops.
- [tapestry](https://github.com/michalparkola/tapestry-skills-for-claude-code/tree/main/tapestry) - Interlink and summarize related documents into knowledge networks.

### Collaboration & Project Management

- [git-pushing](https://github.com/mhattingpete/claude-skills-marketplace/tree/main/engineering-workflow-plugin/skills/git-pushing) - Automate git operations and repository interactions.
- [review-implementing](https://github.com/mhattingpete/claude-skills-marketplace/tree/main/engineering-workflow-plugin/skills/review-implementing) - Evaluate code implementation plans and align with specs.
- [test-fixing](https://github.com/mhattingpete/claude-skills-marketplace/tree/main/engineering-workflow-plugin/skills/test-fixing) - Detect failing tests and propose patches or fixes.

### Security & Systems

- [computer-forensics](https://github.com/mhattingpete/claude-skills-marketplace/tree/main/computer-forensics-skills/skills/computer-forensics) - Digital forensics analysis and investigation techniques.
- [file-deletion](https://github.com/mhattingpete/claude-skills-marketplace/tree/main/computer-forensics-skills/skills/file-deletion) - Secure file deletion and data sanitization methods.
- [metadata-extraction](https://github.com/mhattingpete/claude-skills-marketplace/tree/main/computer-forensics-skills/skills/metadata-extraction) - Extract and analyze file metadata for forensic purposes.
- [threat-hunting-with-sigma-rules](https://github.com/jthack/threat-hunting-with-sigma-rules-skill) - Use Sigma detection rules to hunt for threats and analyze security events.

## Getting Started

### Using Skills in Claude.ai

1. Click the skill icon (🧩) in your chat interface.
2. Add skills from the marketplace or upload custom skills.
3. Claude automatically activates relevant skills based on your task.

### Using Skills in Claude Code

1. Place the skill in `~/.config/claude-code/skills/`:
   ```bash
   mkdir -p ~/.config/claude-code/skills/
   cp -r skill-name ~/.config/claude-code/skills/
   ```

2. Verify skill metadata:
   ```bash
   head ~/.config/claude-code/skills/skill-name/SKILL.md
   ```

3. Start Claude Code:
   ```bash
   claude
   ```

4. The skill loads automatically and activates when relevant.

### Using Skills via API

Use the Claude Skills API to programmatically load and manage skills:

```python
import anthropic

client = anthropic.Anthropic(api_key="your-api-key")

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    skills=["skill-id-here"],
    messages=[{"role": "user", "content": "Your prompt"}]
)
```

See the [Skills API documentation](https://docs.claude.com/en/api/skills-guide) for details.

## Creating Skills

### Skill Structure

Each skill is a folder containing a `SKILL.md` file with YAML frontmatter:

```
skill-name/
├── SKILL.md          # Required: Skill instructions and metadata
├── scripts/          # Optional: Helper scripts
├── templates/        # Optional: Document templates
└── resources/        # Optional: Reference files
```

### Basic Skill Template

```markdown
---
name: my-skill-name
description: A clear description of what this skill does and when to use it.
---

# My Skill Name

Detailed description of the skill's purpose and capabilities.

## When to Use This Skill

- Use case 1
- Use case 2
- Use case 3

## Instructions

[Detailed instructions for Claude on how to execute this skill]

## Examples

[Real-world examples showing the skill in action]
```

### Skill Best Practices

- Focus on specific, repeatable tasks
- Include clear examples and edge cases
- Write instructions for Claude, not end users
- Test across Claude.ai, Claude Code, and API
- Document prerequisites and dependencies
- Include error handling guidance

## Contributing

We welcome contributions! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on:

- How to submit new skills
- Skill quality standards
- Pull request process
- Code of conduct

### Quick Contribution Steps

1. Ensure your skill is based on a real use case
2. Check for duplicates in existing skills
3. Follow the skill structure template
4. Test your skill across platforms
5. Submit a pull request with clear documentation

## MCP Servers

This repository integrates with several MCP (Model Context Protocol) servers that extend Claude's capabilities with external services:

### Available MCP Servers

- **GitHub** (✅ Authenticated) - Full GitHub integration for repositories, issues, PRs, and code management
- **Serena** (✅ Active) - Semantic code intelligence with project-specific memories and code navigation
- **Context7** - Up-to-date documentation search for any programming library or framework
- **Playwright** - Browser automation and web application testing
- **Greptile** - Code search, custom context, and PR review analysis
- **Pinecone** - Vector database for AI applications with embedding and reranking
- **Supabase** - Database integration for Supabase projects
- **Notion** - Workspace integration for creating and managing Notion content
- **Render** - Cloud deployment platform for web services, databases, and cron jobs
- **Railway** - Cloud platform for deploying applications and services

### Setting Up MCP Servers

For detailed setup instructions, see [MCP_SETUP.md](MCP_SETUP.md).

Quick start for common servers:

1. **GitHub** - Already configured and authenticated
2. **Serena** - Activate with `mcp__plugin_serena_serena__activate_project` for semantic code intelligence
3. **Context7** - Ready to use for library documentation queries
4. **Playwright** - Available for webapp testing (requires browser installation)

### MCP Server Documentation

Each MCP server provides specialized tools:
- Use GitHub MCP for repository management, PR reviews, and issue tracking
- Use Serena MCP for understanding codebases with semantic search and symbol navigation
- Use Context7 MCP to get up-to-date library documentation and code examples
- Use Greptile MCP for code reviews and custom context across your codebase

For authentication requirements and troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Resources

### Official Documentation

- [Claude Skills Overview](https://www.anthropic.com/news/skills) - Official announcement and features
- [Skills User Guide](https://support.claude.com/en/articles/12512180-using-skills-in-claude) - How to use skills in Claude
- [Creating Custom Skills](https://support.claude.com/en/articles/12512198-creating-custom-skills) - Skill development guide
- [Skills API Documentation](https://docs.claude.com/en/api/skills-guide) - API integration guide
- [Agent Skills Blog Post](https://anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) - Engineering deep dive

### Community Resources

- [Anthropic Skills Repository](https://github.com/anthropics/skills) - Official example skills
- [Claude Community](https://community.anthropic.com) - Discuss skills with other users
- [Skills Marketplace](https://claude.ai/marketplace) - Discover and share skills

### Inspiration & Use Cases

- [Lenny's Newsletter](https://www.lennysnewsletter.com/p/everyone-should-be-using-claude-code) - 50 ways people use Claude Code
- [Notion Skills](https://www.notion.so/notiondevs/Notion-Skills-for-Claude-28da4445d27180c7af1df7d8615723d0) - Notion integration skills


## Join the Community

- Have questions about integrating Composio with your auth setup? [Hop on a quick call with us](https://calendly.com/thomas-composio/composio-enterprise-setup)
- [Follow us on Twitter](https://x.com/composio)
- [Join our Discord](https://discord.com/invite/composio)

## License

This repository is licensed under the Apache License 2.0.

Individual skills may have different licenses - please check each skill's folder for specific licensing information.

---

**Note**: Claude Skills work across Claude.ai, Claude Code, and the Claude API. Once you create a skill, it's portable across all platforms, making your workflows consistent everywhere you use Claude.

- [AgentsKB](https://agentskb.com) - Upgrade your AI with researched answers. We did the research so your AI gets it right the first time.
