---
name: microservices-architecture
description: Microservices architecture patterns including service design, API gateways, service mesh, inter-service communication, event-driven architecture, circuit breakers, distributed systems, and production deployment.
---

# Microservices Architecture

This skill should be used when the user needs to design, implement, or work with microservices architectures. It covers service design patterns, inter-service communication, API gateways, service mesh, event-driven architecture, resilience patterns, and production deployment strategies.

## When to Use This Skill

Use this skill when you need to:

- Design microservices architecture
- Implement service-to-service communication
- Set up API gateways
- Configure service mesh (Istio, Linkerd)
- Implement event-driven architecture
- Handle distributed transactions (Saga pattern)
- Implement circuit breakers and resilience
- Deploy microservices with Docker and Kubernetes
- Design database per service patterns
- Implement service discovery
- Handle distributed tracing and monitoring

## Core Microservices Patterns

### Service Design Principles

**Single Responsibility**: Each service should do one thing well.

**Bounded Context**: Services should have clear boundaries aligned with business domains.

**Autonomous**: Services should be independently deployable and scalable.

**Decentralized**: Avoid centralized data stores and decision-making.

**Resilient**: Design for failure at every level.

### Example Service Structure

```
ecommerce-microservices/
├── api-gateway/          # Entry point, routing, authentication
├── user-service/         # User management, authentication
├── product-service/      # Product catalog, inventory
├── order-service/        # Order processing, order history
├── payment-service/      # Payment processing
├── notification-service/ # Email, SMS, push notifications
├── search-service/       # Elasticsearch-based product search
└── shared/               # Shared libraries, types
```

## API Gateway Pattern

API Gateway acts as a single entry point for all clients.

### API Gateway with Express

```javascript
// api-gateway/server.js
import express from 'express';
import { createProxyMiddleware } from 'http-proxy-middleware';
import rateLimit from 'express-rate-limit';
import jwt from 'jsonwebtoken';

const app = express();

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100
});
app.use(limiter);

// Authentication middleware
const authenticate = (req, res, next) => {
  const token = req.headers.authorization?.replace('Bearer ', '');

  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Invalid token' });
  }
};

// Service routes with proxying
app.use('/api/users', createProxyMiddleware({
  target: 'http://user-service:3001',
  changeOrigin: true,
  pathRewrite: { '^/api/users': '' }
}));

app.use('/api/products', createProxyMiddleware({
  target: 'http://product-service:3002',
  changeOrigin: true,
  pathRewrite: { '^/api/products': '' }
}));

app.use('/api/orders', authenticate, createProxyMiddleware({
  target: 'http://order-service:3003',
  changeOrigin: true,
  pathRewrite: { '^/api/orders': '' },
  onProxyReq: (proxyReq, req) => {
    // Forward user info to downstream services
    proxyReq.setHeader('X-User-Id', req.user.id);
    proxyReq.setHeader('X-User-Email', req.user.email);
  }
}));

app.listen(3000, () => {
  console.log('API Gateway running on port 3000');
});
```

### Backend for Frontend (BFF) Pattern

Different gateways for different clients (web, mobile, etc.).

```javascript
// web-bff/server.js - Optimized for web clients
app.get('/api/dashboard', authenticate, async (req, res) => {
  // Aggregate data from multiple services
  const [user, orders, recommendations] = await Promise.all([
    fetch(`http://user-service/users/${req.user.id}`),
    fetch(`http://order-service/orders?userId=${req.user.id}&limit=5`),
    fetch(`http://recommendation-service/recommendations/${req.user.id}`)
  ]);

  res.json({
    user: await user.json(),
    recentOrders: await orders.json(),
    recommendations: await recommendations.json()
  });
});

