---
name: graphql-codegen
description: GraphQL Code Generator covering TypeScript type generation, typed document nodes, React Query and Apollo hooks, fragment colocation, schema-first development, and CI integration for type-safe GraphQL operations.
---

# GraphQL Code Generator

This skill should be used when generating TypeScript types and hooks from GraphQL schemas and operations. It covers codegen configuration, typed operations, React integration, and CI workflows.

## When to Use This Skill

Use this skill when you need to:

- Generate TypeScript types from GraphQL schemas
- Create typed hooks for React Query or Apollo
- Implement fragment colocation patterns
- Set up schema-first development workflows
- Automate type generation in CI

## Setup

```bash
npm install graphql
npm install -D @graphql-codegen/cli @graphql-codegen/typescript \
  @graphql-codegen/typescript-operations @graphql-codegen/typed-document-node \
  @graphql-codegen/client-preset
```

## Configuration

```typescript
// codegen.ts
import type { CodegenConfig } from "@graphql-codegen/cli";

const config: CodegenConfig = {
  schema: "http://localhost:4000/graphql",
  documents: ["src/**/*.graphql", "src/**/*.tsx"],
  generates: {
    "./src/gql/": {
      preset: "client",
      config: {
        scalars: {
          DateTime: "string",
          JSON: "Record<string, unknown>",
          UUID: "string",
        },
        enumsAsTypes: true,
        skipTypename: false,
      },
    },
  },
  hooks: {
    afterAllFileWrite: ["prettier --write"],
  },
};

export default config;
```

## GraphQL Operations

```graphql
# src/graphql/posts.graphql

query GetPosts($first: Int!, $after: String, $where: PostFilter) {
  posts(first: $first, after: $after, where: $where) {
    edges {
      node {
        ...PostCard
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}

query GetPost($id: ID!) {
  post(id: $id) {
    ...PostDetail
  }
}

mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    ...PostCard
  }
}

fragment PostCard on Post {
  id
  title
  excerpt
  createdAt
  author {
    id
    name
    avatarUrl
  }
}

fragment PostDetail on Post {
  ...PostCard
  body
  tags
  comments {
    id
    body
    author {
      name
    }
  }
}
```

## Usage with TanStack Query

```typescript
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { graphql } from "@/gql";
import { request } from "graphql-request";

const ENDPOINT = "/api/graphql";

// Typed document nodes — full type safety
const GetPostsDocument = graphql(`
  query GetPosts($first: Int!) {
    posts(first: $first) {
      edges {
        node {
          id
          title
          author { name }
        }
      }
    }
  }
`);

const CreatePostDocument = graphql(`
  mutation CreatePost($input: CreatePostInput!) {
    createPost(input: $input) {
      id
      title
    }
  }
`);

function usePosts(first: number) {
  return useQuery({
    queryKey: ["posts", first],
    queryFn: () => request(ENDPOINT, GetPostsDocument, { first }),
  });
}

function useCreatePost() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: CreatePostInput) =>
      request(ENDPOINT, CreatePostDocument, { input }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["posts"] });
    },
  });
}
```

## Usage with Apollo Client

```typescript
import { useQuery, useMutation } from "@apollo/client";
import { GetPostsDocument, CreatePostDocument } from "@/gql/graphql";

function PostList() {
  const { data, loading, fetchMore } = useQuery(GetPostsDocument, {
    variables: { first: 10 },
  });

  const [createPost, { loading: creating }] = useMutation(CreatePostDocument, {
    refetchQueries: ["GetPosts"],
  });

  if (loading) return <Spinner />;

  return (
    <div>
      {data?.posts.edges.map(({ node }) => (
        <PostCard key={node.id} post={node} />
      ))}
    </div>
  );
}
```

## CLI Commands

```bash
npx graphql-codegen              # Generate types
npx graphql-codegen --watch      # Watch mode
npx graphql-codegen --config codegen.ts
```

## Additional Resources

- GraphQL Codegen: https://the-guild.dev/graphql/codegen
- Client Preset: https://the-guild.dev/graphql/codegen/plugins/presets/preset-client
