---
name: test-driven-development
description: Test-driven development methodology covering the red-green-refactor cycle, writing tests before implementation, test design patterns, behavior-driven development, property-based testing, mutation testing, and maintaining test quality across TypeScript, Python, and Go projects.
---

# Test-Driven Development

This skill should be used when implementing features or fixing bugs using the TDD methodology. It enforces writing tests before implementation code, following the red-green-refactor cycle, and maintaining high test quality.

## When to Use This Skill

Use this skill when:

- Implementing new features (write tests first)
- Fixing bugs (write a failing test that reproduces the bug first)
- Refactoring code (ensure tests pass before and after)
- Building libraries or utilities with well-defined contracts
- Working on critical business logic that must be correct

## The Red-Green-Refactor Cycle

```
1. RED — Write a failing test that describes the desired behavior
   - Test should fail for the RIGHT reason
   - Test should be minimal and focused
   - Test name should describe the expected behavior

2. GREEN — Write the MINIMUM code to make the test pass
   - Do not over-engineer
   - Do not add features not covered by tests
   - "Fake it until you make it" is valid

3. REFACTOR — Improve the code while keeping tests green
   - Remove duplication
   - Improve naming and structure
   - Extract functions/classes as patterns emerge
   - Tests must stay green throughout

4. REPEAT — Write the next failing test
```

## TDD in Practice

### TypeScript Example (Vitest)

```typescript
// Step 1: RED — Write the failing test
// password-validator.test.ts
import { describe, it, expect } from "vitest";
import { validatePassword } from "./password-validator";

describe("validatePassword", () => {
  it("rejects passwords shorter than 8 characters", () => {
    const result = validatePassword("abc");
    expect(result.valid).toBe(false);
    expect(result.errors).toContain("Password must be at least 8 characters");
  });
});

// Run: npx vitest — test FAILS (function doesn't exist yet) ✓ RED

// Step 2: GREEN — Minimum implementation
// password-validator.ts
interface ValidationResult {
  valid: boolean;
  errors: string[];
}

export function validatePassword(password: string): ValidationResult {
  const errors: string[] = [];
  if (password.length < 8) {
    errors.push("Password must be at least 8 characters");
  }
  return { valid: errors.length === 0, errors };
}

// Run: npx vitest — test PASSES ✓ GREEN

// Step 3: Write NEXT failing test
describe("validatePassword", () => {
  it("rejects passwords shorter than 8 characters", () => {
    const result = validatePassword("abc");
    expect(result.valid).toBe(false);
    expect(result.errors).toContain("Password must be at least 8 characters");
  });

  it("rejects passwords without uppercase letters", () => {
    const result = validatePassword("abcdefgh");
    expect(result.valid).toBe(false);
    expect(result.errors).toContain("Password must contain an uppercase letter");
  });

  it("accepts valid passwords", () => {
    const result = validatePassword("SecureP4ss!");
    expect(result.valid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  it("returns all validation errors at once", () => {
    const result = validatePassword("ab");
    expect(result.errors.length).toBeGreaterThan(1);
  });
});

// Step 4: Implement to pass ALL tests, then REFACTOR
```

### Python Example (pytest)

```python
# test_shopping_cart.py
import pytest
from shopping_cart import ShoppingCart, Item

class TestShoppingCart:
    def test_new_cart_is_empty(self):
        cart = ShoppingCart()
        assert cart.total == 0
        assert len(cart.items) == 0

    def test_add_single_item(self):
        cart = ShoppingCart()
        cart.add(Item("Widget", price=9.99, quantity=1))
        assert cart.total == 9.99
        assert len(cart.items) == 1

    def test_add_multiple_items(self):
        cart = ShoppingCart()
        cart.add(Item("Widget", price=9.99, quantity=2))
        cart.add(Item("Gadget", price=19.99, quantity=1))
        assert cart.total == pytest.approx(39.97)

    def test_apply_percentage_discount(self):
        cart = ShoppingCart()
        cart.add(Item("Widget", price=100.00, quantity=1))
        cart.apply_discount(percent=10)
        assert cart.total == pytest.approx(90.00)

    def test_cannot_apply_negative_discount(self):
        cart = ShoppingCart()
        with pytest.raises(ValueError, match="Discount must be between 0 and 100"):
            cart.apply_discount(percent=-5)

    def test_remove_item(self):
        cart = ShoppingCart()
        cart.add(Item("Widget", price=9.99, quantity=1))
        cart.remove("Widget")
        assert len(cart.items) == 0
        assert cart.total == 0
```