// mobile-bff/server.js - Optimized for mobile (less data)
app.get('/api/dashboard', authenticate, async (req, res) => {
  const [user, orders] = await Promise.all([
    fetch(`http://user-service/users/${req.user.id}?fields=id,name,avatar`),
    fetch(`http://order-service/orders?userId=${req.user.id}&limit=3`)
  ]);

  res.json({
    user: await user.json(),
    recentOrders: await orders.json()
  });
});
```

## Inter-Service Communication

### REST API Communication

```javascript
// order-service/services/ProductService.js
import axios from 'axios';
import CircuitBreaker from 'opossum';

class ProductService {
  constructor() {
    // Circuit breaker configuration
    this.breaker = new CircuitBreaker(this.fetchProduct.bind(this), {
      timeout: 3000,
      errorThresholdPercentage: 50,
      resetTimeout: 30000
    });

    this.breaker.on('open', () => {
      console.error('Product service circuit breaker opened');
    });
  }

  async fetchProduct(productId) {
    const response = await axios.get(
      `http://product-service:3002/products/${productId}`,
      {
        headers: {
          'X-Request-ID': generateRequestId(),
          'X-Service': 'order-service'
        },
        timeout: 3000
      }
    );
    return response.data;
  }

  async getProduct(productId) {
    try {
      return await this.breaker.fire(productId);
    } catch (err) {
      console.error('Failed to fetch product:', err);
      // Return cached data or fallback
      return this.getCachedProduct(productId) || {
        id: productId,
        name: 'Product unavailable',
        available: false
      };
    }
  }
}

export default new ProductService();
```

### gRPC Communication

More efficient than REST for service-to-service communication.

```protobuf
// proto/user.proto
syntax = "proto3";

package user;

service UserService {
  rpc GetUser (UserRequest) returns (UserResponse);
  rpc CreateUser (CreateUserRequest) returns (UserResponse);
  rpc ListUsers (ListUsersRequest) returns (ListUsersResponse);
}

message UserRequest {
  string id = 1;
}

message CreateUserRequest {
  string email = 1;
  string name = 2;
}

message UserResponse {
  string id = 1;
  string email = 2;
  string name = 3;
  int64 created_at = 4;
}

message ListUsersRequest {
  int32 page_size = 1;
  string page_token = 2;
}

message ListUsersResponse {
  repeated UserResponse users = 1;
  string next_page_token = 2;
}
```

```javascript
// user-service/server.js - gRPC server
import grpc from '@grpc/grpc-js';
import protoLoader from '@grpc/proto-loader';

const packageDefinition = protoLoader.loadSync('proto/user.proto');
const userProto = grpc.loadPackageDefinition(packageDefinition).user;

const server = new grpc.Server();

server.addService(userProto.UserService.service, {
  getUser: async (call, callback) => {
    const { id } = call.request;
    try {
      const user = await db.users.findById(id);
      callback(null, {
        id: user.id,
        email: user.email,
        name: user.name,
        created_at: user.createdAt.getTime()
      });
    } catch (err) {
      callback({
        code: grpc.status.NOT_FOUND,
        message: 'User not found'
      });
    }
  },

  createUser: async (call, callback) => {
    const { email, name } = call.request;
    try {
      const user = await db.users.create({ email, name });
      callback(null, user);
    } catch (err) {
      callback({
        code: grpc.status.INTERNAL,
        message: err.message
      });
    }
  }
});

server.bindAsync(
  '0.0.0.0:50051',
  grpc.ServerCredentials.createInsecure(),
  () => {
    console.log('gRPC server running on port 50051');
    server.start();
  }
);
```

```javascript
// order-service/clients/UserClient.js - gRPC client
import grpc from '@grpc/grpc-js';
import protoLoader from '@grpc/proto-loader';

const packageDefinition = protoLoader.loadSync('proto/user.proto');
const userProto = grpc.loadPackageDefinition(packageDefinition).user;

class UserClient {
  constructor() {
    this.client = new userProto.UserService(
      'user-service:50051',
      grpc.credentials.createInsecure()
    );
  }

