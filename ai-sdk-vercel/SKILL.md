---
name: ai-sdk-vercel
description: Vercel AI SDK development covering streaming text generation, chat interfaces, tool calling, structured outputs with Zod, multi-provider support (OpenAI, Anthropic, Google), RAG patterns, middleware, useChat and useCompletion hooks, and edge runtime deployment.
---

# Vercel AI SDK

This skill should be used when building AI-powered applications with the Vercel AI SDK. It covers streaming, chat, tool calling, structured output, and multi-provider support.

## When to Use This Skill

Use this skill when you need to:

- Build streaming AI chat interfaces
- Implement tool calling with LLMs
- Generate structured output with Zod schemas
- Support multiple AI providers
- Build RAG (Retrieval-Augmented Generation) pipelines

## Streaming Chat API Route

```typescript
// app/api/chat/route.ts
import { streamText } from "ai";
import { openai } from "@ai-sdk/openai";

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: openai("gpt-4o"),
    system: "You are a helpful assistant.",
    messages,
  });

  return result.toDataStreamResponse();
}
```

## React Chat Component

```tsx
"use client";
import { useChat } from "@ai-sdk/react";

export function Chat() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat();

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((m) => (
          <div key={m.id} className={m.role === "user" ? "text-right" : "text-left"}>
            <div className={`inline-block rounded-lg px-4 py-2 ${
              m.role === "user" ? "bg-blue-500 text-white" : "bg-gray-100"
            }`}>
              {m.content}
            </div>
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="p-4 border-t">
        <input
          value={input}
          onChange={handleInputChange}
          placeholder="Type a message..."
          className="w-full p-2 border rounded"
          disabled={isLoading}
        />
      </form>
    </div>
  );
}
```

## Tool Calling

```typescript
import { streamText, tool } from "ai";
import { openai } from "@ai-sdk/openai";
import { z } from "zod";

const result = streamText({
  model: openai("gpt-4o"),
  messages,
  tools: {
    getWeather: tool({
      description: "Get current weather for a location",
      parameters: z.object({
        city: z.string().describe("City name"),
        unit: z.enum(["celsius", "fahrenheit"]).optional(),
      }),
      execute: async ({ city, unit = "celsius" }) => {
        const weather = await fetchWeather(city, unit);
        return { temperature: weather.temp, condition: weather.condition };
      },
    }),
    searchProducts: tool({
      description: "Search product catalog",
      parameters: z.object({
        query: z.string(),
        maxResults: z.number().default(5),
      }),
      execute: async ({ query, maxResults }) => {
        return await db.product.findMany({
          where: { name: { contains: query } },
          take: maxResults,
        });
      },
    }),
  },
  maxSteps: 5,
});
```

## Structured Output

```typescript
import { generateObject } from "ai";
import { openai } from "@ai-sdk/openai";
import { z } from "zod";

const { object } = await generateObject({
  model: openai("gpt-4o"),
  schema: z.object({
    recipe: z.object({
      name: z.string(),
      ingredients: z.array(z.object({
        item: z.string(),
        amount: z.string(),
      })),
      steps: z.array(z.string()),
      prepTime: z.number().describe("Prep time in minutes"),
    }),
  }),
  prompt: "Generate a recipe for chocolate chip cookies",
});

console.log(object.recipe.name);
console.log(object.recipe.ingredients);
```

## Multi-Provider Support

```typescript
import { openai } from "@ai-sdk/openai";
import { anthropic } from "@ai-sdk/anthropic";
import { google } from "@ai-sdk/google";

// Switch providers with one line
const model = anthropic("claude-sonnet-4-20250514");
// const model = openai("gpt-4o");
// const model = google("gemini-2.0-flash");

const result = streamText({ model, messages });
```

## RAG Pattern

```typescript
import { streamText, embed } from "ai";
import { openai } from "@ai-sdk/openai";

// 1. Embed the query
const { embedding } = await embed({
  model: openai.embedding("text-embedding-3-small"),
  value: userQuery,
});

// 2. Search vector database
const relevantDocs = await vectorDb.search(embedding, { topK: 5 });

// 3. Generate with context
const result = streamText({
  model: openai("gpt-4o"),
  system: `Answer using this context:\n${relevantDocs.map((d) => d.text).join("\n\n")}`,
  messages,
});
```

## Provider Comparison

```
PROVIDER       MODELS                   STRENGTHS
──────────────────────────────────────────────────────
OpenAI         gpt-4o, gpt-4o-mini      Tool calling, vision
Anthropic      claude-sonnet, opus       Long context, coding
Google         gemini-2.0-flash         Multimodal, speed
Mistral        mistral-large            Cost-effective
```

## Additional Resources

- AI SDK docs: https://sdk.vercel.ai/docs
- AI SDK providers: https://sdk.vercel.ai/providers
- AI SDK examples: https://sdk.vercel.ai/examples
