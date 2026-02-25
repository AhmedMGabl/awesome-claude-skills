---
name: testing-library
description: This skill should be used when writing component and integration tests with React Testing Library or DOM Testing Library. It covers accessibility-first queries, user interaction simulation with userEvent, async testing patterns, custom render wrappers with providers, form and modal testing, hook testing with renderHook, and common anti-patterns to avoid.
---

# React Testing Library & DOM Testing Library

Comprehensive guide for writing maintainable, accessibility-driven component tests using React Testing Library and DOM Testing Library. All patterns target production codebases using TypeScript.

## When to Use This Skill

- Writing unit or integration tests for React components
- Querying rendered DOM elements by role, label, text, or test ID
- Simulating user interactions (clicks, typing, selection) with `userEvent`
- Testing asynchronous behavior (data fetching, lazy loading, debounced inputs)
- Setting up custom `render` wrappers with providers (router, theme, store, query client)
- Testing forms, modals, dropdowns, and other interactive UI
- Testing custom hooks with `renderHook`
- Reviewing or refactoring tests to follow accessibility-first query priorities

## Installation & Setup

```bash
npm install -D @testing-library/react @testing-library/jest-dom @testing-library/user-event @testing-library/dom
```

### Setup File (vitest.setup.ts or jest.setup.ts)

```typescript
import "@testing-library/jest-dom/vitest"; // or "@testing-library/jest-dom" for Jest
```

Register in the test runner config:

```typescript
// vitest.config.ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./vitest.setup.ts"],
  },
});
```

## Query Priority (Accessibility-First)

Queries are ranked by how closely they reflect the user experience. Always prefer the highest-priority query that applies.

### Priority 1 -- Accessible to Everyone

| Query | When to Use |
|---|---|
| `getByRole` | Buttons, headings, links, checkboxes, dialogs, textboxes -- any element with an ARIA role |
| `getByLabelText` | Form fields associated with a `<label>` |
| `getByPlaceholderText` | Form fields when no label exists (less ideal) |
| `getByText` | Non-interactive text content, paragraphs, spans |
| `getByDisplayValue` | Inputs that already have a value (e.g., pre-filled forms) |

### Priority 2 -- Semantic Queries

| Query | When to Use |
|---|---|
| `getByAltText` | Images, area elements |
| `getByTitle` | Elements with a `title` attribute (tooltip-like) |

### Priority 3 -- Test IDs (Last Resort)

| Query | When to Use |
|---|---|
| `getByTestId` | Only when no accessible query works -- dynamic content, layout containers |

### Query Variants

Each query has three variants that control timing behavior:

```typescript
// Synchronous -- element must be in the DOM right now
screen.getByRole("button", { name: /submit/i });

// Synchronous -- returns null instead of throwing if not found
screen.queryByRole("button", { name: /submit/i });

// Asynchronous -- waits for the element to appear (returns a Promise)
await screen.findByRole("button", { name: /submit/i });
```

**Decision guide:**
- `getBy*` -- Assert that an element is present.
- `queryBy*` -- Assert that an element is NOT present.
- `findBy*` -- Wait for an element that will appear after an async operation.

All three also have `*AllBy*` variants that return arrays.

## Rendering Components

### Basic Render

```typescript
import { render, screen } from "@testing-library/react";
import { Greeting } from "./Greeting";

it("renders the greeting message", () => {
  render(<Greeting name="Alice" />);

  expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
    "Hello, Alice"
  );
});
```

### Accessing the Container and Rerendering

```typescript
it("updates when props change", () => {
  const { rerender } = render(<Counter count={0} />);
  expect(screen.getByText("Count: 0")).toBeInTheDocument();

  rerender(<Counter count={5} />);
  expect(screen.getByText("Count: 5")).toBeInTheDocument();
});
```

### Unmounting

```typescript
it("cleans up event listeners on unmount", () => {
  const { unmount } = render(<Tooltip text="Info" />);
  unmount();
  // assert side effects are cleaned up
});
```

## User Interaction with userEvent

Always use `userEvent` over `fireEvent`. It simulates full interaction sequences (focus, keydown, keypress, keyup, input, change) that match real browser behavior.

### Setup

```typescript
import userEvent from "@testing-library/user-event";

// Create a user instance at the top of each test (or describe block)
const user = userEvent.setup();
```

### Clicking

