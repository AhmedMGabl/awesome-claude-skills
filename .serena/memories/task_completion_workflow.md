# Task Completion Workflow

## When Adding a New Skill

### 1. Create Skill Structure
```bash
mkdir skill-name
cd skill-name
# Create SKILL.md with proper YAML frontmatter
```

### 2. Write SKILL.md
Required frontmatter:
```yaml
---
name: skill-name
description: Description in third-person form, stating what it does and when to use it.
---
```

Body should include:
- When to Use This Skill
- What This Skill Does
- How to Use
- Examples
- Tips (optional)
- Attribution (if based on someone's workflow)

### 3. Add to README.md
- Choose correct category
- Add in alphabetical order
- Follow format: `- [Skill Name](./skill-name/) - One-sentence description.`
- Include attribution if external contribution

### 4. Update Marketplace
Add entry to `.claude-plugin/marketplace.json`:
```json
{
  "name": "skill-name",
  "description": "Description matching SKILL.md frontmatter",
  "source": "./skill-name",
  "category": "appropriate-category"
}
```

### 5. Create and Verify Zip
```bash
python create_skill_zips.py
python verify_skills.py
```

### 6. Test the Skill
Test across platforms:
- Claude.ai (if applicable)
- Claude Code
- Claude API (if applicable)

### 7. Commit and Push
```bash
git add .
git commit -m "Add [Skill Name] skill"
git push origin add-skill-name
```

### 8. Create Pull Request
Include in PR description:
- What problem it solves
- Who uses this workflow
- Attribution/inspiration source
- Example usage

## When Modifying Existing Skills

### 1. Make Changes
Edit SKILL.md and/or bundled resources

### 2. Update Zip if Needed
```bash
python create_skill_zips.py
python verify_skills.py
```

### 3. Test Changes
Verify skill still works as expected

### 4. Update Documentation
Update README.md if description changed

### 5. Commit Changes
```bash
git add .
git commit -m "Update [Skill Name]: [description of changes]"
git push
```

## Quality Checks Before Completion

- [ ] SKILL.md has proper YAML frontmatter (name + description)
- [ ] Description uses third-person form
- [ ] Instructions use imperative/infinitive form, not second person
- [ ] Skill added to README.md in correct category, alphabetically
- [ ] Skill added to marketplace.json with correct category
- [ ] `verify_skills.py` passes
- [ ] Skill tested on at least one platform
- [ ] Attribution included if based on someone's workflow
- [ ] No emojis in documentation (unless explicitly requested)
- [ ] Consistent punctuation