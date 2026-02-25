---
name: code-refactoring
description: Code refactoring and technical debt management covering refactoring patterns, code smell detection, safe refactoring techniques, extract/inline/rename operations, dependency reduction, architecture improvement, legacy code strategies, and maintaining test coverage during refactoring.
---

# Code Refactoring & Technical Debt Management

This skill should be used when improving existing code structure without changing its external behavior, identifying and eliminating code smells, reducing technical debt, and performing safe transformations on production codebases.

## When to Use This Skill

- Identifying code smells and proposing refactoring strategies
- Performing extract, inline, rename, or move refactoring operations
- Reducing coupling and improving cohesion in a codebase
- Paying down technical debt systematically
- Refactoring legacy code that lacks test coverage
- Improving architecture without rewriting from scratch
- Making code more testable, readable, or maintainable

---

## 1. Common Code Smells

Code smells are surface indicators of deeper structural problems. Recognizing them is the first step toward targeted refactoring.

### Long Method / Function

Functions that do too many things are hard to understand, test, and reuse.

**Before (TypeScript):**
```typescript
function processOrder(order: Order): Receipt {
  // Validate
  if (!order.items.length) throw new Error("Empty order");
  if (!order.customer.email) throw new Error("Missing email");
  for (const item of order.items) {
    if (item.quantity <= 0) throw new Error(`Invalid quantity for ${item.name}`);
    if (item.price < 0) throw new Error(`Invalid price for ${item.name}`);
  }

  // Calculate totals
  let subtotal = 0;
  for (const item of order.items) {
    subtotal += item.price * item.quantity;
  }
  const tax = subtotal * 0.08;
  const shipping = subtotal > 100 ? 0 : 9.99;
  const total = subtotal + tax + shipping;

  // Save to database
  const receiptId = db.insert("receipts", {
    orderId: order.id,
    subtotal,
    tax,
    shipping,
    total,
    createdAt: new Date(),
  });

  // Send confirmation email
  emailService.send({
    to: order.customer.email,
    subject: `Order Confirmation #${receiptId}`,
    body: `Your total is $${total.toFixed(2)}. Thank you!`,
  });

  return { id: receiptId, subtotal, tax, shipping, total };
}
```

**After (TypeScript) -- Extract Function:**
```typescript
function processOrder(order: Order): Receipt {
  validateOrder(order);
  const pricing = calculatePricing(order.items);
  const receiptId = saveReceipt(order.id, pricing);
  sendConfirmationEmail(order.customer.email, receiptId, pricing.total);
  return { id: receiptId, ...pricing };
}

function validateOrder(order: Order): void {
  if (!order.items.length) throw new Error("Empty order");
  if (!order.customer.email) throw new Error("Missing email");
  for (const item of order.items) {
    if (item.quantity <= 0) throw new Error(`Invalid quantity for ${item.name}`);
    if (item.price < 0) throw new Error(`Invalid price for ${item.name}`);
  }
}

function calculatePricing(items: OrderItem[]): Pricing {
  const subtotal = items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const tax = subtotal * 0.08;
  const shipping = subtotal > 100 ? 0 : 9.99;
  return { subtotal, tax, shipping, total: subtotal + tax + shipping };
}

function saveReceipt(orderId: string, pricing: Pricing): string {
  return db.insert("receipts", {
    orderId,
    ...pricing,
    createdAt: new Date(),
  });
}

function sendConfirmationEmail(email: string, receiptId: string, total: number): void {
  emailService.send({
    to: email,
    subject: `Order Confirmation #${receiptId}`,
    body: `Your total is $${total.toFixed(2)}. Thank you!`,
  });
}
```

### Large Class / God Object

A class that knows too much or does too much violates the Single Responsibility Principle.

**Before (Python):**
```python
class UserManager:
    def create_user(self, name, email, password): ...
    def delete_user(self, user_id): ...
    def update_profile(self, user_id, data): ...
    def authenticate(self, email, password): ...
    def reset_password(self, email): ...
    def generate_auth_token(self, user_id): ...
    def validate_token(self, token): ...
    def send_welcome_email(self, user_id): ...
    def send_password_reset_email(self, email): ...
    def generate_usage_report(self, user_id): ...
    def export_user_data(self, user_id): ...
    def calculate_subscription_cost(self, user_id): ...
```

**After (Python) -- Extract Class:**
```python
class UserRepository:
    def create(self, name: str, email: str, password: str) -> User: ...
    def delete(self, user_id: str) -> None: ...
    def update_profile(self, user_id: str, data: dict) -> User: ...

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    def authenticate(self, email: str, password: str) -> User: ...
    def reset_password(self, email: str) -> None: ...
    def generate_token(self, user_id: str) -> str: ...
    def validate_token(self, token: str) -> TokenPayload: ...

class UserNotificationService:
    def send_welcome_email(self, user_id: str) -> None: ...
    def send_password_reset_email(self, email: str) -> None: ...

class UserReportingService:
    def generate_usage_report(self, user_id: str) -> Report: ...
    def export_user_data(self, user_id: str) -> ExportData: ...

class BillingService:
    def calculate_subscription_cost(self, user_id: str) -> Decimal: ...
