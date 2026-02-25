---
name: dependency-injection
description: Dependency injection and inversion of control patterns covering TypeScript DI with tsyringe and InversifyJS, Python with dependency-injector, constructor injection, factory patterns, scope management (singleton/transient/scoped), testing with mocks, and clean architecture boundaries.
---

# Dependency Injection

This skill should be used when implementing dependency injection and inversion of control in applications. It covers DI containers, constructor injection, factory patterns, and testing strategies.

## When to Use This Skill

Use this skill when you need to:

- Decouple components from their dependencies
- Make code testable with injectable mocks
- Manage object lifetimes (singleton/transient/scoped)
- Implement clean architecture boundaries
- Configure DI containers in TypeScript or Python

## TypeScript with tsyringe

```typescript
import { container, injectable, inject, singleton } from "tsyringe";

// Define interfaces
interface Logger { log(msg: string): void; }
interface UserRepository { findById(id: string): Promise<User | null>; }

// Implementations
@singleton()
class ConsoleLogger implements Logger {
  log(msg: string) { console.log(`[${new Date().toISOString()}] ${msg}`); }
}

@injectable()
class PrismaUserRepository implements UserRepository {
  constructor(@inject("PrismaClient") private prisma: PrismaClient) {}

  async findById(id: string) {
    return this.prisma.user.findUnique({ where: { id } });
  }
}

@injectable()
class UserService {
  constructor(
    @inject("UserRepository") private repo: UserRepository,
    @inject("Logger") private logger: Logger,
  ) {}

  async getUser(id: string) {
    this.logger.log(`Fetching user ${id}`);
    const user = await this.repo.findById(id);
    if (!user) throw new Error("User not found");
    return user;
  }
}

// Register dependencies
container.register("Logger", { useClass: ConsoleLogger });
container.register("UserRepository", { useClass: PrismaUserRepository });
container.register("PrismaClient", { useValue: new PrismaClient() });

// Resolve
const userService = container.resolve(UserService);
```

## Manual DI (No Container)

```typescript
// Simple constructor injection — no library needed
interface EmailSender {
  send(to: string, subject: string, body: string): Promise<void>;
}

interface OrderRepository {
  save(order: Order): Promise<void>;
  findById(id: string): Promise<Order | null>;
}

class OrderService {
  constructor(
    private readonly orders: OrderRepository,
    private readonly email: EmailSender,
  ) {}

  async placeOrder(dto: CreateOrderDto): Promise<Order> {
    const order = Order.create(dto);
    await this.orders.save(order);
    await this.email.send(dto.customerEmail, "Order Confirmed", `Order #${order.id}`);
    return order;
  }
}

// Composition root — wire everything together in one place
function createApp() {
  const db = new PrismaClient();
  const emailSender = new ResendEmailSender(process.env.RESEND_API_KEY!);
  const orderRepo = new PrismaOrderRepository(db);
  const orderService = new OrderService(orderRepo, emailSender);
  const orderController = new OrderController(orderService);
  return { orderController };
}

// Testing — inject mocks
describe("OrderService", () => {
  it("sends confirmation email on order", async () => {
    const mockRepo: OrderRepository = {
      save: vi.fn(),
      findById: vi.fn(),
    };
    const mockEmail: EmailSender = { send: vi.fn() };
    const service = new OrderService(mockRepo, mockEmail);

    await service.placeOrder({ customerEmail: "test@example.com", items: [] });

    expect(mockEmail.send).toHaveBeenCalledWith(
      "test@example.com",
      "Order Confirmed",
      expect.stringContaining("Order #"),
    );
  });
});
```

## Python with dependency-injector

```python
from dependency_injector import containers, providers
from dependency_injector.wiring import inject, Provide

class UserRepository:
    def __init__(self, db_session):
        self.db = db_session

    def find_by_id(self, user_id: str):
        return self.db.query(User).get(user_id)

class UserService:
    def __init__(self, repo: UserRepository, logger):
        self.repo = repo
        self.logger = logger

    def get_user(self, user_id: str):
        self.logger.info(f"Fetching user {user_id}")
        user = self.repo.find_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return user

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    db_engine = providers.Singleton(create_engine, config.database_url)
    db_session = providers.Factory(Session, bind=db_engine)

    user_repository = providers.Factory(UserRepository, db_session=db_session)
    logger = providers.Singleton(logging.getLogger, "app")
    user_service = providers.Factory(UserService, repo=user_repository, logger=logger)

# Usage
container = Container()
container.config.database_url.from_env("DATABASE_URL")

# FastAPI integration
@app.get("/users/{user_id}")
@inject
async def get_user(
    user_id: str,
    service: UserService = Depends(Provide[Container.user_service]),
):
    return service.get_user(user_id)

# Testing with overrides
def test_get_user():
    with container.user_repository.override(providers.Factory(MockUserRepository)):
        service = container.user_service()
        user = service.get_user("123")
        assert user.id == "123"
```

## Scope Patterns

```typescript
// Singleton — one instance for entire app lifetime
// Use for: loggers, config, database connections
@singleton()
class AppConfig { /* ... */ }

// Transient — new instance every time
// Use for: request handlers, command objects
@injectable()
class RequestHandler { /* ... */ }

// Scoped — one instance per scope (e.g., per HTTP request)
// Use for: database transactions, unit of work
class RequestScope {
  private instances = new Map<string, unknown>();

  resolve<T>(key: string, factory: () => T): T {
    if (!this.instances.has(key)) {
      this.instances.set(key, factory());
    }
    return this.instances.get(key) as T;
  }
}
```

## Additional Resources

- tsyringe: https://github.com/microsoft/tsyringe
- InversifyJS: https://inversify.io/
- dependency-injector (Python): https://python-dependency-injector.ets-labs.org/
- Clean Architecture: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
