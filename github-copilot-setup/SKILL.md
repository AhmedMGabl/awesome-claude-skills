---
name: github-copilot-setup
description: GitHub Copilot configuration and productivity covering VS Code setup, custom instructions, Copilot Chat usage, code completion optimization, workspace context, slash commands, context variables, agent mode, and team productivity patterns.
---

# GitHub Copilot Setup

This skill should be used when configuring and optimizing GitHub Copilot usage. It covers VS Code setup, custom instructions, chat features, and productivity patterns.

## When to Use This Skill

Use this skill when you need to:

- Configure GitHub Copilot in VS Code
- Write effective custom instructions
- Use Copilot Chat for code generation
- Optimize code completion suggestions
- Set up team-wide Copilot patterns

## VS Code Settings

```json
// .vscode/settings.json
{
  "github.copilot.enable": {
    "*": true,
    "markdown": true,
    "plaintext": false,
    "yaml": true
  },
  "github.copilot.chat.localeOverride": "en",
  "editor.inlineSuggest.enabled": true
}
```

## Custom Instructions

```markdown
<!-- .github/copilot-instructions.md -->
# Project Context

This is a Next.js 14 App Router project using TypeScript, Tailwind CSS, and Prisma.

## Coding Standards
- Use functional components with hooks
- Prefer named exports over default exports
- Use Zod for all runtime validation
- Error handling: use Result<T, E> pattern, never throw in business logic
- Database: use Prisma with transactions for multi-step operations

## Project Structure
- app/ — Next.js App Router pages and layouts
- components/ — React components (ui/ for primitives, features/ for business)
- lib/ — Shared utilities, database client, auth config
- server/ — Server-side business logic and data access

## Naming Conventions
- Components: PascalCase (UserProfile.tsx)
- Utilities: camelCase (formatDate.ts)
- Constants: UPPER_SNAKE_CASE
- Database models: PascalCase singular (User, Post)
```

## Copilot Chat Slash Commands

```
/explain     — Explain selected code
/fix         — Fix issues in selected code
/tests       — Generate tests for selected code
/doc         — Generate documentation
/new         — Scaffold a new project or file
/newNotebook — Create a new Jupyter notebook
```

## Context Variables

```
@workspace   — Reference entire workspace
@terminal    — Include terminal output
@vscode      — VS Code settings and extensions
#file:path   — Reference a specific file
#selection   — Currently selected code
```

## Effective Prompting Patterns

```markdown
// Good: Specific with context
"Create a React hook that fetches paginated data from /api/users,
handles loading/error states, and returns { data, isLoading, error, fetchMore }"

// Good: Reference existing code
"Using the same pattern as #file:hooks/useProducts.ts,
create a useOrders hook that fetches from /api/orders"

// Good: Constraint-based
"Refactor this function to:
1. Use early returns instead of nested if/else
2. Add Zod validation for the input
3. Return a Result type instead of throwing"
```

## .copilotignore

```
# .copilotignore — Exclude files from Copilot context
.env*
*.pem
*.key
secrets/
node_modules/
dist/
coverage/
```

## Team Productivity Tips

```
TIP                                  BENEFIT
──────────────────────────────────────────────────────
Custom instructions file             Consistent code style
.copilotignore for secrets           Security
Comment-driven development           Better suggestions
Accept partial suggestions           Tab then edit
Use Chat for complex logic           Multi-file context
```

## Additional Resources

- Copilot docs: https://docs.github.com/en/copilot
- Copilot Chat: https://docs.github.com/en/copilot/using-github-copilot/asking-github-copilot-questions-in-your-ide
- Custom instructions: https://docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot
