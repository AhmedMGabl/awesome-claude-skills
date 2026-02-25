---
name: redux-toolkit
description: Redux Toolkit state management covering store configuration with configureStore, slice creation with createSlice, async operations with createAsyncThunk, data fetching with RTK Query, entity adapters for normalized state, TypeScript typing patterns, and testing strategies for slices and thunks.
---

# Redux Toolkit

This skill should be used when building or maintaining Redux-based state management in React applications. It covers the full Redux Toolkit (RTK) ecosystem: store setup, slices, async thunks, RTK Query for data fetching, entity adapters, TypeScript integration, middleware configuration, and testing patterns.

## When to Use This Skill

Use this skill when you need to:

- Configure a Redux store with `configureStore`
- Create feature slices with `createSlice` and manage reducers
- Handle async operations with `createAsyncThunk`
- Set up data fetching and caching with RTK Query (`createApi`)
- Normalize entity state with `createEntityAdapter`
- Apply TypeScript typing patterns for `RootState`, `AppDispatch`, and typed hooks
- Configure custom middleware alongside Redux defaults
- Write tests for slices, thunks, and RTK Query endpoints

## Project Setup

```bash
# New project with Vite
npm create vite@latest my-app -- --template react-ts
cd my-app

# Install Redux Toolkit and React-Redux
npm install @reduxjs/toolkit react-redux

# For testing
npm install -D vitest @testing-library/react @testing-library/user-event jsdom msw
```

### Recommended Project Structure

```
src/
├── app/
│   ├── store.ts              # Store configuration
│   └── hooks.ts              # Typed hooks (useAppDispatch, useAppSelector)
├── features/
│   ├── auth/
│   │   ├── authSlice.ts      # Slice + thunks
│   │   ├── authApi.ts        # RTK Query API (optional)
│   │   └── authSlice.test.ts
│   ├── users/
│   │   ├── usersSlice.ts
│   │   ├── usersApi.ts
│   │   └── usersSlice.test.ts
│   └── posts/
│       ├── postsSlice.ts
│       └── postsSlice.test.ts
├── services/
│   └── api.ts                # RTK Query base API definition
└── main.tsx
```

## Store Configuration

### Basic Store Setup

```typescript
// src/app/store.ts
import { configureStore } from "@reduxjs/toolkit";
import authReducer from "../features/auth/authSlice";
import usersReducer from "../features/users/usersSlice";
import postsReducer from "../features/posts/postsSlice";
import { apiSlice } from "../services/api";

export const store = configureStore({
  reducer: {
    auth: authReducer,
    users: usersReducer,
    posts: postsReducer,
    [apiSlice.reducerPath]: apiSlice.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(apiSlice.middleware),
  devTools: process.env.NODE_ENV !== "production",
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

### Provider Setup

```tsx
// src/main.tsx
import React from "react";
import ReactDOM from "react-dom/client";
import { Provider } from "react-redux";
import { store } from "./app/store";
import App from "./App";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>
);
```

### Typed Hooks

```typescript
// src/app/hooks.ts
import { useDispatch, useSelector } from "react-redux";
import type { RootState, AppDispatch } from "./store";

// Typed versions of useDispatch and useSelector — use these throughout the app
export const useAppDispatch = useDispatch.withTypes<AppDispatch>();
export const useAppSelector = useSelector.withTypes<RootState>();
```

## Creating Slices with createSlice

### Basic Slice

```typescript
// src/features/counter/counterSlice.ts
import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

interface CounterState {
  value: number;
  step: number;
}

const initialState: CounterState = {
  value: 0,
  step: 1,
};

const counterSlice = createSlice({
  name: "counter",
  initialState,
  reducers: {
    increment(state) {
      state.value += state.step;
    },
    decrement(state) {
      state.value -= state.step;
    },
    incrementByAmount(state, action: PayloadAction<number>) {
      state.value += action.payload;
    },
    setStep(state, action: PayloadAction<number>) {
      state.step = action.payload;
    },
    reset() {
      return initialState;
    },
  },
});

export const { increment, decrement, incrementByAmount, setStep, reset } =
  counterSlice.actions;

export default counterSlice.reducer;
```

### Feature Slice with Prepare Callbacks

```typescript
// src/features/notifications/notificationsSlice.ts
import { createSlice, type PayloadAction, nanoid } from "@reduxjs/toolkit";

type NotificationType = "success" | "error" | "warning" | "info";

interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  timestamp: number;
  read: boolean;
}