```

### Feature Envy

A method that uses data or methods from another class more than its own.

**Before (TypeScript):**
```typescript
class InvoicePrinter {
  printInvoice(invoice: Invoice): string {
    const subtotal = invoice.items.reduce(
      (sum, item) => sum + item.price * item.quantity, 0
    );
    const tax = subtotal * invoice.taxRate;
    const total = subtotal + tax;
    const due = new Date(invoice.createdAt);
    due.setDate(due.getDate() + invoice.paymentTermDays);

    return `Invoice #${invoice.id}\nSubtotal: $${subtotal}\nTax: $${tax}\nTotal: $${total}\nDue: ${due.toISOString()}`;
  }
}
```

**After (TypeScript) -- Move Method:**
```typescript
class Invoice {
  // Calculations belong on Invoice, not on InvoicePrinter
  get subtotal(): number {
    return this.items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  }

  get tax(): number {
    return this.subtotal * this.taxRate;
  }

  get total(): number {
    return this.subtotal + this.tax;
  }

  get dueDate(): Date {
    const due = new Date(this.createdAt);
    due.setDate(due.getDate() + this.paymentTermDays);
    return due;
  }
}

class InvoicePrinter {
  printInvoice(invoice: Invoice): string {
    return `Invoice #${invoice.id}\nSubtotal: $${invoice.subtotal}\nTax: $${invoice.tax}\nTotal: $${invoice.total}\nDue: ${invoice.dueDate.toISOString()}`;
  }
}
```

### Primitive Obsession

Using primitive types (strings, numbers) instead of small domain objects.

**Before (Python):**
```python
def create_user(name: str, email: str, phone: str, currency: str, amount: float):
    if "@" not in email:
        raise ValueError("Invalid email")
    if not phone.startswith("+"):
        raise ValueError("Phone must include country code")
    if currency not in ("USD", "EUR", "GBP"):
        raise ValueError("Unsupported currency")
    if amount < 0:
        raise ValueError("Negative amount")
    # ... scattered validation everywhere this data is used
```

**After (Python) -- Introduce Value Objects:**
```python
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Email:
    value: str
    def __post_init__(self):
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", self.value):
            raise ValueError(f"Invalid email: {self.value}")

@dataclass(frozen=True)
class PhoneNumber:
    value: str
    def __post_init__(self):
        if not self.value.startswith("+"):
            raise ValueError("Phone must include country code")

@dataclass(frozen=True)
class Money:
    amount: float
    currency: str
    def __post_init__(self):
        if self.currency not in ("USD", "EUR", "GBP"):
            raise ValueError(f"Unsupported currency: {self.currency}")
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")

def create_user(name: str, email: Email, phone: PhoneNumber, balance: Money):
    # Validation already handled by value objects
    # No need to repeat validation logic here or anywhere else
    ...
```

### Other Common Smells -- Quick Reference

| Smell | Symptom | Typical Refactoring |
|-------|---------|---------------------|
| **Duplicated Code** | Same logic in multiple places | Extract Function, Extract Superclass, Template Method |
| **Long Parameter List** | Function takes 5+ parameters | Introduce Parameter Object, Builder Pattern |
| **Divergent Change** | One class modified for unrelated reasons | Extract Class (split responsibilities) |
| **Shotgun Surgery** | One change requires edits in many classes | Move Method, Inline Class (consolidate) |
| **Data Clumps** | Same group of fields appears together repeatedly | Extract Class, Introduce Parameter Object |
| **Switch Statements** | Repeated switch/if-else on the same type | Replace Conditional with Polymorphism |
| **Speculative Generality** | Unused abstractions "just in case" | Inline Class, Remove Parameter, Collapse Hierarchy |
| **Message Chains** | `a.getB().getC().getD().doThing()` | Hide Delegate, Extract Method |
| **Middle Man** | Class that only delegates to another | Remove Middle Man, Inline Class |
| **Refused Bequest** | Subclass ignores most of parent's interface | Replace Inheritance with Delegation |

---

## 2. Safe Refactoring Techniques

### Extract Function

The most common refactoring. Pull a coherent block of code into a named function.

**When to apply:** A block of code inside a function can be given a meaningful name that describes *what* it does, not *how*.

**Before (Python):**
```python
def print_report(employees):
    # Print header
    print("=" * 60)
    print(f"{'Name':<20} {'Department':<20} {'Salary':>10}")
    print("=" * 60)

    # Print rows
    for emp in employees:
        print(f"{emp.name:<20} {emp.department:<20} {emp.salary:>10,.2f}")

    # Print summary
    total = sum(e.salary for e in employees)
    avg = total / len(employees) if employees else 0
    print("-" * 60)
    print(f"{'Total':<40} {total:>10,.2f}")
    print(f"{'Average':<40} {avg:>10,.2f}")
```

**After (Python):**
```python
def print_report(employees):
    print_header()
    print_employee_rows(employees)
    print_summary(employees)

def print_header():
    print("=" * 60)
    print(f"{'Name':<20} {'Department':<20} {'Salary':>10}")
    print("=" * 60)

def print_employee_rows(employees):
    for emp in employees:
        print(f"{emp.name:<20} {emp.department:<20} {emp.salary:>10,.2f}")

def print_summary(employees):
    total = sum(e.salary for e in employees)
    avg = total / len(employees) if employees else 0
    print("-" * 60)
    print(f"{'Total':<40} {total:>10,.2f}")
    print(f"{'Average':<40} {avg:>10,.2f}")
```

### Inline Function

The reverse of Extract Function. When a function body is as clear as its name, inline it.

**Before (TypeScript):**
```typescript
function getRating(driver: Driver): number {
  return moreThanFiveLateDeliveries(driver) ? 2 : 1;
}

