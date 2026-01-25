---
name: graphql-development
description: GraphQL API development with schema design, resolvers, queries, mutations, subscriptions, Apollo Server/Client, type safety, authentication, caching, and real-time capabilities.
---

# GraphQL Development

This skill should be used when the user needs to design, implement, or work with GraphQL APIs. It covers schema design, resolver implementation, client integration, type safety, authentication, caching strategies, and production-ready patterns for building modern GraphQL applications.

## When to Use This Skill

Use this skill when you need to:

- Design GraphQL schemas and type systems
- Implement GraphQL servers with Apollo Server
- Create queries, mutations, and subscriptions
- Integrate GraphQL clients (Apollo Client, urql, React Query)
- Implement authentication and authorization
- Set up caching strategies
- Handle errors and validation
- Implement real-time features with subscriptions
- Optimize GraphQL performance
- Generate TypeScript types from schemas

## GraphQL Fundamentals

### Schema Definition Language (SDL)

GraphQL schemas define your API's type system.

```graphql
# Basic types
type User {
  id: ID!
  email: String!
  name: String!
  age: Int
  posts: [Post!]!
  createdAt: DateTime!
}

type Post {
  id: ID!
  title: String!
  content: String!
  published: Boolean!
  author: User!
  comments: [Comment!]!
  tags: [String!]!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type Comment {
  id: ID!
  content: String!
  author: User!
  post: Post!
  createdAt: DateTime!
}

# Custom scalars
scalar DateTime
scalar JSON
scalar Upload

# Enums
enum Role {
  USER
  ADMIN
  MODERATOR
}

enum PostStatus {
  DRAFT
  PUBLISHED
  ARCHIVED
}

# Input types for mutations
input CreateUserInput {
  email: String!
  name: String!
  password: String!
}

input UpdatePostInput {
  title: String
  content: String
  published: Boolean
  tags: [String!]
}

# Interfaces
interface Node {
  id: ID!
  createdAt: DateTime!
  updatedAt: DateTime!
}

# Unions
union SearchResult = User | Post | Comment

# Root types
type Query {
  # User queries
  user(id: ID!): User
  users(limit: Int, offset: Int): [User!]!
  me: User

  # Post queries
  post(id: ID!): Post
  posts(
    limit: Int
    offset: Int
    status: PostStatus
    authorId: ID
  ): PostConnection!

  # Search
  search(query: String!): [SearchResult!]!
}

type Mutation {
  # User mutations
  createUser(input: CreateUserInput!): User!
  updateUser(id: ID!, input: UpdateUserInput!): User!
  deleteUser(id: ID!): Boolean!

  # Post mutations
  createPost(input: CreatePostInput!): Post!
  updatePost(id: ID!, input: UpdatePostInput!): Post!
  deletePost(id: ID!): Boolean!
  publishPost(id: ID!): Post!

  # Comment mutations
  addComment(postId: ID!, content: String!): Comment!
  deleteComment(id: ID!): Boolean!
}

type Subscription {
  # Real-time updates
  postCreated: Post!
  postUpdated(id: ID!): Post!
  commentAdded(postId: ID!): Comment!
  userOnlineStatus(userId: ID!): OnlineStatus!
}

# Pagination
type PostConnection {
  edges: [PostEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PostEdge {
  node: Post!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
```

## Apollo Server Setup

### Basic Server Configuration

