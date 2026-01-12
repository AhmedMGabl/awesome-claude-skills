#!/usr/bin/env python3
"""
Daily Standup Bot Example
Sends automated standup reminders to team members
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import feishu_pro
sys.path.insert(0, str(Path(__file__).parent.parent))
from feishu_pro import FeishuPro

async def daily_standup():
    """Send daily standup reminder to team"""
    app = FeishuPro()
    await app.start()

    # Define team members
    team = ["John", "Sarah", "Mike", "Alice"]

    # Create standup message
    message = """Daily Standup - 10:00 AM

Please share:
1. What you completed yesterday
2. What you're working on today
3. Any blockers

Join the call: https://meet.example.com/standup"""

    print("[*] Sending standup reminder to team...")

    # Send to all team members
    results = await app.batch_send(team, message)

    # Report results
    successful = [name for name, success in results.items() if success]
    failed = [name for name, success in results.items() if not success]

    print(f"\n[OK] Sent to: {', '.join(successful)}")
    if failed:
        print(f"[ERROR] Failed to send to: {', '.join(failed)}")

    await app.close()

async def send_standup_summary(summary_text: str):
    """Send standup summary after meeting"""
    app = FeishuPro()
    await app.start()

    # Send summary to team chat
    enhanced_summary = f"""Standup Summary - {asyncio.get_event_loop().time()}

{summary_text}

Thanks everyone for participating!"""

    await app.send_message("Team Chat", enhanced_summary, enhance="professional")

    await app.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "summary":
        summary = " ".join(sys.argv[2:])
        asyncio.run(send_standup_summary(summary))
    else:
        asyncio.run(daily_standup())