  async getUser(userId) {
    return new Promise((resolve, reject) => {
      this.client.getUser({ id: userId }, (err, response) => {
        if (err) return reject(err);
        resolve(response);
      });
    });
  }
}

export default new UserClient();
```

## Event-Driven Architecture

### Message Queue with RabbitMQ

```javascript
// shared/messageQueue.js
import amqp from 'amqplib';

class MessageQueue {
  constructor() {
    this.connection = null;
    this.channel = null;
  }

  async connect() {
    this.connection = await amqp.connect(process.env.RABBITMQ_URL);
    this.channel = await this.connection.createChannel();
  }

  async publish(exchange, routingKey, message) {
    await this.channel.assertExchange(exchange, 'topic', { durable: true });

    this.channel.publish(
      exchange,
      routingKey,
      Buffer.from(JSON.stringify(message)),
      { persistent: true }
    );

    console.log(`Published message to ${exchange}:${routingKey}`);
  }

  async subscribe(exchange, queue, routingKeys, handler) {
    await this.channel.assertExchange(exchange, 'topic', { durable: true });
    await this.channel.assertQueue(queue, { durable: true });

    for (const key of routingKeys) {
      await this.channel.bindQueue(queue, exchange, key);
    }

    this.channel.consume(queue, async (msg) => {
      if (msg) {
        const content = JSON.parse(msg.content.toString());
        try {
          await handler(content);
          this.channel.ack(msg);
        } catch (err) {
          console.error('Message processing failed:', err);
          // Retry or dead letter queue
          this.channel.nack(msg, false, false);
        }
      }
    });

    console.log(`Subscribed to ${exchange}:${routingKeys.join(',')}`);
  }
}

export default new MessageQueue();
```

```javascript
// order-service/events/publisher.js
import messageQueue from '../../shared/messageQueue.js';

export async function publishOrderCreated(order) {
  await messageQueue.publish('orders', 'order.created', {
    orderId: order.id,
    userId: order.userId,
    items: order.items,
    total: order.total,
    timestamp: new Date().toISOString()
  });
}

export async function publishOrderCompleted(order) {
  await messageQueue.publish('orders', 'order.completed', {
    orderId: order.id,
    userId: order.userId,
    timestamp: new Date().toISOString()
  });
}
```

```javascript
// notification-service/consumers/orderConsumer.js
import messageQueue from '../../shared/messageQueue.js';
import { sendEmail } from '../services/emailService.js';

await messageQueue.subscribe(
  'orders',
  'notification-service-orders',
  ['order.created', 'order.completed'],
  async (message) => {
    console.log('Received order event:', message);

    if (message.orderId) {
      const user = await userService.getUser(message.userId);

      if (message.type === 'order.created') {
        await sendEmail(user.email, 'Order Confirmed', {
          orderId: message.orderId,
          total: message.total
        });
      } else if (message.type === 'order.completed') {
        await sendEmail(user.email, 'Order Shipped', {
          orderId: message.orderId
        });
      }
    }
  }
);
```

### Event Sourcing with Kafka

```javascript
// shared/kafka.js
import { Kafka } from 'kafkajs';

const kafka = new Kafka({
  clientId: 'microservices',
  brokers: [process.env.KAFKA_BROKER]
});

export const producer = kafka.producer();
export const consumer = kafka.consumer({ groupId: 'order-service' });

// order-service/events/eventStore.js
import { producer } from '../../shared/kafka.js';

export async function appendEvent(aggregateId, eventType, data) {
  await producer.send({
    topic: 'order-events',
    messages: [
      {
        key: aggregateId,
        value: JSON.stringify({
          aggregateId,
          eventType,
          data,
          timestamp: new Date().toISOString(),
          version: await getNextVersion(aggregateId)
        })
      }
    ]
  });
}

