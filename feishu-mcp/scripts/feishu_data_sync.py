#!/usr/bin/env python3
"""
Feishu Data Sync - Complete Data Fetcher
Fetches all your Feishu data and creates local storage
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import requests

# Fix Windows console UTF-8 encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class FeishuDataSync:
    """Fetch and store all Feishu data locally"""

    def __init__(self, storage_dir: str = "feishu_data"):
        self.app_id = os.getenv("FEISHU_APP_ID")
        self.app_secret = os.getenv("FEISHU_APP_SECRET")

        if not self.app_id or not self.app_secret:
            print("[ERROR] Missing credentials!")
            print("Run: SETUP_BOT_API.bat")
            sys.exit(1)

        self.base_url = "https://open.feishu.cn/open-apis"
        self.tenant_token = None

        # Setup storage
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

        self.db_path = self.storage_dir / "feishu.db"
        self.init_database()

    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Chats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                chat_id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                owner_id TEXT,
                chat_mode TEXT,
                chat_type TEXT,
                member_count INTEGER,
                created_at TIMESTAMP,
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                chat_id TEXT,
                sender_id TEXT,
                sender_name TEXT,
                msg_type TEXT,
                content TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chats(chat_id)
            )
        """)

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                en_name TEXT,
                email TEXT,
                mobile TEXT,
                department TEXT,
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Sync log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sync_type TEXT,
                items_synced INTEGER,
                status TEXT,
                error TEXT,
                started_at TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()
        print(f"[OK] Database initialized: {self.db_path}")

    def get_tenant_token(self) -> str:
        """Get tenant access token"""
        if self.tenant_token:
            return self.tenant_token

        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        response = requests.post(url, json=payload)
        data = response.json()

        if data.get("code") != 0:
            raise Exception(f"Failed to get token: {data.get('msg')}")

        self.tenant_token = data["tenant_access_token"]
        return self.tenant_token

    def fetch_all_chats(self) -> List[Dict]:
        """Fetch all chats where bot is a member"""
        print("\n[*] Fetching all chats...")

        url = f"{self.base_url}/im/v1/chats"
        headers = {"Authorization": f"Bearer {self.get_tenant_token()}"}

        all_chats = []
        page_token = None

        while True:
            params = {"page_size": 100}
            if page_token:
                params["page_token"] = page_token

            response = requests.get(url, headers=headers, params=params)
            data = response.json()

            if data.get("code") != 0:
                print(f"[ERROR] Failed to fetch chats: {data.get('msg')}")
                break

            items = data.get("data", {}).get("items", [])
            all_chats.extend(items)

            page_token = data.get("data", {}).get("page_token")
            if not page_token or not items:
                break

        print(f"[OK] Found {len(all_chats)} chats")
        return all_chats

    def fetch_chat_messages(self, chat_id: str, limit: int = 100) -> List[Dict]:
        """Fetch messages from a specific chat"""
        print(f"  [*] Fetching messages from chat: {chat_id[:15]}...")

        url = f"{self.base_url}/im/v1/messages"
        headers = {"Authorization": f"Bearer {self.get_tenant_token()}"}

        all_messages = []
        page_token = None

        while len(all_messages) < limit:
            params = {
                "container_id_type": "chat",
                "container_id": chat_id,
                "page_size": min(50, limit - len(all_messages))
            }
            if page_token:
                params["page_token"] = page_token

            response = requests.get(url, headers=headers, params=params)
            data = response.json()

            if data.get("code") != 0:
                print(f"  [WARN] Could not fetch messages: {data.get('msg')}")
                break

            items = data.get("data", {}).get("items", [])
            if not items:
                break

            all_messages.extend(items)

            page_token = data.get("data", {}).get("page_token")
            if not page_token:
                break

        print(f"  [OK] Fetched {len(all_messages)} messages")
        return all_messages

    def save_chats_to_db(self, chats: List[Dict]):
        """Save chats to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for chat in chats:
            cursor.execute("""
                INSERT OR REPLACE INTO chats
                (chat_id, name, description, owner_id, chat_mode, chat_type, member_count, created_at, synced_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                chat.get("chat_id"),
                chat.get("name"),
                chat.get("description"),
                chat.get("owner_id"),
                chat.get("chat_mode"),
                chat.get("chat_type"),
                len(chat.get("members", [])),
                datetime.fromtimestamp(int(chat.get("create_time", 0))) if chat.get("create_time") else None
            ))

        conn.commit()
        conn.close()
        print(f"[OK] Saved {len(chats)} chats to database")

    def save_messages_to_db(self, chat_id: str, messages: List[Dict]):
        """Save messages to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for msg in messages:
            try:
                # Extract message content
                content_json = msg.get("body", {}).get("content", "{}")
                content = json.loads(content_json) if isinstance(content_json, str) else content_json
                text_content = content.get("text", str(content))

                cursor.execute("""
                    INSERT OR REPLACE INTO messages
                    (message_id, chat_id, sender_id, sender_name, msg_type, content, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    msg.get("message_id"),
                    chat_id,
                    msg.get("sender", {}).get("id"),
                    msg.get("sender", {}).get("sender_name"),
                    msg.get("msg_type"),
                    text_content,
                    datetime.fromtimestamp(int(msg.get("create_time", 0)) / 1000) if msg.get("create_time") else None,
                    datetime.fromtimestamp(int(msg.get("update_time", 0)) / 1000) if msg.get("update_time") else None
                ))
            except Exception as e:
                print(f"  [WARN] Error saving message: {e}")
                continue

        conn.commit()
        conn.close()

    def export_to_json(self):
        """Export all data to JSON files"""
        print("\n[*] Exporting to JSON...")

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Export chats
        cursor.execute("SELECT * FROM chats")
        chats = [dict(row) for row in cursor.fetchall()]

        chats_file = self.storage_dir / "chats.json"
        with open(chats_file, 'w', encoding='utf-8') as f:
            json.dump(chats, f, indent=2, ensure_ascii=False)
        print(f"[OK] Exported {len(chats)} chats to {chats_file}")

        # Export messages grouped by chat
        cursor.execute("SELECT DISTINCT chat_id FROM messages")
        chat_ids = [row["chat_id"] for row in cursor.fetchall()]

        messages_dir = self.storage_dir / "messages"
        messages_dir.mkdir(exist_ok=True)

        total_messages = 0
        for chat_id in chat_ids:
            cursor.execute("SELECT * FROM messages WHERE chat_id = ? ORDER BY created_at", (chat_id,))
            messages = [dict(row) for row in cursor.fetchall()]

            if messages:
                # Get chat name for filename
                cursor.execute("SELECT name FROM chats WHERE chat_id = ?", (chat_id,))
                chat_row = cursor.fetchone()
                chat_name = chat_row["name"] if chat_row else "unknown"

                # Sanitize filename
                safe_name = "".join(c for c in chat_name if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_name = safe_name[:50]  # Limit length

                msg_file = messages_dir / f"{safe_name}_{chat_id[:10]}.json"
                with open(msg_file, 'w', encoding='utf-8') as f:
                    json.dump(messages, f, indent=2, ensure_ascii=False)

                total_messages += len(messages)

        print(f"[OK] Exported {total_messages} messages to {messages_dir}")

        conn.close()

    def generate_summary_report(self):
        """Generate summary report"""
        print("\n[*] Generating summary report...")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Count statistics
        cursor.execute("SELECT COUNT(*) FROM chats")
        total_chats = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM messages")
        total_messages = cursor.fetchone()[0]

        cursor.execute("""
            SELECT c.name, c.chat_id, COUNT(m.message_id) as msg_count
            FROM chats c
            LEFT JOIN messages m ON c.chat_id = m.chat_id
            GROUP BY c.chat_id
            ORDER BY msg_count DESC
        """)
        chat_stats = cursor.fetchall()

        # Create report
        report = []
        report.append("=" * 60)
        report.append("FEISHU DATA SYNC SUMMARY")
        report.append("=" * 60)
        report.append(f"\nSync Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"\nTotal Chats: {total_chats}")
        report.append(f"Total Messages: {total_messages}")
        report.append("\n" + "-" * 60)
        report.append("Chat Statistics:")
        report.append("-" * 60)

        for name, chat_id, count in chat_stats[:20]:  # Top 20
            report.append(f"{name[:40]:40} | {count:5} messages")

        report.append("\n" + "=" * 60)
        report.append(f"Data Location: {self.storage_dir.absolute()}")
        report.append(f"Database: {self.db_path.absolute()}")
        report.append("=" * 60)

        report_text = "\n".join(report)
        print("\n" + report_text)

        # Save report
        report_file = self.storage_dir / "sync_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_text)

        print(f"\n[OK] Report saved to {report_file}")

        conn.close()

    def log_sync(self, sync_type: str, items_synced: int, status: str, error: str = None):
        """Log sync operation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO sync_log (sync_type, items_synced, status, error, started_at, completed_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (sync_type, items_synced, status, error))

        conn.commit()
        conn.close()

    def sync_all(self, fetch_messages: bool = True, message_limit: int = 100):
        """Sync all Feishu data"""
        print("\n" + "=" * 60)
        print("FEISHU DATA SYNC - STARTING")
        print("=" * 60)

        sync_start = datetime.now()

        try:
            # Fetch and save chats
            chats = self.fetch_all_chats()
            self.save_chats_to_db(chats)
            self.log_sync("chats", len(chats), "success")

            # Fetch and save messages
            if fetch_messages:
                print("\n[*] Fetching messages from all chats...")
                total_messages = 0

                for i, chat in enumerate(chats, 1):
                    chat_id = chat.get("chat_id")
                    chat_name = chat.get("name", "Unknown")
                    print(f"\n[{i}/{len(chats)}] Processing: {chat_name}")

                    messages = self.fetch_chat_messages(chat_id, limit=message_limit)
                    if messages:
                        self.save_messages_to_db(chat_id, messages)
                        total_messages += len(messages)

                print(f"\n[OK] Fetched {total_messages} total messages")
                self.log_sync("messages", total_messages, "success")

            # Export to JSON
            self.export_to_json()

            # Generate report
            self.generate_summary_report()

            sync_duration = (datetime.now() - sync_start).total_seconds()
            print(f"\n[OK] Sync completed in {sync_duration:.1f} seconds")

        except Exception as e:
            print(f"\n[ERROR] Sync failed: {e}")
            self.log_sync("full_sync", 0, "failed", str(e))
            raise


def main():
    if len(sys.argv) < 2:
        print("""
Feishu Data Sync - Complete Data Fetcher

SETUP:
  1. Set credentials:
     Windows: run SETUP_BOT_API.bat

  2. Make sure bot is added to chats you want to sync

COMMANDS:
  sync [--no-messages]          - Sync all data
  sync --limit N                - Sync with message limit (default: 100)
  report                        - Show summary report
  export                        - Export to JSON only

EXAMPLES:
  python feishu_data_sync.py sync                    # Full sync
  python feishu_data_sync.py sync --limit 500        # Fetch up to 500 messages per chat
  python feishu_data_sync.py sync --no-messages      # Only fetch chats (no messages)
  python feishu_data_sync.py report                  # Show report

OUTPUT:
  All data saved to: ./feishu_data/
  - feishu.db              (SQLite database)
  - chats.json             (All chats)
  - messages/*.json        (Messages by chat)
  - sync_report.txt        (Summary report)

NOTE:
  - Bot can only access chats it's a member of
  - First sync may take a few minutes
  - Subsequent syncs are faster (updates only)
""")
        return

    command = sys.argv[1]
    syncer = FeishuDataSync()

    if command == "sync":
        fetch_messages = "--no-messages" not in sys.argv

        # Get message limit
        message_limit = 100
        if "--limit" in sys.argv:
            try:
                limit_idx = sys.argv.index("--limit")
                message_limit = int(sys.argv[limit_idx + 1])
            except (ValueError, IndexError):
                print("[WARN] Invalid limit, using default: 100")

        syncer.sync_all(fetch_messages=fetch_messages, message_limit=message_limit)

    elif command == "report":
        syncer.generate_summary_report()

    elif command == "export":
        syncer.export_to_json()

    else:
        print(f"[ERROR] Unknown command: {command}")


if __name__ == "__main__":
    main()
