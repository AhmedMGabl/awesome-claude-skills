# Feishu Enhanced MCP - Visual Usage Guide

**Quick Reference**: Everything you can do with Feishu Enhanced MCP

---

## 🎯 What Can You Do?

The Feishu Enhanced MCP server gives Claude the power to:

```
✅ Find any document across all of Feishu
✅ Read Feishu Docs (rich text documents)
✅ Modify Feishu Bases (spreadsheets/databases)
✅ Search Wiki pages
✅ Track important documents
✅ Fix incorrect data anywhere
```

---

## 📖 Quick Start Examples

### Example 1: Find a Lost Document

**You say:**
```
"I can't find the Q4 planning document in Feishu"
```

**Claude does:**
```
1. Searches across ALL Feishu content (Docs, Bases, Wikis, Chats)
2. Returns ranked results:
   ✓ Q4_Planning_Final.docx (Doc) - Modified Jan 20
   ✓ Q4 Budget Planning (Base) - Modified Jan 18
   ✓ Q4 Strategy Wiki (Wiki) - Modified Jan 15

3. You select the one you want
4. Claude retrieves and shows content
5. Optionally tracks it for future quick access
```

**Tools used:** `search_all_content`, `read_document`, `track_document`

---

### Example 2: Fix Wrong Data in Spreadsheet

**You say:**
```
"The revenue for Marketing in Q4 Budget is wrong, it should be $750k not $500k"
```

**Claude does:**
```
1. Finds "Q4 Budget" Feishu Base
2. Searches for Marketing department record in Q4
3. Shows current value: "$500k"
4. Updates to new value: "$750k"
5. Confirms change successful
6. Tracks the modification with notes
```

**Tools used:** `list_bases`, `search_base_records`, `update_base_record`, `track_document`

---

### Example 3: Read and Summarize Document

**You say:**
```
"What does the engineering roadmap say about Q2 milestones?"
```

**Claude does:**
```
1. Searches for "engineering roadmap" document
2. Reads the full document content
3. Extracts Q2 milestone information
4. Summarizes key points for you
5. Provides document link for reference
```

**Tools used:** `search_all_content`, `read_document`

---

### Example 4: Update Document Status

**You say:**
```
"Change the project status to 'Approved' in the proposal document"
```

**Claude does:**
```
1. Finds "proposal" document
2. Reads document structure to find status block
3. Shows current status: "Under Review"
4. Updates status block to "Approved"
5. Verifies the change
6. Provides confirmation
```

**Tools used:** `search_all_content`, `read_document`, `update_document_block`

---

### Example 5: Search Across Everything

**You say:**
```
"Find everything related to 'project launch' in Feishu"
```

**Claude does:**
```
1. Searches ALL content types:
   - Feishu Docs matching "project launch"
   - Feishu Bases with "project launch" data
   - Wiki pages about "project launch"
   - Chat messages containing "project launch"

2. Returns unified results with metadata:
   ✓ Project Launch Plan (Doc) - 3 days ago
   ✓ Launch Tracker (Base) - 1 day ago
   ✓ Launch Procedures Wiki (Wiki) - 1 week ago
   ✓ Launch Discussion (Chat) - Today
```

**Tools used:** `search_all_content`

---

### Example 6: Batch Update Spreadsheet

**You say:**
```
"Update all 'Pending' tasks to 'In Progress' in the Project Tracker"
```

**Claude does:**
```
1. Finds "Project Tracker" Base
2. Searches for all records where Status = "Pending"
3. Shows how many records will be updated
4. Updates all records to "In Progress"
5. Confirms batch update completed
6. Shows updated count
```

**Tools used:** `list_bases`, `search_base_records`, `update_base_record` (multiple calls)

---

## 🛠️ Available Tools Reference

### Document Discovery (2 tools)

**search_all_content**
```
Purpose: Search across ALL Feishu content types
Parameters:
  - query: Search keywords
  - content_types: Filter by type (doc, sheet, wiki, chat)
  - owner_ids: Filter by owner
  - date_from/date_to: Date range
  - limit: Max results (default 20)

Returns: Unified list of all matching content
```

