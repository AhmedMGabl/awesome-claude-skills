---
name: twilio-communication
description: Twilio communication APIs covering SMS sending, voice calls with TwiML, WhatsApp messaging, Verify OTP, programmable video, webhooks, and Node.js/Python SDK integration. This skill should be used when integrating SMS, voice, WhatsApp, or OTP verification into applications using the Twilio platform.
---

# Twilio Communication

This skill should be used when building communication features with Twilio: SMS, voice calls, WhatsApp messaging, OTP verification, and webhook handling.

## When to Use This Skill

Use this skill when you need to:

- Send SMS or MMS messages programmatically
- Make or receive voice calls using TwiML
- Send WhatsApp messages via the Twilio API
- Implement phone number verification with OTP
- Handle inbound Twilio webhooks for messages or calls
- Manage status callbacks for delivery tracking

## Node.js SDK Setup

```bash
npm install twilio
```

```typescript
// lib/twilio.ts
import Twilio from "twilio";

export const twilio = new Twilio(
  process.env.TWILIO_ACCOUNT_SID!,
  process.env.TWILIO_AUTH_TOKEN!
);
export const FROM_NUMBER = process.env.TWILIO_PHONE_NUMBER!; // E.164: +15551234567
```

Required env vars: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`

## Sending SMS Messages

```typescript
import { twilio, FROM_NUMBER } from "@/lib/twilio";

async function sendSMS(to: string, body: string) {
  const msg = await twilio.messages.create({
    from: FROM_NUMBER,
    to, // E.164: +15559876543
    body,
    statusCallback: `${process.env.APP_URL}/api/twilio/status`,
  });
  return msg.sid;
}
```

## Voice Calls with TwiML

```typescript
import { twiml } from "twilio";
import { NextResponse } from "next/server";

// Initiate an outbound call
async function makeCall(to: string) {
  return twilio.calls.create({
    from: FROM_NUMBER,
    to,
    url: `${process.env.APP_URL}/api/twilio/voice`,
    statusCallback: `${process.env.APP_URL}/api/twilio/call-status`,
    statusCallbackEvent: ["initiated", "ringing", "answered", "completed"],
  });
}

// TwiML response served at /api/twilio/voice
export async function POST() {
  const response = new twiml.VoiceResponse();
  response.say({ voice: "Polly.Joanna" }, "Hello! Your verification code is 1 2 3 4 5 6.");
  response.pause({ length: 1 });
  response.say("Goodbye.");
  return new NextResponse(response.toString(), {
    headers: { "Content-Type": "text/xml" },
  });
}
```

## WhatsApp Messaging

```typescript
// Send a WhatsApp message (use sandbox number "whatsapp:+14155238886" for testing)
async function sendWhatsApp(to: string, body: string) {
  return twilio.messages.create({
    from: `whatsapp:${FROM_NUMBER}`,
    to: `whatsapp:${to}`,
    body,
  });
}

// Send a Content Template message (required outside the 24h session window)
async function sendWhatsAppTemplate(to: string, contentSid: string, variables: Record<string, string>) {
  return twilio.messages.create({
    from: `whatsapp:${FROM_NUMBER}`,
    to: `whatsapp:${to}`,
    contentSid,
    contentVariables: JSON.stringify(variables),
  });
}
```

## Verify API for OTP

```typescript
const SERVICE_SID = process.env.TWILIO_VERIFY_SERVICE_SID!;

async function sendOTP(to: string, channel: "sms" | "call" | "whatsapp" = "sms") {
  await twilio.verify.v2.services(SERVICE_SID).verifications.create({ to, channel });
}

async function verifyOTP(to: string, code: string): Promise<boolean> {
  const check = await twilio.verify.v2
    .services(SERVICE_SID)
    .verificationChecks.create({ to, code });
  return check.status === "approved";
}

// API route: POST { phone } to send, POST { phone, code } to verify
export async function POST(req: Request) {
  const { phone, code } = await req.json();
  if (code) return Response.json({ approved: await verifyOTP(phone, code) });
  await sendOTP(phone);
  return Response.json({ sent: true });
}
```

## Webhook Handling

```typescript
import { validateRequest } from "twilio";

// Inbound SMS handler — app/api/twilio/sms/route.ts
export async function POST(req: Request) {
  const body = await req.text();
  const url = `${process.env.APP_URL}/api/twilio/sms`;
  const signature = req.headers.get("x-twilio-signature") ?? "";
  const params = Object.fromEntries(new URLSearchParams(body));

  if (!validateRequest(process.env.TWILIO_AUTH_TOKEN!, signature, url, params)) {
    return new Response("Forbidden", { status: 403 });
  }

  const { From, Body, MessageSid } = params;
  await handleInboundMessage({ from: From, body: Body, sid: MessageSid });

  const response = new twiml.MessagingResponse();
  response.message("Thanks, we received your message.");
  return new Response(response.toString(), { headers: { "Content-Type": "text/xml" } });
}
```

## Error Handling and Status Callbacks

```typescript
import { RestException } from "twilio/lib/base/rest/version";

async function safeSendSMS(to: string, body: string) {
  try {
    const msg = await twilio.messages.create({ from: FROM_NUMBER, to, body });
    return { success: true, sid: msg.sid };
  } catch (err) {
    if (err instanceof RestException) {
      // Common codes: 21211 = invalid number, 21614 = not SMS-capable
      return { success: false, code: err.code, message: err.message };
    }
    throw err;
  }
}

// Status callback — app/api/twilio/status/route.ts
// MessageStatus lifecycle: queued -> sending -> sent -> delivered | failed | undelivered
export async function POST(req: Request) {
  const params = Object.fromEntries(new URLSearchParams(await req.text()));
  const { MessageSid, MessageStatus, ErrorCode } = params;
  await db.message.update({
    where: { twilioSid: MessageSid },
    data: { status: MessageStatus, errorCode: ErrorCode ?? null },
  });
  return new Response(null, { status: 204 });
}
```

## Additional Resources

- Twilio Docs: https://www.twilio.com/docs
- Error Codes: https://www.twilio.com/docs/api/errors
- TwiML Reference: https://www.twilio.com/docs/voice/twiml
- Verify API: https://www.twilio.com/docs/verify/api
- WhatsApp Sandbox: https://www.twilio.com/docs/whatsapp/sandbox