```typescript
it("opens the menu on click", async () => {
  const user = userEvent.setup();
  render(<DropdownMenu />);

  await user.click(screen.getByRole("button", { name: /options/i }));

  expect(screen.getByRole("menu")).toBeInTheDocument();
});
```

### Typing

```typescript
it("filters the list as the user types", async () => {
  const user = userEvent.setup();
  render(<SearchableList items={["Apple", "Banana", "Cherry"]} />);

  await user.type(screen.getByRole("searchbox"), "ban");

  expect(screen.getByText("Banana")).toBeInTheDocument();
  expect(screen.queryByText("Apple")).not.toBeInTheDocument();
});
```

### Clearing and Replacing Input Values

```typescript
it("clears the input and types a new value", async () => {
  const user = userEvent.setup();
  render(<EditableField defaultValue="old value" />);

  const input = screen.getByRole("textbox");
  await user.clear(input);
  await user.type(input, "new value");

  expect(input).toHaveValue("new value");
});
```

### Keyboard Interactions

```typescript
it("submits the form on Enter", async () => {
  const user = userEvent.setup();
  const onSubmit = vi.fn();
  render(<SearchForm onSubmit={onSubmit} />);

  await user.type(screen.getByRole("searchbox"), "react{Enter}");

  expect(onSubmit).toHaveBeenCalledWith("react");
});

it("closes the modal on Escape", async () => {
  const user = userEvent.setup();
  const onClose = vi.fn();
  render(<Modal isOpen onClose={onClose} />);

  await user.keyboard("{Escape}");

  expect(onClose).toHaveBeenCalledTimes(1);
});
```

### Tab Navigation

```typescript
it("tabs through form fields in order", async () => {
  const user = userEvent.setup();
  render(<RegistrationForm />);

  await user.tab();
  expect(screen.getByLabelText("First name")).toHaveFocus();

  await user.tab();
  expect(screen.getByLabelText("Last name")).toHaveFocus();

  await user.tab();
  expect(screen.getByLabelText("Email")).toHaveFocus();
});
```

### Selecting Options

```typescript
it("selects a country from the dropdown", async () => {
  const user = userEvent.setup();
  const onChange = vi.fn();
  render(<CountrySelect onChange={onChange} />);

  await user.selectOptions(screen.getByRole("combobox"), "US");

  expect(onChange).toHaveBeenCalledWith("US");
});
```

### Pointer and Hover

```typescript
it("shows a tooltip on hover", async () => {
  const user = userEvent.setup();
  render(<IconButton icon="info" tooltip="More information" />);

  await user.hover(screen.getByRole("button"));
  expect(screen.getByRole("tooltip")).toHaveTextContent("More information");

  await user.unhover(screen.getByRole("button"));
  expect(screen.queryByRole("tooltip")).not.toBeInTheDocument();
});
```

## Async Testing Patterns

### waitFor -- Retry Until a Condition Passes

```typescript
import { render, screen, waitFor } from "@testing-library/react";

it("displays data after fetching", async () => {
  render(<UserProfile userId="123" />);

  // Spinner appears immediately
  expect(screen.getByRole("progressbar")).toBeInTheDocument();

  // Wait for data to load
  await waitFor(() => {
    expect(screen.getByRole("heading")).toHaveTextContent("Alice Smith");
  });

  // Spinner is gone
  expect(screen.queryByRole("progressbar")).not.toBeInTheDocument();
});
```

### findBy* -- Shorthand for waitFor + getBy

```typescript
it("loads and displays user data", async () => {
  render(<UserProfile userId="123" />);

  // Equivalent to: await waitFor(() => screen.getByText("Alice Smith"))
  const heading = await screen.findByRole("heading", { name: /alice smith/i });
  expect(heading).toBeInTheDocument();
});
```

### waitForElementToBeRemoved

```typescript
import { waitForElementToBeRemoved } from "@testing-library/react";

it("removes the loading spinner after fetch completes", async () => {
  render(<Dashboard />);

  await waitForElementToBeRemoved(() => screen.queryByRole("progressbar"));

  expect(screen.getByRole("table")).toBeInTheDocument();
});
```

### Testing Debounced Inputs

