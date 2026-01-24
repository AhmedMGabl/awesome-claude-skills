# MCP Server Setup Guide

This guide explains how to set up and configure MCP (Model Context Protocol) servers for use with Claude Code and the awesome-claude-skills repository.

## Table of Contents

- [What are MCP Servers?](#what-are-mcp-servers)
- [Available MCP Servers](#available-mcp-servers)
- [Setup Instructions](#setup-instructions)
  - [GitHub MCP](#github-mcp)
  - [Serena MCP](#serena-mcp)
  - [Context7 MCP](#context7-mcp)
  - [Playwright MCP](#playwright-mcp)
  - [Greptile MCP](#greptile-mcp)
  - [Pinecone MCP](#pinecone-mcp)
  - [Other MCP Servers](#other-mcp-servers)
- [Configuration Files](#configuration-files)
- [Testing Your Setup](#testing-your-setup)
- [Troubleshooting](#troubleshooting)

## What are MCP Servers?

MCP (Model Context Protocol) servers extend Claude's capabilities by providing access to external services, tools, and data sources. They enable Claude to:

- Interact with APIs and services (GitHub, Notion, Supabase, etc.)
- Access documentation and knowledge bases (Context7)
- Analyze code semantically (Serena)
- Automate browser testing (Playwright)
- Deploy to cloud platforms (Render, Railway)

MCP servers run as separate processes and communicate with Claude using a standardized protocol.

## Available MCP Servers

| Server | Status | Purpose | Authentication Required |
|--------|--------|---------|------------------------|
| **GitHub** | ✅ Active | Repository management, PRs, issues | ✅ Yes (GitHub token) |
| **Serena** | ✅ Active | Semantic code intelligence | ❌ No |
| **Context7** | ✅ Active | Library documentation search | ❌ No |
| **Playwright** | ✅ Active | Browser automation and testing | ❌ No (browser install required) |
| **Greptile** | ⚠️ Available | Code search and PR reviews | ✅ Yes (API key) |
| **Pinecone** | ⚠️ Available | Vector database operations | ✅ Yes (API key) |
| **Supabase** | ⚠️ Available | Database management | ✅ Yes (project credentials) |
| **Notion** | ⚠️ Available | Workspace integration | ✅ Yes (integration token) |
| **Render** | ⚠️ Available | Cloud deployment | ✅ Yes (API key) |
| **Railway** | ⚠️ Available | Cloud deployment | ✅ Yes (API token) |

## Setup Instructions

### GitHub MCP

**Status:** ✅ Already configured and authenticated

The GitHub MCP server is pre-configured and working with this repository.

**Verify Authentication:**
```bash
# In Claude Code, you can verify by asking:
# "Check my GitHub username"
```

**Configuration Location:**
- Authentication is handled through Claude's built-in GitHub integration
- No manual configuration required for basic functionality

**Available Operations:**
- Create and manage repositories
- Handle pull requests and code reviews
- Manage issues and labels
- Search code and repositories
- View commit history and diffs

### Serena MCP

**Status:** ✅ Active with awesome-claude-skills project

Serena provides semantic code intelligence with progressive disclosure.

**Setup Steps:**

1. **Activate Serena for a Project:**
   ```bash
   # Serena activates automatically when you work with code in Claude Code
   # To manually activate for a specific project, use the MCP tool:
   # mcp__plugin_serena_serena__activate_project
   ```

2. **View Serena Dashboard:**
   - Dashboard URL: http://localhost:7777
   - Opens automatically when Claude CLI starts (configurable)
   - Shows active project and memory files

3. **Configuration:**
   - Global config: `~/.serena/serena_config.yml`
   - Project config: `.serena/project.yml`
   - Memories: `.serena/memories/` (created during onboarding)

**Memory Files Created:**
- `project_overview.md` - High-level repository description
- `tech_stack.md` - Technologies and languages used
- `code_style_and_conventions.md` - Coding standards
- `suggested_commands.md` - Common development commands
- `codebase_structure.md` - Directory layout
- `task_completion_workflow.md` - Development workflows
- `design_patterns_and_guidelines.md` - Architecture patterns

**Disabling Auto-Open Dashboard:**
Edit `~/.serena/serena_config.yml`:
```yaml
web_dashboard_open_on_launch: false
```

### Context7 MCP

**Status:** ✅ Active - ready to use

Context7 provides up-to-date documentation for programming libraries and frameworks.

**No Setup Required** - works out of the box!

**Usage Examples:**
```
"Search Context7 for React hooks documentation"
"Find Pinecone vector database examples"
"Get the latest FastAPI documentation"
```

**How It Works:**
1. Resolves library names to Context7 IDs
2. Queries documentation with semantic search
3. Returns relevant docs and code examples

**Best Practices:**
- Be specific with library names
- Include version numbers if needed
- Ask for specific concepts or APIs

### Playwright MCP

**Status:** ✅ Active - browser testing available

Playwright enables browser automation and web application testing.

**Setup Steps:**

1. **Install Browser (if not already installed):**
   ```bash
   # Playwright will prompt if browser installation is needed
   # Installation happens automatically via MCP tool
   ```

2. **Usage:**
   - Available through webapp-testing skill
   - Supports Chrome, Firefox, Safari, Edge
   - Can navigate, click, fill forms, take screenshots

**Common Operations:**
- `browser_navigate` - Navigate to URLs
- `browser_snapshot` - Capture accessibility snapshot
- `browser_take_screenshot` - Save screenshot
- `browser_click` - Click elements
- `browser_type` - Type text into inputs
- `browser_evaluate` - Run JavaScript

**Configuration:**
- Browser type: Configurable in skill
- Viewport size: Adjustable via `browser_resize`
- Default: Headless mode

### Greptile MCP

**Status:** ⚠️ Available (authentication required)

Greptile provides code search, custom context, and PR review analysis.

**Setup Steps:**

1. **Get API Key:**
   - Sign up at https://app.greptile.com
   - Generate API key from dashboard

2. **Configure:**
   - API key is configured through Claude's MCP settings
   - Contact Greptile for enterprise setup

**Features:**
- Search custom context across codebase
- List and analyze pull requests
- Get PR comments and review status
- Trigger automated code reviews

### Pinecone MCP

**Status:** ⚠️ Available (API key required)

Pinecone provides vector database operations for AI applications.

**Setup Steps:**

1. **Get API Key:**
   - Sign up at https://www.pinecone.io
   - Create project and get API key

2. **Configure:**
   ```bash
   # Set environment variable:
   export PINECONE_API_KEY="your-api-key"
   ```

**Features:**
- Create indexes with integrated inference
- Upsert and search records
- Rerank documents
- Cascading search across indexes

**Usage with Skills:**
- The pinecone plugin provides quickstart and query skills
- Run `/pinecone:quickstart` for setup wizard

### Other MCP Servers

#### Supabase MCP
- **Purpose:** Database management for Supabase projects
- **Authentication:** Project URL + service role key
- **Setup:** Configure through Claude settings

#### Notion MCP
- **Purpose:** Create and manage Notion pages/databases
- **Authentication:** Integration token from Notion workspace
- **Setup:** Create integration at https://notion.so/my-integrations

#### Render MCP
- **Purpose:** Deploy web services, databases, cron jobs
- **Authentication:** API key from Render dashboard
- **Setup:** Get key from https://dashboard.render.com/account/api-keys

#### Railway MCP
- **Purpose:** Deploy applications to Railway cloud
- **Authentication:** Railway API token
- **Setup:** Generate token at https://railway.app/account/tokens

## Configuration Files

### Claude Desktop Config

Location: `$APPDATA/Claude/claude_desktop_config.json` (Windows) or `~/.config/Claude/claude_desktop_config.json` (Linux/Mac)

Example structure:
```json
{
  "mcpServers": {
    "server-name": {
      "command": "python",
      "args": ["path/to/server.py"],
      "env": {
        "API_KEY": "your-key-here"
      }
    }
  }
}
```

### Serena Config

Global: `~/.serena/serena_config.yml`
```yaml
web_dashboard: true
web_dashboard_open_on_launch: true
registered_projects:
  - /path/to/project
```

Project: `.serena/project.yml`
```yaml
languages:
  - python
  - markdown
encoding: "utf-8"
project_name: "your-project"
```

## Testing Your Setup

### Test GitHub MCP
```bash
# In Claude Code:
"What's my GitHub username?"
"List my recent repositories"
```

### Test Serena MCP
```bash
# In Claude Code:
"Show me the symbols overview for this file"
"Find references to the main function"
```

### Test Context7 MCP
```bash
# In Claude Code:
"Search React documentation for useEffect hook"
```

### Test Playwright MCP
```bash
# In Claude Code:
"Navigate to localhost:3000 and take a screenshot"
```

## Troubleshooting

### Server Not Loading

**Symptom:** MCP server appears in config but isn't accessible

**Solutions:**
1. Check Claude CLI vs Claude Desktop config locations
2. Restart Claude application completely
3. Verify server executable exists at specified path
4. Check environment variables are set correctly

### Serena Dashboard Shows "None"

**Symptom:** Dashboard doesn't show active project

**Solutions:**
1. Check for multiple Serena processes:
   ```bash
   tasklist | findstr serena  # Windows
   ps aux | grep serena       # Linux/Mac
   ```
2. Kill all Serena processes and restart Claude CLI
3. Verify project is registered in `~/.serena/serena_config.yml`

### Authentication Errors

**Symptom:** "Authentication required" or 401 errors

**Solutions:**
1. Verify API keys are correct and not expired
2. Check environment variables are exported
3. Restart Claude to reload environment
4. Regenerate API keys if needed

### Browser Not Found (Playwright)

**Symptom:** "Browser not installed" error

**Solution:**
- Playwright will automatically install browsers when first used
- Or manually install: Use the MCP tool `browser_install`

### Common Issues

**Issue:** MCP server tools not appearing
- **Solution:** Restart Claude Code completely

**Issue:** "Server not responding" errors
- **Solution:** Check if server process is running and restart if needed

**Issue:** Slow MCP responses
- **Solution:** Check network connection, API rate limits, or server load

For more detailed troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Additional Resources

- [MCP Documentation](https://modelcontextprotocol.io)
- [Claude MCP Integration Guide](https://docs.claude.com/mcp)
- [MCP Builder Skill](./mcp-builder/) - Build your own MCP servers
- [Anthropic MCP Repository](https://github.com/anthropics/anthropic-quickstarts/tree/main/mcp-server)

---

**Note:** MCP servers are actively developed and configurations may change. Check individual server documentation for the latest setup instructions.
