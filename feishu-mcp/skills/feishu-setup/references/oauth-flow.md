# Feishu OAuth 2.0 Implementation Guide

Complete OAuth authorization code flow implementation for Feishu user authentication.

## OAuth Flow Overview

```
1. User clicks authorization link
   ↓
2. Feishu shows authorization page
   ↓
3. User authorizes app
   ↓
4. Redirect to callback with code
   ↓
5. Exchange code for access token
   ↓
6. Store and use tokens
```

## Step 1: Generate Authorization URL

```python
import urllib.parse

def generate_auth_url(app_id, redirect_uri, scopes):
    base_url = "https://open.feishu.cn/open-apis/authen/v1/authorize"

    params = {
        "app_id": app_id,
        "redirect_uri": redirect_uri,
        "scope": " ".join(scopes),
        "state": "random_secure_string"  # CSRF protection
    }

    return f"{base_url}?{urllib.parse.urlencode(params)}"

# Example
scopes = ["im:message", "im:chat", "contact:user.base:readonly"]
auth_url = generate_auth_url(
    app_id="cli_xxxxxxxx",
    redirect_uri="http://localhost:8888/callback",
    scopes=scopes
)
```

## Step 2: Handle Callback

### Local Development (http://localhost:8888/callback)

```python
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse callback URL
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if 'code' in params:
            code = params['code'][0]
            state = params.get('state', [None])[0]

            # Verify state matches
            # Exchange code for token
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Authorization successful!")
        else:
            # Handle error
            error = params.get('error', ['unknown'])[0]
            self.send_response(400)

# Start server
server = HTTPServer(('localhost', 8888), OAuthCallbackHandler)
server.handle_request()  # Handle one request then close
```

### Production (HTTPS callback)

Use Flask or FastAPI:

```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/callback")
async def oauth_callback(code: str, state: str):
    # Verify state
    # Exchange code for token
    # Redirect to success page
    return {"status": "success"}
```

## Step 3: Exchange Code for Token

```python
import httpx

async def exchange_code_for_token(code, app_id, app_secret):
    """
    Exchange authorization code for access and refresh tokens
    """
    url = "https://open.feishu.cn/open-apis/authen/v1/access_token"

    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "app_id": app_id,
        "app_secret": app_secret
    }

    headers = {
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        result = response.json()

    if result.get("code") == 0:
        data = result["data"]
        return {
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "expires_in": data["expires_in"],  # Typically 7200 seconds
            "token_type": data["token_type"],
            "scope": data.get("scope"),
            "open_id": data.get("open_id")  # User identifier
        }
    else:
        raise Exception(f"Token exchange failed: {result}")
```

## Step 4: Store Tokens Securely

```python
import json
from datetime import datetime, timedelta

def save_tokens(tokens, file_path="user_token.json"):
    """
    Store tokens with expiry timestamp
    """
    token_data = {
        **tokens,
        "obtained_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(seconds=tokens["expires_in"])).isoformat()
    }

    with open(file_path, 'w') as f:
        json.dump(token_data, f, indent=2)

def load_tokens(file_path="user_token.json"):
    """
    Load tokens from storage
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
```

## Step 5: Refresh Tokens

```python
async def refresh_access_token(refresh_token, app_id, app_secret):
    """
    Refresh expired access token using refresh token
    """
    url = "https://open.feishu.cn/open-apis/authen/v1/oidc/refresh_access_token"

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    # Use Basic Auth
    import base64
    auth_string = base64.b64encode(f"{app_id}:{app_secret}".encode()).decode()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {auth_string}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        result = response.json()

    if result.get("code") == 0:
        data = result["data"]
        return {
            "access_token": data["access_token"],
            "refresh_token": data.get("refresh_token"),  # May get new refresh token
            "expires_in": data["expires_in"]
        }
    else:
        # Refresh failed - need re-authorization
        raise Exception("Refresh failed - re-authorization required")
```

## Step 6: Automatic Token Management