```typescript
it("debounces search input before calling the API", async () => {
  vi.useFakeTimers();
  const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
  const onSearch = vi.fn();

  render(<DebouncedSearch onSearch={onSearch} delay={300} />);

  await user.type(screen.getByRole("searchbox"), "react");

  // Not called yet -- still within debounce window
  expect(onSearch).not.toHaveBeenCalled();

  // Advance past the debounce delay
  vi.advanceTimersByTime(300);

  expect(onSearch).toHaveBeenCalledWith("react");
  expect(onSearch).toHaveBeenCalledTimes(1);

  vi.useRealTimers();
});
```

## Testing Forms

### Complete Form Submission

```typescript
interface ContactFormData {
  name: string;
  email: string;
  subject: string;
  message: string;
}

it("submits the contact form with valid data", async () => {
  const user = userEvent.setup();
  const onSubmit = vi.fn();
  render(<ContactForm onSubmit={onSubmit} />);

  await user.type(screen.getByLabelText(/name/i), "Alice Smith");
  await user.type(screen.getByLabelText(/email/i), "alice@example.com");
  await user.selectOptions(screen.getByLabelText(/subject/i), "support");
  await user.type(
    screen.getByLabelText(/message/i),
    "I need help with my account."
  );

  await user.click(screen.getByRole("button", { name: /send message/i }));

  expect(onSubmit).toHaveBeenCalledWith({
    name: "Alice Smith",
    email: "alice@example.com",
    subject: "support",
    message: "I need help with my account.",
  });
});
```

### Form Validation Errors

```typescript
it("displays validation errors for empty required fields", async () => {
  const user = userEvent.setup();
  render(<ContactForm onSubmit={vi.fn()} />);

  // Submit without filling in fields
  await user.click(screen.getByRole("button", { name: /send/i }));

  expect(screen.getByText(/name is required/i)).toBeInTheDocument();
  expect(screen.getByText(/email is required/i)).toBeInTheDocument();
});

it("displays an error for invalid email format", async () => {
  const user = userEvent.setup();
  render(<ContactForm onSubmit={vi.fn()} />);

  await user.type(screen.getByLabelText(/email/i), "not-an-email");
  await user.tab(); // trigger blur validation

  expect(screen.getByText(/enter a valid email/i)).toBeInTheDocument();
});
```

### Checkbox and Radio Groups

```typescript
it("toggles notification preferences", async () => {
  const user = userEvent.setup();
  const onSave = vi.fn();
  render(<NotificationSettings onSave={onSave} />);

  await user.click(screen.getByRole("checkbox", { name: /email alerts/i }));
  await user.click(screen.getByRole("checkbox", { name: /sms alerts/i }));
  await user.click(screen.getByRole("button", { name: /save/i }));

  expect(onSave).toHaveBeenCalledWith(
    expect.objectContaining({
      emailAlerts: true,
      smsAlerts: true,
    })
  );
});

it("selects a payment method", async () => {
  const user = userEvent.setup();
  render(<PaymentMethodSelector />);

  await user.click(screen.getByRole("radio", { name: /credit card/i }));

  expect(screen.getByRole("radio", { name: /credit card/i })).toBeChecked();
  expect(
    screen.getByRole("radio", { name: /bank transfer/i })
  ).not.toBeChecked();
});
```

## Testing Modals and Dialogs

```typescript
it("opens and closes the confirmation dialog", async () => {
  const user = userEvent.setup();
  const onConfirm = vi.fn();
  render(<DeleteButton onConfirm={onConfirm} />);

  // Open the dialog
  await user.click(screen.getByRole("button", { name: /delete/i }));

  const dialog = screen.getByRole("dialog");
  expect(dialog).toBeInTheDocument();
  expect(
    within(dialog).getByText(/are you sure/i)
  ).toBeInTheDocument();

  // Cancel
  await user.click(within(dialog).getByRole("button", { name: /cancel/i }));
  expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  expect(onConfirm).not.toHaveBeenCalled();
});

it("confirms the deletion", async () => {
  const user = userEvent.setup();
  const onConfirm = vi.fn();
  render(<DeleteButton onConfirm={onConfirm} />);

  await user.click(screen.getByRole("button", { name: /delete/i }));
  await user.click(
    within(screen.getByRole("dialog")).getByRole("button", { name: /confirm/i })
  );

  expect(onConfirm).toHaveBeenCalledTimes(1);
  expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
});
```

### Testing Focus Trap in Modals