// Rebuild state from events
export async function rehydrateAggregate(aggregateId) {
  const events = await getAllEvents(aggregateId);
  let state = {};

  for (const event of events) {
    state = applyEvent(state, event);
  }

  return state;
}

function applyEvent(state, event) {
  switch (event.eventType) {
    case 'ORDER_CREATED':
      return { ...state, ...event.data, status: 'pending' };
    case 'ORDER_PAID':
      return { ...state, status: 'paid', paidAt: event.timestamp };
    case 'ORDER_SHIPPED':
      return { ...state, status: 'shipped', shippedAt: event.timestamp };
    default:
      return state;
  }
}
```

## Saga Pattern (Distributed Transactions)

### Orchestration-Based Saga

```javascript
// order-service/sagas/OrderSaga.js
class OrderSaga {
  constructor(order) {
    this.order = order;
    this.compensations = [];
  }

  async execute() {
    try {
      // Step 1: Reserve inventory
      await this.reserveInventory();
      this.compensations.push(() => this.releaseInventory());

      // Step 2: Process payment
      await this.processPayment();
      this.compensations.push(() => this.refundPayment());

      // Step 3: Create shipment
      await this.createShipment();
      this.compensations.push(() => this.cancelShipment());

      // Step 4: Send notification
      await this.sendNotification();

      // Mark order as completed
      await this.completeOrder();

      return { success: true, order: this.order };
    } catch (err) {
      console.error('Saga failed, compensating:', err);
      await this.compensate();
      return { success: false, error: err.message };
    }
  }

  async reserveInventory() {
    const response = await fetch('http://inventory-service/reserve', {
      method: 'POST',
      body: JSON.stringify({
        items: this.order.items,
        orderId: this.order.id
      })
    });

    if (!response.ok) {
      throw new Error('Inventory reservation failed');
    }
  }

  async processPayment() {
    const response = await fetch('http://payment-service/charge', {
      method: 'POST',
      body: JSON.stringify({
        amount: this.order.total,
        orderId: this.order.id,
        userId: this.order.userId
      })
    });

    if (!response.ok) {
      throw new Error('Payment processing failed');
    }

    const result = await response.json();
    this.order.paymentId = result.paymentId;
  }

  async compensate() {
    // Execute compensating transactions in reverse order
    for (const compensation of this.compensations.reverse()) {
      try {
        await compensation();
      } catch (err) {
        console.error('Compensation failed:', err);
      }
    }

    await this.markOrderAsFailed();
  }

  async releaseInventory() {
    await fetch('http://inventory-service/release', {
      method: 'POST',
      body: JSON.stringify({ orderId: this.order.id })
    });
  }

  async refundPayment() {
    await fetch('http://payment-service/refund', {
      method: 'POST',
      body: JSON.stringify({ paymentId: this.order.paymentId })
    });
  }
}

// Usage
app.post('/orders', async (req, res) => {
  const order = await createOrder(req.body);
  const saga = new OrderSaga(order);
  const result = await saga.execute();

  if (result.success) {
    res.status(201).json(result.order);
  } else {
    res.status(400).json({ error: result.error });
  }
});
```

## Service Discovery

### Consul-Based Discovery

```javascript
// shared/serviceRegistry.js
import Consul from 'consul';

const consul = new Consul({
  host: process.env.CONSUL_HOST,
  port: process.env.CONSUL_PORT
});

export async function registerService(name, port) {
  const serviceId = `${name}-${process.env.HOSTNAME}`;

  await consul.agent.service.register({
    id: serviceId,
    name,
    address: process.env.SERVICE_HOST,
    port,
    check: {
      http: `http://${process.env.SERVICE_HOST}:${port}/health`,
      interval: '10s',
      timeout: '5s'
    }
  });

  console.log(`Service ${name} registered with Consul`);

  // Deregister on shutdown
  process.on('SIGTERM', async () => {
    await consul.agent.service.deregister(serviceId);
    process.exit(0);
  });
}

