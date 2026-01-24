# Feishu Document Management Setup Guide

This guide explains how to enable comprehensive document finding, tracking, and modification across all Feishu content types.

## Problem Statement

**Issue**: Claude can't help find important documents in Feishu, even when they exist.

**Root Cause**: The current Feishu integration only supports:
- ✅ Sending messages to chats
- ✅ Listing chats
- ❌ **NOT** searching documents
- ❌ **NOT** accessing Feishu Docs (rich documents)
- ❌ **NOT** modifying Feishu Bases (spreadsheets/databases)
- ❌ **NOT** searching wikis
- ❌ **NOT** tracking document status

## Solution Overview

Enable Claude to:
1. **Find documents** across all Feishu systems
2. **Read and modify** Feishu Docs
3. **Query and update** Feishu Bases (spreadsheets)
4. **Search** Feishu Wikis
5. **Track** important documents and their status
6. **Fix incorrect data** in any Feishu content

## Setup Steps

### Step 1: Add Required Permissions to Feishu App

Go to [Feishu Open Platform](https://open.feishu.cn/) → Your App → Permissions

#### Required Permissions for Document Access:

**Drive (File System)**:
- `drive:drive` - Full drive access
- `drive:drive:readonly` - Read-only drive access

**Docs (Documents)**:
- `docx:document` - Modify documents
- `docx:document:readonly` - Read documents

**Base (Spreadsheets/Databases)**:
- `bitable:app` - Modify bases
- `bitable:app:readonly` - Read bases

**Wiki (Knowledge Base)**:
- `wiki:wiki` - Modify wikis
- `wiki:wiki:readonly` - Read wikis

**Messages (for reference)**:
- `im:message` - Already enabled
- `im:chat` - Already enabled

#### How to Add Permissions:

1. Navigate to "Permissions & Scopes"
2. Find each permission listed above
3. Click "Apply" next to each permission
4. Create a new app version after adding all permissions
5. Publish the new version
6. Wait 5-10 minutes for permissions to propagate

### Step 2: Replace MCP Server

#### Option A: Use Enhanced Server (Recommended)

1. **Copy enhanced server to feishu-ultimate location**:
   ```bash
   cp feishu-mcp/scripts/enhanced_feishu_server.py C:/Users/eng20/feishu-ultimate-mcp/server_enhanced.py
   ```

2. **Update Claude Desktop config** (`$APPDATA/Claude/claude_desktop_config.json`):
   ```json
   {
     "mcpServers": {
       "feishu-ultimate": {
         "command": "python",
         "args": ["C:\\Users\\eng20\\feishu-ultimate-mcp\\server_enhanced.py"],
         "env": {
           "FEISHU_APP_ID": "cli_a85833b3fc39900e",
           "FEISHU_APP_SECRET": "your-secret-here"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop/CLI** to load new server

#### Option B: Add Tools to Existing Server

Alternatively, add the new tools to your existing `server.py` by copying the functions from `enhanced_feishu_server.py`.

### Step 3: Test Enhanced Features

#### Test 1: Search Documents

```python
# In Claude, ask:
"Search for documents with 'quarterly report' in Feishu"

# This will call: search_all_content(query="quarterly report")
```

#### Test 2: List Bases

```python
# In Claude, ask:
"Show me all the spreadsheets in Feishu"

# This will call: list_bases()
```

#### Test 3: Search Base Records

```python
# In Claude, ask:
"Find all records in the Sales Tracker where Status is 'Pending'"

# This will call: search_base_records(
#     app_token="base_token",
#     table_id="table_id",
#     field_name="Status",
#     search_value="Pending"
# )
```

### Step 4: Set Up Document Tracking System

#### Create Tracking Base

1. Go to Feishu and create a new Base (spreadsheet)
2. Name it "Document Tracking System"
3. Add these columns:
   - **Document Name** (Text)
   - **Type** (Single Select: Doc, Base, Wiki, Chat)
   - **URL/ID** (URL)
   - **Status** (Single Select: Found, Needs Review, Updated, Verified)
   - **Last Updated** (Date)
   - **Owner** (Person)
   - **Priority** (Single Select: High, Medium, Low)
   - **Notes** (Text/Multi-line)

4. Get the Base token and Table ID:
   - Base token: From URL `https://example.feishu.cn/base/xxxxx` → `xxxxx` is token
   - Table ID: From URL or API

5. Add to environment variables:
   ```bash
   # In .env file or environment:
   TRACKING_BASE_TOKEN=your_base_token
   TRACKING_TABLE_ID=your_table_id
   ```

#### Use Tracking System

```python
# Track a document:
track_document(
    document_name="Q4 Planning Doc",
    document_type="Doc",
    document_url="https://feishu.cn/docx/xxx",
    status="Found",
    priority="High",
    notes="Located after search"
)
```

## Usage Examples

### Example 1: Find Lost Document

**User**: "I can't find the engineering roadmap document"

**Claude Process**:
1. Uses `search_all_content(query="engineering roadmap")`
2. Returns list of matching documents with types and locations
3. User selects correct one
4. Claude retrieves and displays summary
5. Optionally tracks in tracking system

### Example 2: Fix Data in Spreadsheet

**User**: "The budget numbers in Q4 finances spreadsheet are wrong for Marketing department"

**Claude Process**:
1. Uses `list_bases()` to find "Q4 finances" base
2. Uses `search_base_records()` to find Marketing department rows
3. Shows current values
4. User provides correct values
5. Uses `update_base_record()` to fix data
6. Verifies update was successful
7. Tracks change in tracking system

### Example 3: Read and Modify Document

**User**: "Update the status in the project proposal doc to 'Approved'"

**Claude Process**:
1. Uses `search_all_content(query="project proposal")`
2. Identifies document
3. Uses `read_document()` to get content
4. Finds status block
5. Uses `update_document_block()` to change status
6. Confirms update
7. Tracks in tracking system

### Example 4: Search Across All Content

**User**: "Find all mentions of 'Q4 budget' across everything"

**Claude Process**:
1. Uses `search_all_content(query="Q4 budget")`
2. Searches across:
   - Feishu Docs
   - Feishu Bases
   - Wikis
   - Chat messages (if integrated)
3. Returns unified results with types and locations
4. User can drill down into specific items

## Available MCP Tools

After setup, Claude has access to these new tools:

### Discovery & Search
- `search_all_content()` - Search across all Feishu content
- `search_wiki()` - Search wiki pages
- `search_base_records()` - Search within a Base table

### Documents (Feishu Docs)
- `read_document()` - Read document content
- `update_document_block()` - Update specific text blocks

### Bases (Spreadsheets)
- `list_bases()` - List all bases
- `search_base_records()` - Find records matching criteria
- `update_base_record()` - Update existing record
- `create_base_record()` - Create new record

### Wiki
- `read_wiki_page()` - Read wiki page content

### Tracking
- `track_document()` - Add document to tracking system

### Testing
- `test_enhanced_connection()` - Verify permissions and access

## Troubleshooting

### "Permission denied" errors

**Problem**: API returns code 99991668 or 20027

**Solution**:
1. Go to Feishu developer console
2. Verify all required permissions are added
3. Create new app version
4. Publish the version
5. Wait 5-10 minutes
6. Restart Claude

### "Can't find document" even after search

**Problem**: Search returns empty results

**Solutions**:
1. Check if user has access to the document/space
2. Try broader search terms
3. Verify document hasn't been deleted
4. Check if document is in a restricted space

### "Document found but can't read"

**Problem**: Document appears in search but can't be opened

**Solutions**:
1. Use user token instead of tenant token (OAuth)
2. Check document permissions
3. Ask document owner to grant access

### "Base operations fail"

**Problem**: Can't list or search bases

**Solutions**:
1. Verify `bitable:app:readonly` permission is enabled
2. Check if user is added to the base
3. Wait for permission propagation (up to 10 minutes)

## Advanced Configuration

### Use User Token for More Access

User tokens provide access to more content than tenant tokens.

1. Set up OAuth flow (see feishu-mcp README)
2. Store user token in user_token.json
3. Server will automatically use it when available

### Set Up Webhooks for Real-Time Tracking

To automatically track document changes:

1. Enable webhooks in Feishu app
2. Set up endpoint to receive events
3. Update tracking base on document changes

### Optimize Search Performance

For large organizations:

1. Use specific content_type filters
2. Limit search by date ranges
3. Cache frequently accessed documents
4. Use base-specific searches when possible

## API Rate Limits

Be aware of Feishu API rate limits:

- **Search**: 100 requests/minute
- **Read operations**: 200 requests/minute
- **Write operations**: 100 requests/minute

Claude will automatically handle rate limiting and retry failed requests.

## Security Notes

1. **Never commit credentials** to git
2. **Use environment variables** for sensitive data
3. **Limit permissions** to only what's needed
4. **Audit tracked changes** regularly
5. **Review tracking base** permissions

## Next Steps

After setup:

1. Test each feature with simple examples
2. Create your tracking base
3. Set up common search queries
4. Document your team's document organization
5. Train team on using Claude for document management

## Support

If you encounter issues:

1. Check Feishu API documentation: https://open.feishu.cn/document
2. Review server logs for error details
3. Test permissions with Feishu API Explorer
4. Ask in Feishu developer community

---

**Last Updated**: 2024-01-22
**Version**: 1.0.0
**Author**: Claude AI (Sonnet 4.5)
