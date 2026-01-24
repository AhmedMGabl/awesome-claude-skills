---
name: Feishu Document Manager
description: This skill should be used when the user needs to find, read, modify, or manage Feishu documents (Docs), spreadsheets (Bases), wikis, and chat messages. Enables comprehensive document tracking, search, and data correction across all Feishu content types.
version: 1.0.0
---

# Feishu Document Manager

Comprehensive management of all Feishu content: documents, spreadsheets (Bases), wikis, and chat messages. This skill enables finding important documents, tracking changes, and fixing incorrect data across all Feishu systems.

## Overview

This skill provides:
1. **Document Discovery** - Find documents across all Feishu spaces
2. **Content Access** - Read and modify Feishu Docs, Bases, and Wikis
3. **Data Management** - Fix incorrect data in spreadsheets and documents
4. **Chat Integration** - Search and reference chat conversations
5. **Tracking System** - Keep track of important documents and their status

## When to Use This Skill

Use this skill when the user:
- Can't find an important document in Feishu
- Needs to modify content in Feishu Docs or Bases
- Wants to fix incorrect data in Feishu spreadsheets
- Needs to track document status and changes
- Wants to search across all Feishu content types
- Needs to correlate information from chats, docs, and bases

## Content Types Supported

### 1. Feishu Docs (Documents)
- **Purpose**: Rich text documents with formatting, images, tables
- **API**: `/docx/v1/documents`
- **Operations**: Create, read, update, search
- **Use for**: Meeting notes, proposals, specifications, reports

### 2. Feishu Bases (Spreadsheets/Databases)
- **Purpose**: Structured data in tables with formulas
- **API**: `/bitable/v1/apps`
- **Operations**: Query, insert, update, delete records
- **Use for**: Data tracking, project management, CRM, inventory

### 3. Feishu Wikis (Knowledge Base)
- **Purpose**: Hierarchical knowledge organization
- **API**: `/wiki/v2/spaces`
- **Operations**: Browse, read, create pages
- **Use for**: Company knowledge, documentation, procedures

### 4. Feishu Chats (Messages)
- **Purpose**: Conversations and file sharing
- **API**: `/im/v1/messages`
- **Operations**: Search, read, send
- **Use for**: Communication history, shared files, decisions

## Document Discovery Workflow

When user says they can't find a document:

### Step 1: Gather Information
Ask the user:
- What type of content? (doc, spreadsheet, wiki, chat)
- What's the topic or keywords?
- Who created it or who's involved?
- Approximate date or time period?
- What space or chat it might be in?

### Step 2: Multi-Source Search

**For Documents**:
```python
# Search across all Feishu Docs
# API: POST /drive/v1/files/search
{
  "search_key": "keyword",
  "owner_ids": ["user_id"],
  "chat_ids": ["chat_id"]
}
```

**For Bases (Spreadsheets)**:
```python
# List all bases user has access to
# API: GET /bitable/v1/apps
# Then search within each base:
# API: POST /bitable/v1/apps/{app_token}/tables/{table_id}/records/search
{
  "filter": {
    "conditions": [
      {
        "field_name": "column_name",
        "operator": "contains",
        "value": ["keyword"]
      }
    ]
  }
}
```

**For Wikis**:
```python
# Search wiki spaces
# API: POST /wiki/v2/nodes/search
{
  "query": "keyword",
  "space_id": "space_id"
}
```

**For Chats**:
```python
# Search messages
# API: POST /im/v1/messages/search
{
  "query": "keyword",
  "chat_id": "optional_chat_id"
}
```

### Step 3: Present Results
Show results organized by:
- **Relevance score** (how well it matches search)
- **Content type** (doc, base, wiki, chat)
- **Last modified date**
- **Owner/creator**
- **Location** (space, folder, chat)

### Step 4: Access and Verify
Once document is found:
1. Retrieve full content
2. Confirm it's the correct document
3. Ask if modifications are needed

## Content Modification Workflow

### Modifying Feishu Docs

**Read Document**:
```python
# Get document content
# API: GET /docx/v1/documents/{document_id}/raw_content
```

**Update Document**:
```python
# Update specific blocks
# API: PATCH /docx/v1/documents/{document_id}/blocks/{block_id}
{
  "block_type": "text",
  "text": {
    "elements": [
      {
        "text_run": {
          "content": "New content"
        }
      }
    ]
  }
}
```

### Modifying Feishu Bases

**Read Records**:
```python
# Get records from table
# API: POST /bitable/v1/apps/{app_token}/tables/{table_id}/records/search
```

**Update Records**:
```python
# Update specific records
# API: PUT /bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_update
{
  "records": [
    {
      "record_id": "record_id",
      "fields": {
        "field_name": "new_value"
      }
    }
  ]
}
```

**Insert Records**:
```python
# Add new records
# API: POST /bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create
{
  "records": [
    {
      "fields": {
        "field_name": "value"
      }
    }
  ]
}
```

### Modifying Wiki Pages

**Read Page**:
```python
# Get wiki page content
# API: GET /wiki/v2/spaces/{space_id}/nodes/{node_token}
```

**Update Page**:
```python
# Update wiki page title or content
# API: PUT /wiki/v2/spaces/{space_id}/nodes/{node_token}
```

## Data Correction Workflow

When fixing incorrect data:

### Step 1: Identify Error
1. Find the document/base with incorrect data
2. Locate specific field or cell
3. Verify current incorrect value

### Step 2: Determine Correct Value
1. Ask user for correct value
2. Or reference from another source
3. Validate data format/type

