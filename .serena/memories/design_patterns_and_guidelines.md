# Design Patterns and Guidelines

## Progressive Disclosure Pattern

Skills use a three-tier loading strategy to optimize context usage:

### Tier 1: Metadata (Always Loaded)
- Name and description from YAML frontmatter
- ~100 words maximum
- Always present in Claude's context
- Helps Claude decide when to activate the skill

### Tier 2: SKILL.md Body (Loaded on Activation)
- Full skill instructions and examples
- <5k words recommended
- Loaded when skill is relevant to the task
- Contains "how-to" information for Claude

### Tier 3: Bundled Resources (Loaded on Demand)
- `scripts/` - Executable code
- `references/` - Detailed documentation
- `assets/` - Templates, images, etc.
- Loaded only when needed by Claude

## Skill Design Principles

### 1. Real-World Use Cases
Skills must be based on actual usage, not theoretical applications. Each skill should solve a real problem that users face.

### 2. Accessibility
Write for non-technical users when possible. Instructions should be clear and actionable without requiring deep technical knowledge.

### 3. Portability
Skills should work across Claude.ai, Claude Code, and the Claude API when applicable. Avoid platform-specific dependencies unless necessary.

### 4. Safety First
Skills that perform destructive operations (file deletion, data modification) must confirm before executing.

### 5. Clear Examples
Every skill should include practical, real-world examples showing:
- Typical user prompts
- Expected outputs
- Common use cases

## Documentation Patterns

### SKILL.md Structure
Standard sections:
1. **Header** - YAML frontmatter with name and description
2. **Overview** - What the skill does and its purpose
3. **When to Use** - Specific scenarios where this skill is valuable
4. **What This Skill Does** - Key capabilities (numbered list)
5. **How to Use** - Basic and advanced usage examples
6. **Examples** - Real-world usage demonstrations
7. **Tips** - Best practices and helpful hints (optional)
8. **Attribution** - Credit to original sources (when applicable)

### Writing Style
- **For frontmatter description**: Third-person ("This skill should be used when...")
- **For body instructions**: Imperative/infinitive form ("To accomplish X, do Y")
- **Avoid**: Second person ("You should...", "You can...")
- **Be**: Objective and instructional

## Resource Organization

### scripts/
- Self-contained executable code
- May be executed without loading into context
- Should include docstrings and comments
- Can have their own requirements.txt if needed

### references/
- Detailed documentation
- Schemas, specifications
- Extended examples
- Reference material too large for SKILL.md

### assets/
- Templates (document templates, HTML templates)
- Images (icons, diagrams)
- Fonts
- Any files used in output generation

## Marketplace Integration

### marketplace.json Entry Format
```json
{
  "name": "skill-name",
  "description": "Must match SKILL.md frontmatter exactly",
  "source": "./skill-name",
  "category": "one-of-five-categories"
}
```

### Categories (Strict List)
- `business-marketing` - Lead generation, competitive research, branding
- `communication-writing` - Communication, content creation
- `creative-media` - Images, videos, design, themes
- `development` - Code tools, automation, testing
- `productivity-organization` - File management, document processing

## Contribution Workflow

### Pull Request Pattern
1. Fork repository
2. Create feature branch: `git checkout -b add-skill-name`
3. Implement skill following all conventions
4. Test across applicable platforms
5. Update README.md and marketplace.json
6. Run verification: `python verify_skills.py`
7. Commit: `git commit -m "Add [Skill Name] skill"`
8. Push and create PR with detailed description

### PR Description Should Include
- Problem the skill solves
- Who uses this workflow
- Attribution/inspiration source
- Example usage
- Testing performed

## Anti-Patterns to Avoid

### ❌ Don't Do This
- Use emojis in documentation (unless explicitly requested)
- Write descriptions in second person
- Create skills for theoretical use cases
- Skip YAML frontmatter
- Forget to test on multiple platforms
- Add skills out of alphabetical order in README
- Use incorrect categories in marketplace.json
- Omit attribution when based on someone's work

### ✅ Do This Instead
- Keep documentation clean and professional
- Use third-person for descriptions, imperative for instructions
- Base skills on real-world usage
- Always include proper frontmatter
- Test thoroughly before submitting
- Maintain alphabetical order
- Use official category names
- Credit original sources properly