```python
from datetime import datetime

class TokenManager:
    def __init__(self, app_id, app_secret, token_file="user_token.json"):
        self.app_id = app_id
        self.app_secret = app_secret
        self.token_file = token_file
        self.tokens = load_tokens(token_file)

    async def get_valid_token(self):
        """
        Get current valid access token, refreshing if needed
        """
        if not self.tokens:
            raise Exception("No tokens available - authorization required")

        # Check if expired (with 60s buffer)
        expires_at = datetime.fromisoformat(self.tokens["expires_at"])
        if datetime.now() >= expires_at - timedelta(seconds=60):
            # Token expired or about to expire - refresh
            new_tokens = await refresh_access_token(
                self.tokens["refresh_token"],
                self.app_id,
                self.app_secret
            )

            # Update stored tokens
            self.tokens.update(new_tokens)
            self.tokens["obtained_at"] = datetime.now().isoformat()
            self.tokens["expires_at"] = (datetime.now() + timedelta(seconds=new_tokens["expires_in"])).isoformat()

            save_tokens(self.tokens, self.token_file)

        return self.tokens["access_token"]
```

## Complete Example

```python
import asyncio

async def complete_oauth_flow():
    APP_ID = "cli_xxxxxxxx"
    APP_SECRET = "your_secret"
    REDIRECT_URI = "http://localhost:8888/callback"
    SCOPES = ["im:message", "im:chat", "contact:user.base:readonly"]

    # Step 1: Generate URL
    auth_url = generate_auth_url(APP_ID, REDIRECT_URI, SCOPES)
    print(f"Open this URL in browser: {auth_url}")

    # Step 2: User authorizes (opens in browser)
    # Step 3: Capture callback
    # (Run local server or manual input)

    code = input("Enter authorization code from callback URL: ")

    # Step 4: Exchange for token
    tokens = await exchange_code_for_token(code, APP_ID, APP_SECRET)

    # Step 5: Store tokens
    save_tokens(tokens)

    print("OAuth setup complete!")
    print(f"Access token: {tokens['access_token'][:20]}...")
    print(f"Expires in: {tokens['expires_in']} seconds")

    return tokens

# Run
asyncio.run(complete_oauth_flow())
```

## Using OAuth Token for API Calls

```python
async def api_call_with_user_token(token, endpoint, method="GET", data=None):
    """
    Make API call with user access token
    """
    base_url = "https://open.feishu.cn/open-apis"
    url = f"{base_url}/{endpoint}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(url, headers=headers)
        elif method == "POST":
            response = await client.post(url, json=data, headers=headers)

        return response.json()

# Example: List all user chats
token_manager = TokenManager(APP_ID, APP_SECRET)
token = await token_manager.get_valid_token()
chats = await api_call_with_user_token(token, "im/v1/chats")
```

## Security Best Practices

### State Parameter

Always use state parameter to prevent CSRF:

```python
import secrets

def generate_state():
    """Generate secure random state"""
    return secrets.token_urlsafe(32)

# Store state in session
state = generate_state()
session['oauth_state'] = state

# Verify on callback
def verify_state(received_state):
    expected_state = session.get('oauth_state')
    if not expected_state or received_state != expected_state:
        raise Exception("Invalid state - possible CSRF attack")
```

### Token Storage

- **Never commit tokens to git**
- Use environment variables or encrypted storage
- Set proper file permissions (600 on Unix)
- Clear tokens on logout

### HTTPS in Production

- Always use HTTPS for redirect URI in production
- HTTP localhost OK for development only
- Configure SSL certificates properly

## Troubleshooting

### Authorization Code Invalid

**Error**: Code 20014 on token exchange

**Causes**:
- Code already used (single-use only)
- Code expired (typically 10 minutes)
- Code generated for different app

**Solutions**:
- Get fresh authorization code
- Complete exchange quickly
- Verify App ID matches

### Redirect URI Mismatch

**Error**: redirect_uri invalid

**Causes**:
- URL not configured in Security Settings
- Protocol mismatch (http vs https)
- Port number mismatch

**Solutions**:
- Add exact redirect URI in console
- Match protocol, domain, and port exactly
- Include trailing slash if present in auth URL

### Refresh Token Expired

**Error**: Refresh fails after long period

**Causes**:
- Refresh token expired (typically 30 days)
- Token invalidated by user
- App permissions changed

**Solutions**:
- Re-run full authorization flow
- Don't cache refresh tokens indefinitely
- Implement graceful re-authorization

## References

- **OAuth 2.0 Spec**: https://oauth.net/2/
- **Feishu OAuth Guide**: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/authen-v1/authen/access_token
- **Security Best Practices**: https://tools.ietf.org/html/rfc6749#section-10
