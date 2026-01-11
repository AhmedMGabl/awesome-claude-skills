---
name: feishu:read-messages-browser
description: Read messages from a Feishu chat using browser automation
argument-hint: (interactive - will prompt for chat selection)
allowed-tools: mcp__plugin_playwright_playwright__*, AskUserQuestion
---

# Read Messages via Feishu Browser

Read and scrape messages from any Feishu chat using browser automation. Keep full context of conversations.

## What This Does

- Navigate to Feishu web interface
- Access any chat you can view
- Read message history
- Extract message content, senders, timestamps
- Keep records for context

## Implementation

### Step 1: Navigate to Feishu

```
Use browser_navigate:
URL: https://applink.feishu.cn/client/chat/open
```

### Step 2: Select Chat

1. Take snapshot to see available chats
2. Ask user which chat to read
3. Click or search for the chat

### Step 3: Read Messages

1. Take snapshot of chat view
2. Extract visible messages from snapshot
3. Optionally scroll up for history
4. Take additional snapshots as needed

### Step 4: Extract Data

From snapshot, extract:
- Message text
- Sender names
- Timestamps
- Message types (text, file, image, etc.)
- Reactions/replies

## Data Extraction

The snapshot provides accessible text including:
- All visible message text
- Sender names
- Relative timestamps ("10 minutes ago", "Yesterday", etc.)
- Chat metadata

## Use Cases

1. **Context gathering**: Read conversation history before responding
2. **Data collection**: Extract messages for analysis
3. **Record keeping**: Archive important conversations
4. **Search**: Find specific messages or information
5. **Monitoring**: Check for new messages

## Advanced Features

### Scroll for History

```
Use browser_evaluate:
function: "() => window.scrollTo(0, 0)"
```

Then take new snapshot to read older messages.

### Search Within Chat

Use Feishu's built-in search:
1. Click search icon in chat
2. Type search query
3. Read search results

### Export Conversations

Read and save multiple snapshots to build complete conversation history.

## Example Flow

```
1. Navigate to Feishu
2. Snapshot (see chats)
3. Click target chat
4. Snapshot (read messages)
5. Scroll up if needed
6. Snapshot again (read more)
7. Extract and summarize
```

## Benefits

- Access ANY chat you can see
- No API limitations
- Full message context
- See formatting, reactions, etc.
- Works exactly like web app
