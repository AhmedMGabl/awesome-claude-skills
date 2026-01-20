# Feishu Bot API - Complete Setup Guide

Your bot **"AA"** is now configured and ready to use from anywhere!

## ✅ What's Already Done

- ✅ Bot app created: **AA** (cli_a85833b3fc39900e)
- ✅ Credentials configured
- ✅ Messaging permissions granted:
  - `im:message` - Read and send messages
  - `im:message.group_at_msg:readonly` - Receive @mentions
  - `im:message.group_msg` - Read group messages

## 🚀 Quick Start (3 Steps)

### Step 1: Set Environment Variables

**Windows CMD:**
```cmd
set FEISHU_APP_ID=cli_a85833b3fc39900e
set FEISHU_APP_SECRET=fiFRoqlAFX7ASY9iUt7Evb2aUx6Qurkd
```

**Or just run:**
```cmd
SETUP_BOT_API.bat
```

**Windows PowerShell:**
```powershell
$env:FEISHU_APP_ID="cli_a85833b3fc39900e"
$env:FEISHU_APP_SECRET="fiFRoqlAFX7ASY9iUt7Evb2aUx6Qurkd"
```

**Linux/Mac (add to ~/.bashrc or ~/.zshrc):**
```bash
export FEISHU_APP_ID="cli_a85833b3fc39900e"
export FEISHU_APP_SECRET="fiFRoqlAFX7ASY9iUt7Evb2aUx6Qurkd"
```

### Step 2: Add Bot to Your Chat

1. Open Feishu and go to the chat with **Hany**
2. Click the **"..."** menu (top right)
3. Select **"Add Bot"** or **"Group Settings"** → **"Bots"**
4. Search for **"AA"**
5. Click **"Add"**

The bot will now appear in the chat member list!

### Step 3: Get Chat ID and Send Message

```bash
# List all chats where bot is a member
python scripts/feishu_bot.py list

# You'll see output like:
# 1. Hany
#    Chat ID: oc_abc123xyz456
#    Description: N/A

# Send a message using the chat_id
python scripts/feishu_bot.py send oc_abc123xyz456 "Hello from Bot API!"
```

## 📚 All Commands

### List Chats
```bash
python scripts/feishu_bot.py list
```
Shows all chats where your bot is a member with their chat IDs.

### Send Message
```bash
python scripts/feishu_bot.py send <chat_id> "Your message here"
```

**Examples:**
```bash
python scripts/feishu_bot.py send oc_abc123 "Hello!"
python scripts/feishu_bot.py send oc_abc123 "Multi word message works fine"
```

### Read Messages
```bash
python scripts/feishu_bot.py read <chat_id> [limit]
```

**Examples:**
```bash
python scripts/feishu_bot.py read oc_abc123 20    # Read last 20 messages
python scripts/feishu_bot.py read oc_abc123 100   # Read last 100 messages
```

### Get Chat Info
```bash
python scripts/feishu_bot.py info <chat_id>
```

Returns detailed information about the chat (name, members, settings).

## 🌍 Use From Anywhere

Once environment variables are set, you can use the bot from:
- ✅ Your local computer
- ✅ Any other computer (just set the env vars)
- ✅ Cloud servers (AWS, Azure, etc.)
- ✅ Docker containers
- ✅ CI/CD pipelines (GitHub Actions, etc.)

## 📦 Requirements

```bash
pip install requests
```

That's it! The bot uses only the standard `requests` library.

## 🔐 Security Best Practices

1. **Never commit credentials to git**
   - `.env.feishu` is already in `.gitignore`
   - Use environment variables instead

2. **For production servers:**
   ```bash
   # Store in secure vault (AWS Secrets Manager, Azure Key Vault, etc.)
   # Or use environment variables in your deployment
   ```

3. **Rotate secrets periodically:**
   - Go to https://open.feishu.cn/app/cli_a85833b3fc39900e/baseinfo
   - Click "Regenerate" next to App Secret

## 🆚 Bot API vs Browser Automation

| Feature | Bot API | Browser Automation |
|---------|---------|-------------------|
| **Setup Time** | 5 min (one-time) | 2 min per computer |
| **Portability** | ✅ Works anywhere | ❌ Needs browser setup |
| **Reliability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Production Ready** | ✅ Yes | ⚠️ Limited |
| **Rate Limits** | Yes (documented) | No official limits |
| **No GUI Needed** | ✅ Yes | ❌ Needs browser |
| **Server Deployable** | ✅ Yes | ⚠️ Requires display |
| **Official Support** | ✅ Yes | ❌ Unofficial |

## 🎯 Use Cases

### Personal Automation
```bash
# Send daily standup
python scripts/feishu_bot.py send oc_abc123 "Daily standup: ..."
```

### Scheduled Messages (with cron/Task Scheduler)
```bash
# Every day at 9 AM
0 9 * * * python /path/to/feishu_bot.py send oc_abc123 "Good morning!"
```

### CI/CD Notifications
```bash
# In GitHub Actions, GitLab CI, etc.
python scripts/feishu_bot.py send oc_abc123 "Build #$BUILD_NUMBER completed!"
```

### Server Monitoring
```python
# monitoring.py
import subprocess

def send_alert(message):
    subprocess.run([
        "python", "scripts/feishu_bot.py",
        "send", "oc_abc123", message
    ])

# If server error detected:
send_alert("🚨 Server CPU usage at 95%!")
```

## 🔧 Troubleshooting

### "Missing credentials" Error
**Solution:** Make sure environment variables are set:
```bash
echo %FEISHU_APP_ID%        # Windows CMD
echo $env:FEISHU_APP_ID     # PowerShell
echo $FEISHU_APP_ID         # Linux/Mac
```

### "Failed to send message" Error
**Cause:** Bot not added to the chat

**Solution:**
1. Open the chat in Feishu
2. Add the bot "AA" to the chat
3. Try sending again

### "Chat not found" Error
**Cause:** Wrong chat_id or bot not in that chat

**Solution:**
1. Run `python scripts/feishu_bot.py list`
2. Find the correct chat_id
3. Make sure bot is added to that chat

### "Token expired" Error
**Solution:** The script auto-refreshes tokens. If this persists, regenerate your App Secret.

## 📖 API Documentation

Full Feishu API documentation: https://open.feishu.cn/document/home/index

Key endpoints used:
- **Authentication:** `/open-apis/auth/v3/tenant_access_token/internal`
- **Send Message:** `/open-apis/im/v1/messages`
- **List Chats:** `/open-apis/im/v1/chats`
- **Read Messages:** `/open-apis/im/v1/messages`

## 🎉 You're All Set!

Your bot is ready to use from anywhere. Just remember:
1. Set environment variables (or run SETUP_BOT_API.bat)
2. Add bot to chat
3. Use `python scripts/feishu_bot.py` commands

**No browser needed, no session needed, works everywhere!** 🚀
