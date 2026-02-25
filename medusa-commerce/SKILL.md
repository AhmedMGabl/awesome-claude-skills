---
name: medusa-commerce
description: Medusa.js patterns covering headless e-commerce, product/variant management, cart and checkout flows, payment/fulfillment providers, custom API routes, subscribers, and Next.js storefront integration.
---

# Medusa Commerce

This skill should be used when building e-commerce applications with Medusa.js. It covers products, carts, checkout, payments, custom routes, and storefront integration.

## When to Use This Skill

Use this skill when you need to:

- Build a headless e-commerce platform
- Manage products, variants, and inventory
- Implement cart and checkout flows
- Integrate payment and fulfillment providers
- Build custom storefronts with Next.js

## Setup

```bash
npx create-medusa-app@latest my-store
cd my-store
npx medusa develop
```

## Product Management

```ts
// src/api/admin/custom-products/route.ts
import { MedusaRequest, MedusaResponse } from "@medusajs/framework";

export async function POST(req: MedusaRequest, res: MedusaResponse) {
  const productService = req.scope.resolve("productModuleService");

  const product = await productService.createProducts({
    title: req.body.title,
    description: req.body.description,
    status: "draft",
    options: [
      { title: "Size", values: ["S", "M", "L", "XL"] },
      { title: "Color", values: ["Black", "White"] },
    ],
    variants: [
      {
        title: "Small Black",
        prices: [{ amount: 2999, currency_code: "usd" }],
        options: { Size: "S", Color: "Black" },
        manage_inventory: true,
      },
    ],
    images: [{ url: req.body.imageUrl }],
    categories: [{ id: req.body.categoryId }],
  });

  res.json({ product });
}
```

## Storefront API (Cart & Checkout)

```ts
import Medusa from "@medusajs/js-sdk";

const client = new Medusa({ baseUrl: "http://localhost:9000", publishableKey: "pk_..." });

// Create cart
const cart = await client.store.cart.create({ region_id: "reg_123" });

// Add item
await client.store.cart.createLineItem(cart.id, {
  variant_id: "variant_123",
  quantity: 2,
});

// Update shipping address
await client.store.cart.update(cart.id, {
  shipping_address: {
    first_name: "John",
    last_name: "Doe",
    address_1: "123 Main St",
    city: "New York",
    country_code: "us",
    postal_code: "10001",
  },
});

// Select shipping method
await client.store.cart.addShippingMethod(cart.id, {
  option_id: "so_express",
});

// Initialize payment
await client.store.cart.createPaymentCollection(cart.id);

// Complete order
const order = await client.store.cart.complete(cart.id);
```

## Custom API Route

```ts
// src/api/store/custom/route.ts
import { MedusaRequest, MedusaResponse } from "@medusajs/framework";

export async function GET(req: MedusaRequest, res: MedusaResponse) {
  const productService = req.scope.resolve("productModuleService");

  const [products, count] = await productService.listAndCountProducts(
    { status: "published" },
    { take: 20, skip: 0, relations: ["variants", "images"] }
  );

  res.json({ products, count });
}
```

## Subscribers (Event Handlers)

```ts
// src/subscribers/order-placed.ts
import { SubscriberArgs, type SubscriberConfig } from "@medusajs/framework";

export default async function orderPlacedHandler({ event, container }: SubscriberArgs) {
  const notificationService = container.resolve("notificationModuleService");
  const { id } = event.data;

  await notificationService.createNotifications({
    to: event.data.email,
    channel: "email",
    template: "order-confirmation",
    data: { order_id: id },
  });
}

export const config: SubscriberConfig = {
  event: "order.placed",
};
```

## Scheduled Jobs

```ts
// src/jobs/sync-inventory.ts
import { MedusaContainer } from "@medusajs/framework";

export default async function syncInventory(container: MedusaContainer) {
  const inventoryService = container.resolve("inventoryModuleService");
  // Sync inventory from external system
  const externalData = await fetchExternalInventory();
  for (const item of externalData) {
    await inventoryService.updateInventoryLevels(item.id, {
      stocked_quantity: item.quantity,
    });
  }
}

export const config = {
  name: "sync-inventory",
  schedule: "0 */6 * * *", // Every 6 hours
};
```

## Additional Resources

- Medusa: https://docs.medusajs.com/
- Store API: https://docs.medusajs.com/api/store
- Recipes: https://docs.medusajs.com/resources/recipes
