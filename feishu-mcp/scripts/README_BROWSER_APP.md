# Feishu Browser Automation App

Standalone Python application that maintains a persistent browser session for reliable Feishu operations.

## Features

- **Persistent Browser Session** - Maintains login across sessions using Chrome user data directory
- **No Lock Issues** - Independent from MCP server, no browser locking problems
- **Simple CLI** - Easy commands for common operations
- **Auto-Login Preservation** - Keeps your Feishu login active

## Setup

1. Install dependencies:
```bash
pip install -r feishu_requirements.txt
playwright install chromium
```

2. Start the browser for initial login verification:
```bash
python feishu_browser_app.py start
```

3. Verify you're logged into Feishu in the opened browser window

4. Keep the browser running or close it - your session is saved!

## Usage

### Start Browser (for verification)
```bash
python feishu_browser_app.py start
# or
feishu.bat start
```
Opens browser at Feishu messenger. Press Ctrl+C to close.

### Send Message
```bash
python feishu_browser_app.py send "Hany" "Hello!"
# or
feishu.bat send Hany "Hello!"
```

### Add Reaction to Message
```bash
python feishu_browser_app.py react "sup" "👍"
# or
feishu.bat react "sup" 👍
```

### Read Messages from Chat
```bash
python feishu_browser_app.py read "Hany"
# or
feishu.bat read Hany
```

## How It Works

1. **Persistent Context**: Uses Playwright's `launch_persistent_context()` to maintain browser state
2. **User Data Directory**: Stores session in `~/.feishu-browser-data/`
3. **No Headless**: Runs in visible mode so you can verify operations
4. **Session Reuse**: Login credentials persist across runs

## Advantages Over MCP Server

- ✅ No browser locking issues
- ✅ Persistent login sessions
- ✅ Can be used independently
- ✅ Simple CLI interface
- ✅ Visible browser for verification

## Integration

Can be called from:
- Python scripts: `import feishu_browser_app`
- Command line: `python feishu_browser_app.py ...`
- Batch files: `feishu.bat ...`
- Claude Code: Via Bash tool

## Troubleshooting

**Browser won't start:**
- Run `playwright install chromium`
- Check Chrome is installed

**Not logged in:**
- Run `python feishu_browser_app.py start`
- Log into Feishu in the opened browser
- Session will be saved automatically

**Message not sending:**
- Check chat name is correct (case-sensitive)
- Verify you're on the messenger page
- Browser must be running

## Storage Location

Browser data stored at: `~/.feishu-browser-data/`
- Windows: `C:\Users\<username>\.feishu-browser-data\`
- Linux/Mac: `~/.feishu-browser-data/`

To reset: Delete this directory and restart browser.
