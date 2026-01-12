# Feishu Pro - Advanced Browser Automation

A comprehensive, feature-rich Feishu automation tool with AI-powered messaging, advanced operations, and multiple methods for every task.

## Features Overview

### 🚀 Core Capabilities
- **Persistent Browser Session** - Maintains login across uses
- **AI-Powered Messaging** - Enhance messages with different styles
- **Smart Replies** - Generate contextual responses automatically
- **Message Templates** - Save and reuse common messages
- **Batch Operations** - Send to multiple chats at once
- **Advanced Reading** - Parse, format, and export message history
- **File Management** - Upload files, take screenshots
- **Group Management** - Create groups, manage members
- **Search** - Find messages across all chats
- **Multiple Methods** - Several ways to accomplish each task for reliability

### 🎯 Key Advantages
1. **Comprehensive** - Does everything you can do manually + more
2. **Intelligent** - AI enhances your messages for better communication
3. **Reliable** - Multiple fallback methods for each operation
4. **Persistent** - Maintains session, no repeated logins
5. **Exportable** - Save chat history, templates, messages
6. **Scriptable** - Easy CLI and Python API

## Installation

```bash
# Install dependencies
pip install playwright asyncio

# Install Chromium
playwright install chromium

# First run - will create persistent session
python feishu_pro.py start
```

## Usage Examples

### Basic Messaging

```bash
# Simple message
python feishu_pro.py send Hany "Hello there"

# AI-enhanced professional message
python feishu_pro.py send-enhanced Hany "meeting tomorrow" professional

# Friendly style
python feishu_pro.py send-enhanced John "thanks for your help" friendly

# Formal style
python feishu_pro.py send-enhanced Boss "project completed" formal
```

### Advanced Messaging

```bash
# Send with @mention
python feishu_pro.py send-mention TeamChat "great work everyone" John

# Multi-line message
python feishu_pro.py send-multiline Hany "Meeting agenda:" "1. Review progress" "2. Plan next sprint"

# Smart reply (AI-generated response to last message)
python feishu_pro.py smart-reply Hany acknowledge
python feishu_pro.py smart-reply TeamChat thanks

# Batch send to multiple chats
python feishu_pro.py batch-send "Hany,John,Sarah" "Team meeting at 3pm today"
```

### Reading & Searching

```bash
# Read recent messages
python feishu_pro.py read Hany

# Read with custom limit
python feishu_pro.py read Hany 100

# Read and export to JSON
python feishu_pro.py read-export Hany backup.json

# Export full chat history
python feishu_pro.py export-history Hany complete_history.json

# Search across all chats
python feishu_pro.py search "project deadline"
```

### Templates

```bash
# Save a template
python feishu_pro.py save-template standup "Daily standup: {task} - {status}"

# List all templates
python feishu_pro.py list-templates

# Send from template
python feishu_pro.py send-template Hany standup

# Templates support variables (manual substitution in code)
```

### Files & Media

```bash
# Upload file
python feishu_pro.py upload Hany report.pdf

# Take screenshot
python feishu_pro.py screenshot current_view.png
```

### Chat Management

```bash
# List all chats
python feishu_pro.py list

# Check unread messages
python feishu_pro.py unread

# Mark chat as read
python feishu_pro.py mark-read Hany

# Create group chat
python feishu_pro.py create-group "Project Team" "John,Sarah,Mike"
```

## AI Message Enhancement Styles

The `send-enhanced` command supports these styles:

- **professional** - Polite, clear, asks for questions
  - "meeting tomorrow" → "Meeting tomorrow. Please let me know if you have any questions."

- **friendly** - Casual, warm, with emoji
  - "thanks" → "Hey! Thanks 😊"

- **formal** - Business letter style with greeting and sign-off
  - "project completed" → "Dear colleague,\n\nProject completed.\n\nBest regards"

- **brief** - Concise, to the point (max 100 chars)
  - "long message..." → "long message... [truncated]"

- **detailed** - Adds context, timestamp, metadata
  - "update" → "Update\n\nContext: This message was sent via automated system.\nTime: 2024-01-12 10:30:45"

## Smart Reply Intents

The `smart-reply` command generates contextual responses:

- **acknowledge** - "Got it, thanks!"
- **agree** - "I agree with this approach."
- **question** - "Could you provide more details?"
- **thanks** - "Thank you for sharing this!"
- **confirm** - "Confirmed. I'll take care of it."
- **schedule** - "Let's schedule a time to discuss this."
- **positive** - "Sounds great! Looking forward to it."
- **negative** - "I need to review this further before proceeding."

## Python API

Use Feishu Pro programmatically:

```python
from feishu_pro import FeishuPro

async def main():
    app = FeishuPro()
    await app.start()

    # Send enhanced message
    await app.send_message("Hany", "Project update", enhance="professional")

    # Read messages
    messages = await app.read_messages("Hany", limit=50)

    # Batch send
    chats = ["John", "Sarah", "Mike"]
    await app.batch_send(chats, "Team meeting at 3pm")

    # Smart reply
    await app.send_smart_reply("TeamChat", intent="thanks")

    # Save template
    await app.add_template("weekly", "Weekly update: {progress}")

    # Send from template with variables
    await app.send_from_template("Boss", "weekly", {"progress": "80% complete"})

    await app.close()

asyncio.run(main())
```