function moreThanFiveLateDeliveries(driver: Driver): boolean {
  return driver.lateDeliveries > 5;
}
```

**After (TypeScript):**
```typescript
function getRating(driver: Driver): number {
  return driver.lateDeliveries > 5 ? 2 : 1;
}
```

### Rename (Variable, Function, Class)

Names should reveal intent. Rename when the current name is misleading or vague.

**Before (TypeScript):**
```typescript
function calc(d: number[]): number {
  let t = 0;
  for (const v of d) {
    t += v;
  }
  return d.length > 0 ? t / d.length : 0;
}
```

**After (TypeScript):**
```typescript
function calculateAverage(measurements: number[]): number {
  let total = 0;
  for (const value of measurements) {
    total += value;
  }
  return measurements.length > 0 ? total / measurements.length : 0;
}
```

### Move Function / Move Field

Move a function or field to the class where it is most used.

**Before (Python):**
```python
class Account:
    def __init__(self, account_type: str, days_overdue: int):
        self.account_type = account_type
        self.days_overdue = days_overdue

class OverdraftCalculator:
    def calculate_fee(self, account: Account) -> float:
        if account.account_type == "premium":
            return max(0, (account.days_overdue - 7) * 1.5)
        else:
            return account.days_overdue * 2.75
```

**After (Python):**
```python
class Account:
    def __init__(self, account_type: str, days_overdue: int):
        self.account_type = account_type
        self.days_overdue = days_overdue

    def overdraft_fee(self) -> float:
        if self.account_type == "premium":
            return max(0, (self.days_overdue - 7) * 1.5)
        else:
            return self.days_overdue * 2.75
```

### Introduce Parameter Object

When multiple parameters travel together, group them into a single object.

**Before (TypeScript):**
```typescript
function searchProducts(
  query: string,
  minPrice: number,
  maxPrice: number,
  category: string,
  sortBy: string,
  sortOrder: "asc" | "desc",
  page: number,
  pageSize: number
): Product[] {
  // ...
}

// Callers must remember parameter order
searchProducts("laptop", 500, 2000, "electronics", "price", "asc", 1, 20);
```

**After (TypeScript):**
```typescript
interface ProductSearchCriteria {
  query: string;
  priceRange: { min: number; max: number };
  category: string;
  sort: { field: string; order: "asc" | "desc" };
  pagination: { page: number; pageSize: number };
}

function searchProducts(criteria: ProductSearchCriteria): Product[] {
  // ...
}

// Clear and self-documenting at the call site
searchProducts({
  query: "laptop",
  priceRange: { min: 500, max: 2000 },
  category: "electronics",
  sort: { field: "price", order: "asc" },
  pagination: { page: 1, pageSize: 20 },
});
```

### Replace Conditional with Polymorphism

When if/else or switch statements dispatch on a type, replace with polymorphism.

**Before (TypeScript):**
```typescript
function calculateShippingCost(order: Order): number {
  switch (order.shippingMethod) {
    case "standard":
      return order.weight * 0.5 + 4.99;
    case "express":
      return order.weight * 1.2 + 14.99;
    case "overnight":
      return order.weight * 2.0 + 29.99;
    case "freight":
      return order.weight * 0.3 + 49.99 + (order.distance * 0.1);
    default:
      throw new Error(`Unknown shipping method: ${order.shippingMethod}`);
  }
}
```

**After (TypeScript):**
```typescript
interface ShippingStrategy {
  calculateCost(weight: number, distance: number): number;
}

class StandardShipping implements ShippingStrategy {
  calculateCost(weight: number): number {
    return weight * 0.5 + 4.99;
  }
}

class ExpressShipping implements ShippingStrategy {
  calculateCost(weight: number): number {
    return weight * 1.2 + 14.99;
  }
}

class OvernightShipping implements ShippingStrategy {
  calculateCost(weight: number): number {
    return weight * 2.0 + 29.99;
  }
}

class FreightShipping implements ShippingStrategy {
  calculateCost(weight: number, distance: number): number {
    return weight * 0.3 + 49.99 + (distance * 0.1);
  }
}

const shippingStrategies: Record<string, ShippingStrategy> = {
  standard: new StandardShipping(),
  express: new ExpressShipping(),
  overnight: new OvernightShipping(),
  freight: new FreightShipping(),
};

function calculateShippingCost(order: Order): number {
  const strategy = shippingStrategies[order.shippingMethod];
  if (!strategy) throw new Error(`Unknown shipping method: ${order.shippingMethod}`);
  return strategy.calculateCost(order.weight, order.distance);
}
```

---

## 3. Refactoring with Confidence

Never refactor without tests. The refactoring process should leave external behavior unchanged.

### The Safety Protocol

```
1. VERIFY  -- Ensure existing tests pass (green baseline)
2. REFACTOR -- Make one structural change at a time
3. TEST    -- Run tests after every change
4. COMMIT  -- Commit each passing refactoring step independently
5. REPEAT  -- Next refactoring step
```

### Writing Tests Before Refactoring

If the code lacks tests, write characterization tests first (see Section 6) to lock in current behavior.

**Example -- Testing before Extract Function (TypeScript):**
```typescript
// STEP 1: Write tests that capture current behavior
import { describe, it, expect } from "vitest";
import { processOrder } from "./order-processor";