export async function discoverService(name) {
  const result = await consul.health.service({
    service: name,
    passing: true
  });

  if (result.length === 0) {
    throw new Error(`No healthy instances of ${name} found`);
  }

  // Round-robin or random selection
  const instance = result[Math.floor(Math.random() * result.length)];

  return {
    host: instance.Service.Address,
    port: instance.Service.Port
  };
}
```

## Circuit Breaker Pattern

```javascript
// shared/circuitBreaker.js
import CircuitBreaker from 'opossum';

export function createCircuitBreaker(fn, options = {}) {
  const breaker = new CircuitBreaker(fn, {
    timeout: 3000,
    errorThresholdPercentage: 50,
    resetTimeout: 30000,
    ...options
  });

  breaker.on('open', () => {
    console.error('Circuit breaker opened');
  });

  breaker.on('halfOpen', () => {
    console.log('Circuit breaker half-open, testing...');
  });

  breaker.on('close', () => {
    console.log('Circuit breaker closed');
  });

  breaker.fallback(() => {
    return { error: 'Service temporarily unavailable' };
  });

  return breaker;
}

// Usage
import { createCircuitBreaker } from './shared/circuitBreaker.js';

const getUser = createCircuitBreaker(async (userId) => {
  const response = await fetch(`http://user-service/users/${userId}`);
  return response.json();
});

const user = await getUser.fire(userId);
```

## Docker Compose Deployment

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Infrastructure
  rabbitmq:
    image: rabbitmq:3-management-alpine
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: password

  consul:
    image: consul:latest
    ports:
      - "8500:8500"
      - "8600:8600/udp"
    command: agent -server -ui -bootstrap-expect=1 -client=0.0.0.0

  # API Gateway
  api-gateway:
    build: ./api-gateway
    ports:
      - "3000:3000"
    environment:
      - JWT_SECRET=${JWT_SECRET}
      - USER_SERVICE_URL=http://user-service:3001
      - PRODUCT_SERVICE_URL=http://product-service:3002
    depends_on:
      - user-service
      - product-service
      - order-service

  # Services
  user-service:
    build: ./user-service
    ports:
      - "3001:3001"
    environment:
      - DATABASE_URL=postgresql://postgres:password@user-db:5432/users
      - RABBITMQ_URL=amqp://admin:password@rabbitmq:5672
    depends_on:
      - user-db
      - rabbitmq

  product-service:
    build: ./product-service
    ports:
      - "3002:3002"
    environment:
      - DATABASE_URL=mongodb://product-db:27017/products
      - RABBITMQ_URL=amqp://admin:password@rabbitmq:5672
    depends_on:
      - product-db
      - rabbitmq

  order-service:
    build: ./order-service
    ports:
      - "3003:3003"
    environment:
      - DATABASE_URL=postgresql://postgres:password@order-db:5432/orders
      - RABBITMQ_URL=amqp://admin:password@rabbitmq:5672
      - USER_SERVICE_URL=http://user-service:3001
      - PRODUCT_SERVICE_URL=http://product-service:3002
    depends_on:
      - order-db
      - rabbitmq

  # Databases
  user-db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: users
      POSTGRES_PASSWORD: password
    volumes:
      - user-data:/var/lib/postgresql/data

  product-db:
    image: mongo:6.0
    volumes:
      - product-data:/data/db

  order-db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: orders
      POSTGRES_PASSWORD: password
    volumes:
      - order-data:/var/lib/postgresql/data

volumes:
  user-data:
  product-data:
  order-data:
```

## Kubernetes Deployment

