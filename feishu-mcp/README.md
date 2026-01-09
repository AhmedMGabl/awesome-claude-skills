# Feishu MCP Plugin

Integrate Feishu (Lark) messaging and collaboration into Claude Code. Send messages, manage chats, and automate workflows directly from your development environment.

## Features

- 🚀 **Send messages** to Feishu chats and users
- 📋 **List and search** your Feishu chats
- 👥 **Create group chats** with team members
- 🤖 **Dual-bot support** for flexibility
- 🔐 **OAuth user authentication** for full access
- ⚡ **MCP-powered** for seamless integration

## Prerequisites

- Python 3.8+ installed
- Feishu bot application (see Setup section)
- FastMCP installed: `pip install fastmcp`

## Installation

1. **Clone or copy** this plugin to your Claude Code plugins directory:
   ```bash
   cp -r feishu-mcp ~/.claude/plugins/
   ```

2. **Set up credentials**:
   ```bash
   cp .claude/feishu.local.md.example .claude/feishu.local.md
   ```
   Edit `.claude/feishu.local.md` with your bot credentials.

3. **Enable the plugin** in Claude Code settings

## Configuration

### Required Environment Variables

Set these in `.claude/feishu.local.md`:

```yaml
---
# Bot 1 Credentials (Primary)
FEISHU_BOT1_APP_ID: "cli_xxxxxxxxx"
FEISHU_BOT1_APP_SECRET: "xxxxxxxxxxxxx"

# Bot 2 Credentials (Optional)
FEISHU_BOT2_APP_ID: "cli_xxxxxxxxx"
FEISHU_BOT2_APP_SECRET: "xxxxxxxxxxxxx"

# Default Bot
FEISHU_DEFAULT_BOT: "bot1"

# User Email
FEISHU_USER_EMAIL: "your.email@company.com"
---
```

### Getting Bot Credentials

1. Go to [Feishu Open Platform](https://open.feishu.cn/)
2. Create a new app or select existing one
3. Navigate to **Credentials** section
4. Copy **App ID** and **App Secret**
5. Add required permissions (see Permissions section)

### Required Permissions

Your Feishu bot needs these permissions:

**Tenant Token (Bot-level)**:
- `im:message` - Send and receive messages
- `im:chat` - Create and manage chats
- `im:chat:readonly` - Read chat information

**User Access Token (OAuth - Optional)**:
- `im:message` - Send messages as user
- `im:chat` - Access all user chats
- `im:message.p2p_msg` - Private messages
- `im:message.group_msg` - Group messages
- `contact:user.base:readonly` - User information

## Usage

### Commands

#### Send Message
```bash
/feishu:send-message
```
Interactively send a message to a Feishu chat.

#### List Chats
```bash
/feishu:list-chats
```
List all your accessible Feishu chats.

#### Create Chat
```bash
/feishu:create-chat
```
Create a new group chat with team members.

### Skills

The plugin includes the **feishu-setup** skill which automatically activates when discussing:
- Bot setup and configuration
- OAuth authentication troubleshooting
- Permission management
- API integration guidance

### MCP Server

The plugin automatically starts a FastMCP server that provides these tools:
- `send_message` - Send messages to chats
- `list_chats` - List available chats
- `create_chat` - Create group chats
- `get_chat_info` - Get chat details
- `add_reaction` - React to messages

## Architecture

```
feishu-mcp/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── .mcp.json                # MCP server configuration
├── commands/                # Slash commands
│   ├── send-message.md
│   ├── list-chats.md
│   └── create-chat.md
├── skills/
│   └── feishu-setup/        # Setup and troubleshooting guide
│       ├── SKILL.md
│       └── references/
└── .claude/
    └── feishu.local.md      # User credentials (gitignored)
```

## Troubleshooting

### MCP Server Not Starting

**Error**: "Failed to start Feishu MCP server"

**Solutions**:
1. Verify Python is installed: `python --version`
2. Install FastMCP: `pip install fastmcp`
3. Check server path in `.mcp.json` is correct
4. Verify credentials in `.claude/feishu.local.md`

### Permission Denied Errors

**Error**: "Code 99991672" or "Code 20027"

**Solutions**:
1. Check bot has required permissions in Feishu console
2. Create new app version after adding permissions
3. For OAuth: Enable user-level scopes, not just tenant
4. Wait 5-10 minutes for permissions to propagate

### OAuth Not Working

**Error**: "This app didn't apply for [scope] related permissions"

**Solutions**:
1. In Feishu console, add scopes for **User Access Token** (not just Tenant Token)
2. Create and publish new app version
3. Re-authorize: Run `/feishu:setup` and follow OAuth flow
4. Check redirect URL is configured: `http://localhost:8888/callback`

## Advanced Usage

### Dual Bot Setup

Use two bots for different purposes:
- **Bot 1**: Production messaging (tenant token)
- **Bot 2**: User-level access (OAuth token)

Configure in `.claude/feishu.local.md`:
```yaml
FEISHU_DEFAULT_BOT: "bot1"  # or "bot2"
```

### Direct API Integration

The MCP server at `C:\Users\eng20\feishu-ultimate-mcp\` can also be used standalone:
```python
from server import FeishuMCP

mcp = FeishuMCP()
await mcp.send_message(chat_id="...", message="Hello!")
```

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Feishu Docs**: [Feishu Open Platform](https://open.feishu.cn/document)
- **MCP Docs**: [Model Context Protocol](https://modelcontextprotocol.io/)

## Credits

Built with:
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [Feishu Open API](https://open.feishu.cn/) - Feishu/Lark API
- [Claude Code](https://claude.com/code) - AI-powered IDE

---

**Version**: 0.1.0
**Author**: Ahmed Gabl
**Email**: ahmedmoah@51talk.com