describe("processOrder", () => {
  it("rejects orders with no items", () => {
    expect(() => processOrder({ items: [], customer: { email: "a@b.com" } }))
      .toThrow("Empty order");
  });

  it("calculates correct total with tax and free shipping", () => {
    const receipt = processOrder({
      items: [{ name: "Widget", price: 50, quantity: 3 }],
      customer: { email: "a@b.com" },
    });
    expect(receipt.subtotal).toBe(150);
    expect(receipt.shipping).toBe(0); // free over $100
    expect(receipt.total).toBeCloseTo(162); // 150 + 12 tax
  });

  it("adds shipping for orders under $100", () => {
    const receipt = processOrder({
      items: [{ name: "Widget", price: 10, quantity: 1 }],
      customer: { email: "a@b.com" },
    });
    expect(receipt.shipping).toBe(9.99);
  });
});

// STEP 2: Confirm tests pass against current implementation
// STEP 3: Perform Extract Function refactoring
// STEP 4: Confirm tests still pass -- behavior is preserved
```

### Snapshot Testing for Large Refactors

When refactoring complex output (HTML, JSON, reports), snapshot tests catch any unintended change.

```typescript
it("generates the same invoice HTML after refactoring", () => {
  const html = renderInvoice(sampleInvoice);
  expect(html).toMatchSnapshot();
});
```

### Continuous Integration Guard

Configure CI to run the full test suite on every commit. A refactoring branch should never break tests.

```yaml
# .github/workflows/refactor-safety.yml
name: Refactoring Safety Net
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm test -- --coverage
      - name: Fail if coverage drops
        run: |
          COVERAGE=$(npx coverage-summary --json | jq '.total.lines.pct')
          if (( $(echo "$COVERAGE < 80" | bc -l) )); then
            echo "Coverage dropped below 80%: $COVERAGE%"
            exit 1
          fi
```

---

## 4. Dependency Reduction Patterns

Tight coupling makes code hard to change, test, and reuse. These patterns reduce dependencies.

### Dependency Injection

Pass dependencies in rather than creating them internally.

**Before (TypeScript) -- Hard-coded dependencies:**
```typescript
class OrderService {
  private db = new PostgresDatabase();
  private mailer = new SmtpMailer();
  private logger = new FileLogger("/var/log/orders.log");

  async placeOrder(order: Order): Promise<string> {
    this.logger.info(`Placing order ${order.id}`);
    const id = await this.db.insert("orders", order);
    await this.mailer.send(order.customerEmail, "Order placed", `Order #${id}`);
    return id;
  }
}

// Cannot test without a real database, SMTP server, and filesystem
```

**After (TypeScript) -- Injected dependencies:**
```typescript
interface Database {
  insert(table: string, data: Record<string, unknown>): Promise<string>;
}

interface Mailer {
  send(to: string, subject: string, body: string): Promise<void>;
}

interface Logger {
  info(message: string): void;
  error(message: string, err?: Error): void;
}

class OrderService {
  constructor(
    private readonly db: Database,
    private readonly mailer: Mailer,
    private readonly logger: Logger
  ) {}

  async placeOrder(order: Order): Promise<string> {
    this.logger.info(`Placing order ${order.id}`);
    const id = await this.db.insert("orders", order);
    await this.mailer.send(order.customerEmail, "Order placed", `Order #${id}`);
    return id;
  }
}

// Now easily testable with mocks
const mockDb: Database = { insert: vi.fn().mockResolvedValue("order-123") };
const mockMailer: Mailer = { send: vi.fn().mockResolvedValue(undefined) };
const mockLogger: Logger = { info: vi.fn(), error: vi.fn() };

const service = new OrderService(mockDb, mockMailer, mockLogger);
```

### Interface Extraction

When a class depends on a concrete implementation, extract an interface and depend on the abstraction.

**Before (Python):**
```python
class ReportGenerator:
    def __init__(self):
        self.storage = S3Storage("my-bucket", "us-east-1")

    def generate(self, data: dict) -> str:
        content = self._build_report(data)
        url = self.storage.upload(f"reports/{data['id']}.pdf", content)
        return url
```

**After (Python):**
```python
from abc import ABC, abstractmethod

class Storage(ABC):
    @abstractmethod
    def upload(self, path: str, content: bytes) -> str: ...

class S3Storage(Storage):
    def __init__(self, bucket: str, region: str):
        self.bucket = bucket
        self.region = region

    def upload(self, path: str, content: bytes) -> str:
        # S3-specific upload logic
        ...

