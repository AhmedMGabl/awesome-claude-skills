---
name: research-and-analysis
description: Deep research and analysis patterns for Claude Code covering systematic codebase exploration, web research strategies, multi-source information synthesis, architecture analysis, technology comparison, decision documentation, and thorough investigation before implementation.
---

# Research & Analysis

This skill should be used to conduct thorough research before making implementation decisions. It covers systematic codebase exploration, web research, technology comparison, and synthesizing findings into actionable recommendations.

## When to Use This Skill

Use this skill when:

- Evaluating technology choices for a project
- Investigating unfamiliar codebases or libraries
- Comparing multiple approaches to solve a problem
- Conducting root cause analysis for bugs
- Gathering requirements before implementation
- Understanding existing architecture before making changes

## Research Methodology

### Phase 1: Define the Question

```
Before researching, be precise about what needs to be answered:

VAGUE: "How should we handle authentication?"
PRECISE: "What auth approach fits a Next.js 15 app with:
  - Social login (Google, GitHub)
  - Role-based access (admin, editor, viewer)
  - API token support for programmatic access
  - Session duration of 30 days
  - Existing Prisma + PostgreSQL stack?"

The more precise the question, the more useful the research.
```

### Phase 2: Gather Information

#### Codebase Research

```
1. PROJECT FOUNDATIONS
   - Read package.json/config files for existing dependencies
   - Check CLAUDE.md and README.md for project conventions
   - Review directory structure for architectural patterns
   - Look at recent git history for active development areas

2. EXISTING PATTERNS
   - Search for similar functionality already in the codebase
   - Identify the patterns used (naming conventions, file structure)
   - Read test files to understand expected behavior
   - Check configuration for environment-specific settings

3. DEPENDENCY ANALYSIS
   - What libraries are already installed?
   - What versions are being used?
   - Are there peer dependency constraints?
   - What does the existing lock file reveal about the dependency tree?
```

#### Web Research

```
Use web search strategically:

1. CURRENT STATE — Search for "[technology] [year]" to get current best practices
2. OFFICIAL DOCS — Go to official documentation first, not blog posts
3. MIGRATION GUIDES — If upgrading, check official migration guides
4. KNOWN ISSUES — Search for "[library] issues [version]" for known problems
5. ALTERNATIVES — Search for "[technology] vs [alternative] 2025" for comparisons
6. COMMUNITY — Check GitHub discussions, Stack Overflow for real-world usage

AVOID: Outdated tutorials, AI-generated blog spam, solutions for old versions
```

#### Documentation Deep-Dive

```
When learning a new library/API:

1. Read the "Getting Started" guide completely
2. Read the API reference for the specific methods needed
3. Check the changelog for recent breaking changes
4. Look at example projects in the official repo
5. Read the "Guides" section for the specific feature needed
```

### Phase 3: Analyze and Compare

#### Technology Comparison Framework

```
For each option, evaluate:

┌─────────────────┬───────────────┬───────────────┬───────────────┐
│ Criteria        │ Option A      │ Option B      │ Option C      │
├─────────────────┼───────────────┼───────────────┼───────────────┤
│ Fits existing   │ High/Med/Low  │ High/Med/Low  │ High/Med/Low  │
│ stack?          │               │               │               │
├─────────────────┼───────────────┼───────────────┼───────────────┤
│ Community/      │               │               │               │
│ maintenance     │               │               │               │
├─────────────────┼───────────────┼───────────────┼───────────────┤
│ Learning curve  │               │               │               │
├─────────────────┼───────────────┼───────────────┼───────────────┤
│ Performance     │               │               │               │
├─────────────────┼───────────────┼───────────────┼───────────────┤
│ Production      │               │               │               │
│ readiness       │               │               │               │
└─────────────────┴───────────────┴───────────────┴───────────────┘

Recommendation: [Option] because [specific reasons tied to project context]
```

#### Architecture Analysis

```
When analyzing existing architecture:

1. COMPONENTS — What are the major components/services?
2. DATA FLOW — How does data move through the system?
3. BOUNDARIES — Where are the module/service boundaries?
4. COUPLING — What are the dependencies between components?
5. PATTERNS — What architectural patterns are used? (MVC, CQRS, event-driven)
6. PAIN POINTS — Where does the current architecture struggle?
7. CONSTRAINTS — What can't be easily changed? (DB schema, public APIs)
```

### Phase 4: Synthesize Findings

#### Research Summary Template

```markdown
## Research: [Topic]

### Context
[Why this research was needed, what triggered it]

### Key Findings
1. [Most important finding]
2. [Second most important]
3. [Third most important]

### Recommendation
[Clear recommendation with reasoning]

### Trade-offs
- Pro: [advantage]
- Con: [disadvantage]
- Mitigated by: [how to handle the cons]

### Implementation Impact
- Files to modify: [list]
- New dependencies: [list]
- Breaking changes: [list or "none"]
- Estimated scope: [small/medium/large]
```

## Research Patterns

### Pattern: Spike Investigation

For unknowns that need quick prototyping:

```
1. Create a minimal test/prototype (not production code)
2. Test the specific question (does library X support feature Y?)
3. Measure what matters (performance, API ergonomics, bundle size)
4. Document findings
5. Discard the spike code
6. Implement the real solution using what was learned
```

### Pattern: Dependency Audit

Before adding a new dependency:

```
CHECK:
□ Is this actively maintained? (last commit, open issues response)
□ What is the download count / GitHub stars? (adoption signal)
□ What is the bundle size? (for frontend dependencies)
□ Are there known security vulnerabilities?
□ Does it have TypeScript types?
□ What are its transitive dependencies? (bloat risk)
□ Is there a simpler alternative or built-in solution?
□ Does the project already have something similar?
```

### Pattern: Root Cause Analysis

For debugging complex issues:

```
1. REPRODUCE — Can the issue be consistently triggered?
2. ISOLATE — What is the minimal reproduction?
3. TIMELINE — When did this start? (git bisect)
4. TRACE — Follow the execution path step by step
5. HYPOTHESIZE — What could cause this behavior?
6. TEST — Verify each hypothesis
7. FIX — Address the root cause, not the symptom
8. VERIFY — Confirm the fix and ensure no regressions
```

## Integration with Other Skills

- Use **Context Management** skill for systematic codebase exploration
- Use **Autonomous Task Execution** skill for research-driven implementation
- Use available **MCP tools** and **web search** for external research
- Use **language/framework skills** for technology-specific patterns

## Additional Resources

- Anthropic Documentation: https://docs.anthropic.com/
- GitHub Explore: https://github.com/explore
- NPM Trends: https://npmtrends.com/
- Bundlephobia: https://bundlephobia.com/