```javascript
// server.js
import { ApolloServer } from '@apollo/server';
import { startStandaloneServer } from '@apollo/server/standalone';
import { readFileSync } from 'fs';

// Load schema from file
const typeDefs = readFileSync('./schema.graphql', { encoding: 'utf-8' });

// Resolvers implement the schema
const resolvers = {
  Query: {
    user: async (parent, { id }, context) => {
      return context.dataSources.userAPI.getUser(id);
    },

    users: async (parent, { limit = 10, offset = 0 }, context) => {
      return context.dataSources.userAPI.getUsers({ limit, offset });
    },

    me: async (parent, args, context) => {
      if (!context.user) {
        throw new GraphQLError('Not authenticated', {
          extensions: { code: 'UNAUTHENTICATED' }
        });
      }
      return context.user;
    },

    post: async (parent, { id }, context) => {
      return context.dataSources.postAPI.getPost(id);
    },

    posts: async (parent, { limit, offset, status, authorId }, context) => {
      return context.dataSources.postAPI.getPosts({
        limit,
        offset,
        status,
        authorId
      });
    }
  },

  Mutation: {
    createUser: async (parent, { input }, context) => {
      const { email, name, password } = input;

      // Validate input
      if (!email.includes('@')) {
        throw new GraphQLError('Invalid email', {
          extensions: {
            code: 'BAD_USER_INPUT',
            argumentName: 'email'
          }
        });
      }

      // Create user
      const user = await context.dataSources.userAPI.createUser({
        email,
        name,
        passwordHash: await hashPassword(password)
      });

      return user;
    },

    createPost: async (parent, { input }, context) => {
      // Check authentication
      if (!context.user) {
        throw new GraphQLError('Not authenticated', {
          extensions: { code: 'UNAUTHENTICATED' }
        });
      }

      const post = await context.dataSources.postAPI.createPost({
        ...input,
        authorId: context.user.id
      });

      // Publish to subscription
      context.pubsub.publish('POST_CREATED', { postCreated: post });

      return post;
    },

    updatePost: async (parent, { id, input }, context) => {
      // Check authentication
      if (!context.user) {
        throw new GraphQLError('Not authenticated', {
          extensions: { code: 'UNAUTHENTICATED' }
        });
      }

      const post = await context.dataSources.postAPI.getPost(id);

      // Check authorization
      if (post.authorId !== context.user.id && context.user.role !== 'ADMIN') {
        throw new GraphQLError('Not authorized', {
          extensions: { code: 'FORBIDDEN' }
        });
      }

      const updated = await context.dataSources.postAPI.updatePost(id, input);
      return updated;
    }
  },

  // Field resolvers
  User: {
    posts: async (user, args, context) => {
      return context.dataSources.postAPI.getPostsByAuthor(user.id);
    }
  },

  Post: {
    author: async (post, args, context) => {
      return context.dataSources.userAPI.getUser(post.authorId);
    },

    comments: async (post, args, context) => {
      return context.dataSources.commentAPI.getCommentsByPost(post.id);
    }
  }
};

// Create server
const server = new ApolloServer({
  typeDefs,
  resolvers,
  formatError: (formattedError, error) => {
    // Custom error formatting
    console.error('GraphQL Error:', error);

    if (formattedError.extensions.code === 'INTERNAL_SERVER_ERROR') {
      return new GraphQLError('Internal server error', {
        extensions: { code: 'INTERNAL_SERVER_ERROR' }
      });
    }

    return formattedError;
  }
});

// Start server
const { url } = await startStandaloneServer(server, {
  listen: { port: 4000 },
  context: async ({ req }) => {
    // Get user from token
    const token = req.headers.authorization?.replace('Bearer ', '');
    const user = token ? await verifyToken(token) : null;

    return {
      user,
      dataSources: {
        userAPI: new UserAPI(),
        postAPI: new PostAPI(),
        commentAPI: new CommentAPI()
      },
      pubsub: new PubSub()
    };
  }
});

console.log(`Server ready at: ${url}`);
```

### DataSource Pattern

```javascript
// dataSources/UserAPI.js
import { DataSource } from 'apollo-datasource';
import { db } from '../database';

export class UserAPI extends DataSource {
  constructor() {
    super();
  }

  initialize(config) {
    this.context = config.context;
  }

  async getUser(id) {
    const user = await db.users.findById(id);
    if (!user) {
      throw new GraphQLError('User not found', {
        extensions: {
          code: 'NOT_FOUND',
          argumentName: 'id'
        }
      });
    }
    return user;
  }

  async getUsers({ limit = 10, offset = 0 }) {
    return db.users.find()
      .limit(limit)
      .skip(offset)
      .toArray();
  }

  async createUser(input) {
    const existing = await db.users.findOne({ email: input.email });
    if (existing) {
      throw new GraphQLError('Email already exists', {
        extensions: {
          code: 'BAD_USER_INPUT',
          argumentName: 'email'
        }
      });
    }

    const user = {
      ...input,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    const result = await db.users.insertOne(user);
    return { ...user, id: result.insertedId };
  }

  async updateUser(id, input) {
    const updated = await db.users.findOneAndUpdate(
      { _id: id },
      { $set: { ...input, updatedAt: new Date() } },
      { returnDocument: 'after' }
    );

    if (!updated.value) {
      throw new GraphQLError('User not found', {
        extensions: { code: 'NOT_FOUND' }
      });
    }

    return updated.value;
  }
}
```

## Apollo Client

### Client Setup

