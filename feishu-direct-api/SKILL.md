---
name: feishu-direct-api
description: This skill should be used when you need to search, read, modify, or manage Feishu (Lark) documents, bases, wikis, and chats using direct API calls without requiring MCP server setup.
---

# Feishu Direct API Access

This skill provides immediate access to Feishu (Lark) APIs for document management, base operations, wiki access, and chat management without requiring MCP server configuration.

## When to Use This Skill

Use this skill when the user needs to:
- Search for documents, wikis, bases, or chats across their Feishu workspace
- Find specific content within documents
- Read or retrieve document content
- Update or modify document blocks
- Work with Feishu Bases (spreadsheets) - list, search, create, or update records
- Access wiki pages and content
- Fix incorrect data in Feishu resources
- Track and manage documents across their workspace

## Feishu API Credentials

The following credentials are configured for this workspace:

```
FEISHU_APP_ID: cli_a85833b3fc39900e
FEISHU_APP_SECRET: fiFRoqlAFX7ASY9iUt7Evb2aUx6Qurkd
```

**IMPORTANT**: If you encounter error `99991663: Invalid access token`, the Feishu app needs permissions configured. See `../feishu-mcp/FEISHU_APP_SETUP.md` for detailed setup instructions.

## Authentication Flow

To make any Feishu API calls, first obtain an access token:

```bash
curl -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d '{
    "app_id": "cli_a85833b3fc39900e",
    "app_secret": "fiFRoqlAFX7ASY9iUt7Evb2aUx6Qurkd"
  }'
```

Response contains `tenant_access_token` which should be used in subsequent API calls.

## Core Operations

### 1. Search All Content

Search across documents, wikis, bases, and chats:

```bash
TOKEN="<tenant_access_token>"

curl -X POST 'https://open.feishu.cn/open-apis/search/v2/message' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "search keywords",
    "page_size": 20
  }'
```

### 2. Search Documents Specifically

```bash
curl -X POST 'https://open.feishu.cn/open-apis/drive/v1/files/search' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "search_key": "document name or content",
    "owner_ids": [],
    "page_size": 50
  }'
```

### 3. Read Document Content

First get document token from search results, then:

```bash
DOC_TOKEN="<document_token>"

curl -X GET "https://open.feishu.cn/open-apis/docx/v1/documents/$DOC_TOKEN/blocks" \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Update Document Block

```bash
BLOCK_ID="<block_id>"

curl -X PATCH "https://open.feishu.cn/open-apis/docx/v1/documents/$DOC_TOKEN/blocks/$BLOCK_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "update_text_elements": {
      "elements": [
        {
          "text_run": {
            "content": "Updated text content"
          }
        }
      ]
    }
  }'
```

### 5. List Bases (Spreadsheets)

```bash
curl -X GET 'https://open.feishu.cn/open-apis/bitable/v1/apps' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json'
```

### 6. Search Base Records

```bash
APP_TOKEN="<base_app_token>"
TABLE_ID="<table_id>"

curl -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/$APP_TOKEN/tables/$TABLE_ID/records/search" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "filter": {
      "conjunction": "and",
      "conditions": [
        {
          "field_name": "column_name",
          "operator": "contains",
          "value": ["search_value"]
        }
      ]
    }
  }'
```

### 7. Update Base Record

```bash
RECORD_ID="<record_id>"

curl -X PUT "https://open.feishu.cn/open-apis/bitable/v1/apps/$APP_TOKEN/tables/$TABLE_ID/records/$RECORD_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "fields": {
      "column_name": "new value"
    }
  }'
```

### 8. Create Base Record

```bash
curl -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/$APP_TOKEN/tables/$TABLE_ID/records" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "fields": {
      "column1": "value1",
      "column2": "value2"
    }
  }'
```

### 9. Search Wiki

```bash
curl -X POST 'https://open.feishu.cn/open-apis/wiki/v2/spaces/query' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json'
```

### 10. Read Wiki Page

```bash
NODE_TOKEN="<wiki_node_token>"

curl -X GET "https://open.feishu.cn/open-apis/wiki/v2/spaces/<space_id>/nodes/$NODE_TOKEN" \
  -H "Authorization: Bearer $TOKEN"
```

## Workflow Pattern

When the user asks to find or modify content:

1. **Get Access Token**: Always start by obtaining a fresh tenant_access_token
2. **Search Broadly**: Use document search or general search to find the resource
3. **Retrieve Details**: Get the specific document/base/wiki content
4. **Identify Issue**: If fixing incorrect data, identify the specific field/block
5. **Update Content**: Use appropriate update endpoint
6. **Verify**: Confirm the update was successful

## Common Tasks

### Task: Find a Document

```bash
# Step 1: Get token
TOKEN=$(curl -s -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d '{"app_id":"cli_a85833b3fc39900e","app_secret":"fiFRoqlAFX7ASY9iUt7Evb2aUx6Qurkd"}' | grep -o '"tenant_access_token":"[^"]*"' | cut -d'"' -f4)

# Step 2: Search for document
curl -X POST 'https://open.feishu.cn/open-apis/drive/v1/files/search' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"search_key":"keywords from user query","page_size":50}'
```

### Task: Fix Incorrect Data in Base

```bash
# Step 1: Get token (as above)

# Step 2: Search base records for incorrect data
curl -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/$APP_TOKEN/tables/$TABLE_ID/records/search" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"filter":{"conjunction":"and","conditions":[{"field_name":"field","operator":"is","value":["old_value"]}]}}'

# Step 3: Update with correct data
curl -X PUT "https://open.feishu.cn/open-apis/bitable/v1/apps/$APP_TOKEN/tables/$TABLE_ID/records/$RECORD_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"fields":{"field_name":"correct_value"}}'
```

## Important Notes

- Token expires after 2 hours, obtain fresh token for each operation sequence
- Document tokens, base tokens, and record IDs are returned from search operations
- Always verify resource type (doc/base/wiki) before attempting operations
- Use page_size parameter to control result limits (max 50 for most endpoints)
- For large documents, blocks API returns paginated results

## Error Handling

Common error codes:
- `99991401`: Token expired, obtain new token
- `99991400`: Invalid token format
- `230001`: Insufficient permissions, check app scopes
- `230002`: Resource not found, verify token/ID

## Best Practices

1. **Always start with search**: Don't assume document locations
2. **Verify before updating**: Read current content before modifications
3. **Use specific searches**: Include context keywords for better results
4. **Batch operations**: Group multiple updates when possible
5. **Handle pagination**: Large result sets require multiple API calls

## API Reference

Full Feishu API documentation: https://open.feishu.cn/document/home/index

Key endpoints used:
- Authentication: `/open-apis/auth/v3/tenant_access_token/internal`
- File search: `/open-apis/drive/v1/files/search`
- Document blocks: `/open-apis/docx/v1/documents/{document_id}/blocks`
- Base operations: `/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records`
- Wiki spaces: `/open-apis/wiki/v2/spaces`
