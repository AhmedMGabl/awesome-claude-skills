---
name: stripe-elements
description: Stripe Elements covering Payment Element, Address Element, Express Checkout, appearance customization, payment intents, setup intents, and React Stripe.js integration patterns.
---

# Stripe Elements

This skill should be used when building payment UIs with Stripe Elements. It covers Payment Element, Express Checkout, appearance theming, and React integration.

## When to Use This Skill

Use this skill when you need to:

- Embed payment forms with Stripe Elements
- Customize payment UI appearance
- Handle payment intents and setup intents
- Build Express Checkout (Apple Pay, Google Pay)
- Integrate Stripe.js with React

## React Setup

```tsx
// app/providers.tsx
import { Elements } from "@stripe/react-stripe-js";
import { loadStripe } from "@stripe/stripe-js";

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!);

function CheckoutProvider({ clientSecret, children }) {
  return (
    <Elements
      stripe={stripePromise}
      options={{
        clientSecret,
        appearance: {
          theme: "stripe",
          variables: {
            colorPrimary: "#3b82f6",
            colorBackground: "#ffffff",
            borderRadius: "8px",
            fontFamily: "system-ui, sans-serif",
          },
          rules: {
            ".Input": { border: "1px solid #e5e7eb", padding: "12px" },
            ".Input:focus": { borderColor: "#3b82f6", boxShadow: "0 0 0 1px #3b82f6" },
            ".Label": { fontWeight: "500" },
          },
        },
      }}
    >
      {children}
    </Elements>
  );
}
```

## Payment Element

```tsx
import { PaymentElement, useStripe, useElements } from "@stripe/react-stripe-js";

function CheckoutForm() {
  const stripe = useStripe();
  const elements = useElements();
  const [error, setError] = useState<string | null>(null);
  const [processing, setProcessing] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!stripe || !elements) return;

    setProcessing(true);
    setError(null);

    const { error: submitError } = await elements.submit();
    if (submitError) {
      setError(submitError.message ?? "An error occurred");
      setProcessing(false);
      return;
    }

    const { error: confirmError } = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: `${window.location.origin}/checkout/success`,
      },
    });

    if (confirmError) {
      setError(confirmError.message ?? "Payment failed");
    }
    setProcessing(false);
  };

  return (
    <form onSubmit={handleSubmit}>
      <PaymentElement
        options={{
          layout: "tabs",
          paymentMethodOrder: ["card", "apple_pay", "google_pay"],
        }}
      />
      {error && <div className="error">{error}</div>}
      <button type="submit" disabled={!stripe || processing}>
        {processing ? "Processing..." : "Pay now"}
      </button>
    </form>
  );
}
```

## Server: Create Payment Intent

```typescript
// app/api/create-payment-intent/route.ts
import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

export async function POST(req: Request) {
  const { amount, currency = "usd" } = await req.json();

  const paymentIntent = await stripe.paymentIntents.create({
    amount: Math.round(amount * 100),
    currency,
    automatic_payment_methods: { enabled: true },
    metadata: { orderId: "order_123" },
  });

  return Response.json({ clientSecret: paymentIntent.client_secret });
}
```

## Express Checkout Element

```tsx
import { ExpressCheckoutElement } from "@stripe/react-stripe-js";

function ExpressCheckout() {
  const stripe = useStripe();
  const elements = useElements();

  const onConfirm = async () => {
    if (!stripe || !elements) return;
    const { error } = await stripe.confirmPayment({
      elements,
      confirmParams: { return_url: `${window.location.origin}/success` },
    });
    if (error) console.error(error);
  };

  return (
    <ExpressCheckoutElement
      onConfirm={onConfirm}
      options={{
        buttonType: { applePay: "buy", googlePay: "buy" },
        buttonTheme: { applePay: "black", googlePay: "black" },
      }}
    />
  );
}
```

## Address Element

```tsx
import { AddressElement } from "@stripe/react-stripe-js";

function ShippingForm() {
  return (
    <AddressElement
      options={{
        mode: "shipping",
        allowedCountries: ["US", "CA", "GB"],
        autocomplete: { mode: "google_maps_api", apiKey: MAPS_KEY },
        fields: { phone: "always" },
        validation: { phone: { required: "always" } },
      }}
      onChange={(event) => {
        if (event.complete) {
          console.log("Address:", event.value);
        }
      }}
    />
  );
}
```

## Additional Resources

- Stripe Elements: https://docs.stripe.com/payments/elements
- React Stripe.js: https://docs.stripe.com/stripe-js/react
- Appearance API: https://docs.stripe.com/elements/appearance-api