## Features Deep Dive

### Multiple Navigation Methods
For reliability, each operation tries multiple approaches:

1. **Direct Click** - Click visible chat in list
2. **Search** - Use search box to find chat
3. **Keyboard Shortcuts** - Ctrl+K quick switcher

### Message History & Logging
- All sent messages logged to `~/.feishu-history.json`
- Preserves last 1000 messages automatically
- Includes timestamp, chat name, message content

### Template System
- Save frequently used messages as templates
- Support variable substitution: `{variable_name}`
- Stored in `~/.feishu-templates.json`
- Persistent across sessions

### Session Management
- Browser context stored in `~/.feishu-browser-data/`
- Maintains cookies, local storage, login state
- No need to log in again

## Architecture

### Class Structure

```
FeishuPro
├── MessageEnhancer (AI utilities)
│   ├── enhance_message()
│   └── create_smart_reply()
├── Session Management
│   ├── start() - Initialize browser
│   ├── close() - Clean shutdown
│   └── navigate_to_chat() - Multiple methods
├── Messaging
│   ├── send_message() - Basic send
│   ├── send_formatted_message() - Markdown
│   ├── send_multiline_message() - Multi-line
│   ├── send_with_mention() - @mentions
│   ├── send_smart_reply() - AI replies
│   └── batch_send() - Bulk operations
├── Reading & Search
│   ├── read_messages() - Parse history
│   ├── search_messages() - Find content
│   ├── export_chat_history() - Full export
│   └── get_unread_count() - Check unreads
├── Templates
│   ├── add_template() - Save template
│   ├── send_from_template() - Use template
│   └── list_templates() - Show all
└── Advanced
    ├── upload_file() - File uploads
    ├── create_group_chat() - New groups
    ├── get_chat_list() - List chats
    ├── mark_as_read() - Mark read
    └── take_screenshot() - Capture screen
```

### Reliability Features

1. **Automatic Retries** - Multiple fallback methods
2. **Error Handling** - Graceful failures with messages
3. **History Logging** - Track all operations
4. **Session Persistence** - No repeated logins
5. **Rate Limiting** - Automatic delays between batch operations

## Troubleshooting

### Browser Won't Start
```bash
# Check if Chrome is installed
playwright install chromium --force

# Clear session data
rm -rf ~/.feishu-browser-data/
python feishu_pro.py start
```

### Chat Not Found
The app tries multiple methods automatically. If still failing:
- Ensure chat name is exact (case-sensitive)
- Check if chat is archived or hidden
- Try opening Feishu manually first

### Messages Not Sending
- Verify you're logged in: `python feishu_pro.py start`
- Check network connection
- Ensure input field is not blocked by popups

### Template Variables Not Replaced
Variables must be manually substituted in code:
```python
await app.send_from_template("chat", "template", {"var": "value"})
```

## Comparison with Basic App

| Feature | Basic App | Feishu Pro |
|---------|-----------|------------|
| Send Messages | ✅ | ✅ |
| Read Messages | ✅ | ✅ |
| Add Reactions | ⚠️ (Limited) | ⚠️ (Limited - Feishu UI limitation) |
| AI Enhancement | ❌ | ✅ |
| Smart Replies | ❌ | ✅ |
| Templates | ❌ | ✅ |
| Batch Operations | ❌ | ✅ |
| Message Search | ❌ | ✅ |
| File Uploads | ❌ | ✅ |
| Group Management | ❌ | ✅ |
| Export History | ❌ | ✅ |
| Multiple Methods | ❌ | ✅ |
| History Logging | ❌ | ✅ |
| @Mentions | ❌ | ✅ |
| Unread Tracking | ❌ | ✅ |

## Integration Examples

### Daily Standup Bot
```python
async def daily_standup():
    app = FeishuPro()
    await app.start()

    team = ["John", "Sarah", "Mike"]
    message = "Daily standup starting in 10 minutes!"

    await app.batch_send(team, message)
    await app.close()
```

### Auto-Reply Bot
```python
async def auto_reply_bot():
    app = FeishuPro()
    await app.start()

    # Check unread
    unread = await app.get_unread_count()

    for chat, count in unread.items():
        if count > 0:
            # Send smart reply
            await app.send_smart_reply(chat, "acknowledge")
            await app.mark_as_read(chat)

    await app.close()
```

### Chat Backup
```python
async def backup_all_chats():
    app = FeishuPro()
    await app.start()

    chats = await app.get_chat_list()

    for chat in chats:
        filename = f"backup_{chat}_{datetime.now().strftime('%Y%m%d')}.json"
        await app.export_chat_history(chat, filename)

    await app.close()
```

## Future Enhancements

Potential additions:
- Voice message support
- Video call automation
- Calendar integration
- Document collaboration
- Approval workflows
- Custom AI models for message enhancement
- Scheduled message sending
- Auto-translation
- Sentiment analysis

## Credits

Built on:
- Playwright - Browser automation
- Python asyncio - Async operations
- Feishu Web API - Messaging platform

## License

MIT License - Free to use and modify