interface NotificationsState {
  items: Notification[];
  unreadCount: number;
}

const initialState: NotificationsState = {
  items: [],
  unreadCount: 0,
};

const notificationsSlice = createSlice({
  name: "notifications",
  initialState,
  reducers: {
    // Prepare callback to generate id and timestamp before reaching the reducer
    addNotification: {
      reducer(state, action: PayloadAction<Notification>) {
        state.items.unshift(action.payload);
        state.unreadCount += 1;
      },
      prepare(type: NotificationType, title: string, message: string) {
        return {
          payload: {
            id: nanoid(),
            type,
            title,
            message,
            timestamp: Date.now(),
            read: false,
          },
        };
      },
    },
    markAsRead(state, action: PayloadAction<string>) {
      const notification = state.items.find((n) => n.id === action.payload);
      if (notification && !notification.read) {
        notification.read = true;
        state.unreadCount -= 1;
      }
    },
    markAllAsRead(state) {
      state.items.forEach((n) => {
        n.read = true;
      });
      state.unreadCount = 0;
    },
    removeNotification(state, action: PayloadAction<string>) {
      const index = state.items.findIndex((n) => n.id === action.payload);
      if (index !== -1) {
        if (!state.items[index].read) {
          state.unreadCount -= 1;
        }
        state.items.splice(index, 1);
      }
    },
    clearAll() {
      return initialState;
    },
  },
});

export const {
  addNotification,
  markAsRead,
  markAllAsRead,
  removeNotification,
  clearAll,
} = notificationsSlice.actions;

// Selectors
export const selectAllNotifications = (state: { notifications: NotificationsState }) =>
  state.notifications.items;
export const selectUnreadCount = (state: { notifications: NotificationsState }) =>
  state.notifications.unreadCount;

export default notificationsSlice.reducer;
```

## Async Thunks with createAsyncThunk

### Basic Async Thunk

```typescript
// src/features/users/usersSlice.ts
import {
  createSlice,
  createAsyncThunk,
  type PayloadAction,
} from "@reduxjs/toolkit";
import type { RootState } from "../../app/store";

interface User {
  id: number;
  name: string;
  email: string;
  role: "admin" | "user";
}

interface UsersState {
  items: User[];
  selectedUser: User | null;
  status: "idle" | "loading" | "succeeded" | "failed";
  error: string | null;
}

const initialState: UsersState = {
  items: [],
  selectedUser: null,
  status: "idle",
  error: null,
};

// Async thunk for fetching users
export const fetchUsers = createAsyncThunk(
  "users/fetchUsers",
  async (_, { rejectWithValue }) => {
    try {
      const response = await fetch("/api/users");
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return (await response.json()) as User[];
    } catch (error) {
      return rejectWithValue(
        error instanceof Error ? error.message : "Failed to fetch users"
      );
    }
  }
);

