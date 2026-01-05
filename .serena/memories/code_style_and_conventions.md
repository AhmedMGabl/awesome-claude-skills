# Code Style and Conventions

## Skill Naming
- **Format**: lowercase-with-hyphens (e.g., `skill-creator`, `mcp-builder`)
- Folder name must match the `name` field in SKILL.md frontmatter
- Be descriptive but concise

## SKILL.md Structure
Required YAML frontmatter:
```yaml
---
name: skill-name
description: What this skill does and when to use it.
---
```

### Frontmatter Requirements
- **name**: Lowercase with hyphens, matches folder name
- **description**: Third-person form ("This skill should be used when..." not "Use this skill when...")
- Must specify what the skill does AND when to use it

### Markdown Body
- **Writing style**: Use imperative/infinitive form (verb-first instructions), NOT second person
- **Language**: Objective, instructional ("To accomplish X, do Y" rather than "You should do X")
- **Structure**: Include "When to Use", "What This Skill Does", "How to Use", "Examples"

## Progressive Disclosure Pattern
Skills use three-level loading:
1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed (loaded on demand)

## Documentation Standards
- Avoid duplicating information between SKILL.md and references files
- Keep SKILL.md lean - move detailed schemas/examples to `references/` files
- For large reference files (>10k words), include grep search patterns in SKILL.md
- Scripts should be self-contained (may execute without loading into context)

## Skill Categories
Must use one of these official categories:
- `business-marketing`
- `communication-writing`
- `creative-media`
- `development`
- `productivity-organization`

## README.md Format
When adding skills to README.md:
- Add in alphabetical order within category
- Repository-hosted: `- [Skill Name](./skill-name/) - One-sentence description.`
- External: `- [Skill Name](./skill-name/) - One-sentence description. *By [@author](https://github.com/author)*`
- No emojis, consistent punctuation

## Attribution Format
When based on someone's workflow:
```markdown
**Inspired by:** [Person Name]'s workflow
```
or
```markdown
**Credit:** Based on [Company/Team]'s process
```