```javascript
// client.js
import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';

const httpLink = createHttpLink({
  uri: 'http://localhost:4000/graphql'
});

const authLink = setContext((_, { headers }) => {
  const token = localStorage.getItem('token');
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : ''
    }
  };
});

const client = new ApolloClient({
  link: authLink.concat(httpLink),
  cache: new InMemoryCache({
    typePolicies: {
      Query: {
        fields: {
          posts: {
            // Merge pagination results
            keyArgs: ['status', 'authorId'],
            merge(existing = { edges: [] }, incoming) {
              return {
                ...incoming,
                edges: [...existing.edges, ...incoming.edges]
              };
            }
          }
        }
      },
      User: {
        fields: {
          posts: {
            merge(existing = [], incoming) {
              return incoming;
            }
          }
        }
      }
    }
  }),
  defaultOptions: {
    watchQuery: {
      fetchPolicy: 'cache-and-network'
    }
  }
});

export default client;
```

### React Integration

```javascript
// App.jsx
import { ApolloProvider } from '@apollo/client';
import client from './client';

function App() {
  return (
    <ApolloProvider client={client}>
      <YourApp />
    </ApolloProvider>
  );
}

// components/UserProfile.jsx
import { useQuery, useMutation, gql } from '@apollo/client';

const GET_USER = gql`
  query GetUser($id: ID!) {
    user(id: $id) {
      id
      name
      email
      posts {
        id
        title
        published
      }
    }
  }
`;

const UPDATE_USER = gql`
  mutation UpdateUser($id: ID!, $input: UpdateUserInput!) {
    updateUser(id: $id, input: $input) {
      id
      name
      email
    }
  }
`;

function UserProfile({ userId }) {
  // Query
  const { data, loading, error, refetch } = useQuery(GET_USER, {
    variables: { id: userId },
    onCompleted: (data) => {
      console.log('User loaded:', data.user);
    }
  });

  // Mutation
  const [updateUser, { loading: updating }] = useMutation(UPDATE_USER, {
    onCompleted: (data) => {
      console.log('User updated:', data.updateUser);
    },
    // Optimistic response
    optimisticResponse: {
      updateUser: {
        __typename: 'User',
        id: userId,
        name: newName,
        email: data?.user.email
      }
    },
    // Update cache
    update(cache, { data: { updateUser } }) {
      cache.modify({
        id: cache.identify(updateUser),
        fields: {
          name() {
            return updateUser.name;
          }
        }
      });
    }
  });

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  const handleUpdate = async (name) => {
    try {
      await updateUser({
        variables: {
          id: userId,
          input: { name }
        }
      });
    } catch (err) {
      console.error('Update failed:', err);
    }
  };

  return (
    <div>
      <h1>{data.user.name}</h1>
      <p>{data.user.email}</p>
      <h2>Posts</h2>
      {data.user.posts.map(post => (
        <div key={post.id}>{post.title}</div>
      ))}
      <button onClick={() => handleUpdate('New Name')} disabled={updating}>
        Update Name
      </button>
    </div>
  );
}
```

## Subscriptions (Real-Time)

### Server Setup with WebSocket

```javascript
// server.js with subscriptions
import { ApolloServer } from '@apollo/server';
import { expressMiddleware } from '@apollo/server/express4';
import { ApolloServerPluginDrainHttpServer } from '@apollo/server/plugin/drainHttpServer';
import { createServer } from 'http';
import { WebSocketServer } from 'ws';
import { useServer } from 'graphql-ws/lib/use/ws';
import { makeExecutableSchema } from '@graphql-tools/schema';
import { PubSub } from 'graphql-subscriptions';
import express from 'express';

const pubsub = new PubSub();

const resolvers = {
  Subscription: {
    postCreated: {
      subscribe: () => pubsub.asyncIterator(['POST_CREATED'])
    },

    postUpdated: {
      subscribe: (parent, { id }) => {
        return pubsub.asyncIterator([`POST_UPDATED_${id}`]);
      }
    },

    commentAdded: {
      subscribe: (parent, { postId }) => {
        return pubsub.asyncIterator([`COMMENT_ADDED_${postId}`]);
      }
    }
  },

  Mutation: {
    createPost: async (parent, { input }, context) => {
      const post = await context.dataSources.postAPI.createPost(input);

      // Publish to subscribers
      pubsub.publish('POST_CREATED', {
        postCreated: post
      });

      return post;
    },

    addComment: async (parent, { postId, content }, context) => {
      const comment = await context.dataSources.commentAPI.createComment({
        postId,
        content,
        authorId: context.user.id
      });

      // Publish to post-specific subscribers
      pubsub.publish(`COMMENT_ADDED_${postId}`, {
        commentAdded: comment
      });

      return comment;
    }
  }
};

const schema = makeExecutableSchema({ typeDefs, resolvers });

const app = express();
const httpServer = createServer(app);

// WebSocket server
const wsServer = new WebSocketServer({
  server: httpServer,
  path: '/graphql'
});

const serverCleanup = useServer({ schema }, wsServer);

const server = new ApolloServer({
  schema,
  plugins: [
    ApolloServerPluginDrainHttpServer({ httpServer }),
    {
      async serverWillStart() {
        return {
          async drainServer() {
            await serverCleanup.dispose();
          }
        };
      }
    }
  ]
});

await server.start();

app.use(
  '/graphql',
  express.json(),
  expressMiddleware(server, {
    context: async ({ req }) => ({
      user: await getUserFromToken(req.headers.authorization)
    })
  })
);

httpServer.listen(4000, () => {
  console.log('Server ready at http://localhost:4000/graphql');
});
```

