---
name: react-email
description: React Email development covering email component creation with @react-email/components, responsive layouts, dark mode, dynamic templates, preview server, and sending with Resend, Nodemailer, and AWS SES.
---

# React Email

This skill should be used when building email templates with React Email. It covers components, responsive layouts, preview, and sending with Resend or Nodemailer.

## When to Use This Skill

Use this skill when you need to:

- Build email templates with React components
- Create responsive, cross-client email layouts
- Preview emails during development
- Send transactional emails with Resend or Nodemailer
- Generate HTML from React email templates

## Setup

```bash
npm install @react-email/components react-email
npm install resend  # or nodemailer
```

## Email Components

```tsx
// emails/welcome.tsx
import {
  Body, Button, Container, Head, Heading, Hr, Html,
  Img, Link, Preview, Section, Text,
} from "@react-email/components";

interface WelcomeEmailProps {
  name: string;
  verifyUrl: string;
}

export default function WelcomeEmail({ name, verifyUrl }: WelcomeEmailProps) {
  return (
    <Html>
      <Head />
      <Preview>Welcome to our platform, {name}!</Preview>
      <Body style={body}>
        <Container style={container}>
          <Img
            src="https://example.com/logo.png"
            width="120"
            height="40"
            alt="Logo"
          />
          <Heading style={heading}>Welcome, {name}!</Heading>
          <Text style={text}>
            Thanks for signing up. Please verify your email address to get started.
          </Text>
          <Section style={buttonSection}>
            <Button style={button} href={verifyUrl}>
              Verify Email
            </Button>
          </Section>
          <Hr style={hr} />
          <Text style={footer}>
            If you didn't create an account, you can safely ignore this email.
          </Text>
        </Container>
      </Body>
    </Html>
  );
}

const body = {
  backgroundColor: "#f6f9fc",
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
};

const container = {
  backgroundColor: "#ffffff",
  margin: "0 auto",
  padding: "40px 20px",
  maxWidth: "560px",
  borderRadius: "8px",
};

const heading = { fontSize: "24px", fontWeight: "bold" as const, color: "#1a1a1a" };
const text = { fontSize: "16px", lineHeight: "26px", color: "#484848" };
const buttonSection = { textAlign: "center" as const, margin: "32px 0" };
const button = {
  backgroundColor: "#000000",
  borderRadius: "6px",
  color: "#ffffff",
  fontSize: "16px",
  padding: "12px 24px",
  textDecoration: "none",
};
const hr = { borderColor: "#e6ebf1", margin: "20px 0" };
const footer = { color: "#8898aa", fontSize: "12px" };
```

## Order Confirmation Template

```tsx
// emails/order-confirmation.tsx
import {
  Body, Container, Column, Head, Heading, Html,
  Preview, Row, Section, Text,
} from "@react-email/components";

interface OrderItem {
  name: string;
  quantity: number;
  price: number;
}

interface OrderEmailProps {
  orderNumber: string;
  items: OrderItem[];
  total: number;
}

export default function OrderConfirmation({ orderNumber, items, total }: OrderEmailProps) {
  return (
    <Html>
      <Head />
      <Preview>Order #{orderNumber} confirmed</Preview>
      <Body style={body}>
        <Container style={container}>
          <Heading style={heading}>Order Confirmed</Heading>
          <Text>Order #{orderNumber}</Text>

          <Section>
            {items.map((item, i) => (
              <Row key={i} style={itemRow}>
                <Column style={{ width: "60%" }}>
                  <Text style={itemName}>{item.name}</Text>
                  <Text style={itemQty}>Qty: {item.quantity}</Text>
                </Column>
                <Column style={{ width: "40%", textAlign: "right" }}>
                  <Text style={itemPrice}>${(item.price * item.quantity).toFixed(2)}</Text>
                </Column>
              </Row>
            ))}
          </Section>

          <Section style={totalSection}>
            <Row>
              <Column><Text style={totalLabel}>Total</Text></Column>
              <Column style={{ textAlign: "right" }}>
                <Text style={totalAmount}>${total.toFixed(2)}</Text>
              </Column>
            </Row>
          </Section>
        </Container>
      </Body>
    </Html>
  );
}

const body = { backgroundColor: "#f6f9fc", fontFamily: "sans-serif" };
const container = { backgroundColor: "#fff", margin: "0 auto", padding: "40px 20px", maxWidth: "560px" };
const heading = { fontSize: "24px", fontWeight: "bold" as const };
const itemRow = { borderBottom: "1px solid #eee", padding: "12px 0" };
const itemName = { fontSize: "14px", margin: "0" };
const itemQty = { fontSize: "12px", color: "#666", margin: "4px 0 0" };
const itemPrice = { fontSize: "14px", fontWeight: "bold" as const, margin: "0" };
const totalSection = { borderTop: "2px solid #000", marginTop: "16px", paddingTop: "16px" };
const totalLabel = { fontSize: "16px", fontWeight: "bold" as const };
const totalAmount = { fontSize: "20px", fontWeight: "bold" as const };
```

## Sending with Resend

```typescript
import { Resend } from "resend";
import WelcomeEmail from "@/emails/welcome";

const resend = new Resend(process.env.RESEND_API_KEY);

async function sendWelcome(email: string, name: string) {
  const { data, error } = await resend.emails.send({
    from: "MyApp <noreply@example.com>",
    to: email,
    subject: `Welcome, ${name}!`,
    react: WelcomeEmail({ name, verifyUrl: `https://example.com/verify?email=${email}` }),
  });

  if (error) throw new Error(`Email failed: ${error.message}`);
  return data;
}
```

## Sending with Nodemailer

```typescript
import { render } from "@react-email/render";
import nodemailer from "nodemailer";
import WelcomeEmail from "@/emails/welcome";

const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST,
  port: 587,
  auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS },
});

async function sendWelcome(email: string, name: string) {
  const html = await render(WelcomeEmail({ name, verifyUrl: "https://..." }));

  await transporter.sendMail({
    from: "MyApp <noreply@example.com>",
    to: email,
    subject: `Welcome, ${name}!`,
    html,
  });
}
```

## Preview and Development

```bash
npx react-email dev       # Preview server at localhost:3000
npx react-email export    # Export to static HTML
```

## Additional Resources

- React Email docs: https://react.email/docs
- Resend: https://resend.com/docs
- Component reference: https://react.email/docs/components
