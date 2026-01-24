# Quick Start: Feishu Document Management

**Goal**: Enable Claude to find, read, and modify all your Feishu content in 15 minutes.

## What This Enables

After setup, you can ask Claude:
- ✅ "Find my Q4 planning document"
- ✅ "Show me all spreadsheets about sales"
- ✅ "Fix the budget numbers in Finance Tracker"
- ✅ "Read the engineering roadmap doc"
- ✅ "Search for 'project status' across everything"
- ✅ "Update the deadline in the proposal"

## 3-Step Setup (15 minutes)

### Step 1: Add Permissions (5 min)

1. Go to https://open.feishu.cn/
2. Select your app: `cli_a85833b3fc39900e`
3. Click "Permissions & Scopes"
4. Add these 8 permissions:
   ```
   ✅ drive:drive
   ✅ drive:drive:readonly
   ✅ docx:document
   ✅ docx:document:readonly
   ✅ bitable:app
   ✅ bitable:app:readonly
   ✅ wiki:wiki
   ✅ wiki:wiki:readonly
   ```
5. Click "Create App Version"
6. Click "Apply for publish online"
7. Wait 5 minutes for permissions to activate

### Step 2: Install Enhanced Server (5 min)

```bash
# Copy enhanced server
cp feishu-mcp/scripts/enhanced_feishu_server.py C:/Users/eng20/feishu-ultimate-mcp/server_enhanced.py

# Update Claude config
# Edit: $APPDATA/Claude/claude_desktop_config.json
# Change "server.py" to "server_enhanced.py" in the args array

# Restart Claude CLI
```

**Full config should look like**:
```json
{
  "mcpServers": {
    "feishu-ultimate": {
      "command": "python",
      "args": ["C:\\Users\\eng20\\feishu-ultimate-mcp\\server_enhanced.py"],
      "env": {
        "FEISHU_APP_ID": "cli_a85833b3fc39900e",
        "FEISHU_APP_SECRET": "fiFRoqlAFX7ASY9iUt7Evb2aUx6Qurkd"
      }
    }
  }
}
```

### Step 3: Test Features (5 min)

Open Claude and try:

```
1. Test connection:
"Test the Feishu document features"
(Should call test_enhanced_connection and show Drive + Base status)

2. Search documents:
"Search for documents with 'meeting' in Feishu"
(Should return list of matching docs)

3. List spreadsheets:
"Show me all my Feishu spreadsheets"
(Should list all Bases you have access to)

4. Done! Now you can find and modify anything in Feishu
```

## Common Use Cases

### Find a Document

```
You: "I can't find the quarterly review document"

Claude will:
1. Search across all Feishu content
2. Show results with types and dates
3. Let you select the correct one
4. Retrieve and show you the content
```

### Fix Spreadsheet Data

```
You: "The revenue number for Marketing is wrong in Q4 Budget spreadsheet"

Claude will:
1. Find the Q4 Budget spreadsheet
2. Locate Marketing department rows
3. Show current revenue value
4. Ask for correct value
5. Update the record
6. Confirm the change
```

### Read Document Content

```
You: "What does the project proposal say about timeline?"

Claude will:
1. Find "project proposal" document
2. Read the full content
3. Extract timeline information
4. Answer your question
```

### Track Important Documents

```
You: "Keep track of all documents related to the new product launch"

Claude will:
1. Search for "product launch" documents
2. Create/update tracking base
3. Add each document with metadata
4. Provide tracking base URL
```

## Troubleshooting

### "Permission denied" error

**Fix**: Wait 10 minutes after adding permissions, then restart Claude

### "Can't find document"

**Fixes**:
- Check if you have access to the document
- Try broader search terms
- Verify document wasn't deleted

### "Server not loading"

**Fixes**:
- Check server_enhanced.py exists at path
- Verify config.json has correct path
- Restart Claude completely
- Check Python is in PATH

## What You Can Do Now

✅ **Find any document** - Search across Docs, Bases, Wikis, Chats
✅ **Read content** - View document text, spreadsheet data, wiki pages
✅ **Modify data** - Update spreadsheet cells, document text, wiki content
✅ **Track documents** - Keep organized list of important files
✅ **Fix errors** - Correct wrong data in any Feishu content

## Next Steps

**Optional Enhancements**:

1. **Set up tracking base** (see DOCUMENT_MANAGEMENT_SETUP.md)
2. **Configure user OAuth** for more access
3. **Create search shortcuts** for common queries

## Need Help?

1. Read: `DOCUMENT_MANAGEMENT_SETUP.md` (comprehensive guide)
2. Read: `skills/feishu-document-manager/SKILL.md` (detailed workflows)
3. Check: Feishu API docs at https://open.feishu.cn/document

---

**Time to complete**: 15 minutes
**Status**: Ready to use immediately after setup
**Features**: 14 new tools for document operations