### Step 3: Apply Correction
1. Use appropriate update API
2. Verify update was successful
3. Document the change (optional logging)

### Step 4: Cross-Reference Check
After correction:
1. Check if same data appears elsewhere
2. Update all instances if needed
3. Prevent future inconsistencies

## Document Tracking System

To keep track of important documents:

### Create Tracking Base

Create a Feishu Base with columns:
- **Document Name** (text)
- **Type** (single_select: Doc, Base, Wiki, Chat)
- **URL/ID** (URL)
- **Status** (single_select: Found, Needs Review, Updated, Verified)
- **Last Updated** (date)
- **Owner** (person)
- **Priority** (single_select: High, Medium, Low)
- **Notes** (text)

### Auto-Track Documents

When a document is found or modified:
```python
# Add to tracking base
# API: POST /bitable/v1/apps/{tracking_base_token}/tables/{table_id}/records/batch_create
{
  "records": [
    {
      "fields": {
        "Document Name": "Document title",
        "Type": "Doc",
        "URL/ID": "document_url",
        "Status": "Found",
        "Last Updated": "2024-01-22",
        "Priority": "High",
        "Notes": "Auto-tracked by Claude"
      }
    }
  ]
}
```

## API Reference

### Document Search
- **Endpoint**: `POST /drive/v1/files/search`
- **Permission**: `drive:drive:readonly`
- **Returns**: List of files matching search

### Base Operations
- **List Bases**: `GET /bitable/v1/apps`
- **Search Records**: `POST /bitable/v1/apps/{app_token}/tables/{table_id}/records/search`
- **Update Records**: `PUT /bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_update`
- **Permission**: `bitable:app`, `bitable:app:readonly`

### Wiki Operations
- **Search Wiki**: `POST /wiki/v2/nodes/search`
- **Get Node**: `GET /wiki/v2/spaces/{space_id}/nodes/{node_token}`
- **Permission**: `wiki:wiki:readonly`

### Document Operations
- **Get Content**: `GET /docx/v1/documents/{document_id}/raw_content`
- **Update Block**: `PATCH /docx/v1/documents/{document_id}/blocks/{block_id}`
- **Permission**: `docx:document`, `docx:document:readonly`

## Permission Requirements

Add these to your Feishu app:

**Tenant Token Permissions**:
- `drive:drive:readonly` - Search and list files
- `bitable:app:readonly` - Read bases
- `bitable:app` - Modify bases
- `wiki:wiki:readonly` - Read wikis
- `docx:document:readonly` - Read documents
- `docx:document` - Modify documents

**User Token Permissions (OAuth)**:
- `drive:drive` - Full drive access
- `bitable` - Full base access
- `wiki` - Full wiki access
- `docx` - Full document access

## Examples

### Example 1: Find Lost Meeting Notes

**User**: "I can't find the meeting notes from last week's planning session"

**Claude**:
1. Search Feishu Docs for "planning" in last 7 days
2. Filter by meeting notes or documents with "notes" in title
3. Present top 5 results with dates and owners
4. User selects correct document
5. Retrieve and display summary

### Example 2: Fix Incorrect Data in Spreadsheet

**User**: "The Q4 revenue numbers in our sales tracker are wrong"

**Claude**:
1. Search for Feishu Bases with "sales tracker" in name
2. Find the Q4 revenue column
3. Show current values
4. Ask user for correct values
5. Update records with correct data
6. Verify update was successful

### Example 3: Track Important Documents

**User**: "Keep track of all documents related to the new product launch"

**Claude**:
1. Create/access tracking base
2. Search for documents with "product launch" keywords
3. Add each document to tracking base
4. Set up monitoring for changes
5. Provide dashboard URL for tracking

## Error Handling

### Document Not Found
If search returns no results:
1. Try broader search terms
2. Search across different content types
3. Check if user has access permissions
4. Suggest asking colleagues who might know location

### Permission Denied
If API returns permission error:
1. Check required permissions in app console
2. Re-authenticate if using user token
3. Request admin to grant permissions
4. Provide alternative manual access method

### Data Conflicts
If updating creates conflicts:
1. Show current value vs. new value
2. Ask user to confirm changes
3. Create backup/version before update
4. Log change for audit trail

## Best Practices

1. **Always Verify Before Modifying**
   - Show current data before changes
   - Get user confirmation
   - Make backups when possible

2. **Use Structured Search**
   - Start specific, broaden if needed
   - Filter by date ranges
   - Filter by creator/owner

3. **Track Changes**
   - Log all modifications
   - Keep audit trail in tracking base
   - Note who requested changes

4. **Cross-Reference Data**
   - Check for duplicate data
   - Update all instances
   - Prevent future inconsistencies

5. **Performance Optimization**
   - Cache frequently accessed documents
   - Use batch operations for multiple updates
   - Limit search results to reasonable number

## Troubleshooting

### "Can't find document" Issues
- Check user permissions on spaces/folders
- Search in different time ranges
- Try alternative keywords
- Check if document was deleted

### "Can't modify" Issues
- Verify write permissions
- Check if document is locked
- Ensure user is owner or has edit rights
- Try user token instead of tenant token

### "Data not updating" Issues
- Verify field names match exactly
- Check data type compatibility
- Ensure record IDs are correct
- Wait for API propagation (up to 1 min)

## Notes

- All operations use Feishu Open Platform APIs
- Requires proper app permissions configured
- User tokens provide more access than tenant tokens
- Some operations require admin approval
- Rate limits apply (check API docs for details)

---

**Version**: 1.0.0
**Last Updated**: 2024-01-22
**Requires**: feishu-ultimate MCP server with extended permissions
