#!/usr/bin/env python3
"""
Complete Feishu Chat Fetcher - Using User Credentials
Fetches ALL chats and messages that the user has access to
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import requests

# Fix Windows console UTF-8 encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class FeishuUserDataFetcher:
    """Fetch all Feishu data using user access token"""

    def __init__(self, storage_dir: str = "feishu_data"):
        self.app_id = os.getenv("FEISHU_APP_ID")
        self.app_secret = os.getenv("FEISHU_APP_SECRET")

        if not self.app_id or not self.app_secret:
            print("[ERROR] Missing FEISHU_APP_ID or FEISHU_APP_SECRET")
            print("Run: SETUP_BOT_API.bat")
            sys.exit(1)

        self.base_url = "https://open.feishu.cn/open-apis"
        self.tenant_token = None
        self.user_access_token = None

        # Setup storage
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

        self.db_path = self.storage_dir / "feishu_complete.db"
        self.init_database()

    def init_database(self):
        """Initialize SQLite database with complete schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Chats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                chat_id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                owner_id TEXT,
                owner_name TEXT,
                chat_mode TEXT,
                chat_type TEXT,
                member_count INTEGER,
                avatar TEXT,
                created_at TIMESTAMP,
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_message_time TIMESTAMP
            )
        """)

        # Messages table with extended fields
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                chat_id TEXT,
                parent_id TEXT,
                root_id TEXT,
                sender_id TEXT,
                sender_name TEXT,
                sender_type TEXT,
                msg_type TEXT,
                content TEXT,
                content_json TEXT,
                mentions TEXT,
                reply_to TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                deleted INTEGER DEFAULT 0,
                FOREIGN KEY (chat_id) REFERENCES chats(chat_id)
            )
        """)

        # Chat members table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT,
                member_id TEXT,
                member_name TEXT,
                member_type TEXT,
                added_at TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chats(chat_id),
                UNIQUE(chat_id, member_id)
            )
        """)

        # Message reactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT,
                reaction_type TEXT,
                user_id TEXT,
                user_name TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY (message_id) REFERENCES messages(message_id)
            )
        """)

        # Sync log
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

        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_sender_id ON messages(sender_id)")

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
        print(f"[OK] Got tenant access token")
        return self.tenant_token

    def fetch_all_chats_with_details(self) -> List[Dict]:
        """Fetch all chats with complete details"""
        print("\n[*] Fetching all chats with details...")

        url = f"{self.base_url}/im/v1/chats"
        headers = {"Authorization": f"Bearer {self.get_tenant_token()}"}

        all_chats = []
        page_token = None

        while True:
            params = {"page_size": 100, "user_id_type": "open_id"}
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

            print(f"  [*] Fetched {len(all_chats)} chats so far...")

        print(f"[OK] Found {len(all_chats)} total chats")
        return all_chats

    def fetch_chat_members(self, chat_id: str) -> List[Dict]:
        """Fetch all members of a chat"""
        url = f"{self.base_url}/im/v1/chats/{chat_id}/members"
        headers = {"Authorization": f"Bearer {self.get_tenant_token()}"}

        all_members = []
        page_token = None

        while True:
            params = {"page_size": 100, "member_id_type": "open_id"}
            if page_token:
                params["page_token"] = page_token

            response = requests.get(url, headers=headers, params=params)
            data = response.json()

            if data.get("code") != 0:
                return []

            items = data.get("data", {}).get("items", [])
            all_members.extend(items)

            page_token = data.get("data", {}).get("page_token")
            if not page_token or not items:
                break

        return all_members

    def fetch_all_messages(self, chat_id: str, limit: int = 1000) -> List[Dict]:
        """Fetch ALL messages from a chat (not just 100)"""
        print(f"  [*] Fetching messages from chat: {chat_id[:15]}...")

        url = f"{self.base_url}/im/v1/messages"
        headers = {"Authorization": f"Bearer {self.get_tenant_token()}"}

        all_messages = []
        page_token = None

        while len(all_messages) < limit:
            params = {
                "container_id_type": "chat",
                "container_id": chat_id,
                "page_size": 50
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

            if len(all_messages) % 100 == 0:
                print(f"    [*] Fetched {len(all_messages)} messages...")

        print(f"  [OK] Fetched {len(all_messages)} total messages")
        return all_messages

    def save_chats_to_db(self, chats: List[Dict]):
        """Save chats to database with full details"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for chat in chats:
            cursor.execute("""
                INSERT OR REPLACE INTO chats
                (chat_id, name, description, owner_id, owner_name, chat_mode, chat_type,
                 member_count, avatar, created_at, synced_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                chat.get("chat_id"),
                chat.get("name"),
                chat.get("description"),
                chat.get("owner_id"),
                chat.get("owner_id_type"),
                chat.get("chat_mode"),
                chat.get("chat_type"),
                len(chat.get("members", [])),
                chat.get("avatar"),
                datetime.fromtimestamp(int(chat.get("create_time", 0))) if chat.get("create_time") else None
            ))

        conn.commit()
        conn.close()
        print(f"[OK] Saved {len(chats)} chats to database")

    def save_chat_members_to_db(self, chat_id: str, members: List[Dict]):
        """Save chat members to database"""
        if not members:
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for member in members:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO chat_members
                    (chat_id, member_id, member_name, member_type, added_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    chat_id,
                    member.get("member_id"),
                    member.get("name"),
                    member.get("member_id_type")
                ))
            except Exception as e:
                print(f"  [WARN] Error saving member: {e}")

        conn.commit()
        conn.close()

    def save_messages_to_db(self, chat_id: str, messages: List[Dict]):
        """Save messages to database with full details"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for msg in messages:
            try:
                # Extract message content
                content_json = msg.get("body", {}).get("content", "{}")
                content = json.loads(content_json) if isinstance(content_json, str) else content_json
                text_content = content.get("text", str(content))

                # Extract mentions
                mentions = json.dumps(msg.get("mentions", [])) if msg.get("mentions") else None

                cursor.execute("""
                    INSERT OR REPLACE INTO messages
                    (message_id, chat_id, parent_id, root_id, sender_id, sender_name,
                     sender_type, msg_type, content, content_json, mentions, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    msg.get("message_id"),
                    chat_id,
                    msg.get("parent_id"),
                    msg.get("root_id"),
                    msg.get("sender", {}).get("id"),
                    msg.get("sender", {}).get("sender_name"),
                    msg.get("sender", {}).get("sender_type"),
                    msg.get("msg_type"),
                    text_content,
                    content_json if isinstance(content_json, str) else json.dumps(content_json),
                    mentions,
                    datetime.fromtimestamp(int(msg.get("create_time", 0)) / 1000) if msg.get("create_time") else None,
                    datetime.fromtimestamp(int(msg.get("update_time", 0)) / 1000) if msg.get("update_time") else None
                ))
            except Exception as e:
                print(f"  [WARN] Error saving message: {e}")
                continue

        conn.commit()
        conn.close()

    def export_to_json(self):
        """Export all data to organized JSON files"""
        print("\n[*] Exporting to JSON...")

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Export chats
        cursor.execute("SELECT * FROM chats ORDER BY last_message_time DESC")
        chats = [dict(row) for row in cursor.fetchall()]

        chats_file = self.storage_dir / "all_chats.json"
        with open(chats_file, 'w', encoding='utf-8') as f:
            json.dump(chats, f, indent=2, ensure_ascii=False)
        print(f"[OK] Exported {len(chats)} chats to {chats_file}")

        # Export messages grouped by chat
        messages_dir = self.storage_dir / "all_messages"
        messages_dir.mkdir(exist_ok=True)

        cursor.execute("SELECT DISTINCT chat_id FROM messages")
        chat_ids = [row["chat_id"] for row in cursor.fetchall()]

        total_messages = 0
        for chat_id in chat_ids:
            cursor.execute("""
                SELECT m.*, c.name as chat_name
                FROM messages m
                LEFT JOIN chats c ON m.chat_id = c.chat_id
                WHERE m.chat_id = ?
                ORDER BY m.created_at
            """, (chat_id,))
            messages = [dict(row) for row in cursor.fetchall()]

            if messages:
                chat_name = messages[0].get("chat_name", "unknown")
                safe_name = "".join(c for c in chat_name if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_name = safe_name[:50]

                msg_file = messages_dir / f"{safe_name}_{chat_id[:10]}.json"
                with open(msg_file, 'w', encoding='utf-8') as f:
                    json.dump(messages, f, indent=2, ensure_ascii=False)

                total_messages += len(messages)

        print(f"[OK] Exported {total_messages} messages to {messages_dir}")

        conn.close()

    def generate_report(self):
        """Generate comprehensive summary report"""
        print("\n[*] Generating summary report...")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Statistics
        cursor.execute("SELECT COUNT(*) FROM chats")
        total_chats = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM messages")
        total_messages = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT sender_id) FROM messages")
        unique_senders = cursor.fetchone()[0]

        cursor.execute("""
            SELECT c.name, c.chat_type, COUNT(m.message_id) as msg_count,
                   MAX(m.created_at) as last_msg
            FROM chats c
            LEFT JOIN messages m ON c.chat_id = m.chat_id
            GROUP BY c.chat_id
            ORDER BY msg_count DESC
        """)
        chat_stats = cursor.fetchall()

        # Create report
        report = []
        report.append("=" * 70)
        report.append("COMPLETE FEISHU DATA SYNC REPORT")
        report.append("=" * 70)
        report.append(f"\nSync Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"\nTotal Chats: {total_chats}")
        report.append(f"Total Messages: {total_messages}")
        report.append(f"Unique Senders: {unique_senders}")
        report.append("\n" + "-" * 70)
        report.append("Chat Details (Top 30):")
        report.append("-" * 70)
        report.append(f"{'Chat Name':<45} {'Type':<12} {'Messages':>8}")
        report.append("-" * 70)

        for name, chat_type, count, last_msg in chat_stats[:30]:
            name = name or "Unknown"
            chat_type = chat_type or "Unknown"
            report.append(f"{name[:44]:<45} {chat_type:<12} {count:>8}")

        report.append("\n" + "=" * 70)
        report.append(f"Database: {self.db_path.absolute()}")
        report.append(f"JSON Exports: {self.storage_dir.absolute()}")
        report.append("=" * 70)

        report_text = "\n".join(report)
        print("\n" + report_text)

        # Save report
        report_file = self.storage_dir / "complete_sync_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_text)

        print(f"\n[OK] Report saved to {report_file}")

        conn.close()

    def sync_everything(self, message_limit_per_chat: int = 1000):
        """Sync ALL Feishu data - complete extraction"""
        print("\n" + "=" * 70)
        print("COMPLETE FEISHU DATA SYNC - STARTING")
        print("=" * 70)

        sync_start = datetime.now()

        try:
            # Fetch all chats
            chats = self.fetch_all_chats_with_details()
            self.save_chats_to_db(chats)

            # Fetch messages and members for each chat
            print(f"\n[*] Fetching messages from all {len(chats)} chats...")
            total_messages = 0

            for i, chat in enumerate(chats, 1):
                chat_id = chat.get("chat_id")
                chat_name = chat.get("name", "Unknown")

                print(f"\n[{i}/{len(chats)}] Processing: {chat_name}")

                # Fetch messages
                messages = self.fetch_all_messages(chat_id, limit=message_limit_per_chat)
                if messages:
                    self.save_messages_to_db(chat_id, messages)
                    total_messages += len(messages)

                # Fetch members
                members = self.fetch_chat_members(chat_id)
                if members:
                    self.save_chat_members_to_db(chat_id, members)
                    print(f"  [OK] Saved {len(members)} members")

            print(f"\n[OK] Fetched {total_messages} total messages from all chats")

            # Export everything
            self.export_to_json()

            # Generate report
            self.generate_report()

            sync_duration = (datetime.now() - sync_start).total_seconds()
            print(f"\n[SUCCESS] Complete sync finished in {sync_duration:.1f} seconds")
            print(f"\n[NEXT] Check the database and JSON files in: {self.storage_dir.absolute()}")

        except Exception as e:
            print(f"\n[ERROR] Sync failed: {e}")
            import traceback
            traceback.print_exc()
            raise


def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║  Feishu Complete Data Fetcher - Using User Access           ║
║  Fetches ALL chats and messages you have access to          ║
╚══════════════════════════════════════════════════════════════╝
    """)

    fetcher = FeishuUserDataFetcher()

    # Sync everything with high message limit
    fetcher.sync_everything(message_limit_per_chat=1000)


if __name__ == "__main__":
    main()
