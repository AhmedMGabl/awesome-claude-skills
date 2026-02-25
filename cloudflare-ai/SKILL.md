---
name: cloudflare-ai
description: Cloudflare AI patterns covering Workers AI inference, text generation, embeddings, image generation, speech-to-text, Vectorize for RAG, AI Gateway, and edge-deployed AI application development.
---

# Cloudflare AI

This skill should be used when building AI-powered applications on Cloudflare's edge network. It covers Workers AI, Vectorize, AI Gateway, and edge-deployed AI patterns.

## When to Use This Skill

Use this skill when you need to:

- Run AI models at the edge with Workers AI
- Generate text, embeddings, or images
- Build RAG applications with Vectorize
- Route and cache AI requests with AI Gateway
- Deploy AI features globally with low latency

## Workers AI Text Generation

```typescript
// src/index.ts
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const { prompt } = await request.json<{ prompt: string }>();

    const response = await env.AI.run("@cf/meta/llama-3.1-8b-instruct", {
      messages: [
        { role: "system", content: "You are a helpful assistant." },
        { role: "user", content: prompt },
      ],
      max_tokens: 512,
      temperature: 0.7,
    });

    return Response.json(response);
  },
};

interface Env {
  AI: Ai;
}
```

## Streaming Responses

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const { prompt } = await request.json<{ prompt: string }>();

    const stream = await env.AI.run("@cf/meta/llama-3.1-8b-instruct", {
      messages: [{ role: "user", content: prompt }],
      stream: true,
    });

    return new Response(stream, {
      headers: { "Content-Type": "text/event-stream" },
    });
  },
};
```

## Embeddings and Vectorize

```typescript
// wrangler.toml
// [[vectorize]]
// binding = "VECTORIZE"
// index_name = "my-index"

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/index" && request.method === "POST") {
      const { text, id } = await request.json<{ text: string; id: string }>();

      // Generate embedding
      const embedding = await env.AI.run("@cf/baai/bge-base-en-v1.5", {
        text: [text],
      });

      // Store in Vectorize
      await env.VECTORIZE.upsert([
        {
          id,
          values: embedding.data[0],
          metadata: { text },
        },
      ]);

      return Response.json({ success: true });
    }

    if (url.pathname === "/search") {
      const query = url.searchParams.get("q") || "";

      // Generate query embedding
      const queryEmbedding = await env.AI.run("@cf/baai/bge-base-en-v1.5", {
        text: [query],
      });

      // Search Vectorize
      const results = await env.VECTORIZE.query(queryEmbedding.data[0], {
        topK: 5,
        returnMetadata: "all",
      });

      return Response.json(results);
    }

    return new Response("Not Found", { status: 404 });
  },
};
```

## RAG Pattern

```typescript
async function ragQuery(env: Env, question: string): Promise<string> {
  // 1. Generate embedding for the question
  const embedding = await env.AI.run("@cf/baai/bge-base-en-v1.5", {
    text: [question],
  });

  // 2. Search for relevant context
  const results = await env.VECTORIZE.query(embedding.data[0], {
    topK: 3,
    returnMetadata: "all",
  });

  const context = results.matches
    .map((m) => m.metadata?.text)
    .filter(Boolean)
    .join("\n\n");

  // 3. Generate answer with context
  const response = await env.AI.run("@cf/meta/llama-3.1-8b-instruct", {
    messages: [
      {
        role: "system",
        content: `Answer based on the following context. If the context doesn't contain the answer, say so.\n\nContext:\n${context}`,
      },
      { role: "user", content: question },
    ],
  });

  return response.response;
}
```

## Image Generation

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const { prompt } = await request.json<{ prompt: string }>();

    const image = await env.AI.run("@cf/stabilityai/stable-diffusion-xl-base-1.0", {
      prompt,
      num_steps: 20,
    });

    return new Response(image, {
      headers: { "Content-Type": "image/png" },
    });
  },
};
```

## Speech to Text

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const audioData = await request.arrayBuffer();

    const result = await env.AI.run("@cf/openai/whisper", {
      audio: [...new Uint8Array(audioData)],
    });

    return Response.json({
      text: result.text,
      language: result.language,
    });
  },
};
```

## AI Gateway

```typescript
// Route requests through AI Gateway for caching, rate limiting, logging
const response = await fetch(
  `https://gateway.ai.cloudflare.com/v1/${accountId}/${gatewayId}/openai/chat/completions`,
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${env.OPENAI_API_KEY}`,
    },
    body: JSON.stringify({
      model: "gpt-4",
      messages: [{ role: "user", content: "Hello!" }],
    }),
  }
);
```

## Configuration

```toml
# wrangler.toml
name = "my-ai-worker"
main = "src/index.ts"
compatibility_date = "2024-01-01"

[ai]
binding = "AI"

[[vectorize]]
binding = "VECTORIZE"
index_name = "my-documents"
```

## Additional Resources

- Workers AI: https://developers.cloudflare.com/workers-ai/
- Vectorize: https://developers.cloudflare.com/vectorize/
- AI Gateway: https://developers.cloudflare.com/ai-gateway/
