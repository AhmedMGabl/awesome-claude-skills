---
name: email-templates
description: Email template development covering responsive HTML email, MJML framework, React Email, transactional emails, email deliverability, dark mode support, inline CSS, Mailgun/SendGrid/Resend integration, and cross-client compatibility testing.
---

# Email Templates

This skill should be used when building email templates or integrating transactional email services. It covers responsive HTML email, modern frameworks, and deliverability patterns.

## When to Use This Skill

Use this skill when you need to:

- Build responsive HTML email templates
- Set up transactional email infrastructure
- Use React Email or MJML for templating
- Integrate with email providers (SendGrid, Resend, Mailgun)
- Ensure cross-client email compatibility
- Implement dark mode support for emails

## React Email (Modern Approach)

```typescript
// emails/welcome.tsx
import { Body, Button, Container, Head, Heading, Html, Img,
  Link, Preview, Section, Text } from "@react-email/components";

interface WelcomeEmailProps {
  name: string;
  loginUrl: string;
}

export default function WelcomeEmail({ name, loginUrl }: WelcomeEmailProps) {
  return (
    <Html>
      <Head />
      <Preview>Welcome to MyApp, {name}!</Preview>
      <Body style={main}>
        <Container style={container}>
          <Img src="https://example.com/logo.png" width={48} height={48} alt="MyApp" />
          <Heading style={h1}>Welcome, {name}!</Heading>
          <Text style={text}>
            Thanks for signing up. Click the button below to get started.
          </Text>
          <Section style={{ textAlign: "center", margin: "32px 0" }}>
            <Button style={button} href={loginUrl}>
              Get Started
            </Button>
          </Section>
          <Text style={footer}>
            MyApp, Inc. | <Link href="https://example.com/unsubscribe">Unsubscribe</Link>
          </Text>
        </Container>
      </Body>
    </Html>
  );
}

const main = { backgroundColor: "#f6f9fc", fontFamily: '-apple-system, "Segoe UI", Roboto, sans-serif' };
const container = { backgroundColor: "#ffffff", margin: "0 auto", padding: "40px 24px", maxWidth: "560px", borderRadius: "8px" };
const h1 = { color: "#1d1c1d", fontSize: "24px", fontWeight: "700", margin: "0 0 16px" };
const text = { color: "#484848", fontSize: "16px", lineHeight: "24px" };
const button = { backgroundColor: "#2563eb", color: "#fff", padding: "12px 24px", borderRadius: "6px", textDecoration: "none", fontSize: "16px", fontWeight: "600" };
const footer = { color: "#898989", fontSize: "12px", marginTop: "32px" };
```

## Sending with Resend

```typescript
import { Resend } from "resend";
import WelcomeEmail from "./emails/welcome";

const resend = new Resend(process.env.RESEND_API_KEY);

async function sendWelcomeEmail(user: { name: string; email: string }) {
  const { data, error } = await resend.emails.send({
    from: "MyApp <hello@myapp.com>",
    to: user.email,
    subject: `Welcome to MyApp, ${user.name}!`,
    react: WelcomeEmail({ name: user.name, loginUrl: "https://myapp.com/login" }),
  });
  if (error) throw new Error(`Failed to send email: ${error.message}`);
  return data;
}
```

## MJML (Framework-Agnostic)

```xml
<mjml>
  <mj-head>
    <mj-preview>Your order has been confirmed</mj-preview>
    <mj-attributes>
      <mj-all font-family="-apple-system, Segoe UI, Roboto, sans-serif" />
      <mj-text font-size="16px" color="#484848" line-height="24px" />
    </mj-attributes>
  </mj-head>
  <mj-body background-color="#f6f9fc">
    <mj-section background-color="#ffffff" border-radius="8px" padding="40px 24px">
      <mj-column>
        <mj-image src="https://example.com/logo.png" width="48px" />
        <mj-text font-size="24px" font-weight="700" color="#1d1c1d">
          Order Confirmed!
        </mj-text>
        <mj-text>
          Your order #{{orderNumber}} has been confirmed. Here are the details:
        </mj-text>
        <mj-table>
          <tr><th>Item</th><th>Qty</th><th>Price</th></tr>
          {{#each items}}
          <tr><td>{{name}}</td><td>{{quantity}}</td><td>{{price}}</td></tr>
          {{/each}}
          <tr><th colspan="2">Total</th><th>{{total}}</th></tr>
        </mj-table>
        <mj-button background-color="#2563eb" href="{{trackingUrl}}">
          Track Order
        </mj-button>
      </mj-column>
    </mj-section>
  </mj-body>
</mjml>
```

## Dark Mode Support

```html
<!-- In email <head> -->
<style>
  @media (prefers-color-scheme: dark) {
    .email-body { background-color: #1a1a1a !important; }
    .email-container { background-color: #2d2d2d !important; }
    .text-primary { color: #e0e0e0 !important; }
    .text-secondary { color: #b0b0b0 !important; }
  }
  /* Outlook dark mode */
  [data-ogsc] .email-body { background-color: #1a1a1a !important; }
  [data-ogsc] .text-primary { color: #e0e0e0 !important; }
</style>
```

## Email Deliverability Checklist

```
AUTHENTICATION:
  [ ] SPF record configured
  [ ] DKIM signing enabled
  [ ] DMARC policy set
  [ ] Custom return-path domain

CONTENT:
  [ ] Subject line under 60 characters
  [ ] Text/plain alternative included
  [ ] Unsubscribe link present (CAN-SPAM)
  [ ] Physical mailing address included
  [ ] Image alt text on all images
  [ ] No broken links
  [ ] Balance text-to-image ratio (60/40)

TECHNICAL:
  [ ] Inline CSS (not external stylesheets)
  [ ] Images hosted on HTTPS CDN
  [ ] Total email size under 102KB (Gmail clip threshold)
  [ ] Responsive design tested
  [ ] Test across major clients (Gmail, Outlook, Apple Mail)
```

## Additional Resources

- React Email: https://react.email/
- MJML: https://mjml.io/
- Resend: https://resend.com/docs
- Email on Acid (testing): https://www.emailonacid.com/
- Can I Email: https://www.caniemail.com/
