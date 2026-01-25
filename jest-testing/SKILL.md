---
name: jest-testing
description: This skill should be used when users need to write, configure, or optimize JavaScript/TypeScript tests using Jest or Vitest. Covers unit tests, integration tests, mocking, coverage, and testing best practices.
---

# Jest & Vitest Testing

Comprehensive guide for writing and configuring JavaScript/TypeScript tests using Jest and Vitest testing frameworks.

## When to Use This Skill

Use this skill when:
- User mentions "Jest", "Vitest", "testing", or "test coverage"
- User wants to write unit tests or integration tests for JavaScript/TypeScript
- User needs help with mocking, spying, or test setup
- User asks about test configuration or optimization
- User mentions "TDD" (Test-Driven Development)
- User wants to improve test coverage or debug failing tests

## Key Features

### 1. Test Writing
- Unit tests for functions and classes
- Integration tests for modules
- Component testing (React, Vue, etc.)
- Async/Promise testing
- Error testing

### 2. Mocking & Spying
- Mock functions and modules
- Spy on function calls
- Mock timers and dates
- Mock HTTP requests

### 3. Configuration
- Jest/Vitest setup
- TypeScript integration
- Coverage configuration
- Custom matchers

### 4. Best Practices
- Test organization
- AAA pattern (Arrange, Act, Assert)
- Test isolation
- Performance optimization

## Installation

### Jest

```bash
# NPM
npm install --save-dev jest

# Yarn
yarn add --dev jest

# With TypeScript
npm install --save-dev jest @types/jest ts-jest

# With Babel
npm install --save-dev jest babel-jest @babel/preset-env
```

### Vitest

```bash
# NPM
npm install --save-dev vitest

# Yarn
yarn add --dev vitest

# With UI
npm install --save-dev vitest @vitest/ui
```

## Configuration

### Jest Configuration (jest.config.js)

```javascript
module.exports = {
  // Test environment
  testEnvironment: 'node', // or 'jsdom' for browser-like environment

  // File patterns
  testMatch: [
    '**/__tests__/**/*.[jt]s?(x)',
    '**/?(*.)+(spec|test).[jt]s?(x)'
  ],

  // Coverage
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.{js,jsx,ts,tsx}'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },

  // Transform files
  transform: {
    '^.+\\.(ts|tsx)$': 'ts-jest'
  },

  // Module paths
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1'
  },

  // Setup files
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js']
};
```

### Vitest Configuration (vitest.config.ts)

```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    // Test environment
    environment: 'node', // or 'jsdom', 'happy-dom'

    // Globals
    globals: true,

    // Coverage
    coverage: {
      provider: 'v8', // or 'istanbul'
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'dist/',
        '**/*.d.ts',
        '**/*.config.*'
      ]
    },

    // Setup files
    setupFiles: ['./vitest.setup.ts']
  }
});
```

## Basic Test Structure

### Simple Unit Test

```javascript
// sum.js
export function sum(a, b) {
  return a + b;
}

// sum.test.js
import { sum } from './sum';

describe('sum function', () => {
  it('adds two numbers correctly', () => {
    expect(sum(1, 2)).toBe(3);
  });

  it('handles negative numbers', () => {
    expect(sum(-1, -2)).toBe(-3);
  });

  it('handles zero', () => {
    expect(sum(0, 5)).toBe(5);
  });
});
```

### Testing with Setup and Teardown

```javascript
describe('Database operations', () => {
  let db;

  // Runs before all tests
  beforeAll(async () => {
    db = await connectDatabase();
  });

  // Runs before each test
  beforeEach(async () => {
    await db.clear();
  });

  // Runs after each test
  afterEach(async () => {
    await db.resetState();
  });

  // Runs after all tests
  afterAll(async () => {
    await db.disconnect();
  });

  it('saves user to database', async () => {
    const user = { name: 'John', email: 'john@example.com' };
    await db.users.save(user);

    const saved = await db.users.findOne({ email: 'john@example.com' });
    expect(saved.name).toBe('John');
  });
});
```

## Matchers (Assertions)

### Common Matchers

```javascript
// Equality
expect(value).toBe(4);              // Strict equality (===)
expect(value).toEqual(expected);    // Deep equality
expect(value).not.toBe(5);          // Negation

// Truthiness
expect(value).toBeTruthy();
expect(value).toBeFalsy();
expect(value).toBeNull();
expect(value).toBeUndefined();
expect(value).toBeDefined();

// Numbers
expect(value).toBeGreaterThan(3);
expect(value).toBeGreaterThanOrEqual(3.5);
expect(value).toBeLessThan(5);
expect(value).toBeLessThanOrEqual(4.5);
expect(value).toBeCloseTo(0.3, 2);  // Floating point

// Strings
expect(string).toMatch(/pattern/);
expect(string).toContain('substring');

// Arrays
expect(array).toContain('item');
expect(array).toHaveLength(3);
expect(array).toEqual(expect.arrayContaining([1, 2]));

// Objects
expect(object).toHaveProperty('key');
expect(object).toHaveProperty('key', 'value');
expect(object).toMatchObject({ key: 'value' });

// Exceptions
expect(() => riskyFunction()).toThrow();
expect(() => riskyFunction()).toThrow('error message');
expect(() => riskyFunction()).toThrow(TypeError);
```