```typescript
it("traps focus within the modal", async () => {
  const user = userEvent.setup();
  render(<Modal isOpen onClose={vi.fn()} />);

  const dialog = screen.getByRole("dialog");
  const firstFocusable = within(dialog).getAllByRole("button")[0];
  const lastFocusable = within(dialog).getAllByRole("button").at(-1)!;

  // Focus should start inside the dialog
  expect(firstFocusable).toHaveFocus();

  // Tab to the last focusable element, then tab again to cycle back
  await user.tab();
  await user.tab();
  expect(lastFocusable).toHaveFocus();

  await user.tab();
  expect(firstFocusable).toHaveFocus(); // focus wraps
});
```

## Testing Dropdowns and Comboboxes

```typescript
it("filters and selects from autocomplete dropdown", async () => {
  const user = userEvent.setup();
  const onSelect = vi.fn();
  render(
    <Autocomplete
      options={["React", "Redux", "Remix", "Vue", "Vite"]}
      onSelect={onSelect}
    />
  );

  const input = screen.getByRole("combobox");
  await user.type(input, "re");

  // Verify filtered options appear
  const listbox = screen.getByRole("listbox");
  expect(within(listbox).getAllByRole("option")).toHaveLength(3); // React, Redux, Remix

  // Select an option
  await user.click(within(listbox).getByRole("option", { name: "Redux" }));

  expect(onSelect).toHaveBeenCalledWith("Redux");
  expect(input).toHaveValue("Redux");
  expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
});
```

## Custom Render with Providers

Most applications require context providers for routing, theming, state, and data fetching. Create a reusable custom `render` function.

### All-in-One Test Utilities File

```typescript
// test/utils.tsx
import { render, type RenderOptions } from "@testing-library/react";
import { MemoryRouter, type MemoryRouterProps } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "@/context/ThemeContext";
import type { ReactElement, ReactNode } from "react";

interface CustomRenderOptions extends Omit<RenderOptions, "wrapper"> {
  routerProps?: MemoryRouterProps;
  queryClient?: QueryClient;
  theme?: "light" | "dark";
}

function createTestQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });
}

function AllProviders({
  children,
  routerProps,
  queryClient,
  theme = "light",
}: {
  children: ReactNode;
} & CustomRenderOptions) {
  const client = queryClient ?? createTestQueryClient();

  return (
    <QueryClientProvider client={client}>
      <ThemeProvider defaultTheme={theme}>
        <MemoryRouter {...routerProps}>{children}</MemoryRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

function customRender(
  ui: ReactElement,
  options: CustomRenderOptions = {}
) {
  const { routerProps, queryClient, theme, ...renderOptions } = options;

  return render(ui, {
    wrapper: ({ children }) => (
      <AllProviders
        routerProps={routerProps}
        queryClient={queryClient}
        theme={theme}
      >
        {children}
      </AllProviders>
    ),
    ...renderOptions,
  });
}

// Re-export everything from testing-library so tests import from one place
export * from "@testing-library/react";
export { default as userEvent } from "@testing-library/user-event";
export { customRender as render };
```

### Using the Custom Render

```typescript
// components/__tests__/Navigation.test.tsx
import { render, screen, userEvent } from "@/test/utils";
import { Navigation } from "../Navigation";

it("highlights the active route", () => {
  render(<Navigation />, {
    routerProps: { initialEntries: ["/dashboard"] },
  });

  expect(screen.getByRole("link", { name: /dashboard/i })).toHaveAttribute(
    "aria-current",
    "page"
  );
});

it("renders in dark theme", () => {
  render(<Navigation />, { theme: "dark" });

  expect(screen.getByRole("navigation")).toHaveClass("dark");
});
```

### Providing a Zustand Store in Tests

Zustand stores do not need a provider. To reset state between tests, call the store's `setState` directly:

```typescript
import { useAuthStore } from "@/store/auth";

beforeEach(() => {
  useAuthStore.setState({
    user: null,
    token: null,
    isAuthenticated: false,
  });
});

it("displays user name when authenticated", () => {
  useAuthStore.setState({
    user: { id: 1, name: "Alice", email: "alice@example.com", role: "admin" },
    isAuthenticated: true,
  });

  render(<Header />);

  expect(screen.getByText("Alice")).toBeInTheDocument();
});
```

## Testing Custom Hooks with renderHook

### Basic Hook Test

