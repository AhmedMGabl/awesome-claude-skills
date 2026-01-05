# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the **Awesome Claude Skills** repository - a curated collection of practical Claude Skills for enhancing productivity across Claude.ai, Claude Code, and the Claude API. The repository serves as both a marketplace of skills and a resource for creating new skills.

## Skill Structure and Architecture

### Core Skill Anatomy

Every skill follows a consistent structure:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (name + description, required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation loaded into context as needed
    └── assets/           - Files used in output (templates, icons, fonts)
```

### Progressive Disclosure Pattern

Skills use a three-level loading system:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed by Claude (loaded on demand)

### SKILL.md Requirements

- **YAML frontmatter** is required with `name` and `description` fields
- `description` must specify what the skill does and when to use it (third-person form: "This skill should be used when..." not "Use this skill when...")
- **Writing style**: Use imperative/infinitive form (verb-first instructions), not second person
- Use objective, instructional language: "To accomplish X, do Y" rather than "You should do X"

## Skill Categories

Skills are organized into these categories in the marketplace:

- `business-marketing` - Lead generation, competitive research, branding
- `communication-writing` - Communication, content creation
- `creative-media` - Images, videos, design, themes
- `development` - Code tools, automation, testing
- `productivity-organization` - File management, document processing

## Contributing New Skills

### Skill Requirements

All skills must:

1. Solve a real problem (based on actual usage, not theoretical)
2. Be well-documented with clear instructions, examples, and use cases
3. Be accessible (written for non-technical users when possible)
4. Include examples showing practical, real-world usage
5. Be tested across Claude.ai, Claude Code, and/or API
6. Be safe (confirm before destructive operations)
7. Be portable across Claude platforms when applicable

### Adding Skills to README.md

When adding a skill to README.md:

1. Choose the appropriate category (listed above)
2. Add in alphabetical order within the category
3. Follow the format: `- [Skill Name](./skill-name/) - One-sentence description. *By [@author](https://github.com/author)*` (for external contributions)
4. For repository-hosted skills: `- [Skill Name](./skill-name/) - One-sentence description.`
5. No emojis, consistent punctuation

### Adding Skills to Marketplace

Update `.claude-plugin/marketplace.json` with:

```json
{
  "name": "skill-name",
  "description": "Description matching SKILL.md frontmatter",
  "source": "./skill-name",
  "category": "appropriate-category"
}
```

Categories must match: `business-marketing`, `communication-writing`, `creative-media`, `development`, or `productivity-organization`.

## Repository-Specific Conventions

### Skill Naming

- Use lowercase with hyphens: `skill-name`
- Folder name should match the `name` field in SKILL.md frontmatter
- Be descriptive but concise

### Documentation Standards

- Avoid duplicating information between SKILL.md and references files
- Keep SKILL.md lean - move detailed schemas, examples, and reference material to `references/` files
- For large reference files (>10k words), include grep search patterns in SKILL.md
- Scripts may be executed without loading into context, so they should be self-contained

### Attribution

When a skill is based on someone's workflow:

```markdown
**Inspired by:** [Person Name]'s workflow
```

or

```markdown
**Credit:** Based on [Company/Team]'s process
```

## Key Repository Files

- `README.md` - Main documentation with skill listings
- `CONTRIBUTING.md` - Detailed contribution guidelines and skill template
- `.claude-plugin/marketplace.json` - Marketplace configuration for Claude Code
- Individual skill folders - Each contains SKILL.md and optional resources

## Document Processing Skills

Several skills in this repository work with Office documents (DOCX, PPTX, XLSX, PDF). These skills contain Python scripts in `scripts/` directories and OOXML validation tools for working with document formats programmatically.

## External vs. Repository-Hosted Skills

- **Repository-hosted skills** are in folders at the root level
- **External skills** are linked from README.md with GitHub URLs and author attribution
- Both types follow the same SKILL.md structure and requirements
