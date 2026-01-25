# Feishu Test Server - Interactive Query Interface

This interactive test script provides a **standalone interface** to query and manage your Feishu content without needing Claude Code running.

## 🎯 What Is This?

Think of this as a **command-line Feishu client** that lets you:

- Search for documents interactively
- List all your spreadsheets
- Read document content
- Verify permissions
- Test all Feishu Enhanced features

**Perfect for:**
- Testing Feishu API connectivity
- Debugging permission issues
- Quick document lookups
- Verifying data before Claude modifies it
- Learning how the Feishu API works

---

## 🚀 Quick Start

### 1. Set Up Environment

```bash
# Navigate to scripts directory
cd feishu-mcp/scripts

# Install dependencies (if not already installed)
pip install httpx python-dotenv

# Set environment variables
export FEISHU_APP_ID="cli_a85833b3fc39900e"
export FEISHU_APP_SECRET="your_secret_here"

# Or create a .env file:
echo "FEISHU_APP_ID=cli_a85833b3fc39900e" > .env
echo "FEISHU_APP_SECRET=your_secret_here" >> .env
```

### 2. Run the Test Server

```bash
python test_feishu_enhanced.py
```

### 3. Use the Interactive Menu

```
╔════════════════════════════════════════════════════════════╗
║     Feishu Enhanced MCP Server - Interactive Tester       ║
║                                                            ║
║  Test all document management features interactively      ║
╚════════════════════════════════════════════════════════════╝

Available Tests:
  1. Test Authentication
  2. Search Documents
  3. List Feishu Bases (Spreadsheets)
  4. Read a Document
  5. Check All Permissions
  6. Run All Tests
  7. Show Server Info
  0. Exit

Select option (0-7):
```

---

## 📖 Usage Examples

### Example 1: Verify Everything Works

```bash
$ python test_feishu_enhanced.py

Select option: 6  # Run All Tests

============================================================
Test 1: Authentication
============================================================
✓ Authentication successful
ℹ Token: t-g1041ol8UO4FLQ3UDKRJPQTDSOA4...

============================================================
Test 2: Document Search
============================================================
Enter search query (or press Enter for 'test'): meeting notes
✓ Found 12 documents
  1. Team Meeting Notes Jan (docx)
  2. Weekly Meeting Archive (base)
  3. Meeting Procedures (wiki)
  ...

============================================================
Test Summary
============================================================
Results: 4/4 tests passed
✓ All tests passed! Feishu Enhanced MCP is working correctly.
```

---

### Example 2: Find Specific Documents

```bash
$ python test_feishu_enhanced.py

Select option: 2  # Search Documents

============================================================
Test 2: Document Search
============================================================
Enter search query: Q4 budget
✓ Found 5 documents
  1. Q4 Budget 2024 (base)
  2. Q4_Budget_Final (docx)
  3. Q4 Financial Plan (docx)
  4. Budget Wiki Q4 (wiki)
  5. Q4 Budget Discussion (chat)
```

---

### Example 3: List All Spreadsheets

```bash
$ python test_feishu_enhanced.py

Select option: 3  # List Bases

============================================================
Test 3: List Feishu Bases
============================================================
✓ Found 8 Feishu Bases
  1. Project Tracker (token: bascnNbO5Kg...)
  2. Sales Pipeline (token: bascnXYZ123...)
  3. Task Management (token: bascnABC456...)
  ...
```

---

### Example 4: Check Permissions

```bash
$ python test_feishu_enhanced.py

Select option: 5  # Check Permissions

============================================================
Test 5: Permission Check
============================================================
✓ Drive Search: Working
✓ List Bases: Working

All permissions verified!
```

---

## 🎨 Features

### Interactive Menu System
- Easy-to-use numbered menu
- Clear visual feedback (colored output)
- Progress indicators
- Error handling and reporting

### Comprehensive Testing
- **Authentication test** - Verify credentials work
- **Search test** - Test document search across all types
- **List test** - Verify access to Feishu Bases
- **Read test** - Test document content retrieval
- **Permission test** - Check all required permissions

### Colored Output
- ✓ Green = Success
- ✗ Red = Error
- ⚠ Yellow = Warning
- ℹ Blue = Information

### Safe Operations
- Read-only by default
- Clear confirmation before any writes
- Shows preview before applying changes

---

## 🔍 What Each Test Does

### Test 1: Authentication
```python
# Verifies your Feishu credentials are correct
# Gets a tenant access token
# Checks token is valid

✓ Success → Credentials work, can proceed
✗ Failure → Check APP_ID and APP_SECRET
```

### Test 2: Search Documents
```python
# Searches across all Feishu content types
# Uses Drive API's search endpoint
# Returns top 10 results

✓ Success → drive:drive permission working
✗ Failure → Need to add drive permissions
```

### Test 3: List Bases
```python
# Lists all accessible Feishu Bases (spreadsheets)
# Uses Base API's list endpoint
# Returns Base names and tokens

✓ Success → bitable:app:readonly permission working
✗ Failure → Need to add bitable permissions
```

