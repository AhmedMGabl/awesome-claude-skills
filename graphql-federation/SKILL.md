---
name: graphql-federation
description: GraphQL Federation patterns covering subgraph schemas, entity resolution, Apollo Router, shared types, migration strategies, and federated gateway configuration.
---

# GraphQL Federation

This skill should be used when building federated GraphQL architectures. It covers subgraph schemas, entity resolution, Apollo Router, shared types, and gateway configuration.

## When to Use This Skill

Use this skill when you need to:

- Split a monolithic GraphQL API into subgraphs
- Share types across services with Federation
- Configure Apollo Router as gateway
- Resolve entities across service boundaries
- Migrate to a federated architecture

## Subgraph Schema (Users Service)

```graphql
# users-subgraph/schema.graphql
extend schema @link(url: "https://specs.apollo.dev/federation/v2.5", import: ["@key", "@shareable"])

type Query {
  user(id: ID!): User
  users(page: Int = 1, limit: Int = 20): UsersConnection!
}

type Mutation {
  createUser(input: CreateUserInput!): User!
}

type User @key(fields: "id") {
  id: ID!
  name: String!
  email: String!
  role: Role!
  createdAt: DateTime!
}

type UsersConnection {
  nodes: [User!]!
  totalCount: Int!
  hasNextPage: Boolean!
}

input CreateUserInput {
  name: String!
  email: String!
  role: Role
}

enum Role {
  USER
  ADMIN
  EDITOR
}
```

## Entity Resolver (Users Service)

```typescript
const resolvers = {
  Query: {
    user: (_, { id }) => userService.getById(id),
    users: (_, { page, limit }) => userService.list(page, limit),
  },
  Mutation: {
    createUser: (_, { input }) => userService.create(input),
  },
  User: {
    __resolveReference: (ref) => userService.getById(ref.id),
  },
};
```

## Subgraph Schema (Posts Service)

```graphql
# posts-subgraph/schema.graphql
extend schema @link(url: "https://specs.apollo.dev/federation/v2.5",
  import: ["@key", "@external", "@requires"])

type Query {
  post(id: ID!): Post
  feed(limit: Int = 20, cursor: String): PostConnection!
}

type Post @key(fields: "id") {
  id: ID!
  title: String!
  content: String!
  author: User!
  tags: [Tag!]!
  createdAt: DateTime!
}

# Extend User from users-subgraph
type User @key(fields: "id") {
  id: ID!
  posts: [Post!]!
  postCount: Int!
}

type Tag {
  name: String!
}

type PostConnection {
  nodes: [Post!]!
  cursor: String
  hasMore: Boolean!
}
```

## Entity Resolver (Posts Service)

```typescript
const resolvers = {
  Query: {
    post: (_, { id }) => postService.getById(id),
    feed: (_, { limit, cursor }) => postService.getFeed(limit, cursor),
  },
  Post: {
    __resolveReference: (ref) => postService.getById(ref.id),
    author: (post) => ({ __typename: "User", id: post.authorId }),
  },
  User: {
    posts: (user) => postService.getByAuthorId(user.id),
    postCount: (user) => postService.countByAuthorId(user.id),
  },
};
```

## Apollo Router Configuration

```yaml
# router.yaml
supergraph:
  listen: 0.0.0.0:4000
  introspection: true

cors:
  origins:
    - https://app.example.com
  allow_headers:
    - Content-Type
    - Authorization

headers:
  all:
    request:
      - propagate:
          named: Authorization

telemetry:
  exporters:
    tracing:
      otlp:
        enabled: true
        endpoint: http://jaeger:4317

limits:
  max_depth: 15
  max_height: 200
```

## Compose Supergraph

```bash
# Install rover CLI
curl -sSL https://rover.apollo.dev/nix/latest | sh

# Compose supergraph schema
rover supergraph compose --config supergraph.yaml > supergraph.graphql
```

```yaml
# supergraph.yaml
federation_version: =2.5.0
subgraphs:
  users:
    routing_url: http://users-service:4001/graphql
    schema:
      file: ./users-subgraph/schema.graphql
  posts:
    routing_url: http://posts-service:4002/graphql
    schema:
      file: ./posts-subgraph/schema.graphql
```

## Subgraph Server Setup

```typescript
import { ApolloServer } from "@apollo/server";
import { buildSubgraphSchema } from "@apollo/subgraph";
import { readFileSync } from "fs";
import { parse } from "graphql";

const typeDefs = parse(readFileSync("./schema.graphql", "utf-8"));

const server = new ApolloServer({
  schema: buildSubgraphSchema({ typeDefs, resolvers }),
});
```

## Additional Resources

- Apollo Federation: https://www.apollographql.com/docs/federation/
- Apollo Router: https://www.apollographql.com/docs/router/
- Rover CLI: https://www.apollographql.com/docs/rover/
