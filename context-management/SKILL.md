---
name: context-management
description: Context management and semantic understanding patterns for Claude Code sessions covering codebase navigation strategies, context window optimization, progressive code exploration, dependency tracing, maintaining working memory across long sessions, and avoiding context drift during complex tasks.
---

# Context Management

This skill should be used to maintain high-quality context awareness throughout Claude Code sessions. It ensures thorough codebase understanding before making changes, prevents context drift, and optimizes how information is gathered and retained.

## When to Use This Skill

Use this skill when:

- Starting work on an unfamiliar codebase or feature
- Working on complex multi-file changes
- Losing track of what was already explored or decided
- Needing to understand how components connect before modifying them
- A task requires deep understanding of existing patterns and conventions

## Core Principles

### 1. Explore Before Acting

Never modify code that has not been read and understood first. Before any implementation:

```
EXPLORATION CHECKLIST:
1. Read the target file(s) completely
2. Identify imports and dependencies
3. Trace call sites (who calls this code?)
4. Check test files for expected behavior
5. Look for related configuration (env vars, config files)
6. Review recent git history for context on recent changes
```

### 2. Progressive Disclosure Strategy

Build understanding in layers — do not try to read the entire codebase at once:

```
Layer 1: Project structure (directory layout, key config files)
   ↓
Layer 2: Entry points (main files, route definitions, exports)
   ↓
Layer 3: Target area (the specific files related to the task)
   ↓
Layer 4: Dependencies (what the target area imports and uses)
   ↓
Layer 5: Consumers (what depends on the target area)
```

### 3. Semantic Code Navigation

When exploring a codebase, follow meaning, not just file paths:

- **Data flow**: Follow how data enters, transforms, and exits
- **Control flow**: Trace execution paths through the system
- **Type flow**: Follow type definitions to understand contracts
- **Error flow**: Trace how errors propagate and are handled
- **State flow**: Understand where state lives and how it changes

### 4. Working Memory Maintenance

During long sessions, actively maintain a mental model:

```
BEFORE EACH MAJOR ACTION, verify:
- What is the current goal?
- What files have been modified so far?
- What decisions were made and why?
- What remains to be done?
- Are there any unresolved questions?
```

## Context Gathering Patterns

### Pattern: Dependency Mapping

Before modifying a function, understand its full dependency graph:

```
Target: updateUserProfile()
  ├── Called by: ProfilePage.tsx (line 45), API route (line 23)
  ├── Calls: validateProfile(), db.user.update(), sendNotification()
  ├── Types: UserProfile, UpdateProfileInput
  ├── Tests: test/user-profile.test.ts (3 test cases)
  └── Config: requires USER_SERVICE_URL env var
```

### Pattern: Convention Discovery

Before writing new code, discover existing patterns:

```
To add a new API endpoint, check:
1. How are existing endpoints structured? (file naming, exports)
2. What middleware is applied? (auth, validation, error handling)
3. How is input validated? (Zod schemas, manual checks)
4. How are responses formatted? (envelope pattern, direct response)
5. How are errors handled? (try/catch, error middleware)
6. Where are tests located? (co-located, separate directory)
```

### Pattern: Change Impact Analysis

Before making changes, assess what might break:

```
Modifying: UserService.getById()
Impact analysis:
  - Direct callers: 4 files (UserController, AdminPanel, AuthMiddleware, ProfileAPI)
  - Indirect consumers: 2 files (Dashboard aggregates user data, Reports)
  - Type changes: UserDTO is used in 8 files
  - Test coverage: 3 direct tests, 5 integration tests touch this
  - Risk: Medium — changing return type would cascade to 8+ files
```

### Pattern: Context Checkpointing

For long tasks, periodically summarize progress:

```
CHECKPOINT — Task: Refactor authentication system
Completed:
  ✓ Read all auth-related files (8 files)
  ✓ Mapped token flow: login → JWT generation → middleware validation
  ✓ Created new token rotation logic in auth/tokens.ts
  ✓ Updated middleware to handle refresh tokens
In progress:
  → Updating login endpoint to return both tokens
  → Need to update 3 client-side token storage files
Remaining:
  - Update logout to invalidate refresh tokens
  - Add tests for token rotation
  - Update API documentation
Decisions made:
  - Using httpOnly cookies (not localStorage) for refresh tokens
  - 15min access token, 7d refresh token lifetimes
  - Storing refresh token hash in DB for revocation
```

## Anti-Patterns to Avoid

### 1. Premature Implementation
Starting to write code before reading existing implementations.

### 2. Assumption-Based Changes
Assuming how code works instead of reading it. "This probably uses X pattern" — check first.

### 3. Single-File Tunnel Vision
Modifying one file without checking what depends on it or what it depends on.

### 4. Context Amnesia
Forgetting what was explored earlier in the session and re-reading the same files.

### 5. Convention Violations
Writing code that doesn't match existing patterns because existing code wasn't reviewed.

## Codebase Exploration Commands

Efficient exploration strategies for different goals:

```
GOAL: "Understand the project"
→ Read package.json/Cargo.toml/pyproject.toml (dependencies reveal architecture)
→ Read directory structure (ls/tree)
→ Read main entry point
→ Read configuration files
→ Read CLAUDE.md/README.md

GOAL: "Understand a feature"
→ Search for feature name in code
→ Read the primary implementation files
→ Trace imports/dependencies
→ Read related tests
→ Check git log for that file/directory

GOAL: "Find where to add something"
→ Find the most similar existing feature
→ Read how it's structured
→ Follow the same pattern
→ Check if there's a generator/template

GOAL: "Debug an issue"
→ Reproduce (read test or try to trigger)
→ Trace the execution path
→ Read error handling in the path
→ Check recent changes (git log/diff)
→ Look for similar issues (grep for error messages)
```

## Integration with Tools

### Effective Tool Usage

When exploring code, use the right tool for each situation:

- **Glob**: Find files by name pattern — "Where are all the test files?"
- **Grep**: Find content in files — "Where is this function called?"
- **Read**: Read full file content — "What does this file do?"
- **Bash (git log)**: Understand history — "Why was this changed?"
- **Bash (git diff)**: See recent changes — "What changed recently?"

### Parallel Exploration

When multiple independent questions need answers, explore in parallel:

```
Instead of sequential:
  Read file A → Read file B → Read file C

Do parallel when files are independent:
  Read file A + Read file B + Read file C (simultaneously)
```

## Additional Resources

- Context Engineering: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering
- Claude Code Best Practices: https://docs.anthropic.com/en/docs/claude-code