### Go Example

```go
// calculator_test.go
package calculator

import (
    "testing"
    "github.com/stretchr/testify/assert"
)

func TestAdd(t *testing.T) {
    assert.Equal(t, 4, Add(2, 2))
    assert.Equal(t, 0, Add(-1, 1))
    assert.Equal(t, -3, Add(-1, -2))
}

func TestDivide(t *testing.T) {
    result, err := Divide(10, 2)
    assert.NoError(t, err)
    assert.Equal(t, 5.0, result)
}

func TestDivideByZero(t *testing.T) {
    _, err := Divide(10, 0)
    assert.Error(t, err)
    assert.EqualError(t, err, "division by zero")
}

// Table-driven tests (Go idiom)
func TestFibonacci(t *testing.T) {
    tests := []struct {
        name     string
        input    int
        expected int
    }{
        {"zero", 0, 0},
        {"one", 1, 1},
        {"small", 5, 5},
        {"medium", 10, 55},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            assert.Equal(t, tt.expected, Fibonacci(tt.input))
        })
    }
}
```

## Test Design Patterns

### Arrange-Act-Assert (AAA)

```typescript
it("transfers funds between accounts", () => {
  // Arrange — set up test data
  const source = new Account(1000);
  const target = new Account(500);

  // Act — perform the action
  source.transferTo(target, 200);

  // Assert — verify the result
  expect(source.balance).toBe(800);
  expect(target.balance).toBe(700);
});
```

### Given-When-Then (BDD style)

```typescript
describe("User registration", () => {
  describe("given valid registration data", () => {
    describe("when the user submits the form", () => {
      it("then creates a new account", async () => {
        const result = await register({ email: "test@example.com", password: "Secure123!" });
        expect(result.user).toBeDefined();
        expect(result.user.email).toBe("test@example.com");
      });

      it("then sends a welcome email", async () => {
        await register({ email: "test@example.com", password: "Secure123!" });
        expect(emailService.send).toHaveBeenCalledWith(
          expect.objectContaining({ to: "test@example.com", subject: "Welcome" })
        );
      });
    });
  });

  describe("given an existing email", () => {
    it("then rejects with duplicate error", async () => {
      await register({ email: "existing@example.com", password: "Secure123!" });
      await expect(
        register({ email: "existing@example.com", password: "Secure123!" })
      ).rejects.toThrow("Email already registered");
    });
  });
});
```

### Test Doubles

```typescript
// Mock — verify interactions
const emailService = { send: vi.fn() };
// ...
expect(emailService.send).toHaveBeenCalledOnce();

// Stub — provide canned responses
const userRepo = { findById: vi.fn().mockResolvedValue({ id: "1", name: "Alice" }) };

// Spy — observe without replacing
const spy = vi.spyOn(console, "log");
// ...
expect(spy).toHaveBeenCalledWith("User created");
spy.mockRestore();

// Fake — simplified working implementation
class InMemoryUserRepository implements UserRepository {
  private users = new Map<string, User>();
  async save(user: User) { this.users.set(user.id, user); }
  async findById(id: string) { return this.users.get(id) ?? null; }
}
```

## TDD Anti-Patterns to Avoid

```
1. Testing implementation details (not behavior)
   BAD:  expect(component.state.count).toBe(1)
   GOOD: expect(screen.getByText("Count: 1")).toBeInTheDocument()

2. Tests that pass regardless of implementation
   BAD:  expect(result).toBeTruthy() // almost anything passes
   GOOD: expect(result).toEqual({ id: "1", name: "Alice" })

3. Writing tests AFTER implementation
   This is not TDD. Write the test first, see it fail, then implement.

4. Testing too many things in one test
   BAD:  "validates, saves, sends email, and redirects"
   GOOD: One assertion per behavior (or closely related assertions)

5. Slow tests
   Unit tests should run in milliseconds.
   Use test doubles for external dependencies.
```

## When NOT to Use TDD

- Exploratory prototypes (throw-away code)
- UI layout/styling (visual testing is better)
- One-off scripts
- Configuration files

## Additional Resources

- Test-Driven Development by Kent Beck
- vitest: https://vitest.dev/
- pytest: https://docs.pytest.org/
- Go testing: https://pkg.go.dev/testing