class LocalStorage(Storage):
    def __init__(self, base_dir: str):
        self.base_dir = base_dir

    def upload(self, path: str, content: bytes) -> str:
        full_path = os.path.join(self.base_dir, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wb") as f:
            f.write(content)
        return f"file://{full_path}"

class ReportGenerator:
    def __init__(self, storage: Storage):
        self.storage = storage

    def generate(self, data: dict) -> str:
        content = self._build_report(data)
        return self.storage.upload(f"reports/{data['id']}.pdf", content)

# Production
generator = ReportGenerator(S3Storage("my-bucket", "us-east-1"))

# Tests
generator = ReportGenerator(LocalStorage("/tmp/test-reports"))
```

### Facade Pattern for Simplifying Complex Subsystems

Wrap a complex set of classes behind a simple interface to reduce the number of dependencies callers need.

**Before (TypeScript):**
```typescript
// Callers must know about and coordinate multiple subsystems
const tokenizer = new Tokenizer(config.language);
const parser = new Parser(tokenizer, config.strict);
const ast = parser.parse(sourceCode);
const analyzer = new SemanticAnalyzer(ast, symbolTable);
const errors = analyzer.validate();
const optimizer = new AstOptimizer(ast, optimizationLevel);
const optimizedAst = optimizer.optimize();
const generator = new CodeGenerator(optimizedAst, targetPlatform);
const output = generator.emit();
```

**After (TypeScript):**
```typescript
class Compiler {
  constructor(private config: CompilerConfig) {}

  compile(sourceCode: string): CompilationResult {
    const tokenizer = new Tokenizer(this.config.language);
    const parser = new Parser(tokenizer, this.config.strict);
    const ast = parser.parse(sourceCode);

    const analyzer = new SemanticAnalyzer(ast, new SymbolTable());
    const errors = analyzer.validate();
    if (errors.length) return { success: false, errors };

    const optimizer = new AstOptimizer(ast, this.config.optimizationLevel);
    const optimizedAst = optimizer.optimize();

    const generator = new CodeGenerator(optimizedAst, this.config.target);
    return { success: true, output: generator.emit(), errors: [] };
  }
}

// Callers only depend on Compiler
const compiler = new Compiler(config);
const result = compiler.compile(sourceCode);
```

---

## 5. Architecture-Level Refactoring

For large-scale changes that cannot be done in a single commit or sprint.

### Strangler Fig Pattern

Gradually replace a legacy system by routing new functionality through a new system, while keeping the old system running.

```
Phase 1: New requests → [Router] → Old System (100%)
Phase 2: New requests → [Router] → Old System (70%) + New System (30%)
Phase 3: New requests → [Router] → Old System (20%) + New System (80%)
Phase 4: New requests → [Router] → New System (100%), Old System decommissioned
```

**Implementation (TypeScript):**
```typescript
// The router decides which system handles each request
class OrderRouter {
  constructor(
    private legacyService: LegacyOrderService,
    private newService: ModernOrderService,
    private featureFlags: FeatureFlags
  ) {}

  async placeOrder(order: Order): Promise<OrderResult> {
    if (this.featureFlags.isEnabled("modern-order-processing", order.region)) {
      return this.newService.placeOrder(order);
    }
    return this.legacyService.placeOrder(order);
  }

  async getOrder(id: string): Promise<Order> {
    // Try new system first, fall back to legacy
    const order = await this.newService.getOrder(id);
    if (order) return order;
    return this.legacyService.getOrder(id);
  }
}
```

### Branch by Abstraction

Replace a dependency by first introducing an abstraction layer, then swapping the implementation behind it.

```
Step 1: Code → Concrete Dependency (direct usage)
Step 2: Code → Abstraction → Concrete Dependency (introduce interface)
Step 3: Code → Abstraction → New Implementation (swap implementation)
Step 4: Code → New Implementation (optionally remove abstraction)
```

**Example (Python):**
```python
# STEP 1: Direct usage of legacy payment processor
class CheckoutService:
    def charge(self, amount: float, card_token: str):
        legacy_client = LegacyPaymentGateway()
        return legacy_client.process_charge(amount, card_token, "USD")

# STEP 2: Introduce abstraction
class PaymentProcessor(ABC):
    @abstractmethod
    def charge(self, amount: float, card_token: str, currency: str) -> ChargeResult: ...

class LegacyPaymentAdapter(PaymentProcessor):
    def charge(self, amount: float, card_token: str, currency: str) -> ChargeResult:
        client = LegacyPaymentGateway()
        return client.process_charge(amount, card_token, currency)

class CheckoutService:
    def __init__(self, payment: PaymentProcessor):
        self.payment = payment

    def charge(self, amount: float, card_token: str):
        return self.payment.charge(amount, card_token, "USD")

# STEP 3: Build new implementation, swap it in
class StripePaymentProcessor(PaymentProcessor):
    def __init__(self, api_key: str):
        self.stripe = stripe.Client(api_key)

    def charge(self, amount: float, card_token: str, currency: str) -> ChargeResult:
        intent = self.stripe.PaymentIntent.create(
            amount=int(amount * 100),
            currency=currency,
            payment_method=card_token,
            confirm=True,
        )
        return ChargeResult(id=intent.id, status=intent.status)

# STEP 4: Production wiring -- old implementation is now fully replaced
checkout = CheckoutService(StripePaymentProcessor(os.environ["STRIPE_KEY"]))
```

### Parallel Change (Expand-Migrate-Contract)

Safely change an interface that has many callers by running old and new versions side by side.

```
1. EXPAND   -- Add new interface alongside old one
2. MIGRATE  -- Move callers to new interface one at a time
3. CONTRACT -- Remove old interface when no callers remain
```

**Example (TypeScript):**
```typescript
// EXPAND: Add new method, keep old one working
class UserService {
  /** @deprecated Use findUsers(criteria) instead */
  getUser(id: string): User {
    return this.findUsers({ id })[0];
  }

  // New, more flexible interface
  findUsers(criteria: UserSearchCriteria): User[] {
    // ...
  }
}

// MIGRATE: Update callers one by one
// Before: const user = userService.getUser("123");
// After:  const [user] = userService.findUsers({ id: "123" });

// CONTRACT: Remove deprecated method when migration is complete
```

---

## 6. Legacy Code Strategies

Legacy code is code without tests (per Michael Feathers). These strategies make it safe to modify.

### Characterization Tests

Tests that document what the code *actually does*, not what it *should do*. Write these before changing anything.

**Process:**
```
1. Identify the code to change
2. Write a test that calls it with known inputs
3. Run the test and observe the ACTUAL output
4. Set the assertion to match the actual output
5. Repeat for edge cases and error paths
6. Now refactor with the characterization tests as a safety net
```

**Example (Python):**
```python
# Legacy function with unknown behavior in edge cases
def calculate_discount(price, customer_type, years_active):
    # 200 lines of spaghetti logic with nested ifs
    ...

# Characterization tests -- discover and lock in current behavior
class TestCalculateDiscountCharacterization:
    """These tests document ACTUAL behavior, not desired behavior."""

    def test_regular_customer_no_discount(self):
        assert calculate_discount(100.0, "regular", 0) == 100.0

    def test_premium_customer_gets_10_percent(self):
        assert calculate_discount(100.0, "premium", 1) == 90.0

    def test_loyalty_discount_after_5_years(self):
        # Discovered: loyalty discount stacks with premium discount
        assert calculate_discount(100.0, "premium", 6) == 81.0

    def test_negative_price_not_handled(self):
        # Discovered: negative prices produce unexpected results
        # This documents a bug, not desired behavior
        assert calculate_discount(-50.0, "regular", 0) == -50.0

    def test_unknown_customer_type_returns_full_price(self):
        assert calculate_discount(100.0, "unknown", 0) == 100.0
```

### Finding Seams

A seam is a place where behavior can be changed without editing the code at that point. Seams are used to break dependencies for testing.

**Object Seam -- Override a method in a subclass for testing:**
```python
# Legacy code with hard-coded dependency
class ReportService:
    def generate_monthly_report(self):
        data = self._fetch_data_from_database()  # Hard to test
        return self._format_report(data)

    def _fetch_data_from_database(self):
        return db.query("SELECT * FROM sales WHERE month = current_month()")

    def _format_report(self, data):
        # Complex formatting logic to test
        ...

# Test seam: subclass and override the database method
class TestableReportService(ReportService):
    def __init__(self, fake_data):
        self._fake_data = fake_data

    def _fetch_data_from_database(self):
        return self._fake_data  # No database needed

# Now test the formatting logic in isolation
def test_report_formatting():
    service = TestableReportService([
        {"product": "Widget", "revenue": 1000},
        {"product": "Gadget", "revenue": 2000},
    ])
    report = service.generate_monthly_report()
    assert "Total Revenue: $3,000" in report
```

**Preprocessing Seam -- Use environment variables or config to change behavior:**
```typescript
class NotificationService {
  async sendAlert(message: string): Promise<void> {
    if (process.env.NODE_ENV === "test") {
      // Seam: skip real notifications in tests
      testNotifications.push(message);
      return;
    }
    await twilioClient.sendSms(this.alertNumber, message);
  }
}
```

### Sprout Method / Sprout Class

When adding new behavior to legacy code, write the new code in a separate, tested method or class, then call it from the legacy code. This avoids modifying untested legacy logic.

**Before (TypeScript):**
```typescript
// Legacy untested function -- 500 lines long
function processPayroll(employees: Employee[]): PayrollResult {
  // ... 200 lines of existing logic ...

  // NEW REQUIREMENT: Add tax withholding calculation
  // DON'T: Add more code to this 500-line function
  // DO: Sprout a new, tested function

  // ... 300 more lines of existing logic ...
}
```

**After (TypeScript):**
```typescript
// New function, fully tested in isolation
function calculateTaxWithholding(employee: Employee, grossPay: number): TaxWithholding {
  const federalRate = getFederalTaxRate(employee.filingStatus, grossPay);
  const stateRate = getStateTaxRate(employee.state, grossPay);
  return {
    federal: grossPay * federalRate,
    state: grossPay * stateRate,
    total: grossPay * (federalRate + stateRate),
  };
}

// Minimal edit to legacy function -- just a single call inserted
function processPayroll(employees: Employee[]): PayrollResult {
  // ... 200 lines of existing logic ...

  const withholding = calculateTaxWithholding(employee, grossPay);

  // ... 300 more lines of existing logic ...
}
```

---

## 7. TypeScript-Specific Refactoring

### Replace `any` with Proper Types

**Before:**
```typescript
function processApiResponse(response: any): any {
  if (response.data && response.data.users) {
    return response.data.users.map((user: any) => ({
      id: user.id,
      name: user.name,
      email: user.email,
    }));
  }
  return [];
}
```

**After:**
```typescript
interface ApiResponse<T> {
  data: T | null;
  error?: string;
}

interface UsersData {
  users: ApiUser[];
}

interface ApiUser {
  id: string;
  name: string;
  email: string;
  // ... other fields returned by API
}

interface UserSummary {
  id: string;
  name: string;
  email: string;
}

function processApiResponse(response: ApiResponse<UsersData>): UserSummary[] {
  if (!response.data?.users) return [];
  return response.data.users.map(({ id, name, email }) => ({ id, name, email }));
}
```

### Replace Enum with Discriminated Union

**Before:**
```typescript
enum ShapeType {
  Circle,
  Rectangle,
  Triangle,
}

interface Shape {
  type: ShapeType;
  radius?: number;
  width?: number;
  height?: number;
  base?: number;
  sideA?: number;
  sideB?: number;
  sideC?: number;
}

function area(shape: Shape): number {
  switch (shape.type) {
    case ShapeType.Circle:
      return Math.PI * shape.radius! ** 2;       // Unsafe ! assertion
    case ShapeType.Rectangle:
      return shape.width! * shape.height!;         // Unsafe
    case ShapeType.Triangle:
      return 0.5 * shape.base! * shape.height!;   // Unsafe
  }
}
```

**After:**
```typescript
type Shape =
  | { type: "circle"; radius: number }
  | { type: "rectangle"; width: number; height: number }
  | { type: "triangle"; base: number; height: number };

function area(shape: Shape): number {
  switch (shape.type) {
    case "circle":
      return Math.PI * shape.radius ** 2;       // Type-safe, no assertion needed
    case "rectangle":
      return shape.width * shape.height;          // Type-safe
    case "triangle":
      return 0.5 * shape.base * shape.height;    // Type-safe
  }
}

// Exhaustiveness checking: add a default case that TypeScript enforces
function area(shape: Shape): number {
  switch (shape.type) {
    case "circle": return Math.PI * shape.radius ** 2;
    case "rectangle": return shape.width * shape.height;
    case "triangle": return 0.5 * shape.base * shape.height;
    default: {
      const _exhaustive: never = shape;
      throw new Error(`Unknown shape: ${_exhaustive}`);
    }
  }
}
```

### Replace Callback Hell with Async/Await

**Before:**
```typescript
function fetchUserData(userId: string, callback: (err: Error | null, data?: UserData) => void) {
  getUser(userId, (err, user) => {
    if (err) return callback(err);
    getOrders(user.id, (err, orders) => {
      if (err) return callback(err);
      getPreferences(user.id, (err, prefs) => {
        if (err) return callback(err);
        callback(null, { user, orders, preferences: prefs });
      });
    });
  });
}
```

**After:**
```typescript
async function fetchUserData(userId: string): Promise<UserData> {
  const user = await getUser(userId);
  const [orders, preferences] = await Promise.all([
    getOrders(user.id),
    getPreferences(user.id),
  ]);
  return { user, orders, preferences };
}
```

### Extract Type Utilities to Reduce Duplication

**Before:**
```typescript
interface CreateUserInput {
  name: string;
  email: string;
  role: "admin" | "editor" | "viewer";
}

interface UpdateUserInput {
  name?: string;
  email?: string;
  role?: "admin" | "editor" | "viewer";
}

interface UserResponse {
  id: string;
  name: string;
  email: string;
  role: "admin" | "editor" | "viewer";
  createdAt: Date;
}
```

**After:**
```typescript
type UserRole = "admin" | "editor" | "viewer";

interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  createdAt: Date;
}

