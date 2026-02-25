---
name: event-sourcing
description: Event sourcing and CQRS patterns covering event store design, aggregate roots, command handlers, event projections, snapshots, EventStoreDB integration, eventual consistency, saga orchestration, and domain-driven design with TypeScript and Python implementations.
---

# Event Sourcing & CQRS

This skill should be used when implementing event sourcing, CQRS (Command Query Responsibility Segregation), or event-driven domain models. It covers event stores, projections, and domain-driven patterns.

## When to Use This Skill

Use this skill when you need to:

- Build audit-complete systems with full history
- Implement CQRS for read/write optimization
- Design event-driven domain models
- Create event projections and read models
- Handle eventual consistency patterns
- Implement sagas for distributed workflows

## Event Store Design

```typescript
// Core event types
interface DomainEvent {
  eventId: string;
  aggregateId: string;
  aggregateType: string;
  eventType: string;
  payload: Record<string, unknown>;
  metadata: { userId: string; timestamp: string; version: number };
}

// Event store interface
interface EventStore {
  append(aggregateId: string, events: DomainEvent[], expectedVersion: number): Promise<void>;
  getEvents(aggregateId: string, fromVersion?: number): Promise<DomainEvent[]>;
  getAllEvents(fromPosition?: number, limit?: number): Promise<DomainEvent[]>;
}

// PostgreSQL-backed event store
class PgEventStore implements EventStore {
  async append(aggregateId: string, events: DomainEvent[], expectedVersion: number) {
    await this.db.transaction(async (tx) => {
      // Optimistic concurrency check
      const current = await tx.query(
        "SELECT MAX(version) as version FROM events WHERE aggregate_id = $1",
        [aggregateId],
      );
      const currentVersion = current.rows[0]?.version ?? 0;

      if (currentVersion !== expectedVersion) {
        throw new ConcurrencyError(`Expected version ${expectedVersion}, got ${currentVersion}`);
      }

      for (let i = 0; i < events.length; i++) {
        await tx.query(
          `INSERT INTO events (event_id, aggregate_id, aggregate_type, event_type, payload, metadata, version)
           VALUES ($1, $2, $3, $4, $5, $6, $7)`,
          [events[i].eventId, aggregateId, events[i].aggregateType, events[i].eventType,
           events[i].payload, events[i].metadata, expectedVersion + i + 1],
        );
      }
    });
  }

  async getEvents(aggregateId: string, fromVersion = 0) {
    const result = await this.db.query(
      "SELECT * FROM events WHERE aggregate_id = $1 AND version > $2 ORDER BY version",
      [aggregateId, fromVersion],
    );
    return result.rows;
  }
}
```

## Aggregate Root

```typescript
abstract class AggregateRoot {
  private uncommittedEvents: DomainEvent[] = [];
  protected version = 0;

  protected apply(event: DomainEvent) {
    this.when(event);
    this.version++;
    this.uncommittedEvents.push(event);
  }

  protected abstract when(event: DomainEvent): void;

  getUncommittedEvents() {
    return [...this.uncommittedEvents];
  }

  clearUncommittedEvents() {
    this.uncommittedEvents = [];
  }

  loadFromHistory(events: DomainEvent[]) {
    for (const event of events) {
      this.when(event);
      this.version++;
    }
  }
}

// Order aggregate
class Order extends AggregateRoot {
  private id!: string;
  private status!: string;
  private items: OrderItem[] = [];
  private total = 0;

  static create(id: string, customerId: string, items: OrderItem[]): Order {
    const order = new Order();
    order.apply({
      eventId: crypto.randomUUID(),
      aggregateId: id,
      aggregateType: "Order",
      eventType: "OrderCreated",
      payload: { customerId, items, total: items.reduce((sum, i) => sum + i.price * i.quantity, 0) },
      metadata: { userId: customerId, timestamp: new Date().toISOString(), version: 0 },
    });
    return order;
  }

  confirm() {
    if (this.status !== "pending") throw new Error("Can only confirm pending orders");
    this.apply({
      eventId: crypto.randomUUID(),
      aggregateId: this.id,
      aggregateType: "Order",
      eventType: "OrderConfirmed",
      payload: { confirmedAt: new Date().toISOString() },
      metadata: { userId: "", timestamp: new Date().toISOString(), version: this.version },
    });
  }

  protected when(event: DomainEvent) {
    switch (event.eventType) {
      case "OrderCreated":
        this.id = event.aggregateId;
        this.status = "pending";
        this.items = event.payload.items as OrderItem[];
        this.total = event.payload.total as number;
        break;
      case "OrderConfirmed":
        this.status = "confirmed";
        break;
    }
  }
}
```

## Command Handler

```typescript
class OrderCommandHandler {
  constructor(
    private eventStore: EventStore,
    private eventBus: EventBus,
  ) {}

  async handle(command: CreateOrderCommand) {
    const order = Order.create(command.orderId, command.customerId, command.items);
    await this.eventStore.append(command.orderId, order.getUncommittedEvents(), 0);
    await this.eventBus.publish(order.getUncommittedEvents());
    order.clearUncommittedEvents();
  }

  async handleConfirm(command: ConfirmOrderCommand) {
    const events = await this.eventStore.getEvents(command.orderId);
    const order = new Order();
    order.loadFromHistory(events);

    order.confirm();

    await this.eventStore.append(command.orderId, order.getUncommittedEvents(), order.version);
    await this.eventBus.publish(order.getUncommittedEvents());
  }
}
```

## Read Model Projection

```typescript
// Project events into a read-optimized view
class OrderListProjection {
  constructor(private db: Database) {}

  async handle(event: DomainEvent) {
    switch (event.eventType) {
      case "OrderCreated":
        await this.db.query(
          `INSERT INTO order_summary (id, customer_id, total, status, created_at)
           VALUES ($1, $2, $3, 'pending', $4)`,
          [event.aggregateId, event.payload.customerId, event.payload.total, event.metadata.timestamp],
        );
        break;

      case "OrderConfirmed":
        await this.db.query(
          `UPDATE order_summary SET status = 'confirmed', confirmed_at = $1 WHERE id = $2`,
          [event.payload.confirmedAt, event.aggregateId],
        );
        break;

      case "OrderShipped":
        await this.db.query(
          `UPDATE order_summary SET status = 'shipped', tracking = $1 WHERE id = $2`,
          [event.payload.trackingNumber, event.aggregateId],
        );
        break;
    }
  }
}

// Query the read model (fast, denormalized)
async function getOrderSummary(orderId: string) {
  return db.query("SELECT * FROM order_summary WHERE id = $1", [orderId]);
}

async function getCustomerOrders(customerId: string, page: number) {
  return db.query(
    "SELECT * FROM order_summary WHERE customer_id = $1 ORDER BY created_at DESC LIMIT 20 OFFSET $2",
    [customerId, (page - 1) * 20],
  );
}
```

## Additional Resources

- EventStoreDB: https://www.eventstore.com/
- Martin Fowler on Event Sourcing: https://martinfowler.com/eaaDev/EventSourcing.html
- CQRS pattern: https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs
- Eventuous (C#): https://eventuous.dev/
