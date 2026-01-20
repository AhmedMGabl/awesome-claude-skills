#!/usr/bin/env python3
"""
Feishu Bot API Controller
Use official Feishu Bot API for production-ready automation
"""

import os
import sys
import json
import requests
from typing import Optional, List, Dict

# Fix Windows console UTF-8 encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class FeishuBotAPI:
    """Official Feishu Bot API wrapper"""

    def __init__(self):
        self.app_id = os.getenv("FEISHU_APP_ID")
        self.app_secret = os.getenv("FEISHU_APP_SECRET")

        if not self.app_id or not self.app_secret:
            print("[ERROR] Missing credentials!")
            print("Set FEISHU_APP_ID and FEISHU_APP_SECRET environment variables")
            print("\nWindows CMD:")
            print("  set FEISHU_APP_ID=your_app_id")
            print("  set FEISHU_APP_SECRET=your_app_secret")
            print("\nOr run: SETUP_BOT_API.bat")
            sys.exit(1)

        self.base_url = "https://open.feishu.cn/open-apis"
        self.tenant_token = None

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

    def send_message(self, chat_id: str, text: str, msg_type: str = "text") -> bool:
        """Send a message to a chat"""
        # Determine receive_id_type based on chat_id format
        if chat_id.startswith("oc_"):
            receive_id_type = "chat_id"
        elif chat_id.startswith("ou_"):
            receive_id_type = "user_id"
        else:
            receive_id_type = "open_id"

        url = f"{self.base_url}/im/v1/messages?receive_id_type={receive_id_type}"

        headers = {
            "Authorization": f"Bearer {self.get_tenant_token()}",
            "Content-Type": "application/json"
        }

        payload = {
            "receive_id": chat_id,
            "msg_type": msg_type,
            "content": json.dumps({"text": text})
        }

        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        if data.get("code") == 0:
            print(f"[OK] Message sent successfully!")
            print(f"Message ID: {data['data']['message_id']}")
            return True
        else:
            print(f"[ERROR] Failed to send message")
            print(f"Error: {data.get('msg')}")
            print(f"Code: {data.get('code')}")
            return False

    def list_chats(self, page_size: int = 20) -> List[Dict]:
        """List chats where the bot is a member"""
        url = f"{self.base_url}/im/v1/chats"

        headers = {
            "Authorization": f"Bearer {self.get_tenant_token()}"
        }

        params = {
            "page_size": page_size
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if data.get("code") == 0:
            chats = data.get("data", {}).get("items", [])
            print(f"\n[OK] Found {len(chats)} chats:\n")

            for i, chat in enumerate(chats, 1):
                print(f"{i}. {chat.get('name', 'Unknown')}")
                print(f"   Chat ID: {chat.get('chat_id')}")
                print(f"   Description: {chat.get('description', 'N/A')}")
                print()

            return chats
        else:
            print(f"[ERROR] Failed to list chats: {data.get('msg')}")
            return []

    def get_chat_info(self, chat_id: str) -> Optional[Dict]:
        """Get information about a specific chat"""
        url = f"{self.base_url}/im/v1/chats/{chat_id}"

        headers = {
            "Authorization": f"Bearer {self.get_tenant_token()}"
        }

        response = requests.get(url, headers=headers)
        data = response.json()

        if data.get("code") == 0:
            return data.get("data")
        else:
            print(f"[ERROR] Failed to get chat info: {data.get('msg')}")
            return None

    def read_messages(self, chat_id: str, limit: int = 20) -> List[Dict]:
        """Read messages from a chat (requires proper permissions)"""
        url = f"{self.base_url}/im/v1/messages"

        headers = {
            "Authorization": f"Bearer {self.get_tenant_token()}"
        }

        params = {
            "container_id_type": "chat",
            "container_id": chat_id,
            "page_size": limit
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if data.get("code") == 0:
            messages = data.get("data", {}).get("items", [])
            print(f"\n[OK] Read {len(messages)} messages:\n")

            for msg in messages:
                content = json.loads(msg.get("body", {}).get("content", "{}"))
                text = content.get('text', '[non-text message]')
                try:
                    print(f"- {text}")
                except UnicodeEncodeError:
                    print(f"- {text.encode('utf-8', errors='ignore').decode('utf-8')}")

            return messages
        else:
            print(f"[ERROR] Failed to read messages: {data.get('msg')}")
            print(f"Note: Bot needs to be added to the chat first!")
            return []


def main():
    if len(sys.argv) < 2:
        print("""
Feishu Bot API Controller

SETUP:
  1. Set environment variables:
     Windows CMD:
       set FEISHU_APP_ID=your_app_id
       set FEISHU_APP_SECRET=your_app_secret

     Or run: SETUP_BOT_API.bat

  2. Add bot to your chat in Feishu:
     - Open chat
     - Click "..." menu
     - Select "Add Bot"
     - Search for your bot name
     - Add to chat

COMMANDS:
  list                          - List all chats where bot is a member
  info <chat_id>                - Get chat information
  send <chat_id> <message>      - Send message to chat
  read <chat_id> [limit]        - Read messages from chat

EXAMPLES:
  python feishu_bot.py list
  python feishu_bot.py send oc_abc123 "Hello from Bot API!"
  python feishu_bot.py read oc_abc123 50
  python feishu_bot.py info oc_abc123

FINDING CHAT ID:
  1. Run: python feishu_bot.py list
  2. Find your chat in the list
  3. Copy the chat_id (starts with oc_)

IMPORTANT:
  - Bot must be added to the chat before sending messages
  - Chat IDs start with "oc_" for group chats
  - User IDs start with "ou_" for direct messages
""")
        return

    command = sys.argv[1]
    bot = FeishuBotAPI()

    if command == "list":
        bot.list_chats()

    elif command == "info":
        if len(sys.argv) < 3:
            print("[ERROR] Usage: info <chat_id>")
            return

        chat_id = sys.argv[2]
        info = bot.get_chat_info(chat_id)

        if info:
            print("\n[OK] Chat Information:")
            print(json.dumps(info, indent=2))

    elif command == "send":
        if len(sys.argv) < 4:
            print("[ERROR] Usage: send <chat_id> <message>")
            return

        chat_id = sys.argv[2]
        message = " ".join(sys.argv[3:])
        bot.send_message(chat_id, message)

    elif command == "read":
        if len(sys.argv) < 3:
            print("[ERROR] Usage: read <chat_id> [limit]")
            return

        chat_id = sys.argv[2]
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
        bot.read_messages(chat_id, limit)

    else:
        print(f"[ERROR] Unknown command: {command}")


if __name__ == "__main__":
    main()
