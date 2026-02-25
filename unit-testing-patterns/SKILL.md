---
name: unit-testing-patterns
description: Unit testing patterns and strategies covering test structure (Arrange-Act-Assert), mocking and stubbing, test doubles, parameterized tests, snapshot testing, coverage analysis, test naming conventions, testing async code, and writing maintainable test suites across JavaScript, TypeScript, and Python.
---

# Unit Testing Patterns

This skill should be used when writing unit tests for functions, classes, and modules. It covers test organization, mocking strategies, parameterized tests, async testing, and maintainability patterns.

## When to Use This Skill

Use this skill when you need to:

- Write unit tests for business logic
- Mock dependencies and external services
- Test async/await code patterns
- Organize test suites for maintainability
- Achieve meaningful test coverage

## Arrange-Act-Assert Pattern

```typescript
// Vitest / Jest
import { describe, it, expect } from "vitest";
import { calculateDiscount } from "./pricing";

describe("calculateDiscount", () => {
  it("applies percentage discount to subtotal", () => {
    // Arrange
    const subtotal = 100;
    const discountPercent = 20;

    // Act
    const result = calculateDiscount(subtotal, discountPercent);

    // Assert
    expect(result).toBe(80);
  });

  it("returns original price when discount is 0", () => {
    expect(calculateDiscount(100, 0)).toBe(100);
  });

  it("throws on negative discount", () => {
    expect(() => calculateDiscount(100, -5)).toThrow("Invalid discount");
  });

  it("caps discount at 100%", () => {
    expect(calculateDiscount(100, 150)).toBe(0);
  });
});
```

## Mocking Patterns

```typescript
import { describe, it, expect, vi, beforeEach } from "vitest";
import { UserService } from "./user-service";
import type { UserRepository } from "./user-repository";

describe("UserService", () => {
  let service: UserService;
  let mockRepo: UserRepository;

  beforeEach(() => {
    // Create mock with all methods stubbed
    mockRepo = {
      findById: vi.fn(),
      save: vi.fn(),
      delete: vi.fn(),
    };
    service = new UserService(mockRepo);
  });

  it("returns user when found", async () => {
    const user = { id: "1", name: "Alice", email: "alice@test.com" };
    vi.mocked(mockRepo.findById).mockResolvedValue(user);

    const result = await service.getUser("1");

    expect(result).toEqual(user);
    expect(mockRepo.findById).toHaveBeenCalledWith("1");
  });

  it("throws when user not found", async () => {
    vi.mocked(mockRepo.findById).mockResolvedValue(null);

    await expect(service.getUser("999")).rejects.toThrow("User not found");
  });

  it("hashes password before saving", async () => {
    vi.mocked(mockRepo.save).mockResolvedValue({ id: "1", name: "Bob", email: "bob@test.com" });

    await service.createUser({ name: "Bob", email: "bob@test.com", password: "secret" });

    const savedData = vi.mocked(mockRepo.save).mock.calls[0][0];
    expect(savedData.password).not.toBe("secret");
    expect(savedData.password).toMatch(/^\$2[aby]\$/); // bcrypt hash
  });
});
```

## Parameterized Tests

```typescript
describe("isValidEmail", () => {
  it.each([
    ["user@example.com", true],
    ["user@sub.example.com", true],
    ["user+tag@example.com", true],
    ["invalid", false],
    ["@example.com", false],
    ["user@", false],
    ["", false],
  ])("validates %s as %s", (email, expected) => {
    expect(isValidEmail(email)).toBe(expected);
  });
});

describe("formatCurrency", () => {
  it.each`
    amount   | currency | expected
    ${10}    | ${"USD"} | ${"$10.00"}
    ${1500}  | ${"USD"} | ${"$1,500.00"}
    ${99.9}  | ${"EUR"} | ${"€99.90"}
    ${0}     | ${"USD"} | ${"$0.00"}
  `("formats $amount $currency as $expected", ({ amount, currency, expected }) => {
    expect(formatCurrency(amount, currency)).toBe(expected);
  });
});
```

## Testing Async Code

```typescript
describe("fetchUserData", () => {
  it("fetches and transforms user data", async () => {
    const data = await fetchUserData("user-1");
    expect(data).toMatchObject({
      id: "user-1",
      displayName: expect.any(String),
    });
  });

  it("retries on transient failure", async () => {
    const fetchFn = vi
      .fn()
      .mockRejectedValueOnce(new Error("Network error"))
      .mockResolvedValueOnce({ id: "1", name: "Alice" });

    const result = await fetchWithRetry(fetchFn, { retries: 2 });

    expect(result).toEqual({ id: "1", name: "Alice" });
    expect(fetchFn).toHaveBeenCalledTimes(2);
  });

  it("times out after configured duration", async () => {
    vi.useFakeTimers();

    const promise = longRunningOperation();
    vi.advanceTimersByTime(5000);

    await expect(promise).rejects.toThrow("Timeout");
    vi.useRealTimers();
  });
});
```

## Python Unit Testing (pytest)

```python
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.order_service import OrderService

class TestOrderService:
    def setup_method(self):
        self.repo = Mock()
        self.payment = Mock()
        self.service = OrderService(self.repo, self.payment)

    def test_creates_order_with_valid_items(self):
        self.repo.save.return_value = {"id": "order-1", "total": 50.0}

        result = self.service.create_order(
            user_id="user-1",
            items=[{"product_id": "p1", "quantity": 2, "price": 25.0}],
        )

        assert result["id"] == "order-1"
        assert result["total"] == 50.0
        self.repo.save.assert_called_once()

    def test_rejects_empty_order(self):
        with pytest.raises(ValueError, match="at least one item"):
            self.service.create_order(user_id="user-1", items=[])

    @pytest.mark.parametrize("quantity,expected", [
        (1, 10.0),
        (5, 45.0),   # 10% bulk discount
        (10, 80.0),  # 20% bulk discount
    ])
    def test_applies_bulk_discount(self, quantity, expected):
        result = self.service.calculate_total(
            [{"product_id": "p1", "quantity": quantity, "price": 10.0}]
        )
        assert result == expected

    @pytest.mark.asyncio
    async def test_processes_payment(self):
        self.payment.charge = AsyncMock(return_value={"status": "success"})

        result = await self.service.process_payment("order-1", amount=50.0)

        assert result["status"] == "success"
        self.payment.charge.assert_awaited_once_with(amount=50.0)
```

## Test Organization

```
NAMING CONVENTIONS:
  TypeScript:  describe("ClassName") → it("does specific thing")
  Python:      class TestClassName → def test_does_specific_thing
  Files:        *.test.ts / *.spec.ts / test_*.py

STRUCTURE:
  tests/
  ├── unit/           # Pure function & class tests (fast, no I/O)
  ├── integration/    # Tests with database, APIs, file system
  └── fixtures/       # Shared test data and factories

GUIDELINES:
  [ ] One assertion concept per test (multiple expect() OK if same concept)
  [ ] Test behavior, not implementation details
  [ ] Avoid testing private methods directly
  [ ] Use descriptive test names that read as specifications
  [ ] Keep tests independent — no shared mutable state between tests
  [ ] Prefer real objects over mocks when practical
```

## Additional Resources

- Vitest: https://vitest.dev/
- Jest: https://jestjs.io/
- pytest: https://docs.pytest.org/
- Testing Library: https://testing-library.com/
