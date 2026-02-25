---
name: shopify-hydrogen
description: Shopify Hydrogen patterns covering Remix-based storefront, Storefront API GraphQL queries, cart management, customer accounts, product pages, collection filtering, SEO, and Oxygen deployment.
---

# Shopify Hydrogen

This skill should be used when building custom Shopify storefronts with Hydrogen. It covers Storefront API, cart management, customer accounts, and Oxygen deployment.

## When to Use This Skill

Use this skill when you need to:

- Build custom Shopify storefronts with Remix
- Query products and collections via Storefront API
- Implement cart and checkout flows
- Handle customer authentication and accounts
- Deploy to Shopify Oxygen

## Setup

```bash
npm create @shopify/hydrogen@latest -- --template demo-store
cd my-store
npm run dev
```

## Product Page

```tsx
// app/routes/products.$handle.tsx
import { json, type LoaderFunctionArgs } from "@shopify/remix-oxygen";
import { useLoaderData } from "@remix-run/react";
import { Image, Money, ShopPayButton } from "@shopify/hydrogen";

export async function loader({ params, context }: LoaderFunctionArgs) {
  const { handle } = params;
  const { product } = await context.storefront.query(PRODUCT_QUERY, {
    variables: { handle },
  });

  if (!product) throw new Response("Not Found", { status: 404 });
  return json({ product });
}

export default function ProductPage() {
  const { product } = useLoaderData<typeof loader>();
  const selectedVariant = product.variants.nodes[0];

  return (
    <div className="product-page">
      <Image
        data={product.featuredImage}
        sizes="(min-width: 768px) 50vw, 100vw"
        aspectRatio="1/1"
      />
      <div>
        <h1>{product.title}</h1>
        <Money data={selectedVariant.price} />
        <AddToCartButton
          variantId={selectedVariant.id}
          available={selectedVariant.availableForSale}
        />
        <div className="prose" />
      </div>
    </div>
  );
}

const PRODUCT_QUERY = `#graphql
  query Product($handle: String!) {
    product(handle: $handle) {
      id
      title
      handle
      descriptionHtml
      featuredImage { url altText width height }
      variants(first: 10) {
        nodes {
          id
          title
          availableForSale
          price { amount currencyCode }
          compareAtPrice { amount currencyCode }
          selectedOptions { name value }
        }
      }
      options { name values }
    }
  }
`;
```

## Cart Management

```tsx
// app/components/Cart.tsx
import { CartForm, Money, Image } from "@shopify/hydrogen";
import type { CartLineInput } from "@shopify/hydrogen/storefront-api-types";

function AddToCartButton({ variantId, available }: { variantId: string; available: boolean }) {
  const lines: CartLineInput[] = [{ merchandiseId: variantId, quantity: 1 }];

  return (
    <CartForm route="/cart" action={CartForm.ACTIONS.LinesAdd} inputs={{ lines }}>
      <button type="submit" disabled={!available}>
        {available ? "Add to Cart" : "Sold Out"}
      </button>
    </CartForm>
  );
}

function CartLineItem({ line }: { line: any }) {
  return (
    <div className="cart-line">
      <Image data={line.merchandise.image} width={100} height={100} />
      <div>
        <p>{line.merchandise.product.title}</p>
        <p>{line.merchandise.title}</p>
        <Money data={line.cost.totalAmount} />
      </div>
      <CartForm
        route="/cart"
        action={CartForm.ACTIONS.LinesUpdate}
        inputs={{ lines: [{ id: line.id, quantity: line.quantity + 1 }] }}
      >
        <button type="submit">+</button>
      </CartForm>
      <CartForm
        route="/cart"
        action={CartForm.ACTIONS.LinesRemove}
        inputs={{ lineIds: [line.id] }}
      >
        <button type="submit">Remove</button>
      </CartForm>
    </div>
  );
}
```

## Collection Page

```tsx
// app/routes/collections.$handle.tsx
import { json, type LoaderFunctionArgs } from "@shopify/remix-oxygen";
import { useLoaderData } from "@remix-run/react";
import { Pagination, getPaginationVariables } from "@shopify/hydrogen";

export async function loader({ params, request, context }: LoaderFunctionArgs) {
  const paginationVariables = getPaginationVariables(request, { pageBy: 12 });
  const { collection } = await context.storefront.query(COLLECTION_QUERY, {
    variables: { handle: params.handle, ...paginationVariables },
  });

  if (!collection) throw new Response("Not Found", { status: 404 });
  return json({ collection });
}

export default function CollectionPage() {
  const { collection } = useLoaderData<typeof loader>();

  return (
    <div>
      <h1>{collection.title}</h1>
      <Pagination connection={collection.products}>
        {({ nodes, NextLink, PreviousLink }) => (
          <>
            <PreviousLink>Load Previous</PreviousLink>
            <div className="products-grid">
              {nodes.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
            <NextLink>Load More</NextLink>
          </>
        )}
      </Pagination>
    </div>
  );
}

const COLLECTION_QUERY = `#graphql
  query Collection($handle: String!, $first: Int, $last: Int, $before: String, $after: String) {
    collection(handle: $handle) {
      id
      title
      description
      products(first: $first, last: $last, before: $before, after: $after) {
        nodes {
          id
          title
          handle
          featuredImage { url altText width height }
          priceRange { minVariantPrice { amount currencyCode } }
        }
        pageInfo { hasNextPage hasPreviousPage startCursor endCursor }
      }
    }
  }
`;
```

## Additional Resources

- Hydrogen: https://shopify.dev/docs/custom-storefronts/hydrogen
- Storefront API: https://shopify.dev/docs/api/storefront
- Oxygen: https://shopify.dev/docs/custom-storefronts/oxygen
