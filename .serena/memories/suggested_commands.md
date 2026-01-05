# Suggested Commands

## Development Commands

### Create Skill Zips
```bash
python create_skill_zips.py
```
Creates zip files for all skills in the `skill-zips/` directory. Used for distribution and uploading to Claude marketplace.

### Verify Skills
```bash
python verify_skills.py
```
Validates all skill zip files for:
- Zip integrity (not corrupted)
- Presence of SKILL.md at root
- YAML frontmatter with name and description fields
- Proper structure

## Git Commands (Windows)

### Standard Git Operations
```bash
git status                    # Check repository status
git add .                     # Stage all changes
git commit -m "message"       # Commit changes
git push                      # Push to remote
git pull                      # Pull from remote
```

### Branch Operations
```bash
git checkout -b add-skill-name     # Create feature branch
git branch                         # List branches
git checkout main                  # Switch to main
```

## File Operations (Windows PowerShell/CMD)

### Navigation
```powershell
cd path\to\directory          # Change directory
dir                           # List directory contents (cmd)
ls                            # List directory contents (PowerShell)
```

### File Management
```powershell
mkdir skill-name              # Create directory
copy source dest              # Copy file
move source dest              # Move file
del filename                  # Delete file
```

### Search
```powershell
findstr /s "pattern" *.md     # Search in files (cmd)
Select-String "pattern" -Path *.md -Recurse  # Search (PowerShell)
```

## Testing New Skills

### Local Testing in Claude Code
```bash
# Copy skill to Claude Code skills directory
mkdir -p ~/.config/claude-code/skills/
cp -r skill-name ~/.config/claude-code/skills/

# Verify skill metadata
head ~/.config/claude-code/skills/skill-name/SKILL.md

# Start Claude Code
claude
```

## Marketplace Update
After adding a new skill, update `.claude-plugin/marketplace.json` with the skill entry following the required format.