### Client Subscription

```javascript
// client.js with WebSocket
import { ApolloClient, InMemoryCache, split, HttpLink } from '@apollo/client';
import { GraphQLWsLink } from '@apollo/client/link/subscriptions';
import { getMainDefinition } from '@apollo/client/utilities';
import { createClient } from 'graphql-ws';

const httpLink = new HttpLink({
  uri: 'http://localhost:4000/graphql'
});

const wsLink = new GraphQLWsLink(
  createClient({
    url: 'ws://localhost:4000/graphql',
    connectionParams: () => ({
      authToken: localStorage.getItem('token')
    })
  })
);

// Split based on operation type
const splitLink = split(
  ({ query }) => {
    const definition = getMainDefinition(query);
    return (
      definition.kind === 'OperationDefinition' &&
      definition.operation === 'subscription'
    );
  },
  wsLink,
  httpLink
);

const client = new ApolloClient({
  link: splitLink,
  cache: new InMemoryCache()
});

// Use subscription in component
import { useSubscription, gql } from '@apollo/client';

const POST_CREATED = gql`
  subscription PostCreated {
    postCreated {
      id
      title
      content
      author {
        id
        name
      }
    }
  }
`;

function RealtimePosts() {
  const { data, loading } = useSubscription(POST_CREATED, {
    onData: ({ data }) => {
      console.log('New post:', data.data.postCreated);
      // Show notification
      showNotification(`New post: ${data.data.postCreated.title}`);
    }
  });

  return <div>Listening for new posts...</div>;
}
```

## Type Safety with TypeScript

### Code Generation

```bash
# Install codegen
npm install --save-dev @graphql-codegen/cli @graphql-codegen/typescript @graphql-codegen/typescript-operations @graphql-codegen/typescript-react-apollo
```

```yaml
# codegen.yml
schema: http://localhost:4000/graphql
documents: 'src/**/*.{ts,tsx}'
generates:
  src/generated/graphql.ts:
    plugins:
      - typescript
      - typescript-operations
      - typescript-react-apollo
    config:
      withHooks: true
      withComponent: false
      withHOC: false
```

Generated types usage:
```typescript
// Fully typed queries and mutations
import { useGetUserQuery, useUpdateUserMutation } from './generated/graphql';

function UserProfile({ userId }: { userId: string }) {
  // Typed query
  const { data, loading, error } = useGetUserQuery({
    variables: { id: userId }
  });

  // Typed mutation
  const [updateUser] = useUpdateUserMutation({
    variables: {
      id: userId,
      input: { name: 'New Name' }
    }
  });

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error!</div>;

  // TypeScript knows the exact shape of data
  return <div>{data?.user.name}</div>;
}
```

## Authentication & Authorization

### JWT Authentication