### Test 4: Read Document
```python
# Reads a specific Feishu Doc by ID
# Requires document_id as input
# Returns full document content

✓ Success → docx:document:readonly permission working
✗ Failure → Need to add docx permissions or invalid ID
```

### Test 5: Check Permissions
```python
# Runs minimal API calls to test each permission
# Drive search, Base list, etc.
# Reports which permissions are working

✓ All pass → Server fully configured
⚠ Some fail → Add missing permissions
```

---

## 🛠️ Advanced Usage

### Scripted Testing

Create a test script that runs automatically:

```bash
#!/bin/bash
# auto_test.sh

export FEISHU_APP_ID="cli_a85833b3fc39900e"
export FEISHU_APP_SECRET="your_secret"

# Run all tests non-interactively
python -c "
import asyncio
from test_feishu_enhanced import run_all_tests

asyncio.run(run_all_tests())
"
```

### Integration with CI/CD

Use in automated testing:

```yaml
# .github/workflows/test-feishu.yml
name: Test Feishu Integration

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Test Feishu MCP
        env:
          FEISHU_APP_ID: ${{ secrets.FEISHU_APP_ID }}
          FEISHU_APP_SECRET: ${{ secrets.FEISHU_APP_SECRET }}
        run: |
          cd feishu-mcp/scripts
          pip install httpx python-dotenv
          python test_feishu_enhanced.py
```

### Custom Queries

Modify the script to add your own tests:

```python
async def test_my_custom_query():
    """Test a specific Feishu query"""
    result = await api_call(
        "POST",
        "/drive/v1/files/search",
        json={"search_key": "my specific search", "count": 50}
    )
    # Process results...
```

---

## 📋 Troubleshooting

### Problem: "FEISHU_APP_SECRET not configured"

**Solution:**
```bash
# Set environment variable
export FEISHU_APP_SECRET="your_secret_here"

# Or create .env file
echo "FEISHU_APP_SECRET=your_secret" > .env
```

---

### Problem: "Authentication failed"

**Solutions:**
1. Verify APP_ID is correct: `cli_a85833b3fc39900e`
2. Check APP_SECRET has no extra spaces
3. Confirm app is published in Feishu console
4. Try regenerating the app secret

---

### Problem: "Permission denied (Code 99991672)"

**Solutions:**
1. Go to https://open.feishu.cn/
2. Add required permissions (see Permission Status above)
3. Create new app version
4. Publish app version
5. Wait 10 minutes for propagation

---

### Problem: "No results found"

**Possible causes:**
1. Search query too specific
2. Don't have access to matching documents
3. Documents were deleted
4. Wrong content type filter

**Fix:** Try broader search terms, check access permissions

---

## 🎓 Learning the Feishu API

This script is also a **learning tool**. By running tests and seeing the responses, you can:

1. **Understand API structure** - See how requests and responses work
2. **Learn permission scopes** - Which permissions enable which features
3. **Debug API issues** - Get detailed error messages
4. **Explore capabilities** - Discover what Feishu API can do

### Example: Learning Document Search

```bash
Select option: 2  # Search Documents
Enter search query: test

# You'll see:
# 1. How search_all_content works
# 2. What data is returned (name, type, modified date)
# 3. How results are structured
# 4. What permissions are required
```

---

## 🔗 Integration with Claude Code

This script **complements** Claude Code:

**Use Test Script For:**
- Quick verification of API connectivity
- Debugging permission issues
- Learning Feishu API structure
- Manual testing before automation

**Use Claude Code For:**
- Complex multi-step workflows
- Natural language queries
- Automated data corrections
- Intelligent document search
- Batch operations

**Together:** Perfect Feishu workflow!

---

## 📊 Comparison: Test Script vs Claude Code

| Feature | Test Script | Claude Code |
|---------|-------------|-------------|
| **Speed** | Instant | Fast |
| **Ease of use** | Technical | Natural language |
| **Flexibility** | Structured tests | Any query |
| **Debugging** | Excellent | Good |
| **Automation** | Manual | Intelligent |
| **Learning** | Great for learning API | Great for productivity |

**Recommendation:** Use test script for setup/debugging, Claude Code for daily work

---

## 🎯 Summary

**test_feishu_enhanced.py** is your **standalone Feishu query interface**:

✅ Test all features interactively
✅ Verify permissions before using Claude
✅ Debug API issues quickly
✅ Learn Feishu API structure
✅ Quick document lookups
✅ No Claude Code required

**Just run it:**
```bash
python test_feishu_enhanced.py
```

And you have a full Feishu query interface at your fingertips!

---

**Created:** January 25, 2026
**Purpose:** Standalone testing and learning tool for Feishu Enhanced MCP
**Dependencies:** httpx, python-dotenv
**Tested:** ✅ Working with Feishu API v3
