# Codebase Structure

## Root Directory Layout
```
awesome-claude-skills/
├── .claude-plugin/           # Claude Code marketplace configuration
│   └── marketplace.json      # Skill listings for marketplace
├── .git/                     # Git repository data
├── .serena/                  # Serena MCP server data
├── skill-zips/               # Generated zip files (gitignored)
│
├── [Individual Skill Folders]
│   ├── artifacts-builder/
│   ├── brand-guidelines/
│   ├── canvas-design/
│   ├── changelog-generator/
│   ├── competitive-ads-extractor/
│   ├── content-research-writer/
│   ├── developer-growth-analysis/
│   ├── document-skills/      # Special: contains multiple sub-skills
│   ├── domain-name-brainstormer/
│   ├── file-organizer/
│   ├── image-enhancer/
│   ├── internal-comms/
│   ├── invoice-organizer/
│   ├── lead-research-assistant/
│   ├── mcp-builder/
│   ├── meeting-insights-analyzer/
│   ├── my-claude-tools/
│   ├── raffle-winner-picker/
│   ├── skill-creator/
│   ├── skill-share/
│   ├── slack-gif-creator/
│   ├── template-skill/        # Template for new skills
│   ├── theme-factory/
│   ├── video-downloader/
│   └── webapp-testing/
│
├── CLAUDE.md                 # Instructions for Claude Code
├── CONTRIBUTING.md           # Contribution guidelines
├── README.md                 # Main documentation
├── create_skill_zips.py      # Utility: Create skill zips
└── verify_skills.py          # Utility: Verify skill structure
```

## Standard Skill Structure
Each skill folder follows this pattern:
```
skill-name/
├── SKILL.md                  # Required: Skill definition
├── scripts/                  # Optional: Executable code
├── references/               # Optional: Documentation/context
├── assets/                   # Optional: Templates, images
└── requirements.txt          # Optional: Python dependencies (if needed)
```

## Special Directories

### document-skills/
Contains multiple document processing skills:
- `docx/` - Word document manipulation
- `pdf/` - PDF processing
- `pptx/` - PowerPoint manipulation
- `xlsx/` - Excel spreadsheet handling

Each has:
- SKILL.md for the skill
- `scripts/` with Python processing code
- `ooxml/` directory with OOXML validation tools (for docx/pptx)

### .claude-plugin/
Contains marketplace configuration:
- `marketplace.json` - Lists all skills with metadata for Claude Code marketplace

## Key Files

### CLAUDE.md
Instructions specifically for Claude Code, including:
- Repository overview
- Skill structure and architecture
- Contributing guidelines
- Naming conventions
- Marketplace integration details

### CONTRIBUTING.md
Guidelines for contributors:
- Skill requirements
- Pull request process
- SKILL.md template
- Attribution format
- Categories

### README.md
Main repository documentation:
- Skill listings by category
- Getting started guides
- Usage instructions for Claude.ai, Claude Code, and API
- Resources and community links