type CreateUserInput = Pick<User, "name" | "email" | "role">;
type UpdateUserInput = Partial<CreateUserInput>;
type UserResponse = User;
```

---

## 8. Python-Specific Refactoring

### Replace Manual Resource Management with Context Managers

**Before:**
```python
def process_data(input_path, output_path):
    f_in = open(input_path, "r")
    try:
        data = f_in.read()
    finally:
        f_in.close()

    result = transform(data)

    f_out = open(output_path, "w")
    try:
        f_out.write(result)
    finally:
        f_out.close()
```

**After:**
```python
def process_data(input_path: str, output_path: str) -> None:
    with open(input_path, "r") as f_in:
        data = f_in.read()

    result = transform(data)

    with open(output_path, "w") as f_out:
        f_out.write(result)
```

### Replace Nested Loops with Comprehensions and itertools

**Before:**
```python
def find_common_tags(articles):
    result = []
    for article in articles:
        for tag in article.tags:
            if tag.category == "technology":
                if tag.name not in result:
                    result.append(tag.name)
    result.sort()
    return result
```

**After:**
```python
def find_common_tags(articles: list[Article]) -> list[str]:
    tech_tags = {
        tag.name
        for article in articles
        for tag in article.tags
        if tag.category == "technology"
    }
    return sorted(tech_tags)
