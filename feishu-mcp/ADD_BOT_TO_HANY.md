# How to Add AA Bot to Hany Chat

## Quick Steps (2 minutes)

### Method 1: Create Group Chat with Bot

Since the bot can't be added to 1-on-1 chats directly, create a small group:

1. **Open Feishu** and click the **"+"** button (top right)
2. Select **"Create Group Chat"**
3. Add members:
   - Search for and add **Hany**
   - Search for and add **AA** (your bot)
4. Name the group (e.g., "Ahmed + Hany + Bot")
5. Click **Create**

### Method 2: Add Bot to Existing Group

If you have a group chat with Hany:

1. **Open the group chat** with Hany
2. Click the **"..."** menu (top right)
3. Select **"Chat Settings"** or **"Group Info"**
4. Find **"Bots"** or **"Add Bot"** section
5. Click **"+"** or **"Add Bot"**
6. Search for **"AA"**
7. Click **"Add"**

## After Adding the Bot

### Get the Chat ID

```bash
python scripts/feishu_bot.py list
```

Look for the chat with Hany in the output. Copy the `Chat ID` (starts with `oc_`).

### Send Test Message

```bash
python scripts/feishu_bot.py send oc_YOURCHATID "Hello Hany! Message via Bot API 🤖"
```

Replace `oc_YOURCHATID` with the actual chat ID from the previous step.

### Read Messages

```bash
python scripts/feishu_bot.py read oc_YOURCHATID 20
```

## Example Usage

Once the bot is in the chat with Hany:

```bash
# Set credentials (if not already set)
set FEISHU_APP_ID=cli_a85833b3fc39900e
set FEISHU_APP_SECRET=fiFRoqlAFX7ASY9iUt7Evb2aUx6Qurkd

# List chats to find the new group
python scripts/feishu_bot.py list

# Send message to Hany
python scripts/feishu_bot.py send oc_abc123xyz "Hey Hany, testing the bot!"

# Read recent messages
python scripts/feishu_bot.py read oc_abc123xyz 10
```

## Why Create a Group?

Feishu bots can only be added to:
- ✅ Group chats (2+ people)
- ✅ Bot-created chats
- ❌ NOT 1-on-1 direct messages

So we need at least 3 members: You + Hany + AA Bot.

## Alternative: Just You + Bot

If you want to test without Hany first:

1. Create group with just **You** + **AA Bot**
2. Test all commands there
3. Then create the final group with Hany

## Troubleshooting

### "Bot not found"
- Make sure the bot "AA" is published
- Check bot is enabled in your organization
- Try searching by App ID: cli_a85833b3fc39900e

### "Cannot add bot"
- Bot can only be added to group chats (not 1-on-1)
- You must be the group creator or have admin rights
- Bot must be published and enabled

### "Bot added but no chat ID"
- Wait 30 seconds after adding bot
- Run `python scripts/feishu_bot.py list` again
- Bot needs a moment to sync

## Quick Test

After adding bot to a chat with Hany:

```bash
# Test the full workflow
python scripts/feishu_bot.py list                              # Find chat ID
python scripts/feishu_bot.py send oc_CHATID "Test message"    # Send message
python scripts/feishu_bot.py read oc_CHATID 5                  # Read responses
```

## Done!

Once the bot is in a chat with Hany, you can:
- ✅ Send automated messages
- ✅ Read conversation history
- ✅ Schedule messages
- ✅ Run from any computer
- ✅ Use in scripts and automation

**The Bot API is production-ready and fully operational!** 🚀
