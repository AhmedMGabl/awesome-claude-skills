# Feishu MCP Plugin

Integrate Feishu (Lark) messaging and collaboration into Claude Code. Send messages, manage chats, and automate workflows directly from your development environment.

## 🚀 Quick Start

**New to Feishu Enhanced?** Start here:
- **Simple guide**: Read [HOW_TO_USE.md](./HOW_TO_USE.md) (5 min)
- **Visual examples**: Read [FEISHU_ENHANCED_GUIDE.md](./FEISHU_ENHANCED_GUIDE.md) (15 min)
- **Test server**: Run `python scripts/test_feishu_enhanced.py` for standalone testing
- **Latest updates**: See [WHATS_NEW.md](./WHATS_NEW.md)

**Just want to try it?**
1. Restart Claude CLI
2. Ask: `"Search for documents in Feishu"`
3. Done!

## Features

### Document Management (NEW in v1.0.0!)
- 🔍 **Find documents** - Search across all Feishu content (Docs, Bases, Wikis, Chats)
- 📄 **Read Feishu Docs** - Access rich document content
- 📝 **Modify documents** - Update specific blocks in Feishu Docs
- 📊 **Manage Feishu Bases** - Query, update, and create spreadsheet records
- 📖 **Search Wikis** - Find and read knowledge base pages
- 📌 **Track documents** - Keep organized list of important files
- 🔧 **Fix data** - Correct errors anywhere in Feishu content

### Messaging Features
- 🚀 **Send messages** to Feishu chats and users
- 📋 **List and search** your Feishu chats
- 👥 **Create group chats** with team members
- 🤖 **Dual-bot support** for flexibility
- 🔐 **OAuth user authentication** for full access
- ⚡ **MCP-powered** for seamless integration

### Browser Automation Features
- 🌐 **Full web access** via Playwright integration
- 💬 **Send messages as yourself** (no bot required)
- 📖 **Read message history** from any chat
- 🔍 **Scrape and analyze** conversations
- ✅ **Bypass API limitations** completely
- 🎯 **Access ANY chat** you can see in web app

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

**Messaging Permissions (Basic)**:
- `im:message` - Send and receive messages
- `im:chat` - Create and manage chats
- `im:chat:readonly` - Read chat information

**Document Management Permissions (For v1.0.0 features)**:
- `drive:drive` - Full drive access (required for search)
- `drive:drive:readonly` - Read-only drive access
- `docx:document` - Modify Feishu Docs
- `docx:document:readonly` - Read Feishu Docs
- `bitable:app` - Modify Feishu Bases (spreadsheets)
- `bitable:app:readonly` - Read Feishu Bases
- `wiki:wiki` - Modify wiki pages
- `wiki:wiki:readonly` - Read wiki pages

**User Access Token (OAuth - Optional)**:
- `im:message` - Send messages as user
- `im:chat` - Access all user chats
- `im:message.p2p_msg` - Private messages
- `im:message.group_msg` - Group messages
- `contact:user.base:readonly` - User information

## Usage

### Commands

#### API-Based Commands

##### Send Message
```bash
/feishu:send-message
```
Interactively send a message to a Feishu chat using bot API.

##### List Chats
```bash
/feishu:list-chats
```
List all your accessible Feishu chats via API.

##### Create Chat
```bash
/feishu:create-chat
```
Create a new group chat with team members.

#### Browser Automation Commands (NEW!)

##### Send Message via Browser
```bash
/feishu:send-message-browser
```
Send messages through Feishu web interface using Playwright. **Benefits**:
- No API scope issues
- Send as yourself (not as bot)
- Access ANY chat you can see
- Works immediately without bot setup

##### Read Messages via Browser
```bash
/feishu:read-messages-browser
```
Read and scrape messages from any chat. **Use cases**:
- Get conversation context
- Archive message history
- Search for specific content
- Monitor important chats

##### List Chats via Browser
```bash
/feishu:list-chats-browser
```
View all your chats exactly as they appear in Feishu web app. Shows:
- Unread message counts
- Last message previews
- Pinned chats
- All accessible conversations

