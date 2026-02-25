---
name: prisma-orm
description: Prisma ORM for TypeScript/Node.js covering schema design, migrations, CRUD operations, relations, transactions, raw queries, middleware, seeding, testing patterns, and production database management.
---

# Prisma ORM

This skill provides comprehensive guidance for working with Prisma ORM in TypeScript and Node.js projects. It covers the full lifecycle from initial setup through production database management.

---

## 1. Setup and Initialization

### Install Prisma

```bash
npm install prisma --save-dev
npm install @prisma/client
npx prisma init
```

This creates a `prisma/` directory with `schema.prisma` and a `.env` file containing `DATABASE_URL`.