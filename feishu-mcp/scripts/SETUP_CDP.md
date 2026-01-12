# Chrome Remote Debugging Setup for Feishu Automation

This setup allows all Feishu automation scripts to control your **existing browser session** without opening blank pages.

## Quick Setup (5 minutes)

### Step 1: Start Chrome with Remote Debugging

**Option A: Use the launcher (Easiest)**
```bash
# Double-click this file or run:
start_chrome_debug.bat
```

**Option B: Manual launch**
```bash
# Close all Chrome first
taskkill /F /IM chrome.exe

# Start with remote debugging
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%USERPROFILE%\.chrome-debug-profile" https://qcn9ppuir8al.feishu.cn/next/messenger/
```

### Step 2: Log into Feishu

1. Chrome will open to Feishu messenger
2. Log in if needed
3. Keep this Chrome window open

### Step 3: Test the Connection

```bash
python feishu_cdp.py test
```

You should see:
```
[OK] Connected to Chrome successfully!
[OK] Feishu found at: https://qcn9ppuir8al.feishu.cn/next/messenger/
[OK] Setup is working perfectly!
```

### Step 4: Start Automating!

```bash
# Send a message
python feishu_cdp.py send Hany "Hello from automation!"

# Read messages
python feishu_cdp.py read Hany 50

# List all chats
python feishu_cdp.py list
```

## How It Works

### Before (Problem)
- Scripts launch NEW Chrome windows → blank pages
- No access to your logged-in session
- Have to log in every time

### After (Solution)
- Scripts connect to YOUR existing Chrome
- Uses your logged-in Feishu session
- No blank pages, instant automation

### Architecture

```
Your Chrome (Port 9222)
    ↓
Chrome DevTools Protocol (CDP)
    ↓
Playwright connects via CDP
    ↓
Controls your existing Feishu tab
```

## Available Scripts

### 1. feishu_cdp.py (Recommended)
Full-featured CDP controller:

```bash
# Test connection
python feishu_cdp.py test

# Send message
python feishu_cdp.py send Hany "Message"

# Read messages
python feishu_cdp.py read Hany 50

# List chats
python feishu_cdp.py list
```

### 2. feishu_simple.py (Original)
Simple send and react:

```bash
# Send message
python feishu_simple.py send Hany "Message"

# Add reaction
python feishu_simple.py react "message text" "👍"
```

### 3. feishu_pro.py (Advanced)
Full automation with AI features:

**Note:** Needs update to use CDP by default. For now, use feishu_cdp.py

## Troubleshooting

### "Could not connect to Chrome"

**Solution 1: Check if Chrome is running with debugging**
```bash
# Windows
netstat -ano | findstr :9222

# Should show Chrome listening on port 9222
```

**Solution 2: Restart Chrome with debugging**
```bash
# Close all Chrome
taskkill /F /IM chrome.exe

# Run the launcher again
start_chrome_debug.bat
```

### "Feishu not found"

**Solution:** Open Feishu in the Chrome window:
```
https://qcn9ppuir8al.feishu.cn/next/messenger/
```

### Port 9222 Already in Use

**Check what's using it:**
```bash
netstat -ano | findstr :9222
```

**Kill the process:**
```bash
taskkill /F /PID <process_id>
```

Then restart Chrome with debugging.

### Messages Not Sending

1. **Verify connection:**
   ```bash
   python feishu_cdp.py test
   ```

2. **Check you're logged in:** Open your Chrome and verify Feishu is logged in

3. **Try clicking the chat manually** first, then run the script

### Chrome Closes Unexpectedly

Keep the `start_chrome_debug.bat` window open. Closing it will close Chrome.

## Advanced Usage

### Run in Background

Create a Windows service or scheduled task:

```xml
<!-- Task Scheduler XML -->
<Task>
  <Exec>
    <Command>C:\Program Files\Google\Chrome\Application\chrome.exe</Command>
    <Arguments>--remote-debugging-port=9222 --user-data-dir=%USERPROFILE%\.chrome-debug-profile</Arguments>
  </Exec>
</Task>
```

### Custom Port

If port 9222 is blocked, use a different port:

```bash
# Launch Chrome
chrome.exe --remote-debugging-port=9223

# Update scripts
CDP_URL = "http://localhost:9223"
```

### Multiple Profiles

Use different profiles for different accounts:

```bash
# Profile 1
chrome.exe --remote-debugging-port=9222 --user-data-dir="%USERPROFILE%\.chrome-profile-1"

# Profile 2
chrome.exe --remote-debugging-port=9223 --user-data-dir="%USERPROFILE%\.chrome-profile-2"
```

## Security Notes

### Is This Safe?

**Yes, for local use:**
- CDP only listens on localhost (127.0.0.1)
- Not accessible from network
- Requires local access to your machine

### Don't expose port 9222 to network!

**Bad (vulnerable):**
```bash
chrome.exe --remote-debugging-address=0.0.0.0 --remote-debugging-port=9222
```

**Good (secure):**
```bash
chrome.exe --remote-debugging-port=9222  # Localhost only
```

### Production Use

For production/server environments:
- Use Feishu API with proper OAuth
- Don't rely on browser automation
- CDP is great for personal/development use only

## Integration with Other Tools

### With Python Scripts

```python
from playwright.async_api import async_playwright

async def use_existing_chrome():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")

        # Find Feishu page
        for context in browser.contexts:
            for page in context.pages:
                if "feishu.cn" in page.url:
                    # Use this page
                    await page.click('text="ChatName"')
                    break
```

### With JavaScript/Node.js

```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const contexts = browser.contexts();
  const page = contexts[0].pages()[0];

  await page.goto('https://feishu.cn/...');
})();
```

## Daily Workflow

### Morning Routine

1. Start Chrome with debugging:
   ```bash
   start_chrome_debug.bat
   ```

2. Log into Feishu (if needed)

3. Keep Chrome open all day

4. Run automation anytime:
   ```bash
   python feishu_cdp.py send Hany "Good morning!"
   ```

### Night Routine

1. Close Chrome normally (Ctrl+W or X button)
2. Your session is saved
3. Next day, Chrome will remember login

## Comparison: CDP vs New Browser

| Feature | CDP (This Setup) | New Browser Launch |
|---------|------------------|-------------------|
| Blank Pages | ❌ None | ✅ Creates many |
| Login Required | ❌ Once only | ✅ Every time |
| Speed | ⚡ Instant | 🐌 Slow (3-5 sec) |
| Session Persistence | ✅ Yes | ⚠️ Sometimes |
| Memory Usage | 💚 Low | 🔴 High (multiple instances) |
| Reliability | ✅ Very high | ⚠️ Medium |

## Next Steps

1. ✅ Run `start_chrome_debug.bat`
2. ✅ Test with `python feishu_cdp.py test`
3. ✅ Send first message: `python feishu_cdp.py send Hany "Test!"`
4. 🚀 Start automating!

## Support

If you have issues:
1. Check this guide's Troubleshooting section
2. Run `python feishu_cdp.py test` for diagnostics
3. Verify Chrome is running with `netstat -ano | findstr :9222`

**Pro tip:** Create a desktop shortcut to `start_chrome_debug.bat` for quick access!