```typescript
import { renderHook, act } from "@testing-library/react";
import { useCounter } from "./useCounter";

it("starts at the initial count", () => {
  const { result } = renderHook(() => useCounter({ initial: 5 }));

  expect(result.current.count).toBe(5);
});

it("increments and decrements", () => {
  const { result } = renderHook(() => useCounter());

  act(() => {
    result.current.increment();
  });
  expect(result.current.count).toBe(1);

  act(() => {
    result.current.decrement();
  });
  expect(result.current.count).toBe(0);
});

it("resets to initial value", () => {
  const { result } = renderHook(() => useCounter({ initial: 10 }));

  act(() => {
    result.current.increment();
    result.current.increment();
  });
  expect(result.current.count).toBe(12);

  act(() => {
    result.current.reset();
  });
  expect(result.current.count).toBe(10);
});
```

### Hook with Provider Dependencies

```typescript
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useUsers } from "./useUsers";
import type { ReactNode } from "react";

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return function Wrapper({ children }: { children: ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );
  };
}

it("fetches and returns users", async () => {
  // Mock the API
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [{ id: 1, name: "Alice" }],
    })
  );

  const { result } = renderHook(() => useUsers(), {
    wrapper: createWrapper(),
  });

  // Initially loading
  expect(result.current.isLoading).toBe(true);

  await waitFor(() => {
    expect(result.current.isLoading).toBe(false);
  });

  expect(result.current.users).toEqual([{ id: 1, name: "Alice" }]);
});
```

### Hook with Changing Arguments

```typescript
it("re-fetches when the user ID changes", async () => {
  const fetchSpy = vi.fn().mockImplementation(async (id: string) => ({
    ok: true,
    json: async () => ({ id, name: `User ${id}` }),
  }));
  vi.stubGlobal("fetch", fetchSpy);

  const { result, rerender } = renderHook(
    (props: { userId: string }) => useUser(props.userId),
    {
      initialProps: { userId: "1" },
      wrapper: createWrapper(),
    }
  );

  await waitFor(() => {
    expect(result.current.data?.name).toBe("User 1");
  });

  rerender({ userId: "2" });

  await waitFor(() => {
    expect(result.current.data?.name).toBe("User 2");
  });
});
```

## Mocking API Calls with MSW

Mock Service Worker (MSW) intercepts network requests at the service worker level, keeping tests realistic. Prefer MSW over mocking `fetch` or `axios` directly.

```typescript
// test/mocks/handlers.ts
import { http, HttpResponse } from "msw";

export const handlers = [
  http.get("/api/users", () => {
    return HttpResponse.json([
      { id: 1, name: "Alice", email: "alice@example.com" },
      { id: 2, name: "Bob", email: "bob@example.com" },
    ]);
  }),

  http.post("/api/users", async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>;
    return HttpResponse.json(
      { id: 3, ...body },
      { status: 201 }
    );
  }),

  http.delete("/api/users/:id", ({ params }) => {
    return new HttpResponse(null, { status: 204 });
  }),
];

// test/mocks/server.ts
import { setupServer } from "msw/node";
import { handlers } from "./handlers";

export const server = setupServer(...handlers);

// vitest.setup.ts
import { server } from "./test/mocks/server";

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

### Overriding Handlers Per Test

```typescript
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";

it("displays an error when the API fails", async () => {
  server.use(
    http.get("/api/users", () => {
      return HttpResponse.json(
        { message: "Internal Server Error" },
        { status: 500 }
      );
    })
  );

  render(<UserList />);

  expect(await screen.findByRole("alert")).toHaveTextContent(
    /something went wrong/i
  );
});
```

## Common Anti-Patterns to Avoid

### 1. Using Container Queries Instead of screen

```typescript
// BAD: Destructuring container and querying the DOM directly
const { container } = render(<MyComponent />);
const button = container.querySelector(".submit-btn");

// GOOD: Use screen queries that mirror how a user finds elements
render(<MyComponent />);
const button = screen.getByRole("button", { name: /submit/i });
```

### 2. Using getBy* When Asserting Absence

```typescript
// BAD: getBy throws if the element is not found, so the test fails with a
// confusing error instead of a clear assertion failure
expect(screen.getByText("Error")).not.toBeInTheDocument();

// GOOD: queryBy returns null if the element is not found
expect(screen.queryByText("Error")).not.toBeInTheDocument();
```

### 3. Using fireEvent Instead of userEvent

```typescript
// BAD: fireEvent dispatches a single synthetic event
fireEvent.change(input, { target: { value: "hello" } });

