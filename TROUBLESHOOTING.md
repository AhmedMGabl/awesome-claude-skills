# Troubleshooting Guide

This guide provides solutions to common issues when working with Claude Skills and MCP servers in the awesome-claude-skills repository.

## Table of Contents

- [Skills Issues](#skills-issues)
- [MCP Server Issues](#mcp-server-issues)
- [Serena Issues](#serena-issues)
- [GitHub Integration Issues](#github-integration-issues)
- [Playwright Issues](#playwright-issues)
- [General Claude Code Issues](#general-claude-code-issues)
- [Getting Help](#getting-help)

## Skills Issues

### Skill Not Loading

**Symptom:** Skill doesn't activate when expected or appears missing from marketplace

**Possible Causes & Solutions:**

1. **Invalid YAML Frontmatter**
   - Check `SKILL.md` has proper YAML structure:
   ```yaml
   ---
   name: skill-name
   description: Description here
   ---
   ```
   - Ensure no extra spaces or tabs
   - Verify the closing `---` delimiter

2. **Name Mismatch**
   - Skill folder name must match `name` field in YAML
   - Example: folder `video-downloader` → name: `video-downloader`
   - Not: folder `video-downloader` → name: `youtube-downloader`

3. **Not in marketplace.json**
   - Check `.claude-plugin/marketplace.json` includes your skill:
   ```json
   {
     "name": "skill-name",
     "description": "...",
     "source": "./skill-name",
     "category": "development"
   }
   ```

4. **Skill Not in Repository**
   - Verify skill folder exists: `ls -d skill-name/`
   - Check `SKILL.md` file exists in folder

**Fix Steps:**
```bash
# 1. Validate YAML frontmatter
head -10 skill-name/SKILL.md

# 2. Check folder name matches YAML name
grep "^name:" skill-name/SKILL.md

# 3. Verify marketplace.json entry
cat .claude-plugin/marketplace.json | grep "skill-name"

# 4. Restart Claude Code
```

### Skill Executes Incorrectly

**Symptom:** Skill activates but doesn't work as expected

**Debugging Steps:**

1. **Check Skill Instructions**
   - Read `SKILL.md` carefully for requirements
   - Verify all prerequisites are met
   - Check for required environment variables

2. **Script Permissions**
   - If skill has `scripts/` directory, check permissions:
   ```bash
   chmod +x skill-name/scripts/*.py
   chmod +x skill-name/scripts/*.sh
   ```

3. **Dependencies Missing**
   - Check if skill requires Python packages:
   ```bash
   pip install -r skill-name/requirements.txt
   ```
   - Verify Node.js dependencies if needed:
   ```bash
   cd skill-name && npm install
   ```

4. **Path Issues**
   - Ensure scripts reference correct paths
   - Use absolute paths or verify working directory

### Skill ZIP Files Invalid

**Symptom:** `verify_skills.py` reports errors

**Common Issues:**

1. **Missing from create_skill_zips.py**
   - Check skills list includes your skill:
   ```python
   skills = [
       'your-skill-name',  # Add here
       'other-skill',
       # ...
   ]
   ```

2. **Regenerate Zips**
   ```bash
   python create_skill_zips.py
   python verify_skills.py
   ```

3. **Invalid Structure**
   - Ensure SKILL.md is at root of skill folder
   - Check for hidden files causing issues
   - Remove temporary files before zipping

## MCP Server Issues

### MCP Server Not Available

**Symptom:** Server configured but tools not accessible

**Solutions:**

1. **Check Server Status**
   - Verify server name in error message
   - List available servers in Claude Code: "What MCP servers are available?"

2. **Restart Claude Code**
   - Complete restart (close all windows)
   - MCP servers load on startup

3. **Check Configuration**
   - Verify config file location:
     - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
     - Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
     - Linux: `~/.config/Claude/claude_desktop_config.json`

4. **Validate JSON**
   ```bash
   # Check for JSON syntax errors
   python -m json.tool claude_desktop_config.json
   ```

5. **Server Path Issues**
   - Verify server executable exists:
   ```bash
   # Windows
   dir "C:\path\to\server.py"

   # Linux/Mac
   ls -la /path/to/server.py
   ```

### MCP Authentication Errors

**Symptom:** "Authentication required" or 401/403 errors

**Solutions:**

1. **Verify API Keys**
   - Check environment variables are set:
   ```bash
   # Windows
   echo %VARIABLE_NAME%

   # Linux/Mac
   echo $VARIABLE_NAME
   ```

2. **Regenerate API Keys**
   - Go to service dashboard
   - Create new API key
   - Update configuration

3. **Check Key Permissions**
   - Ensure API key has required scopes
   - Verify key isn't expired
   - Check rate limits haven't been exceeded

4. **Environment Variables Not Loading**
   - Set in config file instead:
   ```json
   {
     "mcpServers": {
       "server-name": {
         "command": "python",
         "args": ["server.py"],
         "env": {
           "API_KEY": "your-key-here"
         }
       }
     }
   }
   ```

### MCP Server Slow or Timeout

**Symptom:** Long wait times or timeout errors

**Solutions:**

1. **Check Network**
   - Verify internet connection
   - Test API endpoint directly
   - Check for proxy issues

2. **API Rate Limits**
   - Wait and retry
   - Check service status page
   - Upgrade plan if needed

3. **Server Overload**
   - Reduce concurrent requests
   - Simplify queries
   - Contact service support

## Serena Issues

### Dashboard Shows "Active Project: None"

**Symptom:** Serena web dashboard doesn't display current project

**Root Cause:** Multiple Serena processes running or dashboard connected to wrong instance

**Solution:**

1. **Kill All Serena Processes**
   ```bash
   # Windows
   taskkill /F /IM serena.exe

   # Linux/Mac
   pkill -9 serena
   ```

2. **Restart Claude Code**
   ```bash
   claude
   ```

3. **Verify Dashboard**
   - Open http://localhost:7777
   - Should show current project

4. **Check for Multiple Instances**
   ```bash
   # Windows
   tasklist | findstr serena

   # Linux/Mac
   ps aux | grep serena
   ```
   - Should show only ONE process

### Serena Dashboard Opens Every Time

**Symptom:** Dashboard opens automatically on every Claude CLI start

**Solution:**

Edit `~/.serena/serena_config.yml`:
```yaml
web_dashboard: true
web_dashboard_open_on_launch: false  # Change to false
```

### Serena Memories Not Loading

**Symptom:** Serena doesn't seem to use project context

**Solutions:**

1. **Check Memory Files**
   ```bash
   ls -la .serena/memories/
   ```

2. **Recreate Memories**
   - Delete `.serena/memories/` directory
   - Let Serena recreate on next onboarding

3. **Verify Project Activation**
   - Check `~/.serena/serena_config.yml` lists project
   - Re-activate if needed

### Serena Can't Find Symbols

**Symptom:** Symbol search returns no results

**Solutions:**

1. **Check Language Support**
   - Verify `.serena/project.yml` has correct languages:
   ```yaml
   languages:
     - python
     - javascript
     # etc.
   ```

2. **Rebuild Index**
   - Project re-indexing happens automatically
   - May take time for large codebases

3. **Check File Encoding**
   - Ensure files are UTF-8 encoded
   - Check `.serena/project.yml` encoding setting

## GitHub Integration Issues

### GitHub Authentication Failed

**Symptom:** "Not authenticated" or can't access repositories

**Solutions:**

1. **Re-authenticate**
   - Claude Code will prompt for GitHub authentication
   - Follow OAuth flow in browser

2. **Check Token Permissions**
   - Needs `repo`, `read:user` scopes
   - May need additional scopes for organizations

3. **Token Expired**
   - Re-authenticate to get new token
   - Check token in GitHub Settings > Developer Settings

### Can't Access Private Repositories

**Symptom:** Only public repos visible

**Solution:**
- Ensure authentication token has `repo` scope (not just `public_repo`)
- Re-authenticate with full permissions

### Rate Limit Errors

**Symptom:** "API rate limit exceeded" error

**Solutions:**

1. **Wait for Reset**
   - Rate limits reset hourly
   - Check headers for reset time

2. **Reduce Requests**
   - Batch operations when possible
   - Use pagination parameters

3. **Authenticate**
   - Authenticated requests have higher limits
   - Unauthenticated: 60/hour
   - Authenticated: 5000/hour

## Playwright Issues

### Browser Not Found

**Symptom:** "Browser executable not found" error

**Solution:**
```bash
# Let Playwright install browsers automatically
# Or use the MCP tool: browser_install
```

### Playwright Tests Fail

**Symptom:** Navigation or interaction errors

**Debugging Steps:**

1. **Check URL**
   - Verify target URL is accessible
   - Ensure web server is running for local apps

2. **Increase Timeouts**
   - Default timeout may be too short
   - Use `browser_wait_for` tool

3. **Take Screenshots**
   - Use `browser_take_screenshot` to see current state
   - Check for unexpected UI changes

4. **Check Logs**
   - Use `browser_console_messages` to see browser console
   - Review for JavaScript errors

### Element Not Found

**Symptom:** Click or type operations fail

**Solutions:**

1. **Take Snapshot First**
   - Use `browser_snapshot` to see available elements
   - Get correct element references

2. **Wait for Element**
   - Use `browser_wait_for` with text or element
   - Page may still be loading

3. **Check Element Visibility**
   - Element may be hidden or offscreen
   - Scroll into view if needed

## General Claude Code Issues

### Claude Code Won't Start

**Symptom:** CLI crashes or won't launch

**Solutions:**

1. **Check Installation**
   ```bash
   claude --version
   ```

2. **Clear Cache**
   ```bash
   # Windows
   rmdir /s /q "%APPDATA%\Claude\cache"

   # Linux/Mac
   rm -rf ~/.cache/claude
   ```

3. **Reinstall**
   ```bash
   npm uninstall -g @anthropic-ai/claude-code
   npm install -g @anthropic-ai/claude-code
   ```

### Commands Not Working

**Symptom:** Slash commands don't execute

**Solutions:**

1. **Check Spelling**
   - Ensure correct command name
   - Use `/help` to list available commands

2. **Plugin Not Loaded**
   - Restart Claude Code
   - Verify plugin installation

3. **Permissions Issue**
   - Check if command requires authentication
   - Verify required environment variables

### Memory/Performance Issues

**Symptom:** Claude Code slow or crashes

**Solutions:**

1. **Close Unused Sessions**
   - Each session uses memory
   - Exit inactive Claude Code windows

2. **Clear Old Conversations**
   ```bash
   # Conversations are saved in:
   # ~/.claude/projects/
   ```

3. **Reduce Context Size**
   - Avoid reading very large files
   - Use pagination for large results
   - Clear conversation history if needed

### File Modification Conflicts

**Symptom:** "File has been modified since read" errors

**Solutions:**

1. **Re-read File**
   - File was changed externally
   - Read again before editing

2. **Disable Auto-Format**
   - Some editors auto-format on save
   - Disable linters temporarily

3. **Use Git**
   - Commit changes before asking Claude to edit
   - Easier to review and rollback

## Getting Help

### Check Existing Issues

1. **Repository Issues**
   - https://github.com/anthropics/claude-code/issues
   - Search for similar problems

2. **MCP Server Issues**
   - Check individual MCP server repositories
   - Review server-specific documentation

### Report New Issues

When reporting issues, include:

1. **Environment Info**
   - OS and version
   - Claude Code version
   - Node.js/Python version

2. **Steps to Reproduce**
   - Exact command or action
   - Expected vs actual behavior
   - Error messages (full text)

3. **Configuration**
   - Relevant config files (remove sensitive data)
   - Skill YAML frontmatter
   - MCP server setup

4. **Logs**
   - Claude Code logs
   - Server logs if applicable

### Community Resources

- **Claude Community**: https://community.anthropic.com
- **Discord**: Join server for real-time help
- **Documentation**: https://docs.claude.com
- **GitHub Issues**: https://github.com/anthropics/claude-code/issues

### Emergency Fixes

**Nuclear Option** (when nothing else works):

1. **Backup Important Files**
   ```bash
   # Backup config
   cp -r ~/.claude ~/claude-backup
   ```

2. **Complete Reset**
   ```bash
   # Remove all Claude data
   rm -rf ~/.claude
   rm -rf ~/.serena
   rm -rf ~/.config/Claude
   ```

3. **Reinstall Claude Code**
   ```bash
   npm uninstall -g @anthropic-ai/claude-code
   npm install -g @anthropic-ai/claude-code
   ```

4. **Reconfigure**
   - Re-authenticate services
   - Reload skills
   - Reconfigure MCP servers

---

## Quick Reference

### Common Commands

```bash
# Check Claude version
claude --version

# List available skills
claude skills list

# Check MCP server status
# (Ask Claude: "What MCP servers are available?")

# Kill stuck Serena processes
taskkill /F /IM serena.exe  # Windows
pkill -9 serena              # Linux/Mac

# Validate JSON config
python -m json.tool config.json

# Check running processes
tasklist | findstr claude   # Windows
ps aux | grep claude        # Linux/Mac
```

### Log Locations

- **Claude Code**: `~/.claude/logs/`
- **Serena**: `~/.serena/logs/`
- **MCP Servers**: Check individual server documentation

### Config Locations

- **Claude Desktop**: `$APPDATA/Claude/claude_desktop_config.json` (Windows)
- **Serena Global**: `~/.serena/serena_config.yml`
- **Serena Project**: `.serena/project.yml`
- **Skills Marketplace**: `.claude-plugin/marketplace.json`

---

**Note:** This guide is continuously updated. If you encounter an issue not covered here, please open an issue or submit a PR with the solution.
