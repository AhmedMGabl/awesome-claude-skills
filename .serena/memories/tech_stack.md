# Tech Stack

## Primary Languages
- **Python** - For utility scripts, skill automation, and document processing
- **Markdown** - For skill documentation and instructions
- **YAML** - For skill metadata (frontmatter in SKILL.md files)
- **JSON** - For marketplace configuration

## Key Technologies
- **Git** - Version control
- **GitHub** - Repository hosting and collaboration
- **YAML Frontmatter** - Skill metadata in SKILL.md files
- **Markdown (CommonMark)** - Documentation format

## Python Usage
- Script files: `create_skill_zips.py`, `verify_skills.py`
- Document processing skills use Python libraries for DOCX, PPTX, XLSX, PDF
- Some skills include Python scripts in `scripts/` directories
- No global `requirements.txt` - dependencies are per-skill when needed

## File Formats
- **SKILL.md** - Required skill definition file with YAML frontmatter + markdown body
- **marketplace.json** - Claude Code marketplace configuration
- **README.md** - Main repository documentation
- **CONTRIBUTING.md** - Contribution guidelines
- **CLAUDE.md** - Instructions for Claude Code