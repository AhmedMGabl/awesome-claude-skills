---
name: openai-api
description: OpenAI API integration covering chat completions, function calling, structured outputs, streaming, embeddings, image generation, text-to-speech, Whisper transcription, assistants API, and token management.
---

# OpenAI API

This skill should be used when integrating OpenAI APIs into applications. It covers chat completions, function calling, structured outputs, streaming, embeddings, and multimodal features.

## When to Use This Skill

Use this skill when you need to:

- Build chat applications with GPT models
- Implement function calling for tool use
- Generate structured JSON outputs
- Stream responses for real-time UX
- Use embeddings for semantic search

## Setup

```typescript
import OpenAI from "openai";

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});
```

## Chat Completions

```typescript
const completion = await openai.chat.completions.create({
  model: "gpt-4o",
  messages: [
    { role: "system", content: "You are a helpful assistant." },
    { role: "user", content: "Explain quantum computing in simple terms." },
  ],
  temperature: 0.7,
  max_tokens: 1000,
});

console.log(completion.choices[0].message.content);
```

## Function Calling

```typescript
const tools: OpenAI.ChatCompletionTool[] = [
  {
    type: "function",
    function: {
      name: "get_weather",
      description: "Get current weather for a location",
      parameters: {
        type: "object",
        properties: {
          location: { type: "string", description: "City name" },
          unit: { type: "string", enum: ["celsius", "fahrenheit"] },
        },
        required: ["location"],
      },
    },
  },
];

const response = await openai.chat.completions.create({
  model: "gpt-4o",
  messages: [{ role: "user", content: "What's the weather in Tokyo?" }],
  tools,
  tool_choice: "auto",
});

const message = response.choices[0].message;

if (message.tool_calls) {
  for (const call of message.tool_calls) {
    const args = JSON.parse(call.function.arguments);
    const result = await getWeather(args.location, args.unit);

    // Send tool result back
    const followUp = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [
        { role: "user", content: "What's the weather in Tokyo?" },
        message,
        {
          role: "tool",
          tool_call_id: call.id,
          content: JSON.stringify(result),
        },
      ],
    });
  }
}
```

## Structured Outputs

```typescript
import { z } from "zod";
import { zodResponseFormat } from "openai/helpers/zod";

const ProductReview = z.object({
  sentiment: z.enum(["positive", "negative", "neutral"]),
  score: z.number().min(1).max(5),
  summary: z.string(),
  pros: z.array(z.string()),
  cons: z.array(z.string()),
});

const completion = await openai.beta.chat.completions.parse({
  model: "gpt-4o",
  messages: [
    { role: "system", content: "Analyze product reviews." },
    { role: "user", content: reviewText },
  ],
  response_format: zodResponseFormat(ProductReview, "review"),
});

const review = completion.choices[0].message.parsed;
// Fully typed: review.sentiment, review.score, etc.
```

## Streaming

```typescript
const stream = await openai.chat.completions.create({
  model: "gpt-4o",
  messages: [{ role: "user", content: "Write a story." }],
  stream: true,
});

for await (const chunk of stream) {
  const content = chunk.choices[0]?.delta?.content ?? "";
  process.stdout.write(content);
}
```

## Embeddings

```typescript
const response = await openai.embeddings.create({
  model: "text-embedding-3-small",
  input: "Search query or document text",
  dimensions: 512,
});

const embedding = response.data[0].embedding; // number[]

// Cosine similarity
function cosineSimilarity(a: number[], b: number[]): number {
  const dot = a.reduce((sum, val, i) => sum + val * b[i], 0);
  const magA = Math.sqrt(a.reduce((sum, val) => sum + val * val, 0));
  const magB = Math.sqrt(b.reduce((sum, val) => sum + val * val, 0));
  return dot / (magA * magB);
}
```

## Image Generation

```typescript
const image = await openai.images.generate({
  model: "dall-e-3",
  prompt: "A serene mountain landscape at sunset",
  n: 1,
  size: "1024x1024",
  quality: "hd",
});

const imageUrl = image.data[0].url;
```

## Additional Resources

- OpenAI docs: https://platform.openai.com/docs
- OpenAI Cookbook: https://cookbook.openai.com/
- API reference: https://platform.openai.com/docs/api-reference