// Async thunk with arguments
export const fetchUserById = createAsyncThunk(
  "users/fetchUserById",
  async (userId: number, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/users/${userId}`);
      if (!response.ok) {
        throw new Error("User not found");
      }
      return (await response.json()) as User;
    } catch (error) {
      return rejectWithValue(
        error instanceof Error ? error.message : "Failed to fetch user"
      );
    }
  }
);

// Async thunk that accesses state and dispatch
export const createUser = createAsyncThunk(
  "users/createUser",
  async (
    userData: Omit<User, "id">,
    { getState, dispatch, rejectWithValue }
  ) => {
    const state = getState() as RootState;
    const token = state.auth.token;

    try {
      const response = await fetch("/api/users", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        return rejectWithValue(errorData.message ?? "Failed to create user");
      }

      const newUser = (await response.json()) as User;

      // Dispatch another action after success
      dispatch(
        addNotification("success", "User Created", `${newUser.name} was added.`)
      );

      return newUser;
    } catch (error) {
      return rejectWithValue("Network error");
    }
  }
);

// Conditional thunk — skip fetching if data is already loaded
export const fetchUsersIfNeeded = createAsyncThunk(
  "users/fetchUsersIfNeeded",
  async (_, { dispatch }) => {
    return dispatch(fetchUsers()).unwrap();
  },
  {
    condition: (_, { getState }) => {
      const { users } = getState() as RootState;
      // Skip if already loading or loaded
      return users.status === "idle";
    },
  }
);

const usersSlice = createSlice({
  name: "users",
  initialState,
  reducers: {
    clearSelectedUser(state) {
      state.selectedUser = null;
    },
    clearError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // fetchUsers
      .addCase(fetchUsers.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.items = action.payload;
      })
      .addCase(fetchUsers.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload as string;
      })
      // fetchUserById
      .addCase(fetchUserById.fulfilled, (state, action) => {
        state.selectedUser = action.payload;
      })
      // createUser
      .addCase(createUser.fulfilled, (state, action) => {
        state.items.push(action.payload);
      });
  },
});

export const { clearSelectedUser, clearError } = usersSlice.actions;

// Selectors
export const selectAllUsers = (state: RootState) => state.users.items;
export const selectUserById = (state: RootState, userId: number) =>
  state.users.items.find((user) => user.id === userId);
export const selectUsersStatus = (state: RootState) => state.users.status;
export const selectUsersError = (state: RootState) => state.users.error;

export default usersSlice.reducer;
```

### Using Thunks in Components

```tsx
// src/features/users/UsersList.tsx
import { useEffect } from "react";
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import {
  fetchUsers,
  selectAllUsers,
  selectUsersStatus,
  selectUsersError,
} from "./usersSlice";

export function UsersList() {
  const dispatch = useAppDispatch();
  const users = useAppSelector(selectAllUsers);
  const status = useAppSelector(selectUsersStatus);
  const error = useAppSelector(selectUsersError);

  useEffect(() => {
    if (status === "idle") {
      dispatch(fetchUsers());
    }
  }, [status, dispatch]);

  if (status === "loading") return <div>Loading users...</div>;
  if (status === "failed") return <div>Error: {error}</div>;

  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>
          {user.name} ({user.email})
        </li>
      ))}
    </ul>
  );
}
```

## RTK Query for Data Fetching

### Base API Definition

```typescript
// src/services/api.ts
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { RootState } from "../app/store";

export const apiSlice = createApi({
  reducerPath: "api",
  baseQuery: fetchBaseQuery({
    baseUrl: "/api",
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token;
      if (token) {
        headers.set("Authorization", `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ["User", "Post", "Comment"],
  endpoints: () => ({}), // Endpoints injected from feature slices
});
```

### Injecting Endpoints

```typescript
// src/features/users/usersApi.ts
import { apiSlice } from "../../services/api";

interface User {
  id: number;
  name: string;
  email: string;
  role: "admin" | "user";
}

interface UsersResponse {
  users: User[];
  total: number;
  page: number;
}

interface GetUsersParams {
  page?: number;
  limit?: number;
  search?: string;
}

