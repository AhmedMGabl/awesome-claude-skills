# Hey Hany! 👋

Ahmed wants to help you set up **Render MCP** for Claude Code. Here's everything you need:

## What is Render MCP?

Render MCP connects Claude Code with Render's cloud platform. You can:
- 🚀 Create and deploy web services
- 🗄️ Create databases (PostgreSQL, Redis)
- 📊 Monitor logs and metrics
- ⚙️ Manage environment variables
- 📦 Deploy static sites

All directly from Claude Code!

## Quick Setup (5 minutes)

### 1. Get Render API Key
1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Profile → Account Settings → API Keys
3. Create new key and copy it

### 2. Install MCP Server
```bash
npx @render/mcp
```

### 3. Configure Claude Code

Edit config file:
- **Windows**: `%APPDATA%\claude-code\claude_desktop_config.json`
- **Mac/Linux**: `~/.config/claude-code/claude_desktop_config.json`

Add this:
```json
{
  "mcpServers": {
    "render": {
      "command": "npx",
      "args": ["@render/mcp"],
      "env": {
        "RENDER_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

### 4. Restart Claude Code

That's it! Now you can ask Claude things like:
- "List my Render services"
- "Create a Node.js web service on Render"
- "Show logs from my service"

## Full Guide Available

I've attached a complete guide with:
- ✅ All available tools and commands
- ✅ Step-by-step examples
- ✅ Troubleshooting tips
- ✅ Best practices
- ✅ Common use cases

File: `render-mcp-guide.md` (in this folder)

## Need Help?

Reach out if you have questions! The guide has everything, but happy to help troubleshoot.

Good luck! 🎉
