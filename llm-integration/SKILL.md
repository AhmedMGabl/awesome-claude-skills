---
name: llm-integration
description: LLM and AI integration patterns covering the Anthropic Claude API, OpenAI API, structured outputs, function calling, RAG pipelines, embeddings, vector search, prompt engineering, streaming responses, and production AI application patterns.
---

# LLM Integration

This skill should be used when integrating Large Language Models into applications. It covers API usage for Claude and OpenAI, structured outputs, function calling, RAG pipelines, embeddings, and production patterns for AI-powered features.

## When to Use This Skill

Use this skill when you need to:

- Integrate Claude or OpenAI APIs into applications
- Implement structured outputs and function calling
- Build RAG (Retrieval Augmented Generation) pipelines
- Generate and search embeddings
- Stream LLM responses to users
- Implement prompt engineering patterns
- Build AI agents with tool use
- Handle rate limiting and error recovery for AI APIs

## Claude API (Anthropic)

### Basic Usage

```typescript
import Anthropic from "@anthropic-ai/sdk";

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

// Simple message
const message = await anthropic.messages.create({
  model: "claude-sonnet-4-6-20250514",
  max_tokens: 1024,
  messages: [
    { role: "user", content: "Explain quantum computing in 3 sentences." },
  ],
});

console.log(message.content[0].text);
```

### Streaming

```typescript
// Stream responses for real-time UI
const stream = anthropic.messages.stream({
  model: "claude-sonnet-4-6-20250514",
  max_tokens: 2048,
  messages: [{ role: "user", content: "Write a short story about AI." }],
});

for await (const event of stream) {
  if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
    process.stdout.write(event.delta.text);
  }
}

// With event handlers
const stream = anthropic.messages.stream({
  model: "claude-sonnet-4-6-20250514",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Hello" }],
});

stream.on("text", (text) => process.stdout.write(text));
const finalMessage = await stream.finalMessage();
```

### Tool Use (Function Calling)

```typescript
const tools = [
  {
    name: "get_weather",
    description: "Get current weather for a location",
    input_schema: {
      type: "object" as const,
      properties: {
        location: { type: "string", description: "City name" },
        unit: { type: "string", enum: ["celsius", "fahrenheit"], default: "celsius" },
      },
      required: ["location"],
    },
  },
  {
    name: "search_database",
    description: "Search for records in the database",
    input_schema: {
      type: "object" as const,
      properties: {
        query: { type: "string" },
        limit: { type: "number", default: 10 },
      },
      required: ["query"],
    },
  },
];

// Agent loop with tool use
async function runAgent(userMessage: string) {
  const messages: Anthropic.MessageParam[] = [
    { role: "user", content: userMessage },
  ];

  while (true) {
    const response = await anthropic.messages.create({
      model: "claude-sonnet-4-6-20250514",
      max_tokens: 4096,
      tools,
      messages,
    });

    // If model wants to use tools
    if (response.stop_reason === "tool_use") {
      const toolUseBlocks = response.content.filter(
        (block): block is Anthropic.ToolUseBlock => block.type === "tool_use"
      );

      const toolResults: Anthropic.ToolResultBlockParam[] = [];
      for (const toolUse of toolUseBlocks) {
        const result = await executeTool(toolUse.name, toolUse.input);
        toolResults.push({
          type: "tool_result",
          tool_use_id: toolUse.id,
          content: JSON.stringify(result),
        });
      }

      messages.push({ role: "assistant", content: response.content });
      messages.push({ role: "user", content: toolResults });
      continue;
    }

    // Final text response
    const textBlock = response.content.find(
      (block): block is Anthropic.TextBlock => block.type === "text"
    );
    return textBlock?.text ?? "";
  }
}

async function executeTool(name: string, input: Record<string, unknown>) {
  switch (name) {
    case "get_weather":
      return { temperature: 22, condition: "sunny", location: input.location };
    case "search_database":
      return { results: [{ id: 1, name: "Example" }], total: 1 };
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
}
```

### System Prompts and Multi-turn

```typescript
const response = await anthropic.messages.create({
  model: "claude-sonnet-4-6-20250514",
  max_tokens: 2048,
  system: `You are a helpful coding assistant.
    Always provide code examples in TypeScript.
    Be concise and focus on best practices.`,
  messages: [
    { role: "user", content: "How do I handle errors in Express?" },
    { role: "assistant", content: "Here's how to handle errors in Express..." },
    { role: "user", content: "Can you add validation too?" },
  ],
});
```

## OpenAI API

### Structured Outputs

```typescript
import OpenAI from "openai";
import { z } from "zod";
import { zodResponseFormat } from "openai/helpers/zod";

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// Define output schema with Zod
const ExtractedData = z.object({
  name: z.string(),
  email: z.string().email(),
  sentiment: z.enum(["positive", "negative", "neutral"]),
  topics: z.array(z.string()),
  confidence: z.number().min(0).max(1),
});

const completion = await openai.beta.chat.completions.parse({
  model: "gpt-4o",
  messages: [
    {
      role: "system",
      content: "Extract structured data from the user message.",
    },
    {
      role: "user",
      content: "I'm John (john@example.com) and I love your product!",
    },
  ],
  response_format: zodResponseFormat(ExtractedData, "extracted_data"),
});

const data = completion.choices[0].message.parsed;
// { name: "John", email: "john@example.com", sentiment: "positive", ... }
```

