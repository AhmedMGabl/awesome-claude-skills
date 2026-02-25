---
name: resend-email
description: Resend email API covering transactional emails, React Email templates, batch sending, domains, webhooks, audiences, broadcast campaigns, and Next.js integration patterns.
---

# Resend Email

This skill should be used when sending transactional or marketing emails with Resend. It covers the Resend API, React Email templates, webhooks, and batch sending.

## When to Use This Skill

Use this skill when you need to:

- Send transactional emails (verification, receipts, notifications)
- Build email templates with React Email
- Send batch emails efficiently
- Handle email delivery webhooks
- Manage domains and sender identities

## Setup

```typescript
import { Resend } from "resend";

const resend = new Resend(process.env.RESEND_API_KEY);
```

## Send Email

```typescript
const { data, error } = await resend.emails.send({
  from: "App <noreply@myapp.com>",
  to: ["user@example.com"],
  subject: "Welcome to MyApp",
  html: "<h1>Welcome!</h1><p>Thanks for signing up.</p>",
});

if (error) {
  console.error("Failed to send:", error);
}
```

## React Email Template

```tsx
// emails/welcome.tsx
import { Html, Head, Body, Container, Text, Button, Preview } from "@react-email/components";

interface WelcomeEmailProps {
  name: string;
  loginUrl: string;
}

export function WelcomeEmail({ name, loginUrl }: WelcomeEmailProps) {
  return (
    <Html>
      <Head />
      <Preview>Welcome to MyApp, {name}!</Preview>
      <Body style={{ fontFamily: "sans-serif", backgroundColor: "#f6f9fc" }}>
        <Container style={{ padding: "40px 20px", maxWidth: "560px", margin: "0 auto" }}>
          <Text style={{ fontSize: "24px", fontWeight: "bold" }}>Welcome, {name}!</Text>
          <Text>Thanks for signing up. Click below to get started.</Text>
          <Button
            href={loginUrl}
            style={{
              backgroundColor: "#000",
              color: "#fff",
              padding: "12px 24px",
              borderRadius: "6px",
              textDecoration: "none",
            }}
          >
            Get Started
          </Button>
        </Container>
      </Body>
    </Html>
  );
}
```

```typescript
// Send with React template
import { WelcomeEmail } from "@/emails/welcome";

await resend.emails.send({
  from: "App <noreply@myapp.com>",
  to: [user.email],
  subject: "Welcome to MyApp",
  react: WelcomeEmail({ name: user.name, loginUrl: "https://myapp.com/login" }),
});
```

## Batch Sending

```typescript
const { data, error } = await resend.batch.send([
  {
    from: "App <noreply@myapp.com>",
    to: ["user1@example.com"],
    subject: "Your weekly digest",
    react: DigestEmail({ userId: "1" }),
  },
  {
    from: "App <noreply@myapp.com>",
    to: ["user2@example.com"],
    subject: "Your weekly digest",
    react: DigestEmail({ userId: "2" }),
  },
]);
```

## Webhook Handling

```typescript
// app/api/webhooks/resend/route.ts
import { Webhook } from "svix";

export async function POST(request: Request) {
  const body = await request.text();
  const headers = Object.fromEntries(request.headers);

  const wh = new Webhook(process.env.RESEND_WEBHOOK_SECRET!);
  const event = wh.verify(body, headers) as any;

  switch (event.type) {
    case "email.sent":
      console.log("Email sent:", event.data.email_id);
      break;
    case "email.delivered":
      await markDelivered(event.data.email_id);
      break;
    case "email.bounced":
      await handleBounce(event.data.to[0]);
      break;
    case "email.complained":
      await unsubscribeUser(event.data.to[0]);
      break;
  }

  return new Response("OK");
}
```

## Additional Resources

- Resend docs: https://resend.com/docs
- React Email: https://react.email/docs/introduction
- Resend examples: https://resend.com/examples
