---
name: claude-api
description: Anthropic Claude API integration covering messages API, streaming, tool use, vision, system prompts, prompt caching, extended thinking, batch processing, and TypeScript/Python SDK patterns.
---

# Anthropic Claude API

This skill should be used when integrating the Anthropic Claude API into applications. It covers messages, streaming, tool use, vision, prompt caching, extended thinking, and batch processing.

## When to Use This Skill

Use this skill when you need to:

- Build applications with Claude models
- Implement tool use for agentic workflows
- Stream responses for real-time UX
- Process images and documents with vision
- Optimize costs with prompt caching

## Setup

```typescript
import Anthropic from "@anthropic-ai/sdk";

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});
```

## Messages API

```typescript
const message = await anthropic.messages.create({
  model: "claude-sonnet-4-20250514",
  max_tokens: 1024,
  system: "You are a helpful coding assistant.",
  messages: [
    { role: "user", content: "Explain closures in JavaScript." },
  ],
});

console.log(message.content[0].type === "text" ? message.content[0].text : "");
```

## Streaming

```typescript
const stream = anthropic.messages.stream({
  model: "claude-sonnet-4-20250514",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Write a haiku about coding." }],
});

for await (const event of stream) {
  if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
    process.stdout.write(event.delta.text);
  }
}

const finalMessage = await stream.finalMessage();
```

## Tool Use

```typescript
const tools: Anthropic.Tool[] = [
  {
    name: "get_weather",
    description: "Get current weather for a location",
    input_schema: {
      type: "object",
      properties: {
        location: { type: "string", description: "City name" },
      },
      required: ["location"],
    },
  },
];

const response = await anthropic.messages.create({
  model: "claude-sonnet-4-20250514",
  max_tokens: 1024,
  tools,
  messages: [{ role: "user", content: "What's the weather in London?" }],
});

// Handle tool use
for (const block of response.content) {
  if (block.type === "tool_use") {
    const result = await getWeather(block.input.location);

    // Send tool result back
    const followUp = await anthropic.messages.create({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1024,
      tools,
      messages: [
        { role: "user", content: "What's the weather in London?" },
        { role: "assistant", content: response.content },
        {
          role: "user",
          content: [{
            type: "tool_result",
            tool_use_id: block.id,
            content: JSON.stringify(result),
          }],
        },
      ],
    });
  }
}
```

## Vision

```typescript
const message = await anthropic.messages.create({
  model: "claude-sonnet-4-20250514",
  max_tokens: 1024,
  messages: [{
    role: "user",
    content: [
      {
        type: "image",
        source: {
          type: "base64",
          media_type: "image/png",
          data: base64ImageData,
        },
      },
      { type: "text", text: "Describe this image in detail." },
    ],
  }],
});
```

## Prompt Caching

```typescript
const message = await anthropic.messages.create({
  model: "claude-sonnet-4-20250514",
  max_tokens: 1024,
  system: [
    {
      type: "text",
      text: longSystemPrompt, // Large context to cache
      cache_control: { type: "ephemeral" },
    },
  ],
  messages: [{ role: "user", content: "Question about the context above." }],
});

// Check cache usage
console.log("Cache read:", message.usage.cache_read_input_tokens);
console.log("Cache created:", message.usage.cache_creation_input_tokens);
```

## Extended Thinking

```typescript
const message = await anthropic.messages.create({
  model: "claude-sonnet-4-20250514",
  max_tokens: 16000,
  thinking: {
    type: "enabled",
    budget_tokens: 10000,
  },
  messages: [{ role: "user", content: "Solve this complex math problem..." }],
});

for (const block of message.content) {
  if (block.type === "thinking") console.log("Thinking:", block.thinking);
  if (block.type === "text") console.log("Answer:", block.text);
}
```

## Additional Resources

- Anthropic docs: https://docs.anthropic.com/
- TypeScript SDK: https://github.com/anthropics/anthropic-sdk-typescript
- Python SDK: https://github.com/anthropics/anthropic-sdk-python
