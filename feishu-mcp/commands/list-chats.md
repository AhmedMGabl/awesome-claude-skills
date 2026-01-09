---
name: feishu:list-chats
description: List all accessible Feishu chats with names and IDs
argument-hint: (no arguments required)
allowed-tools: mcp_feishu
---

# List Feishu Chats

Display all Feishu chats that the bot or user can access.

## Usage

Run `/feishu:list-chats` to see:
- Chat names
- Chat IDs
- Chat types (group, private, etc.)
- Number of members

## Implementation

1. **Call MCP tool** to list chats:
   ```
   Use mcp_feishu tool: list_chats
   Parameters:
   - page_size: 50 (or user-specified)
   ```

2. **Format and display results**:
   Present chats in a clear, readable format:
   ```
   Your Feishu Chats:

   1. Engineering Team (oc_xxx)
      Type: Group | Members: 15

   2. John Smith (oc_yyy)
      Type: Private | Members: 2

   3. Project Alpha (oc_zzz)
      Type: Group | Members: 8
   ```

3. **Handle pagination** if many chats:
   - Show first 20-30 chats
   - Offer to show more if available
   - Allow search/filter by name

4. **Provide context**:
   - Explain chat access depends on bot membership or OAuth
   - Suggest using OAuth for full chat list

## Examples

**Example 1: Basic listing**
```
User: /feishu:list-chats
Assistant: Displays formatted list of 12 chats
```

**Example 2: Many chats**
```
User: /feishu:list-chats
Assistant: Shows first 30 chats
Assistant: "Showing 30 of 150 chats. Would you like to see more or search for specific chat?"
```

**Example 3: No chats available**
```
User: /feishu:list-chats
Assistant: "No chats found. This can happen if:
- Bot hasn't been added to any chats
- OAuth not configured for user-level access
- Insufficient permissions

Would you like help setting up OAuth?"
```

## Output Format

Use this format for clear presentation:

```
📋 Your Feishu Chats ({count} total)

{index}. {chat_name}
   ID: {chat_id}
   Type: {chat_type} | Members: {member_count}

[Repeat for each chat]
```

## Error Handling

- **Empty result**: Explain possible causes and solutions
- **Permission error**: Guide to OAuth setup or permission checking
- **API error**: Show error code and message, suggest retry

## Tips

- Save chat IDs for quick access in future messages
- Use with `/feishu:send-message` to see available targets
- OAuth provides access to all user chats, not just bot chats