```javascript
// context.js
import jwt from 'jsonwebtoken';

export const context = async ({ req }) => {
  const token = req.headers.authorization?.replace('Bearer ', '');

  if (!token) {
    return { user: null };
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    const user = await db.users.findById(decoded.userId);
    return { user };
  } catch (err) {
    return { user: null };
  }
};

// Directive-based authorization
import { mapSchema, getDirective, MapperKind } from '@graphql-tools/utils';
import { defaultFieldResolver } from 'graphql';

function authDirective(directiveName = 'auth') {
  return {
    authDirectiveTypeDefs: `directive @${directiveName}(requires: Role) on FIELD_DEFINITION`,
    authDirectiveTransformer: (schema) =>
      mapSchema(schema, {
        [MapperKind.OBJECT_FIELD]: (fieldConfig) => {
          const authDirective = getDirective(schema, fieldConfig, directiveName)?.[0];

          if (authDirective) {
            const { requires } = authDirective;
            const { resolve = defaultFieldResolver } = fieldConfig;

            fieldConfig.resolve = async function (source, args, context, info) {
              if (!context.user) {
                throw new GraphQLError('Not authenticated', {
                  extensions: { code: 'UNAUTHENTICATED' }
                });
              }

              if (requires && context.user.role !== requires) {
                throw new GraphQLError('Not authorized', {
                  extensions: { code: 'FORBIDDEN' }
                });
              }

              return resolve(source, args, context, info);
            };
          }

          return fieldConfig;
        }
      })
  };
}

// Usage in schema
const typeDefs = `
  type Mutation {
    deleteUser(id: ID!): Boolean! @auth(requires: ADMIN)
    updatePost(id: ID!, input: UpdatePostInput!): Post! @auth
  }
`;
```

## Caching Strategies

### DataLoader for N+1 Prevention

```javascript
import DataLoader from 'dataloader';

// Create batched loader
const userLoader = new DataLoader(async (userIds) => {
  const users = await db.users.find({ _id: { $in: userIds } }).toArray();

  // Return in same order as requested
  return userIds.map(id => users.find(user => user._id.equals(id)));
});

// Use in resolver
const resolvers = {
  Post: {
    author: (post, args, context) => {
      // Batches multiple requests into one database query
      return context.loaders.user.load(post.authorId);
    }
  }
};

// Add to context
const server = new ApolloServer({
  typeDefs,
  resolvers,
  context: () => ({
    loaders: {
      user: new DataLoader(batchGetUsers),
      post: new DataLoader(batchGetPosts)
    }
  })
});
```

### Cache Control

```javascript
// Set cache hints
const resolvers = {
  Query: {
    user: (parent, { id }, context, info) => {
      info.cacheControl.setCacheHint({ maxAge: 60, scope: 'PRIVATE' });
      return context.dataSources.userAPI.getUser(id);
    },

    posts: (parent, args, context, info) => {
      info.cacheControl.setCacheHint({ maxAge: 300, scope: 'PUBLIC' });
      return context.dataSources.postAPI.getPosts(args);
    }
  }
};
```

## Production Best Practices

### Error Handling

```javascript
import { GraphQLError } from 'graphql';

// Custom error classes
class NotFoundError extends GraphQLError {
  constructor(message, resource) {
    super(message, {
      extensions: {
        code: 'NOT_FOUND',
        resource,
        timestamp: new Date().toISOString()
      }
    });
  }
}

class ValidationError extends GraphQLError {
  constructor(message, field) {
    super(message, {
      extensions: {
        code: 'BAD_USER_INPUT',
        field,
        timestamp: new Date().toISOString()
      }
    });
  }
}

// Use in resolvers
const resolvers = {
  Query: {
    user: async (parent, { id }, context) => {
      const user = await context.dataSources.userAPI.getUser(id);
      if (!user) {
        throw new NotFoundError(`User with id ${id} not found`, 'User');
      }
      return user;
    }
  }
};

// Format errors
const server = new ApolloServer({
  typeDefs,
  resolvers,
  formatError: (formattedError, error) => {
    // Log errors
    logger.error('GraphQL Error:', {
      message: error.message,
      code: formattedError.extensions?.code,
      path: formattedError.path,
      stack: error.stack
    });

    // Don't expose internal errors to clients
    if (formattedError.extensions?.code === 'INTERNAL_SERVER_ERROR') {
      return {
        message: 'Internal server error',
        extensions: { code: 'INTERNAL_SERVER_ERROR' }
      };
    }

    return formattedError;
  }
});
```

### Rate Limiting

```javascript
import { RateLimiterMemory } from 'rate-limiter-flexible';

const rateLimiter = new RateLimiterMemory({
  points: 100, // Number of requests
  duration: 60  // Per 60 seconds
});

const server = new ApolloServer({
  typeDefs,
  resolvers,
  plugins: [
    {
      async requestDidStart({ request, contextValue }) {
        const key = contextValue.user?.id || contextValue.ip;

        try {
          await rateLimiter.consume(key);
        } catch (err) {
          throw new GraphQLError('Rate limit exceeded', {
            extensions: { code: 'RATE_LIMIT_EXCEEDED' }
          });
        }
      }
    }
  ]
});
```