### Skills

The plugin includes two skills:

**feishu-setup** - Automatically activates when discussing:
- Bot setup and configuration
- OAuth authentication troubleshooting
- Permission management
- API integration guidance

**feishu-document-manager** (NEW!) - Automatically activates when you need to:
- Find documents across Feishu
- Read or modify Feishu Docs
- Query or update Feishu Bases (spreadsheets)
- Search or access wiki pages
- Track important documents
- Fix incorrect data in Feishu content

See [QUICK_START_DOCUMENT_MANAGEMENT.md](./QUICK_START_DOCUMENT_MANAGEMENT.md) for 15-minute setup guide.

### Testing & Debugging (NEW!)

**Interactive Test Server** - Test all features without Claude Code:
```bash
cd scripts
python test_feishu_enhanced.py
```

**Features:**
- 7-option interactive menu
- 5 comprehensive test suites
- Colored output (visual feedback)
- Permission verification
- Standalone operation

See [scripts/README_TEST_SERVER.md](./scripts/README_TEST_SERVER.md) for complete guide.

### MCP Server

The plugin automatically starts a FastMCP server that provides these tools:

**Messaging Tools**:
- `send_message` - Send messages to chats
- `list_chats` - List available chats
- `create_chat` - Create group chats
- `get_chat_info` - Get chat details
- `add_reaction` - React to messages

**Document Management Tools (NEW!)**:
- `search_all_content` - Search across all Feishu content types
- `list_bases` - List all accessible Feishu Bases (spreadsheets)
- `search_base_records` - Find records matching criteria
- `update_base_record` - Update existing spreadsheet records
- `create_base_record` - Create new spreadsheet records
- `read_document` - Read Feishu Doc content
- `update_document_block` - Modify specific blocks in documents
- `search_wiki` - Search wiki pages
- `read_wiki_page` - Read wiki page content
- `track_document` - Add documents to tracking system
- `test_enhanced_connection` - Verify permissions and connectivity

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

## What's New in v1.0.0

### Enhanced Document Management

The plugin now includes comprehensive document management capabilities:

- **Universal Search**: Find any document across Docs, Bases, Wikis, and Chats
- **Content Access**: Read Feishu Docs, spreadsheets, and wiki pages
- **Data Modification**: Update spreadsheet records and document content
- **Document Tracking**: Keep track of important documents
- **Data Correction**: Fix incorrect data anywhere in Feishu

### Interactive Test Server (NEW!)

Test all Feishu features independently:
```bash
cd scripts
python test_feishu_enhanced.py
```

**Menu options:**
- Search documents across all Feishu
- List all spreadsheets
- Read document content
- Verify permissions
- Run automated test suite

See [scripts/README_TEST_SERVER.md](./scripts/README_TEST_SERVER.md) for complete guide.

### Quick Start Guide

1. **Restart Claude** to load the enhanced server
2. **Test document search**: "Search for documents in Feishu"
3. **Add permissions** (optional, for full features): See [QUICK_START_DOCUMENT_MANAGEMENT.md](./QUICK_START_DOCUMENT_MANAGEMENT.md)

### Documentation

**Getting Started:**
- [How to Use](./HOW_TO_USE.md) - Simple 5-minute guide
- [What's New](./WHATS_NEW.md) - Latest features and updates
- [Visual Guide](./FEISHU_ENHANCED_GUIDE.md) - Examples and workflows

**Setup:**
- [Quick Start Guide](./QUICK_START_DOCUMENT_MANAGEMENT.md) - 15-minute setup
- [Complete Setup Guide](./DOCUMENT_MANAGEMENT_SETUP.md) - Comprehensive documentation
- [Deployment Status](../DEPLOYMENT_STATUS.md) - Current deployment info

**Testing:**
- [Test Server Guide](./scripts/README_TEST_SERVER.md) - Interactive testing
- [Test After Restart](./TEST_AFTER_RESTART.md) - Quick verification

---

**Version**: 1.0.0
**Author**: Ahmed Gabl
**Email**: ahmedmoah@51talk.com