## Async Testing

### Promises

```javascript
// Using async/await
it('fetches user data', async () => {
  const data = await fetchUser(1);
  expect(data.name).toBe('John');
});

// Using .resolves
it('fetches user data', () => {
  return expect(fetchUser(1)).resolves.toEqual({
    id: 1,
    name: 'John'
  });
});

// Testing rejections
it('handles fetch error', async () => {
  await expect(fetchUser(999)).rejects.toThrow('User not found');
});
```

### Callbacks

```javascript
it('calls callback with data', (done) => {
  function callback(data) {
    try {
      expect(data).toBe('result');
      done();
    } catch (error) {
      done(error);
    }
  }

  fetchData(callback);
});
```

## Mocking

### Mock Functions

```javascript
// Create mock function
const mockFn = jest.fn();

// Mock implementation
const mockFn = jest.fn(() => 'mocked value');

// Mock implementation once
const mockFn = jest.fn()
  .mockImplementationOnce(() => 'first call')
  .mockImplementationOnce(() => 'second call');

// Mock return value
const mockFn = jest.fn().mockReturnValue('value');

// Mock resolved/rejected promises
const mockFn = jest.fn().mockResolvedValue('success');
const mockFn = jest.fn().mockRejectedValue(new Error('failed'));

// Usage
it('calls mock function', () => {
  mockFn('arg1', 'arg2');

  expect(mockFn).toHaveBeenCalled();
  expect(mockFn).toHaveBeenCalledTimes(1);
  expect(mockFn).toHaveBeenCalledWith('arg1', 'arg2');
  expect(mockFn).toHaveBeenLastCalledWith('arg1', 'arg2');
});
```

### Mock Modules

```javascript
// Auto-mock entire module
jest.mock('./module');

// Manual mock with implementation
jest.mock('./api', () => ({
  fetchUser: jest.fn(() => Promise.resolve({ id: 1, name: 'John' })),
  saveUser: jest.fn()
}));

// Partial mock (keep some real implementations)
jest.mock('./utils', () => ({
  ...jest.requireActual('./utils'),
  helperFunction: jest.fn()
}));

// Example usage
import { fetchUser } from './api';

it('uses mocked API', async () => {
  const user = await fetchUser(1);
  expect(user.name).toBe('John');
  expect(fetchUser).toHaveBeenCalledWith(1);
});
```

### Spying on Methods

```javascript
// Spy on object method
const spy = jest.spyOn(object, 'method');

// Spy and mock implementation
jest.spyOn(object, 'method').mockImplementation(() => 'mocked');

// Restore original implementation
spy.mockRestore();

// Example
it('spies on Math.random', () => {
  const spy = jest.spyOn(Math, 'random').mockReturnValue(0.5);

  expect(Math.random()).toBe(0.5);
  expect(spy).toHaveBeenCalled();

  spy.mockRestore();
});
```

## Testing Timers

```javascript
// Use fake timers
jest.useFakeTimers();

it('delays callback', () => {
  const callback = jest.fn();

  setTimeout(callback, 1000);

  // Fast-forward time
  jest.advanceTimersByTime(1000);

  expect(callback).toHaveBeenCalled();
});

it('runs all timers', () => {
  const callback = jest.fn();

  setTimeout(callback, 1000);
  setInterval(callback, 2000);

  // Run all timers
  jest.runAllTimers();

  expect(callback).toHaveBeenCalled();
});

// Clear timers
jest.clearAllTimers();

// Use real timers
jest.useRealTimers();
```

## Testing React Components

### Basic Component Test

```javascript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Button from './Button';

describe('Button component', () => {
  it('renders button with text', () => {
    render(<Button>Click me</Button>);

    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', async () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    await userEvent.click(screen.getByText('Click me'));

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Click me</Button>);

    expect(screen.getByRole('button')).toBeDisabled();
  });
});
```

### Testing with Props

```javascript
it('renders different variants', () => {
  const { rerender } = render(<Button variant="primary">Primary</Button>);
  expect(screen.getByRole('button')).toHaveClass('btn-primary');

  rerender(<Button variant="secondary">Secondary</Button>);
  expect(screen.getByRole('button')).toHaveClass('btn-secondary');
});
```

### Testing Hooks

```javascript
import { renderHook, act } from '@testing-library/react';
import useCounter from './useCounter';

it('increments counter', () => {
  const { result } = renderHook(() => useCounter());

  expect(result.current.count).toBe(0);

  act(() => {
    result.current.increment();
  });

  expect(result.current.count).toBe(1);
});
```

## Snapshot Testing