**track_document**
```
Purpose: Add documents to tracking system
Parameters:
  - document_name: Name of document
  - document_type: Type (doc/base/wiki/chat)
  - document_url: Feishu URL
  - status: Tracking status
  - priority: High/Medium/Low
  - notes: Additional information

Returns: Confirmation with tracking ID
```

---

### Feishu Docs Operations (2 tools)

**read_document**
```
Purpose: Read full content of a Feishu Doc
Parameters:
  - document_id: Document identifier

Returns: Full document content with all blocks and structure
```

**update_document_block**
```
Purpose: Modify specific content blocks in a document
Parameters:
  - document_id: Document identifier
  - block_id: Specific block to update
  - new_content: Updated text/content

Returns: Confirmation of update
```

---

### Feishu Bases Operations (4 tools)

**list_bases**
```
Purpose: List all accessible Feishu Bases (spreadsheets)
Parameters:
  - page_size: Number of results (default 20)

Returns: List of all Bases with names and tokens
```

**search_base_records**
```
Purpose: Find records matching specific criteria
Parameters:
  - app_token: Base identifier
  - table_id: Table within the Base
  - field_name: Column to search
  - search_value: Value to find
  - operator: eq/contains/gte/lte/etc

Returns: Matching records with all fields
```

**update_base_record**
```
Purpose: Update an existing record in a Base
Parameters:
  - app_token: Base identifier
  - table_id: Table identifier
  - record_id: Specific record to update
  - fields: Dictionary of {field_name: new_value}

Returns: Confirmation with updated record
```

**create_base_record**
```
Purpose: Create a new record in a Base
Parameters:
  - app_token: Base identifier
  - table_id: Table identifier
  - fields: Dictionary of {field_name: value}

Returns: New record ID and confirmation
```

---

### Wiki Operations (2 tools)

**search_wiki**
```
Purpose: Search for wiki pages
Parameters:
  - query: Search keywords
  - space_id: Optional wiki space filter

Returns: Matching wiki pages with metadata
```

**read_wiki_page**
```
Purpose: Read wiki page content
Parameters:
  - space_id: Wiki space identifier
  - node_token: Page identifier

Returns: Full page content
```

---

### System Tools (1 tool)

**test_enhanced_connection**
```
Purpose: Verify server is working and check permissions
Parameters: None

Returns: Status report of all capabilities and permissions
```

---

## 🎨 Usage Patterns

### Pattern 1: Search → Read → Track
```
1. Search for document with keywords
2. Read the document content
3. Track it for future quick access
```

**Use case:** Finding and organizing important documents

---

### Pattern 2: Search → Modify → Verify
```
1. Search for the spreadsheet/document
2. Find the specific record/block to modify
3. Apply the change
4. Verify the update succeeded
```

**Use case:** Fixing incorrect data

---

### Pattern 3: List → Filter → Batch Update
```
1. List all records in a Base
2. Filter to find matching records
3. Update multiple records at once
4. Confirm batch operation
```

**Use case:** Bulk data corrections

---

## 📊 Content Types Supported

| Type | Search | Read | Modify | Create |
|------|--------|------|--------|--------|
| **Feishu Docs** | ✅ | ✅ | ✅ | ❌ |
| **Feishu Bases** | ✅ | ✅ | ✅ | ✅ |
| **Wiki Pages** | ✅ | ✅ | ❌ | ❌ |
| **Chat Messages** | ✅ | ✅ | ❌ | ❌ |

---

## 🔧 Testing the Server

### Option 1: Use Interactive Test Script
```bash
cd feishu-mcp/scripts
python test_feishu_enhanced.py
```

This provides a menu-driven interface to test all features.

### Option 2: Ask Claude Directly
```
"Test the Feishu Enhanced MCP connection"
```

Claude will use `test_enhanced_connection` to verify everything.

### Option 3: Try a Real Query
```
"Search for documents about [your topic] in Feishu"
```

If it works, you'll see `search_all_content` being called.

---

## 🚦 Permission Status

### Required Permissions

