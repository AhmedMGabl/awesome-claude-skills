# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the **Awesome Claude Skills** repository - a curated collection of practical Claude Skills for enhancing productivity across Claude.ai, Claude Code, and the Claude API. The repository serves as both a marketplace of skills and a resource for creating new skills.

## Repository Commands

### Skill Management

Create zip files for all skills (for distribution):
```bash
python create_skill_zips.py
```

Verify all skill zip files have correct structure:
```bash
python verify_skills.py
```

### Git Operations

This is a standard git repository. Common operations:
```bash
git status                    # Check repository status
git add <skill-name>/         # Stage new skill
git commit -m "message"       # Commit changes
git push                      # Push to remote
```

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

**Important**: The `name` field must match the folder name exactly, and the `description` should match the description in the SKILL.md frontmatter. Categories must be one of: `business-marketing`, `communication-writing`, `creative-media`, `development`, or `productivity-organization`.

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
- `create_skill_zips.py` - Utility to create zip files for skill distribution
- `verify_skills.py` - Utility to verify skill zip file structure and integrity
- Individual skill folders - Each contains SKILL.md and optional resources

## Repository Architecture

### Skill Distribution

Skills are distributed in two ways:

1. **Repository-hosted skills** - Folders at root level, included in marketplace.json
2. **External skills** - Listed in README.md with GitHub URLs and author attribution

Both types follow the same SKILL.md structure and requirements.

### Marketplace Integration

The `.claude-plugin/marketplace.json` file defines which skills appear in Claude Code's marketplace. When adding a new skill:

1. Create the skill folder with SKILL.md
2. Add entry to marketplace.json with matching name and description
3. Update README.md in the appropriate category
4. Optionally run `create_skill_zips.py` to generate distributable zip files

### Document Processing Skills

Several skills in this repository work with Office documents (DOCX, PPTX, XLSX, PDF). These skills:

- Contain Python scripts in `scripts/` directories
- Use OOXML validation tools for working with document formats programmatically
- Are self-contained and can be executed without loading full scripts into context

## Working with Skills

### Reading Skills

When examining or modifying skills:

1. Always read the SKILL.md file first to understand the skill's purpose
2. Check the YAML frontmatter for name and description
3. Look for bundled resources in subdirectories (scripts/, references/, assets/)
4. Verify the skill is listed in marketplace.json

### Creating New Skills

1. Create a new folder with lowercase hyphenated name
2. Add SKILL.md with required YAML frontmatter (name, description)
3. Write clear instructions for Claude (not end users)
4. Add bundled resources as needed
5. Update marketplace.json
6. Update README.md in appropriate category
7. Test the skill across platforms

### Modifying Existing Skills

1. Read the entire SKILL.md file before making changes
2. Preserve the YAML frontmatter structure
3. If changing the skill name or description, update marketplace.json
4. If description changes, also update README.md
5. Maintain consistency with the repository's writing style