## RAG Pipeline

### Embeddings and Vector Search

```typescript
// Generate embeddings
async function getEmbedding(text: string): Promise<number[]> {
  const response = await openai.embeddings.create({
    model: "text-embedding-3-small",
    input: text,
  });
  return response.data[0].embedding;
}

// Store in PostgreSQL with pgvector
import postgres from "postgres";

const sql = postgres(process.env.DATABASE_URL!);

// Create table
await sql`
  CREATE EXTENSION IF NOT EXISTS vector;
  CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB DEFAULT '{}'
  )
`;

// Index documents
async function indexDocument(content: string, metadata: Record<string, unknown>) {
  const embedding = await getEmbedding(content);
  await sql`
    INSERT INTO documents (content, embedding, metadata)
    VALUES (${content}, ${JSON.stringify(embedding)}::vector, ${JSON.stringify(metadata)})
  `;
}

// Semantic search
async function search(query: string, limit = 5) {
  const queryEmbedding = await getEmbedding(query);
  return sql`
    SELECT content, metadata,
           1 - (embedding <=> ${JSON.stringify(queryEmbedding)}::vector) AS similarity
    FROM documents
    ORDER BY embedding <=> ${JSON.stringify(queryEmbedding)}::vector
    LIMIT ${limit}
  `;
}

// RAG: combine search + LLM
async function ragQuery(question: string): Promise<string> {
  // 1. Search for relevant documents
  const docs = await search(question, 5);
  const context = docs.map((d) => d.content).join("\n\n---\n\n");

  // 2. Generate answer with context
  const response = await anthropic.messages.create({
    model: "claude-sonnet-4-6-20250514",
    max_tokens: 2048,
    system: `Answer the question based on the provided context.
             If the context doesn't contain the answer, say so.`,
    messages: [
      {
        role: "user",
        content: `Context:\n${context}\n\nQuestion: ${question}`,
      },
    ],
  });

  return response.content[0].text;
}
```

### Chunking Strategies

```typescript
// Split documents into chunks for embedding
function chunkText(text: string, maxChunkSize = 500, overlap = 50): string[] {
  const sentences = text.match(/[^.!?]+[.!?]+/g) ?? [text];
  const chunks: string[] = [];
  let currentChunk = "";

  for (const sentence of sentences) {
    if ((currentChunk + sentence).length > maxChunkSize && currentChunk) {
      chunks.push(currentChunk.trim());
      // Keep overlap from end of previous chunk
      const words = currentChunk.split(" ");
      currentChunk = words.slice(-Math.ceil(overlap / 5)).join(" ") + " ";
    }
    currentChunk += sentence;
  }

  if (currentChunk.trim()) chunks.push(currentChunk.trim());
  return chunks;
}

// Index a full document
async function indexFullDocument(title: string, content: string) {
  const chunks = chunkText(content);
  for (let i = 0; i < chunks.length; i++) {
    await indexDocument(chunks[i], {
      title,
      chunk_index: i,
      total_chunks: chunks.length,
    });
  }
}
```

## Prompt Engineering Patterns

```typescript
// Few-shot prompting
const messages = [
  {
    role: "user" as const,
    content: "Classify: 'This product is amazing!' -> ",
  },
  { role: "assistant" as const, content: "positive" },
  {
    role: "user" as const,
    content: "Classify: 'Terrible experience, never again' -> ",
  },
  { role: "assistant" as const, content: "negative" },
  {
    role: "user" as const,
    content: `Classify: '${userInput}' -> `,
  },
];

// Chain of thought
const system = `Think step by step before answering.
First, identify the key information.
Then, reason through the problem.
Finally, provide a clear answer.`;

// Constrained output
const system = `You are a JSON generator. Output ONLY valid JSON, no explanation.
Schema: { "summary": string, "keywords": string[], "category": string }`;
```

## Production Patterns

### Rate Limiting and Retries

```typescript
import pRetry from "p-retry";

async function callWithRetry(fn: () => Promise<any>) {
  return pRetry(fn, {
    retries: 3,
    onFailedAttempt: (error) => {
      if (error.message.includes("rate_limit")) {
        // Wait longer for rate limits
        return new Promise((r) => setTimeout(r, 60_000));
      }
    },
    minTimeout: 1000,
    factor: 2,
  });
}

// Token counting (approximate)
function estimateTokens(text: string): number {
  return Math.ceil(text.length / 4); // Rough estimate
}

// Cost tracking
function estimateCost(inputTokens: number, outputTokens: number, model: string) {
  const pricing: Record<string, { input: number; output: number }> = {
    "claude-sonnet-4-6-20250514": { input: 3.0, output: 15.0 },
    "claude-haiku-4-5-20251001": { input: 0.80, output: 4.0 },
    "gpt-4o": { input: 2.5, output: 10.0 },
  };
  const p = pricing[model] ?? pricing["gpt-4o"];
  return (inputTokens * p.input + outputTokens * p.output) / 1_000_000;
}
```

## Additional Resources

- Anthropic SDK: https://docs.anthropic.com/en/api
- OpenAI SDK: https://platform.openai.com/docs
- pgvector: https://github.com/pgvector/pgvector
- LangChain.js: https://js.langchain.com/
- Vercel AI SDK: https://sdk.vercel.ai/
