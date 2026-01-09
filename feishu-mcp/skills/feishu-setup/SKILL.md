---
name: Feishu Setup and Configuration
description: This skill should be used when the user needs help with Feishu bot setup, OAuth configuration, permission management, or troubleshooting Feishu API integration issues.
version: 1.0.0
---

# Feishu Setup and Configuration

Comprehensive guide for setting up Feishu bots, configuring OAuth authentication, managing permissions, and troubleshooting common integration issues.

## When to Use This Skill

Activate this skill when encountering:
- Feishu bot creation and initial setup
- OAuth 2.0 authorization flow configuration
- Permission errors (codes 20027, 99991672, 99991679, etc.)
- MCP server connection issues
- API authentication problems
- Dual-bot architecture setup

## Bot Creation and Setup

### Create a Feishu Bot Application

1. **Access Feishu Open Platform**:
   - Navigate to https://open.feishu.cn/
   - Log in with Feishu account
   - Click "Create App" or "Create Custom App"

2. **Basic Configuration**:
   - Enter app name (e.g., "Claude MCP Bot")
   - Add app description
   - Upload app icon (optional)
   - Select app type: "Custom App" (自建应用)

3. **Get Credentials**:
   - Navigate to "Credentials" section
   - Copy **App ID** (cli_xxxxxxxx)
   - Copy **App Secret** (secret string)
   - Store securely in `.claude/feishu.local.md`

4. **Enable Features**:
   - Bot functionality (required)
   - Messaging capabilities
   - Chat management (if needed)

### Configure Bot Permissions

**Critical Understanding**: Feishu has TWO separate permission systems:
1. **Tenant Token Permissions** (bot-level) - For bot acting as itself
2. **User Access Token Permissions** (OAuth-level) - For bot acting as user

Both must be configured separately!

#### Add Tenant Permissions

1. Go to **"Permission Management"** (权限管理)
2. Click **"Add permission scopes to app"**
3. Select **"Tenant token"** as type
4. Add required scopes:
   - `im:message` - Send/receive messages
   - `im:chat` - Manage chats
   - `im:chat:readonly` - Read chat info
   - `contact:user.base:readonly` - User information
   - `im:message.group_msg` - Group messages
   - `im:message.p2p_msg` - Private messages

#### Add User OAuth Permissions

**IMPORTANT**: This is separate from tenant permissions!

1. In **"Permission Management"**, click **"Add permission scopes to app"** again
2. This time select **"User access token"** as type
3. Add the SAME scopes but for user-level:
   - `im:message`
   - `im:chat`
   - `im:chat:readonly`
   - `contact:user.base:readonly`
   - `im:message.group_msg`
   - `im:message.p2p_msg`

4. **Create New Version**:
   - Go to "Version Management & Release"
   - Click "Create Version"
   - Increment version number (e.g., 5.0.0 → 6.0.0)
   - Add description: "Added OAuth user permissions"
   - Click "Publish"

5. **Wait for Approval**:
   - Some permissions auto-approve
   - Others may require admin approval
   - Check status in version management

## OAuth 2.0 Configuration

### Setup Redirect URL

1. **Access Security Settings**:
   - Go to "Security Settings" (安全设置)
   - Find "Redirect URLs" section

2. **Add Redirect URL**:
   - Enter: `http://localhost:8888/callback`
   - For production: `https://yourdomain.com/callback`
   - Save changes

3. **Note**: Cannot edit redirect URLs while app is under review

### OAuth Authorization Flow

1. **Generate Authorization URL**:
   ```
   https://open.feishu.cn/open-apis/authen/v1/authorize
     ?app_id={APP_ID}
     &redirect_uri=http://localhost:8888/callback
     &scope=im:message im:chat contact:user.base:readonly
     &state=random_state_string
   ```

2. **User authorizes**: Opens URL in browser, clicks "Authorize"

3. **Receive authorization code**:
   Browser redirects to: `http://localhost:8888/callback?code=XXXXX&state=...`

4. **Exchange code for token**:
   ```http
   POST /authen/v1/access_token
   {
     "grant_type": "authorization_code",
     "code": "AUTHORIZATION_CODE",
     "app_id": "APP_ID",
     "app_secret": "APP_SECRET"
   }
   ```

5. **Store tokens**:
   - Access token (expires in ~2 hours)
   - Refresh token (for renewing access)
   - Save to secure location

### Token Refresh

User access tokens expire. Implement automatic refresh:

```http
POST /authen/v1/oidc/refresh_access_token
{
  "grant_type": "refresh_token",
  "refresh_token": "REFRESH_TOKEN"
}
Headers:
  Authorization: Basic {APP_ID}:{APP_SECRET}
```

## Permission Troubleshooting

### Error Code 20027

**Message**: "This app didn't apply for [scope] related permissions"

**Root Cause**: OAuth user permissions not configured

**Solution**:
1. Add permissions specifically for **"User access token"** type
2. Do NOT just add tenant token permissions
3. Create and publish new app version
4. Re-authorize with OAuth flow

### Error Code 99991672

**Message**: "Access denied. Required scope: [scope]"

**Root Cause**: Tenant token missing required permission

