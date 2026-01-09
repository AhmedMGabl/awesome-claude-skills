---
name: feishu:create-chat
description: Create a new Feishu group chat with specified members
argument-hint: (interactive - will prompt for chat name and members)
allowed-tools: mcp_feishu, AskUserQuestion
---

# Create Feishu Group Chat

Create a new group chat in Feishu with specified name and members.

## Usage

Run `/feishu:create-chat` and follow prompts to:
1. Enter chat name
2. Specify member emails or user IDs
3. Optionally set chat description
4. Create the chat

## Implementation

1. **Get chat name** from user:
   ```
   Ask: "What should the chat be named?"
   Example: "Project Alpha Team", "Sprint Planning"
   ```

2. **Get member list**:
   ```
   Ask: "Enter member emails (comma-separated) or user IDs:"
   Example: "john@51talk.com, sarah@51talk.com"
   ```

3. **Optional: Get description**:
   ```
   Ask: "Add a chat description? (optional)"
   ```

4. **Create chat** using MCP tool:
   ```
   Use mcp_feishu tool: create_chat
   Parameters:
   - name: [chat name]
   - user_ids: [list of emails or IDs]
   - description: [optional description]
   ```

5. **Confirm and provide details**:
   ```
   Show:
   - Chat name
   - Chat ID (for future reference)
   - Number of members added
   - Link to chat (if available)
   ```

## Examples

**Example 1: Simple team chat**
```
User: /feishu:create-chat
Assistant: "What should the chat be named?"
User: "Frontend Team"
Assistant: "Enter member emails (comma-separated):"
User: "john@51talk.com, sarah@51talk.com"
Assistant: Creates chat, shows ID and confirmation
```

**Example 2: Project chat with description**
```
User: /feishu:create-chat
Assistant: Prompts for name
User: "Q1 Planning"
Assistant: Prompts for members
User: "team-leads@51talk.com"
Assistant: "Add a description?"
User: "Q1 2026 planning and coordination"
Assistant: Creates chat with description
```

**Example 3: Quick chat creation**
```
User: /feishu:create-chat
Assistant: Guides through minimal setup
User: Provides name and 2 members
Assistant: Creates basic chat, provides chat ID
```

## Input Formats

**Member specification** (accept multiple formats):
- Emails: `john@51talk.com, sarah@51talk.com`
- User IDs: `ou_xxx, ou_yyy`
- Mixed: `john@51talk.com, ou_yyy`

**Chat names**:
- Plain text: `Engineering Team`
- With emojis: `🚀 Launch Team`
- Descriptive: `Q1 2026 - Marketing Strategy`

## Success Response

Format the success message clearly:

```
✅ Chat Created Successfully!

Name: {chat_name}
Chat ID: {chat_id}
Members: {member_count} added
Description: {description or "None"}

The chat is now available in your Feishu app.
Use this Chat ID for sending messages: {chat_id}
```

## Error Handling

**Invalid emails**:
- Message: "Some emails weren't recognized: {emails}"
- Action: Ask user to verify emails or use user IDs

**Permission denied**:
- Message: "Bot doesn't have permission to create chats"
- Action: Guide to check `im:chat` permission in Feishu console

**Already exists**:
- Message: "A chat with similar name exists: {existing_chat}"
- Action: Ask if user wants to use existing chat or create with different name

**No members specified**:
- Message: "At least one member is required"
- Action: Prompt again for member list

## Tips

- Include yourself in member list to join the chat
- Bot automatically gets added as member
- Use clear, descriptive names for easy identification
- Save chat IDs for quick access later
- Maximum members per chat: Check Feishu limits (typically 500-1000)

## Related Commands

- `/feishu:list-chats` - See all your chats including newly created one
- `/feishu:send-message` - Send first message to new chat
