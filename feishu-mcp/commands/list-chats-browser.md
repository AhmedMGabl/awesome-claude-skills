---
name: feishu:list-chats-browser
description: List all accessible Feishu chats using browser automation
argument-hint: (no arguments required)
allowed-tools: mcp__plugin_playwright_playwright__*
---

# List Chats via Feishu Browser

Display all your Feishu chats using browser automation. See everything exactly as it appears in the web app.

## What This Does

- Opens Feishu web interface
- Captures list of all chats
- Shows chat names, last messages, unread counts
- Provides full context of your conversations

## Implementation

### Step 1: Navigate to Feishu

```
Use browser_navigate:
URL: https://applink.feishu.cn/client/chat/open
```

### Step 2: Wait for Chats to Load

```
Use browser_wait_for:
- Wait for chat list to appear
- Time: 3 seconds
```

### Step 3: Capture Chat List

```
Use browser_snapshot
```

The snapshot will show:
- All chat names
- Last message preview
- Timestamps
- Unread message counts
- Pinned chats
- Chat types (group, private, etc.)

### Step 4: Scroll for More Chats

If you have many chats:

```
Use browser_evaluate:
function: "() => window.scrollBy(0, 500)"
```

Then take another snapshot to see more chats.

## Information Available

From the snapshot, you can see:
- **Chat names**: Full names of all chats
- **Last messages**: Preview of most recent message
- **Time**: When last message was sent
- **Unread**: Number of unread messages
- **Type**: Group, private, bot chats
- **Status**: Online/offline for private chats
- **Pinned**: Which chats are pinned to top

## Use Cases

1. **Chat discovery**: Find specific chats quickly
2. **Unread monitoring**: See which chats have unread messages
3. **Context**: Understand your active conversations
4. **Organization**: See chat structure and grouping

## Example Output

After taking snapshot, you'll see something like:

```
Chats:
1. Hany, Ahmed Abogabl
   Last: "Hello!" - 2 minutes ago
   Type: Private

2. Project Team Meeting
   Last: "@Ahmed can you review?" - 1 hour ago
   Unread: 3
   Type: Group

3. Engineering Team
   Last: "Daily standup in 5 mins" - Today 09:00
   Type: Group
   (Pinned)
```

## Benefits

- See ALL your chats (no API limitations)
- Exactly matches what you see in app
- Includes unread counts
- Shows pinned chats
- No authentication issues

## Advanced Usage

### Search Chats

1. Click search box in Feishu
2. Type search query
3. Snapshot to see results

### Filter by Type

Use Feishu's built-in filters (if visible):
- Click "Groups" or "Private" tabs
- Snapshot filtered results

### Refresh

Simply take a new snapshot to refresh the list.