### Query Complexity

```javascript
import { getComplexity, simpleEstimator, fieldExtensionsEstimator } from 'graphql-query-complexity';

const server = new ApolloServer({
  typeDefs,
  resolvers,
  plugins: [
    {
      requestDidStart: () => ({
        didResolveOperation({ request, document }) {
          const complexity = getComplexity({
            schema,
            operationName: request.operationName,
            query: document,
            variables: request.variables,
            estimators: [
              fieldExtensionsEstimator(),
              simpleEstimator({ defaultComplexity: 1 })
            ]
          });

          if (complexity > 1000) {
            throw new GraphQLError('Query is too complex', {
              extensions: {
                code: 'COMPLEXITY_LIMIT_EXCEEDED',
                complexity
              }
            });
          }
        }
      })
    }
  ]
});
```

## Testing GraphQL APIs

### Unit Testing Resolvers

```javascript
import { describe, it, expect, vi } from 'vitest';

describe('User Resolvers', () => {
  it('should get user by id', async () => {
    const mockUserAPI = {
      getUser: vi.fn().mockResolvedValue({
        id: '1',
        name: 'Test User',
        email: 'test@example.com'
      })
    };

    const result = await resolvers.Query.user(
      {},
      { id: '1' },
      { dataSources: { userAPI: mockUserAPI } }
    );

    expect(mockUserAPI.getUser).toHaveBeenCalledWith('1');
    expect(result).toEqual({
      id: '1',
      name: 'Test User',
      email: 'test@example.com'
    });
  });

  it('should throw error when not authenticated', async () => {
    await expect(
      resolvers.Query.me({}, {}, { user: null })
    ).rejects.toThrow('Not authenticated');
  });
});
```

### Integration Testing

```javascript
import { ApolloServer } from '@apollo/server';
import assert from 'assert';

describe('GraphQL Integration', () => {
  let server;

  beforeAll(() => {
    server = new ApolloServer({ typeDefs, resolvers });
  });

  it('should create and query user', async () => {
    // Create user
    const createResponse = await server.executeOperation({
      query: `
        mutation CreateUser($input: CreateUserInput!) {
          createUser(input: $input) {
            id
            name
            email
          }
        }
      `,
      variables: {
        input: {
          name: 'Test User',
          email: 'test@example.com',
          password: 'password123'
        }
      }
    });

    assert(createResponse.body.kind === 'single');
    const userId = createResponse.body.singleResult.data.createUser.id;

    // Query user
    const queryResponse = await server.executeOperation({
      query: `
        query GetUser($id: ID!) {
          user(id: $id) {
            id
            name
            email
          }
        }
      `,
      variables: { id: userId }
    });

    assert(queryResponse.body.kind === 'single');
    expect(queryResponse.body.singleResult.data.user).toEqual({
      id: userId,
      name: 'Test User',
      email: 'test@example.com'
    });
  });
});
```

## Common Patterns

### Cursor-Based Pagination

```graphql
type Query {
  posts(first: Int, after: String, last: Int, before: String): PostConnection!
}

type PostConnection {
  edges: [PostEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PostEdge {
  cursor: String!
  node: Post!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
```

```javascript
const resolvers = {
  Query: {
    posts: async (parent, { first, after, last, before }, context) => {
      const limit = first || last || 10;
      const cursor = after || before;

      const posts = await context.dataSources.postAPI.getPosts({
        limit: limit + 1,
        cursor,
        direction: before ? 'before' : 'after'
      });

      const hasMore = posts.length > limit;
      const items = hasMore ? posts.slice(0, limit) : posts;

      return {
        edges: items.map(post => ({
          cursor: post.id,
          node: post
        })),
        pageInfo: {
          hasNextPage: hasMore && !before,
          hasPreviousPage: hasMore && !!before,
          startCursor: items[0]?.id,
          endCursor: items[items.length - 1]?.id
        },
        totalCount: await context.dataSources.postAPI.count()
      };
    }
  }
};
```

## Additional Resources

- GraphQL official docs: https://graphql.org/learn/
- Apollo Server docs: https://www.apollographql.com/docs/apollo-server/
- Apollo Client docs: https://www.apollographql.com/docs/react/
- GraphQL best practices: https://graphql.org/learn/best-practices/
- TypeScript + GraphQL: https://the-guild.dev/graphql/codegen
