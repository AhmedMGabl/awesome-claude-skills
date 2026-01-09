# Feishu API Error Codes Reference

Complete list of Feishu API error codes with causes and solutions.

## Authentication Errors

### Code 20014
**Message**: "The app access token passed is invalid"

**Causes**:
- Expired tenant access token
- Invalid app credentials
- Wrong authentication method

**Solutions**:
1. Request new tenant token
2. Verify App ID and App Secret
3. Check token format in Authorization header

### Code 20027
**Message**: "This app didn't apply for [scope] related permissions"

**Causes**:
- OAuth scope not configured for user access token
- Permission added but not published
- Using wrong token type

**Solutions**:
1. Add permissions for **"User access token"** type (not just tenant)
2. Create and publish new app version
3. Re-authorize OAuth flow
4. Verify redirect URL is configured

### Code 20029
**Message**: "redirect_uri invalid"

**Causes**:
- Redirect URL not added in Security Settings
- URL mismatch (http vs https)
- App under review (can't edit redirect URLs)

**Solutions**:
1. Add redirect URL in Security Settings
2. Ensure exact match including protocol
3. Wait for app review to complete

## Permission Errors

### Code 99991672
**Message**: "Access denied. Required scope: [scope]"

**Causes**:
- Tenant token missing required permission
- Permission not yet propagated
- Wrong token type used

**Solutions**:
1. Add missing scope in Permission Management
2. Ensure scope type is "Tenant token"
3. Wait 5-10 minutes for propagation
4. Create new version if required

### Code 99991679
**Message**: "Required user identity privileges: [scopes]"

**Causes**:
- User OAuth token missing required scope
- Permission not approved for OAuth
- Token not refreshed after permission change

**Solutions**:
1. Add scopes for **"User access token"** type
2. Create and publish new version
3. Re-run OAuth authorization
4. Verify all scopes are approved

### Code 230001
**Message**: "Invalid request parameter"

**Causes**:
- Invalid receive_id format
- Wrong receive_id_type
- Malformed request body

**Solutions**:
1. Verify email/user ID format
2. Match receive_id_type to receive_id format:
   - email → receive_id_type=email
   - open_id → receive_id_type=open_id
   - chat_id → receive_id_type=chat_id
3. Check JSON structure

### Code 230027
**Message**: "Permission denied"

**Causes**:
- Bot not member of chat
- Insufficient permissions
- User not accessible

**Solutions**:
1. Add bot to chat manually
2. Use OAuth for user-level access
3. Verify permission scopes
4. Check user exists and is accessible

## API Errors

### Code 1002
**Message**: "Request frequency limit exceeded"

**Causes**:
- Too many API requests
- Rate limit reached

**Solutions**:
1. Implement exponential backoff
2. Cache frequently accessed data
3. Batch operations
4. Upgrade API tier if needed

### Code 10014
**Message**: "API not found"

**Causes**:
- Wrong API endpoint
- Typo in URL
- API version mismatch

**Solutions**:
1. Verify endpoint URL
2. Check API documentation
3. Use correct API version

## Token Errors

### Code 99991663
**Message**: "Authorization token expired"

**Causes**:
- Access token expired (typically 2 hours)
- Token not refreshed

**Solutions**:
1. Implement automatic token refresh
2. Use refresh_token to get new access_token
3. Handle token expiry gracefully

### Code 99991677
**Message**: "Authentication token expired"

**Causes**:
- User access token expired
- Refresh token expired

**Solutions**:
1. Use refresh token to renew
2. Re-authorize OAuth if refresh fails
3. Store tokens securely

## Chat Errors

### Code 235001
**Message**: "Chat not found"

**Causes**:
- Invalid chat ID
- Chat deleted
- No access to chat

**Solutions**:
1. Verify chat ID format
2. List chats to get valid IDs
3. Check bot membership in chat

### Code 235002
**Message**: "Chat member not found"

**Causes**:
- User not in chat
- Invalid user ID

**Solutions**:
1. Verify user is chat member
2. Check user ID format
3. Add user to chat first

## General Errors

### Code 1
**Message**: "System error"

**Causes**:
- Feishu server issue
- Temporary outage
- Network problem

**Solutions**:
1. Retry after delay
2. Check Feishu status page
3. Verify network connectivity

### Code -1
**Message**: "Unknown error"

**Causes**:
- Unexpected server error
- Malformed request

**Solutions**:
1. Check request format
2. Validate all parameters
3. Review API documentation
4. Contact Feishu support if persists

## Error Handling Best Practices

### Implement Retry Logic

```python
async def api_call_with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = await func()
            if result.get("code") == 0:
                return result
            elif result.get("code") in [1002, 1]:
                # Rate limit or temporary error - retry
                await asyncio.sleep(2 ** attempt)
                continue
            else:
                # Permanent error - don't retry
                return result
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)
```

### Log Errors Properly

Always log:
- Error code
- Error message
- Request parameters (sanitized)
- Timestamp
- User context

### User-Friendly Error Messages

Convert error codes to actionable messages:

```python
error_messages = {
    20027: "OAuth permissions not configured. Please run setup.",
    99991672: "Bot missing required permission. Check Feishu console.",
    230027: "Cannot access this chat. Add bot or enable OAuth.",
    99991679: "User permissions not approved. Re-authorize required."
}
```

## Permission Approval Checklist

When permission errors occur:

1. **Check permission type**: Tenant vs User access token
2. **Verify permissions added**: In Permission Management section
3. **Create new version**: After adding permissions
4. **Publish version**: Must be published, not draft
5. **Wait for approval**: Some permissions need admin approval
6. **Wait for propagation**: Allow 5-10 minutes after approval
7. **Clear token cache**: Get fresh tokens
8. **Re-authorize OAuth**: If using user tokens
9. **Test with simple call**: Verify token works
10. **Check error code**: Consult this reference

## Debugging Tips

### Enable Debug Logging

Set environment variable:
```bash
export FEISHU_DEBUG=true
```

This will log:
- All API requests
- Token generation
- Error details
- Response payloads

### Test Token Validity

```bash
# Test tenant token
curl -X GET https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal \
  -H "Authorization: Bearer YOUR_TOKEN"

# Should return token info or error
```

### Verify Permissions

Check current permissions:
1. Go to Feishu Open Platform
2. Select your app
3. View "Permission Management"
4. Check both Tenant and User token columns
5. Verify all are marked as "Added" or "Approved"

## Common Error Patterns

### OAuth Configuration Issues

**Symptoms**:
- Error 20027 repeatedly
- OAuth redirect fails
- Token exchange fails

**Root Cause**: User permissions not properly configured

**Solution**:
1. Add permissions specifically for "User access token"
2. Not the same as tenant permissions
3. Create new version
4. Publish and wait for approval

### Permission Propagation Delay

**Symptoms**:
- Permissions show as approved
- Still getting permission errors
- Works after waiting

**Root Cause**: Feishu needs time to propagate changes

**Solution**:
1. Wait 5-10 minutes after approval
2. Clear local token cache
3. Get fresh tokens
4. Retry operation

### Token Confusion

**Symptoms**:
- Works with one method, fails with another
- Inconsistent access to chats

**Root Cause**: Using wrong token type for operation

**Solution**:
- Tenant token: Bot-visible chats only
- User token: All user chats
- Match token to use case

## Support Resources

- **Feishu Error Codes**: https://open.feishu.cn/document/ukTMukTMukTM/ugjM14COyUjL4ITN
- **Permission Guide**: https://open.feishu.cn/document/ukTMukTMukTM/uczM3QjL3MzN04yNzcDN
- **OAuth Troubleshooting**: https://open.feishu.cn/document/uAjLw4CM/ugTN1YjL4UTN24CO1UjN/trouble-shooting