export const usersApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    // GET /api/users
    getUsers: builder.query<UsersResponse, GetUsersParams | void>({
      query: (params) => ({
        url: "/users",
        params: params ?? undefined,
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.users.map(({ id }) => ({
                type: "User" as const,
                id,
              })),
              { type: "User", id: "LIST" },
            ]
          : [{ type: "User", id: "LIST" }],
    }),

    // GET /api/users/:id
    getUserById: builder.query<User, number>({
      query: (id) => `/users/${id}`,
      providesTags: (_result, _error, id) => [{ type: "User", id }],
    }),

    // POST /api/users
    createUser: builder.mutation<User, Omit<User, "id">>({
      query: (body) => ({
        url: "/users",
        method: "POST",
        body,
      }),
      invalidatesTags: [{ type: "User", id: "LIST" }],
    }),

    // PUT /api/users/:id
    updateUser: builder.mutation<User, Pick<User, "id"> & Partial<User>>({
      query: ({ id, ...patch }) => ({
        url: `/users/${id}`,
        method: "PUT",
        body: patch,
      }),
      invalidatesTags: (_result, _error, { id }) => [{ type: "User", id }],
    }),

    // DELETE /api/users/:id
    deleteUser: builder.mutation<void, number>({
      query: (id) => ({
        url: `/users/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: (_result, _error, id) => [
        { type: "User", id },
        { type: "User", id: "LIST" },
      ],
    }),
  }),
});

export const {
  useGetUsersQuery,
  useGetUserByIdQuery,
  useCreateUserMutation,
  useUpdateUserMutation,
  useDeleteUserMutation,
} = usersApi;
```

### Using RTK Query Hooks in Components

```tsx
// src/features/users/UsersPage.tsx
import {
  useGetUsersQuery,
  useCreateUserMutation,
  useDeleteUserMutation,
} from "./usersApi";
import { useState } from "react";

export function UsersPage() {
  const [page, setPage] = useState(1);

  // Query hook — auto-fetches, caches, and re-renders
  const {
    data,
    isLoading,
    isFetching,
    isError,
    error,
    refetch,
  } = useGetUsersQuery({ page, limit: 10 });

  // Mutation hooks
  const [createUser, { isLoading: isCreating }] = useCreateUserMutation();
  const [deleteUser] = useDeleteUserMutation();

  const handleCreate = async () => {
    try {
      const newUser = await createUser({
        name: "New User",
        email: "new@example.com",
        role: "user",
      }).unwrap();
      console.log("Created:", newUser);
    } catch (err) {
      console.error("Failed to create user:", err);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteUser(id).unwrap();
    } catch (err) {
      console.error("Failed to delete user:", err);
    }
  };

  if (isLoading) return <div>Loading...</div>;
  if (isError) return <div>Error: {JSON.stringify(error)}</div>;

  return (
    <div>
      <h1>Users {isFetching && <span>(refreshing...)</span>}</h1>

      <button onClick={handleCreate} disabled={isCreating}>
        {isCreating ? "Creating..." : "Add User"}
      </button>
      <button onClick={refetch}>Refresh</button>

      <ul>
        {data?.users.map((user) => (
          <li key={user.id}>
            {user.name} - {user.email}
            <button onClick={() => handleDelete(user.id)}>Delete</button>
          </li>
        ))}
      </ul>

      <div>
        <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}>
          Previous
        </button>
        <span>Page {page}</span>
        <button onClick={() => setPage((p) => p + 1)}>Next</button>
      </div>
    </div>
  );
}
```

### RTK Query with Optimistic Updates

```typescript
// Optimistic update for a mutation
updateUser: builder.mutation<User, Pick<User, "id"> & Partial<User>>({
  query: ({ id, ...patch }) => ({
    url: `/users/${id}`,
    method: "PUT",
    body: patch,
  }),
  async onQueryStarted({ id, ...patch }, { dispatch, queryFulfilled }) {
    // Optimistically update the cache
    const patchResult = dispatch(
      usersApi.util.updateQueryData("getUserById", id, (draft) => {
        Object.assign(draft, patch);
      })
    );
    try {
      await queryFulfilled;
    } catch {
      // Revert the optimistic update on failure
      patchResult.undo();
    }
  },
  invalidatesTags: (_result, _error, { id }) => [{ type: "User", id }],
}),
```

### RTK Query with Transforming Responses

```typescript
// Transform API response shape before caching
getPosts: builder.query<Post[], void>({
  query: () => "/posts",
  transformResponse: (response: { data: Post[]; meta: unknown }) =>
    response.data,
  transformErrorResponse: (response) => ({
    status: response.status,
    message:
      typeof response.data === "object" && response.data !== null && "message" in response.data
        ? (response.data as { message: string }).message
        : "An error occurred",
  }),
  providesTags: ["Post"],
}),
```

## Entity Adapters for Normalized State

### Setting Up an Entity Adapter

```typescript
// src/features/posts/postsSlice.ts
import {
  createSlice,
  createAsyncThunk,
  createEntityAdapter,
  type PayloadAction,
  type EntityState,
} from "@reduxjs/toolkit";
import type { RootState } from "../../app/store";

interface Post {
  id: string;
  title: string;
  body: string;
  authorId: number;
  createdAt: string;
  reactions: { thumbsUp: number; heart: number };
}

// Create the entity adapter — manages normalized { ids: [], entities: {} } state
const postsAdapter = createEntityAdapter<Post>({
  // Sort posts by creation date (newest first)
  sortComparer: (a, b) => b.createdAt.localeCompare(a.createdAt),
});

// Adapter provides getInitialState() with ids[] and entities{}
interface PostsExtraState {
  status: "idle" | "loading" | "succeeded" | "failed";
  error: string | null;
}

const initialState = postsAdapter.getInitialState<PostsExtraState>({
  status: "idle",
  error: null,
});

export const fetchPosts = createAsyncThunk("posts/fetchPosts", async () => {
  const response = await fetch("/api/posts");
  return (await response.json()) as Post[];
});

export const addNewPost = createAsyncThunk(
  "posts/addNewPost",
  async (post: Omit<Post, "id" | "createdAt" | "reactions">) => {
    const response = await fetch("/api/posts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(post),
    });
    return (await response.json()) as Post;
  }
);

const postsSlice = createSlice({
  name: "posts",
  initialState,
  reducers: {
    // Adapter CRUD methods as reducers
    postUpdated: postsAdapter.updateOne,
    postRemoved: postsAdapter.removeOne,
    reactionAdded(
      state,
      action: PayloadAction<{ postId: string; reaction: keyof Post["reactions"] }>
    ) {
      const { postId, reaction } = action.payload;
      const post = state.entities[postId];
      if (post) {
        post.reactions[reaction] += 1;
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchPosts.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchPosts.fulfilled, (state, action) => {
        state.status = "succeeded";
        // Use adapter method to set all entities at once
        postsAdapter.setAll(state, action.payload);
      })
      .addCase(fetchPosts.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message ?? "Failed to fetch posts";
      })
      .addCase(addNewPost.fulfilled, postsAdapter.addOne);
  },
});

export const { postUpdated, postRemoved, reactionAdded } = postsSlice.actions;

// Entity adapter provides pre-built selectors
export const {
  selectAll: selectAllPosts,
  selectById: selectPostById,
  selectIds: selectPostIds,
  selectTotal: selectTotalPosts,
} = postsAdapter.getSelectors<RootState>((state) => state.posts);

// Custom selectors composed with adapter selectors
export const selectPostsByAuthor = (state: RootState, authorId: number) =>
  selectAllPosts(state).filter((post) => post.authorId === authorId);

export default postsSlice.reducer;
```

### Entity Adapter CRUD Methods Reference

```typescript
// All adapter methods available:
postsAdapter.addOne(state, post);          // Add one entity
postsAdapter.addMany(state, posts);        // Add multiple entities
postsAdapter.setOne(state, post);          // Add or replace one entity
postsAdapter.setMany(state, posts);        // Add or replace multiple entities
postsAdapter.setAll(state, posts);         // Replace all entities
postsAdapter.updateOne(state, { id, changes });   // Update one entity
postsAdapter.updateMany(state, updates);   // Update multiple entities
postsAdapter.upsertOne(state, post);       // Add or update one entity
postsAdapter.upsertMany(state, posts);     // Add or update multiple entities
postsAdapter.removeOne(state, id);         // Remove one entity
postsAdapter.removeMany(state, ids);       // Remove multiple entities
postsAdapter.removeAll(state);             // Remove all entities
```

## TypeScript Typing Patterns

### Typing the Store

```typescript
// src/app/store.ts
import { configureStore } from "@reduxjs/toolkit";

export const store = configureStore({
  reducer: {
    // ...reducers
  },
});

// Infer RootState and AppDispatch from the store itself
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

### Typed Hooks (Recommended Approach)

```typescript
// src/app/hooks.ts
import { useDispatch, useSelector } from "react-redux";
import type { RootState, AppDispatch } from "./store";

// Use these typed hooks in components instead of plain useDispatch/useSelector
export const useAppDispatch = useDispatch.withTypes<AppDispatch>();
export const useAppSelector = useSelector.withTypes<RootState>();
```

### Typing createAsyncThunk

```typescript
import { createAsyncThunk } from "@reduxjs/toolkit";
import type { RootState, AppDispatch } from "../app/store";

// Typed thunkAPI for accessing state and dispatch
interface ThunkApiConfig {
  state: RootState;
  dispatch: AppDispatch;
  rejectValue: string;
  extra: { apiClient: ApiClient }; // Extra argument passed to thunk middleware
}

export const fetchUserProfile = createAsyncThunk<
  User,           // Return type
  number,         // Argument type
  ThunkApiConfig  // ThunkAPI config
>("users/fetchProfile", async (userId, { getState, rejectWithValue, extra }) => {
  const token = getState().auth.token;
  try {
    return await extra.apiClient.get<User>(`/users/${userId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  } catch (error) {
    return rejectWithValue("Failed to fetch profile");
  }
});
```

### Typing Selectors with createSelector

```typescript
import { createSelector } from "@reduxjs/toolkit";
import type { RootState } from "../app/store";

// Memoized selector — only recomputes when inputs change
export const selectActiveUsers = createSelector(
  [(state: RootState) => state.users.items],
  (users) => users.filter((user) => user.role === "admin")
);

// Parameterized selector factory
export const selectUsersByRole = (role: string) =>
  createSelector(
    [(state: RootState) => state.users.items],
    (users) => users.filter((user) => user.role === role)
  );

// Composing selectors
export const selectActiveUserCount = createSelector(
  [selectActiveUsers],
  (activeUsers) => activeUsers.length
);
```

## Middleware Configuration

### Adding Custom Middleware

```typescript
// src/app/store.ts
import { configureStore, type Middleware } from "@reduxjs/toolkit";

// Custom logging middleware
const loggerMiddleware: Middleware = (storeAPI) => (next) => (action) => {
  console.log("Dispatching:", action);
  const result = next(action);
  console.log("Next state:", storeAPI.getState());
  return result;
};

// Error reporting middleware
const errorMiddleware: Middleware = (_storeAPI) => (next) => (action) => {
  try {
    return next(action);
  } catch (err) {
    console.error("Caught an exception in middleware:", err);
    throw err;
  }
};

export const store = configureStore({
  reducer: {
    // ...reducers
    [apiSlice.reducerPath]: apiSlice.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore specific action paths for non-serializable values
        ignoredActions: ["auth/setCredentials"],
        ignoredPaths: ["auth.expiresAt"],
      },
      thunk: {
        extraArgument: { apiClient }, // Accessible via thunkAPI.extra
      },
    })
      .concat(apiSlice.middleware)
      .concat(loggerMiddleware)
      .concat(errorMiddleware),
});
```

### Listener Middleware (Side Effects)

```typescript
// src/app/listenerMiddleware.ts
import { createListenerMiddleware, addListener } from "@reduxjs/toolkit";
import type { RootState, AppDispatch } from "./store";

export const listenerMiddleware = createListenerMiddleware();

// Typed versions for convenience
export const startAppListening = listenerMiddleware.startListening.withTypes<
  RootState,
  AppDispatch
>();

// React to auth changes
startAppListening({
  predicate: (_action, currentState, previousState) =>
    currentState.auth.token !== previousState.auth.token,
  effect: async (_action, listenerApi) => {
    const token = listenerApi.getState().auth.token;
    if (token) {
      // Token changed — refetch user data
      listenerApi.dispatch(fetchUserProfile());
    } else {
      // Token cleared — clean up
      listenerApi.dispatch(apiSlice.util.resetApiState());
    }
  },
});

// Debounced search
startAppListening({
  actionCreator: setSearchQuery,
  effect: async (action, listenerApi) => {
    // Cancel any pending search
    listenerApi.cancelActiveListeners();

    // Debounce 300ms
    await listenerApi.delay(300);

    // Dispatch search
    listenerApi.dispatch(searchUsers(action.payload));
  },
});

// Add to store
export const store = configureStore({
  reducer: { /* ... */ },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware()
      .prepend(listenerMiddleware.middleware)
      .concat(apiSlice.middleware),
});
```

## Authentication Slice (Real-World Example)

```typescript
// src/features/auth/authSlice.ts
import { createSlice, createAsyncThunk, type PayloadAction } from "@reduxjs/toolkit";
import type { RootState } from "../../app/store";

interface AuthUser {
  id: number;
  name: string;
  email: string;
  role: "admin" | "user";
}

interface AuthState {
  user: AuthUser | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  status: "idle" | "loading" | "succeeded" | "failed";
  error: string | null;
}

const initialState: AuthState = {
  user: null,
  token: localStorage.getItem("token"),
  refreshToken: localStorage.getItem("refreshToken"),
  isAuthenticated: !!localStorage.getItem("token"),
  status: "idle",
  error: null,
};

export const login = createAsyncThunk<
  { user: AuthUser; token: string; refreshToken: string },
  { email: string; password: string },
  { rejectValue: string }
>("auth/login", async (credentials, { rejectWithValue }) => {
  try {
    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const data = await response.json();
      return rejectWithValue(data.message ?? "Invalid credentials");
    }

    const data = await response.json();
    localStorage.setItem("token", data.token);
    localStorage.setItem("refreshToken", data.refreshToken);
    return data;
  } catch {
    return rejectWithValue("Network error. Please try again.");
  }
});

export const refreshAccessToken = createAsyncThunk<
  { token: string },
  void,
  { state: RootState; rejectValue: string }
>("auth/refreshToken", async (_, { getState, rejectWithValue }) => {
  const refreshToken = getState().auth.refreshToken;
  if (!refreshToken) return rejectWithValue("No refresh token");

  try {
    const response = await fetch("/api/auth/refresh", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refreshToken }),
    });

    if (!response.ok) return rejectWithValue("Token refresh failed");

    const data = await response.json();
    localStorage.setItem("token", data.token);
    return data;
  } catch {
    return rejectWithValue("Network error");
  }
});

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    logout(state) {
      state.user = null;
      state.token = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
      state.status = "idle";
      state.error = null;
      localStorage.removeItem("token");
      localStorage.removeItem("refreshToken");
    },
    clearAuthError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.user = action.payload.user;
        state.token = action.payload.token;
        state.refreshToken = action.payload.refreshToken;
        state.isAuthenticated = true;
      })
      .addCase(login.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload ?? "Login failed";
        state.isAuthenticated = false;
      })
      .addCase(refreshAccessToken.fulfilled, (state, action) => {
        state.token = action.payload.token;
      })
      .addCase(refreshAccessToken.rejected, (state) => {
        // Refresh failed — force logout
        state.user = null;
        state.token = null;
        state.refreshToken = null;
        state.isAuthenticated = false;
        localStorage.removeItem("token");
        localStorage.removeItem("refreshToken");
      });
  },
});

export const { logout, clearAuthError } = authSlice.actions;

export const selectCurrentUser = (state: RootState) => state.auth.user;
export const selectIsAuthenticated = (state: RootState) => state.auth.isAuthenticated;
export const selectAuthToken = (state: RootState) => state.auth.token;
export const selectAuthStatus = (state: RootState) => state.auth.status;
export const selectAuthError = (state: RootState) => state.auth.error;

export default authSlice.reducer;
```

## Testing Patterns

### Testing Slices (Reducer Logic)

```typescript
// src/features/counter/counterSlice.test.ts
import { describe, it, expect } from "vitest";
import counterReducer, {
  increment,
  decrement,
  incrementByAmount,
  setStep,
  reset,
} from "./counterSlice";

describe("counterSlice", () => {
  const initialState = { value: 0, step: 1 };

  it("should return the initial state", () => {
    expect(counterReducer(undefined, { type: "unknown" })).toEqual(initialState);
  });

  it("should handle increment", () => {
    const state = counterReducer(initialState, increment());
    expect(state.value).toBe(1);
  });

  it("should handle decrement", () => {
    const state = counterReducer({ value: 5, step: 1 }, decrement());
    expect(state.value).toBe(4);
  });

  it("should handle incrementByAmount", () => {
    const state = counterReducer(initialState, incrementByAmount(10));
    expect(state.value).toBe(10);
  });

  it("should use step for increment", () => {
    const stateWithStep = counterReducer(initialState, setStep(5));
    const afterIncrement = counterReducer(stateWithStep, increment());
    expect(afterIncrement.value).toBe(5);
  });

  it("should handle reset", () => {
    const modifiedState = { value: 42, step: 3 };
    const state = counterReducer(modifiedState, reset());
    expect(state).toEqual(initialState);
  });
});
```

### Testing Async Thunks

```typescript
// src/features/users/usersSlice.test.ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import { configureStore } from "@reduxjs/toolkit";
import usersReducer, { fetchUsers, createUser } from "./usersSlice";
import authReducer from "../auth/authSlice";

// Helper to create a test store
function createTestStore(preloadedState?: Record<string, unknown>) {
  return configureStore({
    reducer: {
      users: usersReducer,
      auth: authReducer,
    },
    preloadedState,
  });
}

describe("usersSlice async thunks", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  describe("fetchUsers", () => {
    it("should fetch users successfully", async () => {
      const mockUsers = [
        { id: 1, name: "Alice", email: "alice@test.com", role: "admin" as const },
        { id: 2, name: "Bob", email: "bob@test.com", role: "user" as const },
      ];

      vi.stubGlobal(
        "fetch",
        vi.fn().mockResolvedValue({
          ok: true,
          json: async () => mockUsers,
        })
      );

      const store = createTestStore();
      await store.dispatch(fetchUsers());

      const state = store.getState().users;
      expect(state.status).toBe("succeeded");
      expect(state.items).toEqual(mockUsers);
      expect(state.error).toBeNull();
    });

    it("should handle fetch failure", async () => {
      vi.stubGlobal(
        "fetch",
        vi.fn().mockResolvedValue({
          ok: false,
          status: 500,
          statusText: "Internal Server Error",
        })
      );

      const store = createTestStore();
      await store.dispatch(fetchUsers());

      const state = store.getState().users;
      expect(state.status).toBe("failed");
      expect(state.error).toBe("HTTP 500: Internal Server Error");
    });

    it("should handle network error", async () => {
      vi.stubGlobal(
        "fetch",
        vi.fn().mockRejectedValue(new Error("Network error"))
      );

      const store = createTestStore();
      await store.dispatch(fetchUsers());

      const state = store.getState().users;
      expect(state.status).toBe("failed");
      expect(state.error).toBe("Network error");
    });
  });

  describe("createUser", () => {
    it("should create a user and add to state", async () => {
      const newUser = { id: 3, name: "Charlie", email: "charlie@test.com", role: "user" as const };

      vi.stubGlobal(
        "fetch",
        vi.fn().mockResolvedValue({
          ok: true,
          json: async () => newUser,
        })
      );

      const store = createTestStore({
        auth: {
          user: null,
          token: "test-token",
          refreshToken: null,
          isAuthenticated: true,
          status: "idle",
          error: null,
        },
        users: {
          items: [],
          selectedUser: null,
          status: "succeeded",
          error: null,
        },
      });

      const result = await store.dispatch(
        createUser({ name: "Charlie", email: "charlie@test.com", role: "user" })
      );

      expect(result.type).toBe("users/createUser/fulfilled");
      expect(store.getState().users.items).toContainEqual(newUser);
    });
  });
});
```

### Testing RTK Query Endpoints

```typescript
// src/features/users/usersApi.test.ts
import { describe, it, expect, afterEach } from "vitest";
import { setupServer } from "msw/node";
import { http, HttpResponse } from "msw";
import { renderHook, waitFor } from "@testing-library/react";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { apiSlice } from "../../services/api";
import { useGetUsersQuery } from "./usersApi";
import type { ReactNode } from "react";

// Mock server with MSW
const mockUsers = [
  { id: 1, name: "Alice", email: "alice@test.com", role: "admin" },
  { id: 2, name: "Bob", email: "bob@test.com", role: "user" },
];

const server = setupServer(
  http.get("/api/users", () => {
    return HttpResponse.json({ users: mockUsers, total: 2, page: 1 });
  })
);

beforeAll(() => server.listen());
afterEach(() => {
  server.resetHandlers();
});
afterAll(() => server.close());

function createWrapper() {
  const store = configureStore({
    reducer: {
      [apiSlice.reducerPath]: apiSlice.reducer,
    },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(apiSlice.middleware),
  });

  return ({ children }: { children: ReactNode }) => (
    <Provider store={store}>{children}</Provider>
  );
}

describe("usersApi", () => {
  it("should fetch users", async () => {
    const { result } = renderHook(() => useGetUsersQuery(), {
      wrapper: createWrapper(),
    });

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data?.users).toHaveLength(2);
    expect(result.current.data?.users[0].name).toBe("Alice");
  });

  it("should handle server error", async () => {
    server.use(
      http.get("/api/users", () => {
        return HttpResponse.json(
          { message: "Internal server error" },
          { status: 500 }
        );
      })
    );

    const { result } = renderHook(() => useGetUsersQuery(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
  });
});
```

### Testing Components with Redux

```tsx
// src/features/users/UsersList.test.tsx
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { setupServer } from "msw/node";
import { http, HttpResponse } from "msw";
import usersReducer from "./usersSlice";
import { UsersList } from "./UsersList";

function renderWithStore(
  ui: React.ReactElement,
  preloadedState?: Record<string, unknown>
) {
  const store = configureStore({
    reducer: { users: usersReducer },
    preloadedState,
  });
  return render(<Provider store={store}>{ui}</Provider>);
}

describe("UsersList", () => {
  it("should show loading state initially", () => {
    renderWithStore(<UsersList />);
    expect(screen.getByText("Loading users...")).toBeInTheDocument();
  });

  it("should display users when loaded", () => {
    renderWithStore(<UsersList />, {
      users: {
        items: [
          { id: 1, name: "Alice", email: "alice@test.com", role: "admin" },
          { id: 2, name: "Bob", email: "bob@test.com", role: "user" },
        ],
        selectedUser: null,
        status: "succeeded",
        error: null,
      },
    });

    expect(screen.getByText(/Alice/)).toBeInTheDocument();
    expect(screen.getByText(/Bob/)).toBeInTheDocument();
  });

  it("should display error message on failure", () => {
    renderWithStore(<UsersList />, {
      users: {
        items: [],
        selectedUser: null,
        status: "failed",
        error: "Network error",
      },
    });

    expect(screen.getByText("Error: Network error")).toBeInTheDocument();
  });
});
```

## Additional Resources

- Redux Toolkit docs: https://redux-toolkit.js.org/
- RTK Query overview: https://redux-toolkit.js.org/rtk-query/overview
- Redux style guide: https://redux.js.org/style-guide/
- Redux TypeScript guide: https://redux.js.org/usage/usage-with-typescript
- Redux DevTools extension: https://github.com/reduxjs/redux-devtools
