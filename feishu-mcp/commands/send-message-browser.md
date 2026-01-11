---
name: feishu:send-message-browser
description: Send a message to a Feishu chat using browser automation (bypasses API limitations)
argument-hint: (interactive - will prompt for chat and message)
allowed-tools: mcp__plugin_playwright_playwright__*, AskUserQuestion
---

# Send Message via Feishu Browser

Send messages to any Feishu chat using browser automation. This bypasses API limitations and works exactly like using the Feishu web app.

## Why Use Browser Automation?

- **No API scope issues**: Works without OAuth complications
- **Full access**: Access any chat you can see in the web app
- **No bot required**: Send as yourself, not as a bot
- **Complete features**: Access all Feishu features available in web UI

## Implementation

### Step 1: Navigate to Feishu Web

```
Use mcp__plugin_playwright_playwright__browser_navigate:
URL: https://applink.feishu.cn/client/chat/open
```

### Step 2: Wait for Page Load

```
Use mcp__plugin_playwright_playwright__browser_wait_for:
- Wait for: "search" or "chats" text to appear (indicates loaded)
- Time: 3 seconds
```

### Step 3: Take Snapshot

```
Use mcp__plugin_playwright_playwright__browser_snapshot
```

This will show available chats and UI elements.

### Step 4: Search for Chat

If user specified a chat name:
1. Click search box
2. Type chat name
3. Click matching chat

Use:
- `browser_click` - Click search box
- `browser_type` - Type chat name
- `browser_snapshot` - See results
- `browser_click` - Click target chat

### Step 5: Send Message

1. Take snapshot to find message input box
2. Click message input area
3. Type the message
4. Press Enter or click Send button

Use:
- `browser_click` - Click message input
- `browser_type` - Type message with submit: true
- `browser_snapshot` - Verify message sent

## Example Flow

```
1. Navigate to Feishu
2. Wait for load
3. Snapshot (see chats)
4. Ask user which chat
5. Click/search for chat
6. Snapshot (see message box)
7. Click message input
8. Type message + send
9. Snapshot (verify sent)
```

## Error Handling

If not logged in:
- Snapshot will show login screen
- Inform user to log in to Feishu web in their browser first
- Session should persist

If chat not found:
- Show available chats from snapshot
- Let user select by number or search

## Advantages

- Works for ALL chats (no "bot not member" errors)
- Sends as YOU (not as bot)
- No scope requirements
- Can see message history
- Can access any Feishu feature

## Usage Tips

- First run may require login
- Browser session persists
- Can send to any chat visible in web app
- Supports all message types (text, files, etc.)
