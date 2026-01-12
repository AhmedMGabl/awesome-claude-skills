#!/usr/bin/env python3
"""
Chat Backup & Analytics Example
Backup all chats and generate analytics
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent))
from feishu_pro import FeishuPro

async def backup_all_chats():
    """Backup all chat histories to JSON files"""
    app = FeishuPro()
    await app.start()

    # Create backup directory
    backup_dir = Path(f"feishu_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    backup_dir.mkdir(exist_ok=True)

    print(f"[*] Creating backup in: {backup_dir}")

    # Get all chats
    chats = await app.get_chat_list()
    print(f"[*] Found {len(chats)} chats to backup")

    successful = 0
    failed = 0

    for chat in chats:
        try:
            # Sanitize filename
            safe_name = "".join(c for c in chat if c.isalnum() or c in (' ', '-', '_')).strip()
            filename = backup_dir / f"{safe_name}.json"

            print(f"[*] Backing up: {chat}")
            await app.export_chat_history(chat, str(filename))

            successful += 1
        except Exception as e:
            print(f"[ERROR] Failed to backup {chat}: {e}")
            failed += 1

        # Small delay
        await asyncio.sleep(1)

    print(f"\n[OK] Backup complete: {successful} successful, {failed} failed")
    print(f"[OK] Files saved to: {backup_dir}")

    await app.close()

async def analyze_chat(chat_name: str):
    """Generate analytics for a specific chat"""
    app = FeishuPro()
    await app.start()

    print(f"[*] Analyzing chat: {chat_name}")

    # Read all messages
    messages = await app.read_messages(chat_name, limit=500)

    if not messages:
        print("[ERROR] No messages found")
        await app.close()
        return

    print(f"\n=== Chat Analytics: {chat_name} ===")
    print(f"Total messages: {len(messages)}")

    # Word frequency
    all_text = " ".join(msg["text"] for msg in messages)
    words = all_text.lower().split()
    word_freq = Counter(words)

    print(f"\nMost common words:")
    for word, count in word_freq.most_common(10):
        if len(word) > 3:  # Skip short words
            print(f"  - {word}: {count}")

    # Message length stats
    lengths = [len(msg["text"]) for msg in messages]
    avg_length = sum(lengths) / len(lengths)
    print(f"\nAverage message length: {avg_length:.1f} characters")
    print(f"Shortest message: {min(lengths)} characters")
    print(f"Longest message: {max(lengths)} characters")

    # Time-based stats (if timestamps available)
    timestamps = [msg.get("timestamp") for msg in messages if msg.get("timestamp")]
    if timestamps:
        print(f"\nFirst message: {timestamps[0]}")
        print(f"Last message: {timestamps[-1]}")

    # Export detailed report
    report = {
        "chat": chat_name,
        "analyzed_at": datetime.now().isoformat(),
        "total_messages": len(messages),
        "avg_message_length": avg_length,
        "word_frequency": dict(word_freq.most_common(50)),
        "messages": messages
    }

    report_file = f"analysis_{chat_name}_{datetime.now().strftime('%Y%m%d')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Detailed report saved to: {report_file}")

    await app.close()

async def backup_important_chats():
    """Backup only important chats (with many unread messages)"""
    app = FeishuPro()
    await app.start()

    print("[*] Identifying important chats...")

    # Get chats with unread messages
    unread = await app.get_unread_count()

    # Sort by unread count
    important_chats = sorted(unread.items(), key=lambda x: x[1], reverse=True)[:10]

    if not important_chats:
        print("[*] No chats with unread messages")
        await app.close()
        return

    print(f"[*] Backing up {len(important_chats)} important chats:")
    for chat, count in important_chats:
        print(f"  - {chat}: {count} unread")

    backup_dir = Path(f"important_backup_{datetime.now().strftime('%Y%m%d')}")
    backup_dir.mkdir(exist_ok=True)

    for chat, _ in important_chats:
        safe_name = "".join(c for c in chat if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = backup_dir / f"{safe_name}.json"
        await app.export_chat_history(chat, str(filename))
        print(f"[OK] Backed up: {chat}")
        await asyncio.sleep(1)

    print(f"\n[OK] Important chats backed up to: {backup_dir}")
    await app.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "all":
            asyncio.run(backup_all_chats())
        elif command == "important":
            asyncio.run(backup_important_chats())
        elif command == "analyze" and len(sys.argv) > 2:
            asyncio.run(analyze_chat(sys.argv[2]))
        else:
            print("""
Chat Backup & Analytics

Usage:
  python chat_backup.py all              - Backup all chats
  python chat_backup.py important        - Backup important chats (with unreads)
  python chat_backup.py analyze <chat>   - Analyze specific chat

Examples:
  python chat_backup.py all
  python chat_backup.py important
  python chat_backup.py analyze "Team Chat"
""")
    else:
        # Default: backup important chats
        asyncio.run(backup_important_chats())
