---
name: email-sending
description: Transactional email sending covering Resend, SendGrid, and AWS SES APIs, email queue management, template rendering, bounce and complaint handling, SPF/DKIM/DMARC authentication, deliverability monitoring, and bulk email patterns with rate limiting.
---

# Email Sending

This skill should be used when implementing transactional or automated email sending. It covers email APIs, deliverability, authentication, templates, and production email patterns.

## When to Use This Skill

Use this skill when you need to:

- Send transactional emails (confirmations, resets, notifications)
- Integrate with email APIs (Resend, SendGrid, SES)
- Handle bounces and complaints
- Configure email authentication (SPF/DKIM/DMARC)
- Build email queues with retry logic

## Resend (Modern API)

```typescript
import { Resend } from "resend";

const resend = new Resend(process.env.RESEND_API_KEY!);

// Send a single email
async function sendWelcomeEmail(user: { email: string; name: string }) {
  const { data, error } = await resend.emails.send({
    from: "App <noreply@app.example.com>",
    to: user.email,
    subject: `Welcome, ${user.name}!`,
    html: `
      <h1>Welcome to App!</h1>
      <p>Hi ${user.name}, your account is ready.</p>
      <a href="https://app.example.com/dashboard"
         style="display:inline-block;padding:12px 24px;background:#4F46E5;color:white;text-decoration:none;border-radius:6px;">
        Get Started
      </a>
    `,
  });

  if (error) throw new Error(`Email failed: ${error.message}`);
  return data;
}

// Batch sending
async function sendBatchNotifications(recipients: Array<{ email: string; name: string; data: any }>) {
  const batch = recipients.map((r) => ({
    from: "App <noreply@app.example.com>",
    to: r.email,
    subject: "Your weekly summary",
    html: renderTemplate("weekly-summary", { name: r.name, ...r.data }),
  }));

  // Resend supports up to 100 per batch
  const { data, error } = await resend.batch.send(batch);
  return { data, error };
}
```

## SendGrid

```typescript
import sgMail from "@sendgrid/mail";
sgMail.setApiKey(process.env.SENDGRID_API_KEY!);

// Send with dynamic template
async function sendOrderConfirmation(order: Order) {
  await sgMail.send({
    to: order.customerEmail,
    from: { email: "orders@app.example.com", name: "App Orders" },
    templateId: "d-abc123",  // SendGrid dynamic template ID
    dynamicTemplateData: {
      customerName: order.customerName,
      orderNumber: order.id,
      items: order.items,
      total: order.total.toFixed(2),
    },
  });
}

// Webhook for bounces/complaints
app.post("/api/webhooks/sendgrid", (req, res) => {
  for (const event of req.body) {
    switch (event.event) {
      case "bounce":
        handleBounce(event.email, event.reason);
        break;
      case "spamreport":
        handleComplaint(event.email);
        break;
      case "delivered":
        markDelivered(event.email, event.sg_message_id);
        break;
    }
  }
  res.sendStatus(200);
});
```

## Email Queue with BullMQ

```typescript
import { Queue, Worker } from "bullmq";

const emailQueue = new Queue("emails", { connection: { url: process.env.REDIS_URL } });

// Enqueue email
async function queueEmail(to: string, template: string, data: Record<string, unknown>) {
  await emailQueue.add("send", { to, template, data }, {
    attempts: 3,
    backoff: { type: "exponential", delay: 60_000 },
    removeOnComplete: { age: 86400 },
  });
}

// Worker processes emails
const worker = new Worker("emails", async (job) => {
  const { to, template, data } = job.data;
  const html = renderTemplate(template, data);
  await resend.emails.send({
    from: "App <noreply@app.example.com>",
    to,
    subject: getSubject(template, data),
    html,
  });
}, {
  connection: { url: process.env.REDIS_URL },
  limiter: { max: 10, duration: 1000 },  // 10 emails/second
});

worker.on("failed", (job, err) => {
  console.error(`Email to ${job?.data.to} failed: ${err.message}`);
});
```

## Email Authentication (DNS)

```
SPF — Authorize sending servers
  app.example.com TXT "v=spf1 include:amazonses.com include:sendgrid.net -all"

DKIM — Sign emails cryptographically
  resend._domainkey.app.example.com CNAME resend.domainkey.example.com

DMARC — Policy for failed auth
  _dmarc.app.example.com TXT "v=DMARC1; p=quarantine; rua=mailto:dmarc@app.example.com; pct=100"

DELIVERABILITY CHECKLIST:
  [ ] SPF record configured
  [ ] DKIM signing enabled
  [ ] DMARC policy set
  [ ] Custom return-path domain
  [ ] Warm up new sending domains gradually
  [ ] Monitor bounce rate (keep under 2%)
  [ ] Process unsubscribes within 24 hours
  [ ] Include physical address (CAN-SPAM)
  [ ] One-click unsubscribe header (RFC 8058)
```

## Additional Resources

- Resend: https://resend.com/docs
- SendGrid: https://docs.sendgrid.com/
- AWS SES: https://docs.aws.amazon.com/ses/
- DMARC: https://dmarc.org/
