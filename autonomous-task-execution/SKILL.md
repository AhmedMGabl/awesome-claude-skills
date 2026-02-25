---
name: autonomous-task-execution
description: Autonomous task execution patterns for AI coding assistants covering goal decomposition, self-directed research, decision-making without hand-holding, progress tracking, error recovery, proactive tool and skill usage, and completing complex multi-step tasks independently.
---

# Autonomous Task Execution

This skill should be used to drive tasks to completion independently. It ensures thorough research, smart decomposition, proactive use of available tools and skills, self-correction, and consistent progress without requiring constant user intervention.

## When to Use This Skill

Use this skill when:

- Receiving a complex or multi-step task from the user
- The task requires research, planning, and execution
- Working independently without step-by-step guidance
- Needing to make implementation decisions autonomously
- A previous approach hit a blocker and needs recovery

## Core Principles

### 1. Understand Before Acting

```
BEFORE starting any task:
1. What exactly is the user asking for? (Restate in precise terms)
2. What is the success criteria? (How to know when done)
3. What do I already know? (From context, CLAUDE.md, codebase)
4. What do I need to learn? (Research before implementation)
5. What tools/skills/plugins are available? (Check installed capabilities)
```

### 2. Proactive Tool and Skill Discovery

Before starting work, check what capabilities are available:

```
TOOL/SKILL CHECKLIST:
- Are there relevant skills installed? → Use Skill tool to check
- Are there MCP servers with useful tools? → Check available tools
- Are there plugins that handle part of this task? → Use them
- Are there existing patterns in the codebase? → Follow them
- Are there tests I should run? → Run them before and after changes

RULE: If a tool or skill exists for a task, USE IT.
Do not manually do what a tool can automate.
Do not write from scratch what a skill provides patterns for.
```

### 3. Goal Decomposition

Break complex tasks into clear, ordered steps:

```
TASK: "Add user authentication to the API"

DECOMPOSITION:
1. Research — Read existing code structure, check for auth dependencies
2. Design — Choose approach (JWT vs sessions), plan file changes
3. Dependencies — Install needed packages
4. Implementation — Write auth logic, middleware, routes
5. Integration — Wire auth into existing endpoints
6. Testing — Write tests, verify manually
7. Documentation — Update API docs, README if needed
8. Review — Self-review changes, check for security issues
```

### 4. Decision-Making Framework

When facing a choice, decide and move forward:

```
DECISION PROCESS:
1. Is this a reversible decision? → Make the best choice, keep moving
2. Is this a significant architectural choice? → Ask user for confirmation
3. Are there strong conventions in the codebase? → Follow them
4. Are there multiple valid approaches? → Choose the simplest one
5. Am I unsure about user preference? → Make a reasonable default, note it

RULE: Don't stall on minor decisions. Progress > perfection.
```

### 5. Self-Correction and Recovery

When something goes wrong:

```
ERROR RECOVERY PROTOCOL:
1. Read the error message carefully (don't just retry)
2. Understand WHY it failed (root cause, not symptoms)
3. Check if the approach is fundamentally wrong (not just a typo)
4. If blocked:
   a. Try an alternative approach
   b. Search for similar solutions in the codebase
   c. Check documentation
   d. Only ask the user if truly stuck after trying alternatives
5. Never brute-force: if retrying the same thing, stop and rethink
```

## Execution Patterns

### Pattern: Research-First Execution

```
1. RESEARCH PHASE (do not skip)
   - Read all relevant source files
   - Check existing patterns and conventions
   - Look at dependencies and config
   - Review recent git history for context
   - Search for similar implementations in the codebase

2. PLAN PHASE
   - List specific files to create/modify
   - Define the order of changes
   - Identify potential risks or breaking changes
   - Note any decisions to communicate to user

3. EXECUTE PHASE
   - Work through the plan step by step
   - Run tests after each significant change
   - Verify changes compile/lint
   - Keep track of what's done and what remains

4. VERIFY PHASE
   - Re-read modified files for correctness
   - Run full test suite
   - Check for common mistakes (imports, types, edge cases)
   - Confirm the original goal is met
```

### Pattern: Parallel Exploration

When research requires checking multiple independent things:

```
Instead of:
  Read config → then read routes → then read tests → then read types

Do (in parallel when independent):
  Read config + Read routes + Read tests + Read types
  → Then synthesize findings and plan

This is faster AND builds a more complete picture.
```

### Pattern: Progressive Implementation

For large changes, implement in testable increments:

```
Step 1: Core logic (smallest working piece)
  → Test it
Step 2: Integration with existing code
  → Test it
Step 3: Edge cases and error handling
  → Test it
Step 4: Polish (logging, documentation, cleanup)
  → Final test

NOT: Write everything at once → hope it works
```

### Pattern: Proactive Communication

Keep the user informed without asking unnecessary questions:

```
GOOD:
  "I'm implementing JWT auth with refresh token rotation.
   Using httpOnly cookies based on the existing session pattern
   I found in auth/middleware.ts. Running tests now."

BAD:
  "Should I use JWT or sessions?"
  (When the codebase already has JWT infrastructure)

BAD:
  [silence for 20 tool calls, then a wall of code]
  (User has no idea what's happening)
```

## Anti-Patterns to Avoid

### 1. Permission Paralysis
Asking the user for approval on every minor decision instead of making reasonable choices.

### 2. Tunnel Vision
Jumping into implementation without reading existing code or understanding the broader context.

### 3. Tool Blindness
Writing code manually when a tool, skill, or plugin could handle it automatically.

### 4. Retry Loops
Repeating the same failing approach instead of trying an alternative.

### 5. Context Dump
Dumping large amounts of information at the user instead of synthesizing findings.

### 6. Scope Creep
Adding features or improvements not requested, especially when the core task is not yet complete.

### 7. Abandoning Research
Reading one file and jumping to conclusions instead of building a complete picture.

## Task Completion Checklist

Before declaring a task complete:

```
□ Original goal is met (re-read user's request)
□ Code compiles/runs without errors
□ Tests pass (existing + new if applicable)
□ No obvious security issues introduced
□ Changes follow existing codebase conventions
□ No unnecessary files or debug code left behind
□ User is informed of what was done and any decisions made
□ Any follow-up items are noted
```

## Additional Resources

- Claude Code Documentation: https://docs.anthropic.com/en/docs/claude-code
- Anthropic Prompt Engineering: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering
