#!/usr/bin/env python3
"""
Auto Responder Example
Automatically responds to unread messages with smart replies
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from feishu_pro import FeishuPro

async def auto_respond_to_unread():
    """Respond to all unread messages with appropriate smart replies"""
    app = FeishuPro()
    await app.start()

    print("[*] Checking for unread messages...")

    # Get unread messages
    unread = await app.get_unread_count()

    if not unread:
        print("[OK] No unread messages")
        await app.close()
        return

    print(f"\n[*] Found unread messages in {len(unread)} chats")

    for chat, count in unread.items():
        print(f"\n[*] Processing {chat} ({count} unread)...")

        # Read last few messages to understand context
        messages = await app.read_messages(chat, limit=5)

        if not messages:
            continue

        last_message = messages[-1]["text"].lower()

        # Determine appropriate intent based on message content
        if any(word in last_message for word in ["thanks", "thank you"]):
            intent = "acknowledge"
        elif "?" in last_message:
            intent = "question"
        elif any(word in last_message for word in ["agree", "good idea", "sounds good"]):
            intent = "agree"
        elif any(word in last_message for word in ["meeting", "schedule", "call"]):
            intent = "schedule"
        else:
            intent = "acknowledge"

        # Send smart reply
        await app.send_smart_reply(chat, intent)

        # Mark as read
        await app.mark_as_read(chat)

        print(f"[OK] Responded to {chat} with {intent} intent")

        # Small delay to avoid rate limiting
        await asyncio.sleep(2)

    print("\n[OK] All unread messages processed")
    await app.close()

async def vacation_responder():
    """Send vacation auto-reply to all incoming messages"""
    app = FeishuPro()
    await app.start()

    vacation_message = """I'm currently on vacation and will have limited access to messages.

I'll respond to your message when I return on [date].

For urgent matters, please contact [backup person] at [contact].

Thanks for your understanding!"""

    print("[*] Setting up vacation responder...")

    # Get unread messages
    unread = await app.get_unread_count()

    for chat in unread.keys():
        await app.send_message(chat, vacation_message)
        await app.mark_as_read(chat)
        print(f"[OK] Sent vacation reply to {chat}")
        await asyncio.sleep(2)

    print("[OK] Vacation responder complete")
    await app.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "vacation":
        asyncio.run(vacation_responder())
    else:
        asyncio.run(auto_respond_to_unread())
