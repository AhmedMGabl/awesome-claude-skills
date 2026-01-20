#!/usr/bin/env python3
"""
Extract ALL visible chat data from Feishu
Uses browser data and API to get complete chat history
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import requests

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class CompleteFeishuExtractor:
    """Extract EVERYTHING from Feishu - all chats, all messages, all context"""

    def __init__(self, storage_dir: str = "feishu_data/complete_extraction"):
        self.app_id = os.getenv("FEISHU_APP_ID")
        self.app_secret = os.getenv("FEISHU_APP_SECRET")

        if not self.app_id or not self.app_secret:
            print("[ERROR] Missing credentials")
            sys.exit(1)

        self.base_url = "https://open.feishu.cn/open-apis"
        self.tenant_token = None

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = self.storage_dir / "ahmed_complete_context.db"
        self.init_database()

        # List of all visible chats from browser
        self.visible_chats = [
            {"name": "王东", "id": "hany_wang_dong", "type": "1-on-1", "priority": "HIGH"},
            {"name": "AI Efficient Center", "type": "group", "priority": "MEDIUM"},
            {"name": "AIEC ME", "type": "group", "priority": "HIGH"},
            {"name": "Hassan Alkarmy", "type": "1-on-1", "priority": "MEDIUM"},
            {"name": "AI Hackers", "type": "group", "priority": "LOW"},
            {"name": "ARRT - Automatically Report Refresher Toolkit", "type": "group", "priority": "HIGH"},
            {"name": "Ahmed Abogabl, Hany", "type": "group", "priority": "HIGH"},
            {"name": "Mohamad Atef", "type": "1-on-1", "priority": "MEDIUM"},
            {"name": "Moustafa Mohamed", "type": "1-on-1", "priority": "MEDIUM"},
            {"name": "Youssef Reda", "type": "1-on-1", "priority": "MEDIUM"},
            {"name": "Ahmed Ezzat", "type": "1-on-1", "priority": "LOW"},
            {"name": "Muhammad Ashraf", "type": "1-on-1", "priority": "LOW"},
            {"name": "Mostafa Mahmoud 白杨", "type": "1-on-1", "priority": "MEDIUM"},
            {"name": "Hadeel Manaseer 李姝", "type": "1-on-1", "priority": "MEDIUM"},
            {"name": "陈玲", "type": "1-on-1", "priority": "LOW"},
            {"name": "FSD-Atomic-CM", "type": "group", "priority": "MEDIUM"},
            {"name": "Qays Basim", "type": "1-on-1", "priority": "MEDIUM"},
            {"name": "罗悦兰Lorraine", "type": "1-on-1", "priority": "LOW"},
            {"name": "Omar Abdelghany", "type": "1-on-1", "priority": "LOW"},
            {"name": "Remonda Zakhary", "type": "1-on-1", "priority": "MEDIUM"},
            {"name": "孙可", "type": "1-on-1", "priority": "LOW"},
        ]

    def init_database(self):
        """Initialize comprehensive database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Chats with extended metadata
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                chat_id TEXT PRIMARY KEY,
                name TEXT,
                type TEXT,
                priority TEXT,
                description TEXT,
                member_count INTEGER,
                total_messages INTEGER DEFAULT 0,
                last_extracted TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Messages with full context
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                chat_id TEXT,
                sender_id TEXT,
                sender_name TEXT,
                msg_type TEXT,
                content TEXT,
                reply_to TEXT,
                reactions TEXT,
                created_at TIMESTAMP,
                extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chats(chat_id)
            )
        """)

        # Insights and patterns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                insight TEXT,
                source_chat TEXT,
                source_messages TEXT,
                confidence TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Hany-specific insights
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hany_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                pattern TEXT,
                examples TEXT,
                frequency TEXT,
                importance TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        response = requests.post(url, json={"app_id": self.app_id, "app_secret": self.app_secret})
        data = response.json()

        if data.get("code") != 0:
            raise Exception(f"Failed to get token: {data.get('msg')}")

        self.tenant_token = data["tenant_access_token"]
        return self.tenant_token

    def fetch_all_accessible_chats(self) -> List[Dict]:
        """Fetch all chats the bot has access to"""
        print("\n[*] Fetching all accessible chats...")

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
                print(f"[WARN] API returned: {data.get('msg')}")
                break

            items = data.get("data", {}).get("items", [])
            all_chats.extend(items)

            page_token = data.get("data", {}).get("page_token")
            if not page_token or not items:
                break

        print(f"[OK] Found {len(all_chats)} accessible chats via API")
        return all_chats

    def fetch_messages_comprehensive(self, chat_id: str, chat_name: str) -> List[Dict]:
        """Fetch ALL messages from a chat with retries"""
        print(f"  [*] Extracting: {chat_name}")

        url = f"{self.base_url}/im/v1/messages"
        headers = {"Authorization": f"Bearer {self.get_tenant_token()}"}

        all_messages = []
        page_token = None
        max_retries = 3

        while len(all_messages) < 10000:  # Safety limit
            retry_count = 0

            while retry_count < max_retries:
                try:
                    params = {
                        "container_id_type": "chat",
                        "container_id": chat_id,
                        "page_size": 50
                    }
                    if page_token:
                        params["page_token"] = page_token

                    response = requests.get(url, headers=headers, params=params, timeout=30)
                    data = response.json()

                    if data.get("code") != 0:
                        print(f"  [WARN] {data.get('msg')}")
                        return all_messages

                    items = data.get("data", {}).get("items", [])
                    if not items:
                        return all_messages

                    all_messages.extend(items)

                    if len(all_messages) % 100 == 0:
                        print(f"    [*] {len(all_messages)} messages...")

                    page_token = data.get("data", {}).get("page_token")
                    if not page_token:
                        return all_messages

                    break  # Success, exit retry loop

                except Exception as e:
                    retry_count += 1
                    print(f"  [WARN] Retry {retry_count}/{max_retries}: {e}")
                    if retry_count >= max_retries:
                        return all_messages

        return all_messages

    def save_complete_data(self, chats: List[Dict], all_messages: Dict[str, List[Dict]]):
        """Save everything to database and files"""
        print("\n[*] Saving complete data...")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Save chats
        for chat in chats:
            chat_id = chat.get("chat_id", chat.get("id", "unknown"))
            chat_name = chat.get("name", "Unknown")
            msg_count = len(all_messages.get(chat_id, []))

            cursor.execute("""
                INSERT OR REPLACE INTO chats
                (chat_id, name, type, total_messages, last_extracted)
                VALUES (?, ?, ?, ?, ?)
            """, (chat_id, chat_name, chat.get("type", "unknown"), msg_count, datetime.now()))

        # Save all messages
        total_saved = 0
        for chat_id, messages in all_messages.items():
            for msg in messages:
                try:
                    content_json = msg.get("body", {}).get("content", "{}")
                    content = json.loads(content_json) if isinstance(content_json, str) else content_json
                    text_content = content.get("text", str(content))

                    cursor.execute("""
                        INSERT OR REPLACE INTO messages
                        (message_id, chat_id, sender_id, sender_name, msg_type, content, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        msg.get("message_id"),
                        chat_id,
                        msg.get("sender", {}).get("id"),
                        msg.get("sender", {}).get("sender_name"),
                        msg.get("msg_type"),
                        text_content,
                        datetime.fromtimestamp(int(msg.get("create_time", 0)) / 1000) if msg.get("create_time") else None
                    ))
                    total_saved += 1
                except Exception as e:
                    print(f"  [WARN] Error saving message: {e}")

        conn.commit()
        conn.close()

        print(f"[OK] Saved {total_saved} messages to database")

    def extract_all(self):
        """Extract EVERYTHING"""
        print("\n" + "=" * 70)
        print("COMPLETE FEISHU EXTRACTION - GETTING EVERYTHING")
        print("=" * 70)

        # Fetch all chats via API
        api_chats = self.fetch_all_accessible_chats()

        # Combine with known visible chats
        all_chat_refs = {}

        for chat in api_chats:
            chat_id = chat.get("chat_id")
            all_chat_refs[chat_id] = chat

        print(f"\n[*] Total unique chats to process: {len(all_chat_refs)}")

        # Extract messages from each chat
        all_messages = {}

        for i, (chat_id, chat_info) in enumerate(all_chat_refs.items(), 1):
            chat_name = chat_info.get("name", "Unknown")
            print(f"\n[{i}/{len(all_chat_refs)}] Processing: {chat_name}")

            messages = self.fetch_messages_comprehensive(chat_id, chat_name)
            if messages:
                all_messages[chat_id] = messages
                print(f"  [OK] Got {len(messages)} messages")
            else:
                print(f"  [SKIP] No messages accessible")

        # Save everything
        self.save_complete_data(list(all_chat_refs.values()), all_messages)

        # Export to JSON
        self.export_everything(all_chat_refs, all_messages)

        print("\n[SUCCESS] Complete extraction finished!")
        print(f"[LOCATION] {self.storage_dir.absolute()}")

    def export_everything(self, chats: Dict, messages: Dict):
        """Export everything to organized JSON files"""
        print("\n[*] Exporting to JSON...")

        # Export chats list
        chats_file = self.storage_dir / "all_chats_complete.json"
        with open(chats_file, 'w', encoding='utf-8') as f:
            json.dump(list(chats.values()), f, indent=2, ensure_ascii=False)
        print(f"[OK] Chats: {chats_file}")

        # Export messages by chat
        messages_dir = self.storage_dir / "messages"
        messages_dir.mkdir(exist_ok=True)

        for chat_id, msgs in messages.items():
            chat_name = chats.get(chat_id, {}).get("name", "unknown")
            safe_name = "".join(c for c in chat_name if c.isalnum() or c in (' ', '-', '_')).strip()[:50]

            msg_file = messages_dir / f"{safe_name}_{chat_id[:10]}.json"
            with open(msg_file, 'w', encoding='utf-8') as f:
                json.dump(msgs, f, indent=2, ensure_ascii=False)

        print(f"[OK] Messages: {messages_dir}")


def main():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║     COMPLETE FEISHU DATA EXTRACTION                          ║
    ║     Getting EVERYTHING for permanent context                 ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    extractor = CompleteFeishuExtractor()
    extractor.extract_all()


if __name__ == "__main__":
    main()