**Solution**:
1. Add missing scope in Permission Management
2. Ensure scope is for "Tenant token" type
3. Create new version if required
4. Restart MCP server to use new token

### Error Code 99991679

**Message**: "Required user identity privileges: [scopes]"

**Root Cause**: Using user token without proper OAuth scopes

**Solution**:
1. Verify OAuth permissions are approved (not just added)
2. Check app version status - must be published
3. Re-run OAuth authorization flow
4. Verify redirect URL is configured

### Permission Propagation Delay

**Issue**: Permissions added but still getting errors

**Cause**: Feishu takes time to propagate permission changes

**Solution**:
1. Wait 5-10 minutes after approval
2. Clear token cache
3. Get fresh tenant/user tokens
4. Retry failed operation

## Dual Bot Architecture

### Why Use Two Bots?

**Bot 1 (Primary)**:
- Production messaging
- Tenant token authentication
- Always available
- Limited to bot-visible chats

**Bot 2 (Secondary)**:
- User-level OAuth
- Access to ALL user chats
- Requires authorization
- Full user permissions

### Configuration

In `.claude/feishu.local.md`:

```yaml
---
FEISHU_BOT1_APP_ID: "cli_primary_bot"
FEISHU_BOT1_APP_SECRET: "primary_secret"

FEISHU_BOT2_APP_ID: "cli_secondary_bot"
FEISHU_BOT2_APP_SECRET: "secondary_secret"

FEISHU_DEFAULT_BOT: "bot1"  # or "bot2"
---
```

### When to Use Each Bot

**Use Bot 1** when:
- Sending to chats bot is member of
- Official bot communications
- No user context needed

**Use Bot 2** when:
- Accessing all user chats
- Acting on behalf of user
- Need user-level permissions

## MCP Server Configuration

### Server Setup

The Feishu MCP server (`server.py`) requires:

1. **Python 3.8+** with FastMCP installed
2. **Environment variables** from settings
3. **Network access** to Feishu API

### Verify Server Status

Check if MCP server is running:
1. In Claude Code, open MCP panel
2. Look for "feishu" server
3. Status should be "Connected"
4. Check available tools: send_message, list_chats, etc.

### Server Logs

If server fails to start, check logs:
- Windows: Check Claude Code console
- Check for import errors (fastmcp not installed)
- Verify credentials are loaded
- Check network connectivity

### Common MCP Issues

**Issue**: "MCP server not found"
- **Fix**: Verify `.mcp.json` path to server.py is correct
- **Fix**: Check Python is in PATH

**Issue**: "Import error: fastmcp"
- **Fix**: Install FastMCP: `pip install fastmcp`

**Issue**: "Authentication failed"
- **Fix**: Verify credentials in `.claude/feishu.local.md`
- **Fix**: Check environment variables are loaded

## API Integration Best Practices

### Authentication Strategy

1. **Start with Tenant Token**: Simpler, no OAuth required
2. **Add OAuth Later**: When need user-level access
3. **Implement Token Refresh**: For long-running applications
4. **Handle Errors Gracefully**: Provide clear error messages

### Rate Limiting

Feishu API has rate limits:
- Tenant token: ~100 requests/minute
- User token: ~50 requests/minute per user

**Mitigation**:
- Implement retry with exponential backoff
- Cache frequently accessed data
- Batch operations when possible

### Error Handling

Always check response codes:
- `code: 0` - Success
- `code: 20014` - Invalid app token
- `code: 20027` - Missing OAuth permission
- `code: 99991672` - Missing tenant permission
- `code: 99991679` - Missing user permission

## Testing and Verification

### Test Tenant Token Authentication

```bash
# Get tenant token
curl -X POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal \
  -H "Content-Type: application/json" \
  -d '{"app_id":"APP_ID","app_secret":"APP_SECRET"}'

# Response should have tenant_access_token
```

### Test Message Sending

Use MCP tools or direct API:
```
/feishu:send-message
# Select test chat
# Send test message
# Verify in Feishu app
```

### Test OAuth Flow

1. Generate authorization URL
2. Authorize in browser
3. Capture authorization code
4. Exchange for tokens
5. Test user-level API call

## Reference Files

For detailed technical information, see:
- `references/api-reference.md` - Complete API documentation
- `references/error-codes.md` - All error codes and solutions
- `references/oauth-flow.md` - Detailed OAuth implementation

## Quick Troubleshooting Checklist

When encountering issues:

- [ ] Verify bot credentials are correct
- [ ] Check permissions are added (both tenant AND user if using OAuth)
- [ ] Confirm app version is published and approved
- [ ] Wait 5-10 minutes after permission changes
- [ ] Clear token cache and get fresh tokens
- [ ] Verify redirect URL is configured (for OAuth)
- [ ] Check MCP server is running
- [ ] Review error code in error-codes.md reference
- [ ] Test with simple API call (get tenant token)
- [ ] Verify network connectivity to open.feishu.cn

## Additional Resources

- **Feishu Open Platform**: https://open.feishu.cn/
- **API Documentation**: https://open.feishu.cn/document/
- **OAuth Guide**: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/authen-v1/authen/access_token
- **Permission Guide**: https://open.feishu.cn/document/ukTMukTMukTM/uczM3QjL3MzN04yNzcDN