```

### Replace Dict with Dataclass or TypedDict

**Before:**
```python
def create_user(name, email, age):
    return {
        "name": name,
        "email": email,
        "age": age,
        "active": True,
        "created_at": datetime.now(),
    }

# No type safety, no autocomplete, typos silently create new keys
user = create_user("Alice", "alice@example.com", 30)
user["emal"]  # Typo -- no error, just None
```

**After:**
```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class User:
    name: str
    email: str
    age: int
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)

user = User(name="Alice", email="alice@example.com", age=30)
user.emal  # AttributeError -- caught immediately
```

### Replace Inheritance with Composition

**Before:**
```python
class Animal:
    def __init__(self, name): self.name = name
    def eat(self): print(f"{self.name} eats")

class Flyable(Animal):
    def fly(self): print(f"{self.name} flies")

class Swimmable(Animal):
    def swim(self): print(f"{self.name} swims")

# Diamond problem: Duck both flies and swims
class Duck(Flyable, Swimmable):  # Complex MRO, fragile hierarchy
    pass
```

**After:**
```python
from dataclasses import dataclass
from typing import Protocol

class CanFly(Protocol):
    def fly(self) -> None: ...

class CanSwim(Protocol):
    def swim(self) -> None: ...

@dataclass
class Wings:
    def fly(self, name: str) -> None:
        print(f"{name} flies with wings")

@dataclass
class Fins:
    def swim(self, name: str) -> None:
        print(f"{name} swims with fins")

@dataclass
class Duck:
    name: str
    wings: Wings = field(default_factory=Wings)
    fins: Fins = field(default_factory=Fins)

    def fly(self) -> None:
        self.wings.fly(self.name)

    def swim(self) -> None:
        self.fins.swim(self.name)
```

### Replace Global State with Dependency Injection

**Before:**
```python
# settings.py
config = {}

def load_config():
    global config
    config = json.load(open("config.json"))

# service.py
from settings import config

class PaymentService:
    def process(self, amount):
        api_key = config["payment_api_key"]  # Hidden global dependency
        timeout = config["payment_timeout"]
        # ...
```

**After:**
```python
@dataclass(frozen=True)
class PaymentConfig:
    api_key: str
    timeout: int = 30