```javascript
it('matches snapshot', () => {
  const component = render(<MyComponent />);
  expect(component).toMatchSnapshot();
});

// Inline snapshots
it('renders correctly', () => {
  const tree = render(<Button>Click me</Button>);
  expect(tree).toMatchInlineSnapshot(`
    <button class="btn">
      Click me
    </button>
  `);
});
```

## Coverage

### Generate Coverage Report

```bash
# Jest
npm test -- --coverage

# Vitest
npm test -- --coverage

# Watch mode with coverage
npm test -- --coverage --watch
```

### Coverage Configuration

```javascript
// jest.config.js
module.exports = {
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/index.ts'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    },
    './src/components/': {
      branches: 90,
      functions: 90,
      lines: 90,
      statements: 90
    }
  }
};
```

## Best Practices

### 1. Test Organization

```javascript
// Good: Descriptive test names
describe('UserService', () => {
  describe('createUser', () => {
    it('creates user with valid data', () => {});
    it('throws error when email is invalid', () => {});
    it('throws error when email already exists', () => {});
  });

  describe('deleteUser', () => {
    it('deletes existing user', () => {});
    it('throws error when user not found', () => {});
  });
});
```

### 2. AAA Pattern (Arrange, Act, Assert)

```javascript
it('calculates total price with discount', () => {
  // Arrange
  const cart = new ShoppingCart();
  cart.addItem({ price: 100, quantity: 2 });
  const discount = 0.1;

  // Act
  const total = cart.calculateTotal(discount);

  // Assert
  expect(total).toBe(180);
});
```

### 3. Test Isolation

```javascript
// Bad: Tests depend on each other
let user;
it('creates user', () => {
  user = createUser({ name: 'John' });
});
it('updates user', () => {
  updateUser(user.id, { name: 'Jane' });
});

// Good: Each test is independent
it('creates user', () => {
  const user = createUser({ name: 'John' });
  expect(user.name).toBe('John');
});

it('updates user', () => {
  const user = createUser({ name: 'John' });
  updateUser(user.id, { name: 'Jane' });
  expect(user.name).toBe('Jane');
});
```

### 4. Testing Edge Cases

```javascript
describe('divide function', () => {
  it('divides two numbers', () => {
    expect(divide(10, 2)).toBe(5);
  });

  it('handles division by zero', () => {
    expect(() => divide(10, 0)).toThrow('Division by zero');
  });

  it('handles negative numbers', () => {
    expect(divide(-10, 2)).toBe(-5);
  });

  it('handles floating point precision', () => {
    expect(divide(1, 3)).toBeCloseTo(0.333, 2);
  });
});
```

## Debugging Tests

### Run Specific Tests

```bash
# Run single test file
npm test -- path/to/test.spec.js

# Run tests matching pattern
npm test -- --testNamePattern="user"

# Run only tests with .only
it.only('runs only this test', () => {});

# Skip tests with .skip
it.skip('skips this test', () => {});
```

### Debug Mode

```bash
# Node debug mode
node --inspect-brk node_modules/.bin/jest --runInBand

# VS Code launch.json
{
  "type": "node",
  "request": "launch",
  "name": "Jest Debug",
  "program": "${workspaceFolder}/node_modules/.bin/jest",
  "args": ["--runInBand"],
  "console": "integratedTerminal"
}
```

## Common Patterns

### Testing API Calls

```javascript
import axios from 'axios';
import { fetchUsers } from './api';

jest.mock('axios');

it('fetches users successfully', async () => {
  const users = [{ id: 1, name: 'John' }];
  axios.get.mockResolvedValue({ data: users });

  const result = await fetchUsers();

  expect(result).toEqual(users);
  expect(axios.get).toHaveBeenCalledWith('/api/users');
});

it('handles API error', async () => {
  axios.get.mockRejectedValue(new Error('Network error'));

  await expect(fetchUsers()).rejects.toThrow('Network error');
});
```

### Testing Forms

```javascript
it('submits form with valid data', async () => {
  const handleSubmit = jest.fn();
  render(<ContactForm onSubmit={handleSubmit} />);

  await userEvent.type(screen.getByLabelText('Name'), 'John Doe');
  await userEvent.type(screen.getByLabelText('Email'), 'john@example.com');
  await userEvent.click(screen.getByRole('button', { name: 'Submit' }));

  expect(handleSubmit).toHaveBeenCalledWith({
    name: 'John Doe',
    email: 'john@example.com'
  });
});
```

## Performance Testing

```javascript
it('performs within acceptable time', () => {
  const start = Date.now();

  heavyComputation();

  const duration = Date.now() - start;
  expect(duration).toBeLessThan(1000); // Should take less than 1 second
});
```

## References

- Jest Documentation: https://jestjs.io/docs/getting-started
- Vitest Documentation: https://vitest.dev/guide/
- Testing Library: https://testing-library.com/docs/
- Jest Cheat Sheet: https://github.com/sapegin/jest-cheat-sheet

---

**Created for**: awesome-claude-skills repository
**Version**: 1.0.0
**Last Updated**: January 25, 2026
