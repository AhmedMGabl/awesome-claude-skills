# Feishu App Configuration Guide

## Problem

The Feishu MCP server and Direct API skill require specific OAuth scopes/permissions to access documents, bases, wikis, and chats. Without proper permissions, API calls fail with error `99991663: Invalid access token for authorization`.

## Solution: Configure App Permissions

### Step 1: Access Feishu Admin Console

1. Go to https://open.feishu.cn/app
2. Log in with your Feishu account
3. Find your app: `cli_a85833b3fc39900e`

### Step 2: Configure Required Permissions

Navigate to **Permissions & Scopes** section and enable the following:

#### Document Access (Required for document search/modify)

- `drive:drive` - Access drive files
- `docx:document` - Read and write documents
- `docx:document.readonly` - Read documents (if write not needed)
- `drive:file` - File operations

#### Base (Spreadsheet) Operations

- `bitable:app` - Access base applications
- `bitable:app.readonly` - Read base applications
- `bitable:table` - Table operations
- `bitable:record` - Record CRUD operations

#### Wiki Access

- `wiki:wiki` - Access wiki spaces
- `wiki:wiki.readonly` - Read wiki content

#### Search Capabilities

- `search:message` - Search across all content
- `search:file` - File-specific search

#### Chat/Message Access (Optional)

- `im:message` - Send and read messages
- `im:chat` - Chat operations

### Step 3: Request Admin Approval

After selecting permissions:

1. Click **Apply for Permissions**
2. Provide justification: "Enable Claude AI integration for document management"
3. Wait for admin approval (can take 1-24 hours depending on your org)

### Step 4: Verify Permissions

Once approved, test with this command:

```bash
# Get access token
TOKEN=$(curl -s -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d '{"app_id":"cli_a85833b3fc39900e","app_secret":"fiFRoqlAFX7ASY9iUt7Evb2aUx6Qurkd"}' \
  | grep -o '"tenant_access_token":"[^"]*"' | cut -d'"' -f4)

# Test document search
curl -X POST 'https://open.feishu.cn/open-apis/drive/v1/files/search' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"page_size":10}'
```

If you get results instead of error 99991663, permissions are configured correctly.

### Step 5: Restart Claude Code (for MCP Server)

After permissions are approved:

1. Close Claude Code completely
2. Reopen Claude Code
3. Navigate to project directory
4. Verify MCP server loaded:

```bash
# This should show feishu tools available
/tools
```

## Alternative: Create New App with Correct Permissions

If you can't modify existing app permissions:

### Option A: Create New Self-Built App

1. Go to https://open.feishu.cn/app
2. Click **Create custom app**
3. Choose **Self-built app**
4. Fill in details:
   - **App Name**: Claude AI Integration
   - **Description**: Document management for Claude Code
   - **Icon**: Upload an icon (optional)

5. Configure permissions (all scopes listed above)
6. Get credentials from **Credentials & Basic Info**:
   - App ID
   - App Secret

7. Update `.mcp.json` and skill files with new credentials

### Option B: Use User Access Token (More Permissions)

Instead of tenant_access_token, use user_access_token flow:

1. In Feishu app console, enable **User OAuth**
2. Set redirect URI: `http://localhost:8080/callback`
3. Run OAuth flow to get user token
4. Modify server.py to use user token instead

This gives user-level permissions which are typically broader.

## Minimal Required Permissions

If you want minimal setup, these are absolutely required:

1. `drive:drive` - Basic drive access
2. `docx:document` - Document operations
3. `bitable:app` - Base access
4. `wiki:wiki` - Wiki access
5. `search:message` - Search functionality

## Troubleshooting

### Error 99991663 persists after approvals

**Cause**: Token generated before permissions were approved

**Solution**: Wait 5 minutes for token cache to expire, or restart Claude Code to force new token

### Error 230001: Insufficient permissions

**Cause**: Specific API requires permission not granted

**Solution**: Check error message for specific scope needed, add it in admin console

### Token expires quickly

**Cause**: tenant_access_token expires in 2 hours

**Solution**: Server auto-refreshes tokens. If using direct API, get new token when you see auth errors

### Can't find app in admin console

**Cause**: You're not the app owner/admin

**Solution**: Contact your Feishu workspace admin to grant permissions

## Current Status

**App ID**: cli_a85833b3fc39900e
**App Secret**: fiFRoqlAFX7ASY9iUt7Evb2aUx6Qurkd (configured)

**Status**: ⚠️ **Needs Permission Configuration**

**Next Steps**:
1. Configure app permissions at https://open.feishu.cn/app
2. Request admin approval
3. Restart Claude Code after approval
4. Test with document search

## Security Notes

- App credentials are stored in `.mcp.json` (gitignored)
- Tokens expire every 2 hours (auto-refreshed)
- Only grant minimum required permissions
- Consider using separate app for development vs production
- Never commit `.mcp.json` to public repositories

## Additional Resources

- Feishu Open Platform: https://open.feishu.cn/document/home/index
- OAuth Guide: https://open.feishu.cn/document/ukTMukTMukTM/ukzN4UjL5cDO14SO3gTN
- Permission Scopes: https://open.feishu.cn/document/ukTMukTMukTM/uQjN3QjL0YzN04CN2cDN
- Troubleshooting: https://open.feishu.cn/document/uAjLw4CM/ugTN1YjL4UTN24CO1UjN/trouble-shooting