class PaymentService:
    def __init__(self, config: PaymentConfig):
        self._config = config

    def process(self, amount: float) -> PaymentResult:
        # Dependencies are explicit and testable
        ...

# Wiring at application startup
config = PaymentConfig(
    api_key=os.environ["PAYMENT_API_KEY"],
    timeout=int(os.environ.get("PAYMENT_TIMEOUT", "30")),
)
service = PaymentService(config)
```

---

## 9. Technical Debt Tracking and Prioritization

### Categorizing Technical Debt

| Category | Description | Example | Risk |
|----------|-------------|---------|------|
| **Deliberate-Prudent** | Conscious tradeoff with a plan | "Ship now, refactor in sprint 3" | Low if tracked |
| **Deliberate-Reckless** | Known shortcuts with no plan | "We don't have time for tests" | High |
| **Inadvertent-Prudent** | Better approach discovered later | "Now that we understand the domain, this model is wrong" | Medium |
| **Inadvertent-Reckless** | Lack of knowledge or skill | Junior developer's first codebase | High |

### Tracking Debt in Code

Use consistent TODO/FIXME comments that can be searched and measured.

```typescript
// TECH-DEBT(high): Replace raw SQL with query builder -- SQL injection risk
// Ticket: PROJ-1234
// Added: 2025-03-15
const users = await db.query(`SELECT * FROM users WHERE name = '${name}'`);

// TECH-DEBT(medium): Extract notification logic into NotificationService
// This function handles both order processing and email sending
// Ticket: PROJ-1235

// TECH-DEBT(low): Rename 'data' to 'customerProfile' for clarity
```

### Prioritization Matrix

Prioritize based on **impact** (how much it slows development or risks bugs) and **effort** (how long to fix).

```
                    High Impact
                        |
    Quick Wins          |       Strategic Investments
    (Do First)          |       (Plan for next sprint)
                        |
  Low Effort -----------+----------- High Effort
                        |
    Don't Bother        |       Avoid / Defer
    (Leave it)          |       (Not worth it now)
                        |
                    Low Impact
```

**Practical prioritization criteria:**

1. **Blocks new features** -- highest priority
2. **Causes production incidents** -- highest priority
3. **Slows every developer, every day** (slow builds, flaky tests) -- high priority
4. **Concentrated in code that changes often** -- high priority
5. **In stable code that rarely changes** -- low priority
6. **Cosmetic or stylistic** -- lowest priority

### Measuring Debt

```bash
# Count TECH-DEBT comments by severity
grep -r "TECH-DEBT(high)" --include="*.ts" --include="*.py" -c
grep -r "TECH-DEBT(medium)" --include="*.ts" --include="*.py" -c
grep -r "TECH-DEBT(low)" --include="*.ts" --include="*.py" -c

# Find the most changed files (likely high-debt areas)
git log --format=format: --name-only --since="6 months ago" | sort | uniq -c | sort -rn | head -20

# Find files with the most complexity (cyclomatic complexity)
npx ts-complexity src/        # TypeScript
radon cc src/ -a -nc          # Python
```

### Debt Reduction Sprint Cadence

A sustainable approach to paying down debt:

```
- Allocate 15-20% of each sprint to tech debt reduction
- Rotate "debt champion" role among team members
- Track debt items on the backlog alongside features
- Celebrate debt reduction in sprint reviews
- Never defer high-severity debt beyond two sprints
```

---

## 10. When NOT to Refactor

Refactoring has costs. Avoid refactoring when:

### Code That Will Be Replaced

```
If a module is scheduled for replacement or retirement, refactoring it is waste.
Exception: If replacement is 6+ months out and the code is actively blocking work.
```

### Working Code That Nobody Touches

```
Stable, untouched code that works is low priority. Refactoring it risks introducing
bugs for no practical benefit. Focus effort on code that changes frequently.
```

### During a Critical Deadline

```
Refactoring requires focus and comprehensive testing. Under deadline pressure,
refactoring increases the risk of shipping regressions. Note the debt and return later.
```

### Without Tests

```
Refactoring without a test safety net is dangerous. Write characterization tests first
(Section 6), or defer the refactoring until tests exist.
Exception: Rename refactoring with IDE support is generally safe without tests.
```

### Premature Abstraction

```
Do not refactor to "prepare for future requirements" that may never arrive.
Wait until you have three concrete examples of a pattern before extracting an abstraction.
Rule of Three: The first time, just do it. The second time, wince at the duplication.
The third time, refactor.
```

### Cosmetic-Only Changes on Shared Code

```
Reformatting or renaming across a large shared codebase creates noisy diffs that
cause merge conflicts for every other developer. Coordinate with the team first,
or limit cosmetic changes to files already being modified for other reasons.
```

### Decision Checklist

Before starting a refactoring, answer these questions:

```
[ ] Is there test coverage for the code being refactored?
[ ] Is this code actively causing pain (bugs, slow development, confusion)?
[ ] Will this code be modified again in the near future?
[ ] Is the team aligned on the refactoring approach?
[ ] Is there time to complete the refactoring without leaving it half-done?
[ ] Has the refactoring goal been clearly defined (not open-ended "cleanup")?

If any answer is NO, reconsider or address the gap first.
```

---

## Additional Resources

- *Refactoring: Improving the Design of Existing Code* by Martin Fowler
- *Working Effectively with Legacy Code* by Michael Feathers
- *Clean Code* by Robert C. Martin
- Refactoring catalog: https://refactoring.com/catalog/
- SourceMaking patterns: https://sourcemaking.com/refactoring