```yaml
# user-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
  labels:
    app: user-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
        version: v1
    spec:
      containers:
      - name: user-service
        image: user-service:1.0.0
        ports:
        - containerPort: 3001
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: user-db-credentials
              key: url
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 3001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3001
          initialDelaySeconds: 10
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: user-service
spec:
  selector:
    app: user-service
  ports:
  - port: 3001
    targetPort: 3001
  type: ClusterIP

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: user-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: user-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Production Best Practices

### Health Checks

```javascript
// health.js
export function setupHealthChecks(app) {
  // Liveness probe
  app.get('/health', (req, res) => {
    res.status(200).json({ status: 'ok' });
  });

  // Readiness probe
  app.get('/ready', async (req, res) => {
    try {
      // Check database
      await db.ping();

      // Check message queue
      if (!messageQueue.isConnected()) {
        throw new Error('Message queue not connected');
      }

      // Check dependencies
      await checkDependencies();

      res.status(200).json({ status: 'ready' });
    } catch (err) {
      res.status(503).json({
        status: 'not ready',
        error: err.message
      });
    }
  });
}

async function checkDependencies() {
  const services = [
    'http://user-service/health',
    'http://product-service/health'
  ];

  const results = await Promise.all(
    services.map(url =>
      fetch(url, { timeout: 2000 })
        .then(r => r.ok)
        .catch(() => false)
    )
  );

  if (!results.every(Boolean)) {
    throw new Error('Dependent services not healthy');
  }
}
```

### Distributed Tracing

```javascript
// tracing.js
import { trace } from '@opentelemetry/api';
import { NodeTracerProvider } from '@opentelemetry/sdk-trace-node';
import { JaegerExporter } from '@opentelemetry/exporter-jaeger';

const provider = new NodeTracerProvider();
const exporter = new JaegerExporter({
  serviceName: process.env.SERVICE_NAME,
  endpoint: process.env.JAEGER_ENDPOINT
});

provider.addSpanProcessor(new BatchSpanProcessor(exporter));
provider.register();

const tracer = trace.getTracer('default');

export function traceMiddleware(req, res, next) {
  const span = tracer.startSpan(`${req.method} ${req.path}`);

  span.setAttributes({
    'http.method': req.method,
    'http.url': req.url,
    'http.target': req.path
  });

  res.on('finish', () => {
    span.setAttributes({
      'http.status_code': res.statusCode
    });
    span.end();
  });

  req.span = span;
  next();
}
```

### Service Mesh with Istio

```yaml
# istio-gateway.yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: microservices-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "*"

---
# istio-virtualservice.yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: user-service
spec:
  hosts:
  - user-service
  http:
  - match:
    - headers:
        version:
          exact: v2
    route:
    - destination:
        host: user-service
        subset: v2
  - route:
    - destination:
        host: user-service
        subset: v1

---
# istio-destinationrule.yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: user-service
spec:
  host: user-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
        maxRequestsPerConnection: 2
    outlierDetection:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 30s
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

## Testing Microservices

### Contract Testing

```javascript
// user-service/tests/contract.test.js
import { Pact } from '@pact-foundation/pact';

describe('User Service Contract', () => {
  const provider = new Pact({
    consumer: 'order-service',
    provider: 'user-service',
    port: 8080
  });

  beforeAll(() => provider.setup());
  afterEach(() => provider.verify());
  afterAll(() => provider.finalize());

  it('should get user by ID', async () => {
    await provider.addInteraction({
      state: 'user exists',
      uponReceiving: 'a request for user',
      withRequest: {
        method: 'GET',
        path: '/users/123'
      },
      willRespondWith: {
        status: 200,
        body: {
          id: '123',
          name: 'Test User',
          email: 'test@example.com'
        }
      }
    });

    const user = await userService.getUser('123');
    expect(user.id).toBe('123');
  });
});
```

## Additional Resources

- Microservices patterns: https://microservices.io/patterns/
- API Gateway pattern: https://microservices.io/patterns/apigateway.html
- Saga pattern: https://microservices.io/patterns/data/saga.html
- Circuit breaker: https://martinfowler.com/bliki/CircuitBreaker.html
- gRPC: https://grpc.io/docs/
- Istio: https://istio.io/latest/docs/
