---
name: email-templates
description: Email template development covering React Email component-based templates, MJML responsive layouts, inline CSS for email clients, transactional email patterns with Resend and Nodemailer, preview and testing workflows, dark mode support, and accessibility in email design.
---

# Email Templates

This skill should be used when building email templates for transactional or marketing emails. It covers React Email, MJML, inline styling, sending with Resend/Nodemailer, and testing.

## When to Use This Skill

Use this skill when you need to:

- Build responsive HTML email templates
- Use React Email for component-based emails
- Send transactional emails (welcome, reset, invoice)
- Test emails across clients (Gmail, Outlook, Apple Mail)
- Implement dark mode support in emails

## React Email

```tsx
// emails/welcome.tsx
import {
  Html, Head, Body, Container, Section,
  Text, Button, Img, Hr, Preview,
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
          <Img src="https://example.com/logo.png" width={120} height={40} alt="Logo" />
          <Section style={content}>
            <Text style={heading}>Welcome, {name}!</Text>
            <Text style={paragraph}>
              Thanks for signing up. Please verify your email address to get started.
            </Text>
            <Button style={button} href={verifyUrl}>
              Verify Email
            </Button>
            <Hr style={divider} />
            <Text style={footer}>
              If you did not create an account, you can safely ignore this email.
            </Text>
          </Section>
        </Container>
      </Body>
    </Html>
  );
}

const body = { backgroundColor: "#f6f9fc", fontFamily: "Arial, sans-serif" };
const container = { margin: "0 auto", padding: "40px 20px", maxWidth: "560px" };
const content = { backgroundColor: "#ffffff", borderRadius: "8px", padding: "32px" };
const heading = { fontSize: "24px", fontWeight: "bold", color: "#1a1a1a" };
const paragraph = { fontSize: "16px", lineHeight: "1.6", color: "#4a4a4a" };
const button = {
  backgroundColor: "#5469d4",
  borderRadius: "6px",
  color: "#fff",
  fontSize: "16px",
  padding: "12px 24px",
  textDecoration: "none",
  display: "inline-block",
};
const divider = { borderColor: "#e6e6e6", margin: "24px 0" };
const footer = { fontSize: "14px", color: "#8898aa" };
```

## Sending with Resend

```typescript
import { Resend } from "resend";
import WelcomeEmail from "./emails/welcome";

const resend = new Resend(process.env.RESEND_API_KEY);

async function sendWelcomeEmail(user: { email: string; name: string }) {
  const { data, error } = await resend.emails.send({
    from: "App <noreply@example.com>",
    to: user.email,
    subject: `Welcome, ${user.name}!`,
    react: WelcomeEmail({ name: user.name, verifyUrl: "https://example.com/verify" }),
  });

  if (error) throw new Error(`Failed to send email: ${error.message}`);
  return data;
}
```

## Sending with Nodemailer

```typescript
import nodemailer from "nodemailer";
import { render } from "@react-email/render";
import WelcomeEmail from "./emails/welcome";

const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST,
  port: 587,
  auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS },
});

async function sendEmail(to: string, name: string) {
  const html = await render(
    WelcomeEmail({ name, verifyUrl: "https://example.com/verify" }),
  );
  await transporter.sendMail({
    from: '"App" <noreply@example.com>',
    to,
    subject: `Welcome, ${name}!`,
    html,
  });
}
```

## MJML Template

```xml
<mjml>
  <mj-head>
    <mj-attributes>
      <mj-all font-family="Arial, sans-serif" />
      <mj-text font-size="16px" line-height="1.6" color="#4a4a4a" />
    </mj-attributes>
  </mj-head>
  <mj-body background-color="#f6f9fc">
    <mj-section background-color="#ffffff" border-radius="8px" padding="32px">
      <mj-column>
        <mj-image src="https://example.com/logo.png" width="120px" />
        <mj-text font-size="24px" font-weight="bold" color="#1a1a1a">
          Welcome!
        </mj-text>
        <mj-text>Thanks for signing up. Click below to verify.</mj-text>
        <mj-button background-color="#5469d4" border-radius="6px">
          Verify Email
        </mj-button>
      </mj-column>
    </mj-section>
  </mj-body>
</mjml>
```

## Email Client Compatibility

```
CLIENT          QUIRKS                           WORKAROUND
─────────────────────────────────────────────────────────────
Outlook         No flexbox, limited CSS          Use tables for layout
Gmail           Strips style tags                Inline all CSS
Apple Mail      Good CSS support                 Most modern CSS works
Yahoo           Strips some attributes           Test padding/margins
Dark Mode       Inverts colors unexpectedly      Use meta color-scheme
```

## Preview and Testing

```bash
# Preview React Email in browser
npx react-email dev

# Build to HTML for testing
npx react-email export
```

## Additional Resources

- React Email: https://react.email/
- Resend: https://resend.com/docs
- MJML: https://mjml.io/
- Can I Email: https://www.caniemail.com/
