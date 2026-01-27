# Post-Restart Checklist

**Status**: All pre-checks PASSED ✅
**Ready to restart**: YES

---

## Pre-Restart Validation Results

```
[OK] PASS: Python Version (3.13.9)
[OK] PASS: Dependencies (httpx, fastmcp, python-dotenv)
[OK] PASS: Server File (16,211 bytes)
[OK] PASS: Credentials (App ID & Secret configured)
[OK] PASS: Server Import (Module loads successfully)
[OK] PASS: MCP Tools (11/11 tools found)
```

---

## Restart Steps

### 1. Save Your Work
- Save any open files in Claude Code
- Note the current directory: `W:\WS\AhmedGabl\awesome-claude-skills`

### 2. Close Claude Code COMPLETELY
- File → Exit (or Alt+F4)
- Wait 5 seconds to ensure it's fully closed
- Check Task Manager if needed (no Claude Code processes)

### 3. Restart Claude Code
- Launch Claude Code
- Wait for startup to complete
- MCP servers load automatically during startup

### 4. Navigate Back
- Go to: `W:\WS\AhmedGabl\awesome-claude-skills`

---

## Verification Tests (Run After Restart)

### Test 1: Check MCP Server Loaded
```
"List available MCP servers"
```
**Expected**: Should see "feishu-enhanced" in the list

### Test 2: Test Connection
```
"Test Feishu MCP connection"
```
**Expected**:
```
Enhanced Features Status:
[OK] Drive: OK
[OK] Base: OK
```

### Test 3: Universal Search
```
"Search Feishu for any documents"
```
**Expected**: Returns search results or "No results found"

### Test 4: List Bases
```
"List all my Feishu Bases"
```
**Expected**: Shows list of spreadsheets/databases

### Test 5: Find Your Important Document
```
"Search Feishu for [description of your lost document]"
```
**Expected**: Returns matching documents

---

## Available Commands After Restart

### Document Discovery
```
"Search Feishu for documents about [topic]"
"Find documents created by [owner] in the last [timeframe]"
"Show all documents modified this week"
```

### Feishu Docs Operations
```
"Read the document [document_id or name]"
"Update block [block_id] in document [doc_id] with [new content]"
"Show me the content of [document name]"
```

### Feishu Base (Spreadsheet) Operations
```
"List all my Feishu Bases"
"Search [base_name] for records where [field] is [value]"
"Update record [record_id] in [base_name] and set [field] to [value]"
"Create a new record in [base_name] with [field]=[value]"
```

### Wiki Operations
```
"Search wiki for [topic]"
"Read wiki page [page_id]"
```

### Document Tracking
```
"Track this document: [name/url]"
"Add [document] to tracking with priority High"
```

### Data Correction
```
"Find incorrect data in [base_name] where [condition]"
"Fix the [field] value in [base_name] for [criteria]"
```

---

## If Something Goes Wrong

### Issue: Feishu MCP Server Not Loading

**Check:**
1. Look for error messages during Claude Code startup
2. Verify `.mcp.json` exists in the feishu-mcp folder
3. Check logs (if available)

**Fix:**
1. Re-run test: `python test_server.py`
2. Check credentials in `.mcp.json`
3. Restart Claude Code again

### Issue: "Permission Denied" Errors

**Symptoms:**
- Error codes like 99991672, 20027
- "No permission to access" messages

**Fix:**
1. Run: `"Test Feishu MCP connection"` to see which permissions are missing
2. Go to https://open.feishu.cn/
3. Add missing permissions:
   - `drive:drive` - Full drive access
   - `docx:document` / `docx:document:readonly` - Document access
   - `bitable:app` / `bitable:app:readonly` - Base access
   - `wiki:wiki` / `wiki:wiki:readonly` - Wiki access
4. Create new app version
5. Wait 10 minutes for permissions to activate
6. Restart Claude Code

### Issue: "No Results Found" When Searching

**Reasons:**
- Document doesn't exist or was deleted
- Bot doesn't have access to the folder/space
- Search terms too specific

**Fix:**
1. Try broader search terms
2. Check document exists in Feishu web
3. Verify bot is added to relevant chats/folders
4. Try: `"List all my Feishu Bases"` to verify access

### Issue: Tools Not Showing Up

**Check:**
1. Restart Claude Code (may need full restart)
2. Verify MCP server config:
   ```json
   {
     "mcpServers": {
       "feishu-enhanced": {
         "command": "python",
         "args": ["${CLAUDE_PLUGIN_ROOT}/server.py"],
         "env": {
           "FEISHU_APP_ID": "cli_a85833b3fc39900e",
           "FEISHU_APP_SECRET": "..."
         }
       }
     }
   }
   ```

---

## What to Expect

### Tools Now Available:
1. `search_all_content` - Universal Feishu search
2. `read_document` - Read Feishu Docs
3. `update_document_block` - Modify documents
4. `list_bases` - List all Bases
5. `search_base_records` - Query spreadsheets
6. `update_base_record` - Update spreadsheet data
7. `create_base_record` - Add new records
8. `search_wiki` - Search wikis
9. `read_wiki_page` - Read wiki pages
10. `track_document` - Document tracking
11. `test_enhanced_connection` - Verify setup

### Skills Auto-Activate:
- **feishu-document-manager** - When finding/modifying documents
- **feishu-setup** - When configuring bots

---

## Success Criteria

✅ All 5 verification tests pass
✅ Can search for documents
✅ Can list Feishu Bases
✅ Can find your important document
✅ Can update records if needed

---

## Quick Reference

**Project Path**: `W:\WS\AhmedGabl\awesome-claude-skills`
**Server**: `feishu-mcp/server.py`
**Config**: `feishu-mcp/.mcp.json`
**App ID**: `cli_a85833b3fc39900e`

**Test Command**: `"Test Feishu MCP connection"`
**Find Document**: `"Search Feishu for [description]"`
**List Bases**: `"List all my Feishu Bases"`

---

**Next Action**: RESTART CLAUDE CODE NOW

After restart, return to this directory and run the verification tests above.