// GOOD: userEvent simulates the full sequence a real user would produce
const user = userEvent.setup();
await user.type(input, "hello");
```

### 4. Not Awaiting userEvent Calls

```typescript
// BAD: Missing await -- the event has not completed before the assertion runs
user.click(button);
expect(onSubmit).toHaveBeenCalled();

// GOOD: Await every userEvent call
await user.click(button);
expect(onSubmit).toHaveBeenCalled();
```

### 5. Wrapping Non-State-Updates in act()

```typescript
// BAD: Wrapping userEvent in act is redundant -- userEvent already handles it
await act(async () => {
  await user.click(button);
});

// GOOD: Just use userEvent directly
await user.click(button);
```

### 6. Using waitFor with Side Effects

```typescript
// BAD: Side effects inside waitFor run multiple times on each retry
await waitFor(async () => {
  await user.click(button);
  expect(screen.getByText("Done")).toBeInTheDocument();
});

// GOOD: Keep side effects outside, only assertions inside waitFor
await user.click(button);
await waitFor(() => {
  expect(screen.getByText("Done")).toBeInTheDocument();
});
```

### 7. Using getByTestId as the Default Query

```typescript
// BAD: Test IDs couple tests to implementation details
screen.getByTestId("submit-button");

// GOOD: Prefer accessible queries that verify semantics
screen.getByRole("button", { name: /submit/i });
```

### 8. Testing Implementation Details

```typescript
// BAD: Testing internal state or class names
expect(component.state.isOpen).toBe(true);
expect(screen.getByTestId("menu")).toHaveClass("menu--open");

// GOOD: Test what the user sees and experiences
expect(screen.getByRole("menu")).toBeVisible();
```

### 9. Snapshot-Heavy Test Suites

```typescript
// BAD: Large snapshots are brittle and diffs are hard to review
expect(container).toMatchSnapshot();

// GOOD: Make targeted assertions on specific elements
expect(screen.getByRole("heading")).toHaveTextContent("Dashboard");
expect(screen.getByRole("navigation")).toBeInTheDocument();
expect(screen.getAllByRole("listitem")).toHaveLength(5);
```

## Useful Custom Matchers (jest-dom)

```typescript
// Visibility
expect(element).toBeVisible();
expect(element).toBeInTheDocument();

// Form state
expect(input).toHaveValue("hello");
expect(input).toBeRequired();
expect(input).toBeValid();
expect(input).toBeInvalid();
expect(input).toBeDisabled();
expect(input).toBeEnabled();
expect(checkbox).toBeChecked();

// Content
expect(element).toHaveTextContent("hello");
expect(element).toHaveTextContent(/hello/i);
expect(element).toBeEmptyDOMElement();

// Attributes and classes
expect(element).toHaveAttribute("aria-expanded", "true");
expect(element).toHaveClass("active");
expect(element).toHaveStyle({ color: "red" });

// Focus
expect(input).toHaveFocus();

// Accessibility
expect(element).toHaveAccessibleName("Submit form");
expect(element).toHaveAccessibleDescription("Sends the form data");
expect(element).toHaveRole("button");
```

## Debugging Failing Tests

### screen.debug()

```typescript
it("debugging example", () => {
  render(<ComplexComponent />);

  // Print the entire DOM to the console
  screen.debug();

  // Print a specific element
  screen.debug(screen.getByRole("navigation"));

  // Increase max output length
  screen.debug(undefined, 30000);
});
```

### logRoles

```typescript
import { logRoles } from "@testing-library/react";

it("discovers available roles", () => {
  const { container } = render(<MyForm />);
  logRoles(container);
  // Prints all ARIA roles found in the DOM -- helpful for choosing queries
});
```

### Testing Playground

Use the browser extension or `screen.logTestingPlaygroundURL()` to generate a URL that opens Testing Playground with the current DOM, showing suggested queries for each element.

```typescript
it("generates a Testing Playground link", () => {
  render(<MyComponent />);
  screen.logTestingPlaygroundURL();
  // Outputs a URL to the console -- open it in a browser
});
```

## References

- React Testing Library Docs: https://testing-library.com/docs/react-testing-library/intro/
- Query Priority Guide: https://testing-library.com/docs/queries/about#priority
- userEvent API: https://testing-library.com/docs/user-event/intro
- jest-dom Matchers: https://github.com/testing-library/jest-dom
- MSW (Mock Service Worker): https://mswjs.io/docs
- Common Mistakes: https://kentcdodds.com/blog/common-mistakes-with-react-testing-library
