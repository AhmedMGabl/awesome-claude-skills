---
name: github-copilot-patterns
description: AI-assisted development patterns covering effective prompt engineering for code generation, Copilot Chat workflows, context management, code review with AI, test generation, documentation generation, refactoring suggestions, and maximizing AI coding assistant productivity.
---

# AI-Assisted Development Patterns

This skill should be used when leveraging AI coding assistants effectively. It covers prompt engineering, context management, code review, test generation, and productivity patterns.

## When to Use This Skill

Use this skill when you need to:

- Write effective prompts for code generation
- Use AI assistants for code review
- Generate tests with AI assistance
- Manage context for better suggestions
- Establish team patterns for AI tool usage

## Effective Prompting for Code

```typescript
// PATTERN: Provide context through comments before writing code
// AI generates better code when it understands the intent

// BAD: No context
// function processOrder() { ... }

// GOOD: Clear intent and constraints
// Process a customer order:
// - Validate stock availability
// - Calculate total with tax (8.5%)
// - Apply discount code if present
// - Create order record and decrement stock
// - Return order confirmation with estimated delivery
async function processOrder(input: {
  customerId: string;
  items: Array<{ productId: string; quantity: number }>;
  discountCode?: string;
}): Promise<OrderConfirmation> {
  // AI can now generate appropriate implementation
}
```

## Context Management

```typescript
// PATTERN: Type signatures guide generation
// Detailed types produce better AI-generated implementations

interface PaymentResult {
  success: boolean;
  transactionId: string;
  amount: number;
  currency: string;
  error?: { code: string; message: string };
}

// The return type tells AI what the function should produce
async function processPayment(
  amount: number,
  currency: string,
  paymentMethod: PaymentMethod,
): Promise<PaymentResult> {
  // AI generates implementation matching the return type
}
```

## AI-Assisted Code Review Checklist

```
REVIEW WITH AI:
  [ ] Ask AI to explain complex code sections
  [ ] Request edge case analysis
  [ ] Check for security vulnerabilities
  [ ] Identify potential performance issues
  [ ] Verify error handling completeness

REVIEW PROMPTS:
  "Review this function for edge cases and error handling"
  "What security vulnerabilities exist in this code?"
  "How could this code fail under high concurrency?"
  "Suggest performance improvements for this query"
  "Does this implementation handle all error states?"

ALWAYS VERIFY AI OUTPUT:
  [ ] Test generated code thoroughly
  [ ] Check for hallucinated APIs or methods
  [ ] Verify security implications
  [ ] Ensure code follows project conventions
  [ ] Review imported dependencies actually exist
```

## Test Generation Patterns

```typescript
// PATTERN: Write the function first, then ask AI to generate tests
// Provide the function signature and behavior description

// Given this function:
function calculateShipping(
  weight: number,
  distance: number,
  priority: "standard" | "express" | "overnight",
): number {
  const baseRate = weight * 0.5;
  const distanceRate = distance * 0.01;
  const priorityMultiplier = { standard: 1, express: 1.5, overnight: 3 }[priority];
  return Math.round((baseRate + distanceRate) * priorityMultiplier * 100) / 100;
}

// AI-assisted test prompt:
// "Generate comprehensive tests for calculateShipping covering:
//  - Each priority level
//  - Edge cases (zero weight, zero distance)
//  - Large values
//  - Decimal precision"
```

## Documentation Generation

```typescript
// PATTERN: Use AI to generate JSDoc from implementation
// Then review and refine the generated docs

/**
 * Processes a batch of webhook events with retry logic.
 *
 * @param events - Array of webhook events to process
 * @param options - Processing configuration
 * @param options.maxRetries - Maximum retry attempts per event (default: 3)
 * @param options.concurrency - Number of events to process in parallel (default: 5)
 * @returns Summary of processed, failed, and skipped events
 * @throws {ValidationError} If events array is empty
 *
 * @example
 * ```typescript
 * const result = await processWebhookBatch(events, {
 *   maxRetries: 3,
 *   concurrency: 10,
 * });
 * console.log(`Processed: ${result.processed}, Failed: ${result.failed}`);
 * ```
 */
async function processWebhookBatch(
  events: WebhookEvent[],
  options?: { maxRetries?: number; concurrency?: number },
): Promise<BatchResult> {
  // Implementation
}
```

## Team Guidelines

```
AI CODING ASSISTANT GUIDELINES:

DO:
  - Use AI for boilerplate, tests, and documentation
  - Provide clear context (types, comments, examples)
  - Review all generated code before committing
  - Use AI to explore unfamiliar APIs and patterns
  - Verify generated imports and API calls exist

DON'T:
  - Blindly accept generated code without review
  - Use AI for security-critical logic without audit
  - Trust AI-generated test assertions without verification
  - Copy AI code that you don't understand
  - Skip testing because "AI wrote it"
```

## Additional Resources

- GitHub Copilot: https://github.com/features/copilot
- Claude Code: https://claude.ai/code
- Cursor: https://www.cursor.com/