| Permission | Capability | Status |
|------------|------------|--------|
| `drive:drive` | Search all content | ⚠️ Add in console |
| `docx:document` | Modify documents | ⚠️ Add in console |
| `docx:document:readonly` | Read documents | ⚠️ Add in console |
| `bitable:app` | Modify Bases | ⚠️ Add in console |
| `bitable:app:readonly` | Read Bases | ⚠️ Add in console |
| `wiki:wiki` | Modify wikis | ⚠️ Add in console |
| `wiki:wiki:readonly` | Read wikis | ⚠️ Add in console |
| `im:message` | Send messages | ✅ Already configured |
| `im:chat` | Manage chats | ✅ Already configured |

### How to Add Permissions

1. Go to https://open.feishu.cn/
2. Select app: `cli_a85833b3fc39900e`
3. Click "Permissions & Scopes"
4. Add all permissions marked with ⚠️
5. Click "Create App Version"
6. Click "Apply for publish online"
7. Wait 5-10 minutes for activation

---

## 🎯 Common Use Cases

### For Project Managers
```
"Find all project documents in Feishu"
"Update project status to Completed in Project Tracker"
"Show me all tasks where Status is Blocked"
```

### For Data Analysts
```
"List all Feishu Bases I have access to"
"Search for Q4 revenue data in Finance Base"
"Fix the incorrect budget numbers in Marketing spreadsheet"
```

### For Knowledge Workers
```
"Find the onboarding wiki page"
"Search for documents about company policies"
"Track all documents related to the new product launch"
```

### For Developers
```
"Find the API documentation in Feishu"
"Read the technical spec document"
"Update the deployment checklist status"
```

---

## 🐛 Troubleshooting

### "Permission denied" errors
**Fix:** Add missing permissions at open.feishu.cn (see Permission Status above)

### "Document not found"
**Possible causes:**
- You don't have access to the document
- Document was deleted
- Search query too specific

**Fix:** Try broader search terms, verify access

### "Server not responding"
**Fix:**
1. Restart Claude CLI completely
2. Verify server.py exists at `feishu-mcp/server.py`
3. Check credentials are set in `.mcp.json`

### Tools not appearing in Claude
**Fix:**
1. Ensure `.mcp.json` points to correct server.py
2. Restart Claude CLI
3. Check Python dependencies: `pip install fastmcp httpx python-dotenv`

---

## 📈 Performance Tips

### Efficient Searching
```
✓ Use specific keywords: "Q4 planning"
✗ Avoid generic terms: "document"

✓ Filter by content type: content_types=["docx"]
✗ Search everything every time

✓ Set reasonable limits: limit=10
✗ Request 1000+ results
```

### Efficient Updates
```
✓ Search first to verify record exists
✗ Update without checking

✓ Update specific fields only
✗ Replace entire record

✓ Batch updates when possible
✗ Individual API calls for each record
```

---

## 📚 Additional Resources

### Documentation Files
- `QUICK_START_DOCUMENT_MANAGEMENT.md` - 15-minute setup guide
- `DOCUMENT_MANAGEMENT_SETUP.md` - Comprehensive setup
- `skills/feishu-document-manager/SKILL.md` - Detailed workflows
- `DEPLOYMENT_STATUS.md` - Current deployment status

### Test Files
- `scripts/test_feishu_enhanced.py` - Interactive test script (this guide)
- `TEST_AFTER_RESTART.md` - Quick test commands

### Feishu Resources
- [Feishu Open Platform](https://open.feishu.cn/)
- [Feishu API Docs](https://open.feishu.cn/document)
- [Permission Guide](https://open.feishu.cn/document/ukTMukTMukTM/uQjN3QjL0YzN04CN2cDN)

---

## 🎉 Success Checklist

After setup, you should be able to:

- [ ] Search for documents: `"Find documents about X in Feishu"`
- [ ] List spreadsheets: `"Show me all my Feishu Bases"`
- [ ] Read document: `"Read the content of [doc_name]"`
- [ ] Search records: `"Find records where Status is Pending"`
- [ ] Update data: `"Change X to Y in [spreadsheet]"`
- [ ] Track documents: `"Track this document for later"`

If all work, you're ready to go! 🚀

---

**Version:** 1.0.0
**Status:** Deployed and Ready
**Server:** `feishu-mcp/server.py`
**Last Updated:** January 25, 2026
