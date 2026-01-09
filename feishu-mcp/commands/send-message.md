---
name: feishu:send-message
description: Send a message to a Feishu chat interactively
argument-hint: (interactive - will prompt for chat and message)
allowed-tools: mcp_feishu, AskUserQuestion
---

# Send Message to Feishu Chat

Send a message to any accessible Feishu chat with interactive prompts.

## Usage

Simply run `/feishu:send-message` and follow the prompts to:
1. Select or search for a chat
2. Compose your message
3. Send

## Implementation

Use these steps to send a message:

1. **List available chats** using the MCP tool:
   ```
   Use mcp_feishu tool: list_chats
   ```

2. **Show chat options** to user using AskUserQuestion:
   - Present chat names as options
   - Allow user to select from list
   - Or allow custom chat ID input

3. **Get message content** from user:
   ```
   Ask: "What message would you like to send?"
   ```

4. **Send the message** using MCP tool:
   ```
   Use mcp_feishu tool: send_message
   Parameters:
   - chat_id: [selected chat ID]
   - message: [user's message text]
   - msg_type: "text"
   ```

5. **Confirm success**:
   - Show message ID if successful
   - Report any errors clearly

## Examples

**Example 1: Send to team chat**
```
User: /feishu:send-message
Assistant: Lists chats, user selects "Engineering Team"
Assistant: Asks for message
User: "Meeting at 3pm today"
Assistant: Sends message, confirms with message ID
```

**Example 2: Send to specific person**
```
User: /feishu:send-message
Assistant: Lists chats including "John Smith"
User: Selects "John Smith" chat
Assistant: Asks for message
User: "Can you review my PR?"
Assistant: Sends message
```

## Error Handling

- **No chats available**: Explain user needs to add bot to chats or enable OAuth
- **Permission denied**: Guide user to check bot permissions in Feishu console
- **Invalid chat**: Suggest using `/feishu:list-chats` to see available chats

## Tips

- Use natural language for messages
- Bot will send as itself (tenant token) or as user (OAuth token)
- Check message status in Feishu app to confirm delivery
