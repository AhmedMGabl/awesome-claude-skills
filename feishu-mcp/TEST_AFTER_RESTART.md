# Feishu MCP - Post-Restart Test Guide

After you restart Claude Code, use these commands to verify the Feishu Enhanced MCP is working:

## Quick Tests

### 1. Test Basic Connection
```
"Test Feishu MCP connection"
```
This should trigger the `test_enhanced_connection` tool and verify your bot has proper permissions.

### 2. Search for Documents
```
"Search Feishu for documents about [topic]"
```
or
```
"Find all documents in Feishu"
```
This uses `search_all_content` to find documents across Docs, Bases, Wikis, and Chats.

### 3. List Feishu Bases (Spreadsheets)
```
"List all my Feishu Bases"
```
or
```
"Show me all spreadsheets in Feishu"
```
This uses `list_bases` to show all accessible Feishu Base applications.

### 4. Read a Document
```
"Read the Feishu document [document_id or name]"
```
This uses `read_document` to fetch document content.

### 5. Search in a Feishu Base
```
"Search for records in Feishu Base [base_name] where [criteria]"
```
This uses `search_base_records` to query spreadsheet data.

## Expected Behavior

If Feishu MCP is working correctly, you should see:

✅ Claude will use tools like:
- `mcp__feishu-enhanced__search_all_content`
- `mcp__feishu-enhanced__list_bases`
- `mcp__feishu-enhanced__read_document`
- `mcp__feishu-enhanced__search_base_records`
- `mcp__feishu-enhanced__update_base_record`
- `mcp__feishu-enhanced__create_base_record`
- `mcp__feishu-enhanced__track_document`
- etc.

❌ If NOT working, you'll see:
- "I don't have tools to access Feishu"
- No `mcp__feishu-enhanced__*` tools available
- Errors about missing MCP server

## What These Tools Do

### Document Discovery
- `search_all_content` - Search across ALL Feishu content (Docs, Bases, Wikis, Chats)
- `track_document` - Track important documents for easy access

### Feishu Docs (Documents)
- `read_document` - Read document content with all blocks
- `update_document_block` - Modify specific blocks in documents

### Feishu Bases (Spreadsheets)
- `list_bases` - List all accessible Bases
- `search_base_records` - Find records matching criteria
- `update_base_record` - Update existing records
- `create_base_record` - Create new records

### Wiki Pages
- `search_wiki` - Search wiki pages
- `read_wiki_page` - Read wiki content

### System
- `test_enhanced_connection` - Verify permissions and connectivity

## Configuration Status

Current setup:
- ✅ Server: `W:\WS\AhmedGabl\awesome-claude-skills\feishu-mcp\server.py`
- ✅ App ID: `cli_a85833b3fc39900e`
- ✅ App Secret: Configured in `.mcp.json`
- ✅ MCP Server Name: `feishu-enhanced`

## Required Permissions

For full functionality, your Feishu bot needs:

**Document Management**:
- `drive:drive` - Full drive access (for search)
- `docx:document` - Modify Feishu Docs
- `docx:document:readonly` - Read Feishu Docs
- `bitable:app` - Modify Feishu Bases
- `bitable:app:readonly` - Read Feishu Bases
- `wiki:wiki` - Modify wiki pages
- `wiki:wiki:readonly` - Read wiki pages

**Basic Messaging** (already configured):
- `im:message` - Send messages
- `im:chat` - Manage chats

## Troubleshooting

If tests fail after restart:

1. **Check Claude Code loaded the MCP server**:
   - Look for "Feishu Enhanced" in MCP server list
   - Check for any startup errors

2. **Verify credentials**:
   - App ID: `cli_a85833b3fc39900e`
   - App Secret is set in `.mcp.json`

3. **Check permissions**:
   - Run "Test Feishu MCP connection"
   - Add missing permissions at [open.feishu.cn](https://open.feishu.cn)

4. **Check server.py exists**:
   - Path: `W:\WS\AhmedGabl\awesome-claude-skills\feishu-mcp\server.py`
   - Should be 16KB+ with all document management tools

## Next Steps After Successful Test

Once verified working:

1. **Find your important document**:
   ```
   "Search Feishu for [document description or keywords]"
   ```

2. **Track it for future access**:
   ```
   "Track this Feishu document: [document_id]"
   ```

3. **Update Feishu Base records**:
   ```
   "Update the record in [base_name] where [field] is [value] and set [field] to [new_value]"
   ```

4. **Fix incorrect data**:
   ```
   "Find and fix the incorrect [field] value in Feishu Base [base_name]"
   ```

---

**Remember**: This file is just for testing. Delete it after you've verified everything works!
