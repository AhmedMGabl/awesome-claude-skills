# How to Use Feishu Enhanced MCP

**Simple Guide**: Everything you need to know to use Feishu with Claude

---

## 🎯 Two Ways to Use Feishu

### Method 1: Through Claude Code (Recommended)

**Best for:** Natural language queries, complex workflows, automation

**How to use:**

Just ask Claude anything about Feishu:

```
"Find the Q4 budget document in Feishu"
"Show me all spreadsheets about sales"
"Fix the revenue number in Marketing spreadsheet"
"Read the engineering roadmap document"
```

Claude will automatically use the enhanced MCP server to:
1. Search for what you need
2. Read the content
3. Make changes if requested
4. Track important documents

---

### Method 2: Direct Test Script (For Testing/Debugging)

**Best for:** Quick tests, debugging, learning the API

**How to use:**

```bash
cd feishu-mcp/scripts
python test_feishu_enhanced.py
```

Then select from menu:
- Search documents
- List spreadsheets
- Read content
- Check permissions

See `README_TEST_SERVER.md` for full guide.

---

## 📚 What Can You Do?

### Find Documents
```
"I can't find the project proposal"
"Search for documents about customer feedback"
"Find all spreadsheets related to Q4"
```

### Read Content
```
"What does the roadmap document say?"
"Show me the data in Sales Tracker spreadsheet"
"Read the deployment wiki page"
```

### Modify Data
```
"Update the status to 'Approved' in the proposal"
"Fix the revenue number in Q4 Budget"
"Change all 'Pending' tasks to 'In Progress'"
```

### Track Documents
```
"Track all documents related to product launch"
"Keep track of this important document"
"Show me my tracked documents"
```

---

## 🎓 Learning Path

### Day 1: Setup and Testing
1. Restart Claude Code
2. Run: `"Test Feishu connection"`
3. Try: `"Search for documents in Feishu"`
4. Verify tools are working

### Day 2: Add Permissions (Optional)
1. Go to https://open.feishu.cn/
2. Add 8 document management permissions
3. Wait 10 minutes
4. Test: `"List all my Feishu spreadsheets"`

### Day 3: Real Usage
1. Find a document you need
2. Read its content through Claude
3. Make a data correction if needed
4. Track important documents

---

## 🗂️ Documentation Map

### Quick References
- **This file** - How to use overview
- `FEISHU_ENHANCED_GUIDE.md` - Visual usage guide with examples
- `TEST_AFTER_RESTART.md` - Quick test commands

### Setup Guides
- `QUICK_START_DOCUMENT_MANAGEMENT.md` - 15-minute setup
- `DOCUMENT_MANAGEMENT_SETUP.md` - Comprehensive setup

### Technical Details
- `skills/feishu-document-manager/SKILL.md` - Detailed workflows for Claude
- `scripts/README_TEST_SERVER.md` - Test script documentation
- `DEPLOYMENT_STATUS.md` - Current deployment status

### Status Files
- `ITERATION_2_SUMMARY.md` - What was built in Iteration 2

---

## 🎯 Common Workflows

### Workflow 1: Find and Read

```
You: "Find the engineering roadmap"
     ↓
Claude searches across all Feishu
     ↓
Claude shows results (3 documents found)
     ↓
You: "Read the second one"
     ↓
Claude reads and displays content
     ↓
Done! ✓
```

---

### Workflow 2: Find and Fix Data

```
You: "The budget number for Marketing is wrong"
     ↓
Claude: "Which spreadsheet?"
     ↓
You: "Q4 Budget spreadsheet"
     ↓
Claude finds spreadsheet, shows current value
     ↓
Claude: "What should it be?"
     ↓
You: "$750,000"
     ↓
Claude updates the record
     ↓
Claude: "Updated successfully! Changed from $500k to $750k"
     ↓
Done! ✓
```

---

### Workflow 3: Search and Track

```
You: "Find all documents about product launch"
     ↓
Claude searches across Docs, Bases, Wikis
     ↓
Claude shows 12 results
     ↓
You: "Track the top 5"
     ↓
Claude tracks each document with metadata
     ↓
Claude: "Tracked 5 documents. Total tracked: 5"
     ↓
Done! ✓
```

---

## 🚦 Feature Status

| Feature | Status | Required Permission |
|---------|--------|---------------------|
| **Search Documents** | 🟡 Needs permission | `drive:drive` |
| **List Bases** | 🟡 Needs permission | `bitable:app:readonly` |
| **Read Documents** | 🟡 Needs permission | `docx:document:readonly` |
| **Modify Docs** | 🟡 Needs permission | `docx:document` |
| **Modify Bases** | 🟡 Needs permission | `bitable:app` |
| **Search Wikis** | 🟡 Needs permission | `wiki:wiki:readonly` |
| **Send Messages** | ✅ Working | `im:message` (already added) |
| **List Chats** | ✅ Working | `im:chat` (already added) |

**Legend:**
- ✅ Working now
- 🟡 Works after adding permission
- ❌ Not available

---

## 🎯 Next Steps

### If You Just Want to Try It

```
1. Restart Claude Code
2. Ask: "Search for documents in Feishu"
3. See what happens
```

### If You Want Full Features

```
1. Add permissions at open.feishu.cn (10 minutes)
2. Restart Claude Code
3. Ask: "List all my Feishu spreadsheets"
4. Enjoy full document management! 🎉
```

### If You Want to Debug Issues

```
1. Run test script: python test_feishu_enhanced.py
2. Select option 6: Run All Tests
3. Check which tests fail
4. Add missing permissions
5. Re-test until all pass
```

---

## 💡 Pro Tips

### Tip 1: Be Specific in Searches
```
✓ Good: "Q4 budget spreadsheet"
✗ Bad: "spreadsheet"

✓ Good: "engineering roadmap document"
✗ Bad: "document"
```

### Tip 2: Use the Test Script First
```
Before asking Claude to modify data:
1. Use test script to find the document
2. Verify you have access
3. Note the document ID
4. Then ask Claude to make changes
```

### Tip 3: Track Important Documents
```
Once you find a critical document:
"Track this document for future access"

Then later:
"Show me my tracked documents about Q4"
```

### Tip 4: Verify Before Modifying
```
Always have Claude show current value first:
"What's the current revenue for Marketing in Q4 Budget?"

Then modify:
"Change it to $750,000"
```

---

## 🎉 You're Ready!

Everything you need is set up. Choose your path:

**Path A - Quick Test (2 minutes)**
1. Restart Claude
2. Ask: `"Test Feishu connection"`
3. Done!

**Path B - Full Setup (15 minutes)**
1. Add permissions at open.feishu.cn
2. Restart Claude
3. Ask: `"List all my Feishu spreadsheets"`
4. Done!

**Path C - Testing (5 minutes)**
1. Run: `python test_feishu_enhanced.py`
2. Select: Option 6 (Run All Tests)
3. Done!

---

## 📞 Need Help?

### Quick Troubleshooting
- **Can't find document** → Try broader search, check access
- **Permission denied** → Add permissions at open.feishu.cn
- **Server not loading** → Restart Claude completely
- **Script won't run** → Install: `pip install httpx python-dotenv`

### Read These Docs
- Quick issues → `FEISHU_ENHANCED_GUIDE.md`
- Setup help → `QUICK_START_DOCUMENT_MANAGEMENT.md`
- Deep dive → `DOCUMENT_MANAGEMENT_SETUP.md`
- Script help → `scripts/README_TEST_SERVER.md`

---

**You have everything you need. Just restart Claude and start using it!** 🚀

---

**Version:** 1.0.0
**Created:** January 25, 2026
**Status:** Ready to Use
