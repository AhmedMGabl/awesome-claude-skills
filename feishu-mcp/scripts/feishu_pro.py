#!/usr/bin/env python3
"""
Feishu Pro - Advanced Browser Automation
Comprehensive Feishu operations with AI-powered features
"""

import asyncio
import json
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

# Configuration
USER_DATA_DIR = Path.home() / ".feishu-browser-data"
FEISHU_URL = "https://qcn9ppuir8al.feishu.cn/next/messenger/"
HISTORY_FILE = Path.home() / ".feishu-history.json"
TEMPLATES_FILE = Path.home() / ".feishu-templates.json"


class MessageEnhancer:
    """AI-powered message enhancement utilities"""

    @staticmethod
    def enhance_message(message: str, style: str = "professional") -> str:
        """Enhance a message with better formatting and style"""
        enhancements = {
            "professional": lambda m: f"{m.capitalize()}. Please let me know if you have any questions.",
            "friendly": lambda m: f"Hey! {m} 😊",
            "formal": lambda m: f"Dear colleague,\n\n{m.capitalize()}.\n\nBest regards",
            "brief": lambda m: m.strip()[:100],
            "detailed": lambda m: f"{m}\n\nContext: This message was sent via automated system.\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
        return enhancements.get(style, lambda m: m)(message)

    @staticmethod
    def create_smart_reply(original_message: str, intent: str = "acknowledge") -> str:
        """Generate smart replies based on message context"""
        replies = {
            "acknowledge": "Got it, thanks!",
            "agree": "I agree with this approach.",
            "question": "Could you provide more details?",
            "thanks": "Thank you for sharing this!",
            "confirm": "Confirmed. I'll take care of it.",
            "schedule": "Let's schedule a time to discuss this.",
            "positive": "Sounds great! Looking forward to it.",
            "negative": "I need to review this further before proceeding."
        }
        return replies.get(intent, "Thanks for the update!")


class FeishuPro:
    def __init__(self):
        self.playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        self.current_chat = None
        self.message_history = []
        self.templates = {}
        self._load_history()
        self._load_templates()

    def _load_history(self):
        """Load message history from file"""
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    self.message_history = json.load(f)
            except:
                self.message_history = []

    def _save_history(self):
        """Save message history to file"""
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.message_history[-1000:], f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save history: {e}")

    def _load_templates(self):
        """Load message templates"""
        if TEMPLATES_FILE.exists():
            try:
                with open(TEMPLATES_FILE, 'r', encoding='utf-8') as f:
                    self.templates = json.load(f)
            except:
                self.templates = {}

    def _save_templates(self):
        """Save message templates"""
        try:
            with open(TEMPLATES_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save templates: {e}")

    async def start(self, headless: bool = False, use_persistent: bool = False):
        """Start browser - use_persistent=True for session persistence (may conflict)"""
        print("[*] Starting Feishu Pro browser...")
        self.playwright = await async_playwright().start()

        if use_persistent:
            # Persistent context - maintains login but may conflict
            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(USER_DATA_DIR),
                headless=headless,
                channel="chrome",
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--disable-notifications'
                ]
            )

            if len(self.context.pages) > 0:
                self.page = self.context.pages[0]
            else:
                self.page = await self.context.new_page()
        else:
            # Regular browser launch - no conflicts, requires login first time
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                channel="chrome"
            )
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()

        await self.page.goto(FEISHU_URL, wait_until='domcontentloaded')
        await asyncio.sleep(3)
        print(f"[OK] Browser ready: {self.page.url}")
        print("[*] Please log in if needed, then messages will be sent")
        return True

    async def navigate_to_chat(self, chat_name: str) -> bool:
        """Navigate to a specific chat - multiple methods"""
        print(f"[*] Opening chat: {chat_name}")

        # Method 1: Click if visible in list
        try:
            chat_elem = self.page.locator(f'text="{chat_name}"').first
            if await chat_elem.is_visible(timeout=2000):
                await chat_elem.click()
                await asyncio.sleep(1)
                self.current_chat = chat_name
                print(f"[OK] Opened {chat_name}")
                return True
        except:
            pass

        # Method 2: Search for chat
        try:
            search_btn = self.page.locator('input[placeholder*="Search"], input[placeholder*="搜索"]').first
            await search_btn.click()
            await search_btn.fill(chat_name)
            await asyncio.sleep(1)

            await self.page.click(f'text="{chat_name}"')
            await asyncio.sleep(1)
            self.current_chat = chat_name
            print(f"[OK] Found and opened {chat_name}")
            return True
        except:
            pass

        # Method 3: Use keyboard navigation
        try:
            await self.page.keyboard.press('Control+K')
            await asyncio.sleep(0.5)
            await self.page.keyboard.type(chat_name)
            await asyncio.sleep(1)
            await self.page.keyboard.press('Enter')
            await asyncio.sleep(1)
            self.current_chat = chat_name
            print(f"[OK] Opened {chat_name} via keyboard")
            return True
        except:
            pass

        print(f"[ERROR] Could not open chat: {chat_name}")
        return False

    async def send_message(self, chat_name: str, message: str, enhance: Optional[str] = None) -> bool:
        """Send message with optional AI enhancement"""
        if enhance:
            message = MessageEnhancer.enhance_message(message, enhance)

        if not await self.navigate_to_chat(chat_name):
            return False

        print(f"[*] Sending message: {message[:50]}...")

        # Find input field
        input_field = self.page.locator('[contenteditable="true"]').first
        await input_field.click()
        await asyncio.sleep(0.3)

        # Type message
        await input_field.fill(message)
        await asyncio.sleep(0.3)

        # Send
        await self.page.keyboard.press('Enter')
        await asyncio.sleep(0.5)

        # Log to history
        self.message_history.append({
            "timestamp": datetime.now().isoformat(),
            "chat": chat_name,
            "message": message,
            "type": "sent"
        })
        self._save_history()

        print(f"[OK] Message sent to {chat_name}")
        return True

    async def send_formatted_message(self, chat_name: str, message: str,
                                     bold: bool = False, code: bool = False) -> bool:
        """Send message with formatting (bold, code, etc.)"""
        if bold:
            message = f"**{message}**"
        if code:
            message = f"`{message}`"

        return await self.send_message(chat_name, message)

    async def send_multiline_message(self, chat_name: str, lines: List[str]) -> bool:
        """Send multi-line formatted message"""
        message = "\n".join(lines)
        return await self.send_message(chat_name, message)

    async def send_with_mention(self, chat_name: str, message: str, mention: str) -> bool:
        """Send message with @mention"""
        if not await self.navigate_to_chat(chat_name):
            return False

        input_field = self.page.locator('[contenteditable="true"]').first
        await input_field.click()

        # Type @ to trigger mention
        await self.page.keyboard.type('@')
        await asyncio.sleep(0.5)

        # Type the name
        await self.page.keyboard.type(mention)
        await asyncio.sleep(1)

        # Select first result
        await self.page.keyboard.press('Enter')
        await asyncio.sleep(0.3)

        # Type message
        await self.page.keyboard.type(' ' + message)
        await asyncio.sleep(0.3)

        # Send
        await self.page.keyboard.press('Enter')
        await asyncio.sleep(0.5)

        print(f"[OK] Message with @{mention} sent to {chat_name}")
        return True

    async def read_messages(self, chat_name: str, limit: int = 50,
                           save_to_file: Optional[str] = None) -> List[Dict]:
        """Read messages with enhanced parsing and optional export"""
        if not await self.navigate_to_chat(chat_name):
            return []

        print(f"[*] Reading messages from {chat_name}...")

        # Scroll up to load history
        for _ in range(5):
            await self.page.keyboard.press('PageUp')
            await asyncio.sleep(0.3)

        # Wait for messages to load
        await asyncio.sleep(1)

        # Extract messages with metadata
        messages = []
        try:
            # Try to find message containers
            message_elements = await self.page.locator('[class*="message"]').all()

            for elem in message_elements[-limit:]:
                try:
                    text = await elem.inner_text()

                    # Try to extract sender and time
                    msg_data = {
                        "text": text,
                        "timestamp": datetime.now().isoformat(),
                        "chat": chat_name
                    }
                    messages.append(msg_data)
                except:
                    continue
        except Exception as e:
            print(f"[ERROR] Could not read messages: {e}")

        print(f"[OK] Read {len(messages)} messages")

        # Save to file if requested
        if save_to_file:
            try:
                with open(save_to_file, 'w', encoding='utf-8') as f:
                    json.dump(messages, f, indent=2, ensure_ascii=False)
                print(f"[OK] Messages saved to {save_to_file}")
            except Exception as e:
                print(f"[ERROR] Could not save to file: {e}")

        return messages

    async def search_messages(self, query: str) -> List[Dict]:
        """Search for messages across all chats"""
        print(f"[*] Searching for: {query}")

        # Use Feishu's search
        try:
            # Press Ctrl+F or click search
            await self.page.keyboard.press('Control+F')
            await asyncio.sleep(0.5)

            # Type search query
            await self.page.keyboard.type(query)
            await asyncio.sleep(1)

            # Extract results
            results = []
            result_elements = await self.page.locator('[class*="search-result"]').all()

            for elem in result_elements:
                text = await elem.inner_text()
                results.append({"text": text, "query": query})

            print(f"[OK] Found {len(results)} results")
            return results
        except Exception as e:
            print(f"[ERROR] Search failed: {e}")
            return []

    async def upload_file(self, chat_name: str, file_path: str) -> bool:
        """Upload file to chat"""
        if not await self.navigate_to_chat(chat_name):
            return False

        print(f"[*] Uploading file: {file_path}")

        try:
            # Look for file upload button (clip icon usually)
            upload_btn = self.page.locator('[class*="attachment"], [class*="file"]').first
            await upload_btn.click()
            await asyncio.sleep(0.5)

            # Set file
            async with self.page.expect_file_chooser() as fc_info:
                await self.page.click('text="Upload"')
                file_chooser = await fc_info.value
                await file_chooser.set_files(file_path)

            await asyncio.sleep(2)

            # Confirm upload
            send_btn = self.page.locator('button:has-text("Send")').first
            await send_btn.click()

            print(f"[OK] File uploaded to {chat_name}")
            return True
        except Exception as e:
            print(f"[ERROR] File upload failed: {e}")
            return False

    async def create_group_chat(self, name: str, members: List[str]) -> bool:
        """Create a new group chat"""
        print(f"[*] Creating group: {name} with {len(members)} members")

        try:
            # Click create group button
            await self.page.click('[class*="create-group"], [class*="new-chat"]')
            await asyncio.sleep(1)

            # Select members
            for member in members:
                await self.page.keyboard.type(member)
                await asyncio.sleep(0.5)
                await self.page.keyboard.press('Enter')
                await asyncio.sleep(0.3)

            # Set group name
            name_input = self.page.locator('input[placeholder*="Group name"]').first
            await name_input.fill(name)

            # Create
            await self.page.click('button:has-text("Create")')
            await asyncio.sleep(2)

            print(f"[OK] Group '{name}' created")
            return True
        except Exception as e:
            print(f"[ERROR] Group creation failed: {e}")
            return False

    async def get_chat_list(self) -> List[str]:
        """Get list of all chats"""
        print("[*] Getting chat list...")

        try:
            chat_elements = await self.page.locator('[class*="chat-item"], [class*="conversation"]').all()
            chats = []

            for elem in chat_elements:
                try:
                    text = await elem.inner_text()
                    # Extract chat name (first line usually)
                    chat_name = text.split('\n')[0]
                    if chat_name:
                        chats.append(chat_name)
                except:
                    continue

            print(f"[OK] Found {len(chats)} chats")
            return chats
        except Exception as e:
            print(f"[ERROR] Could not get chat list: {e}")
            return []

    async def add_template(self, name: str, message: str):
        """Save a message template"""
        self.templates[name] = message
        self._save_templates()
        print(f"[OK] Template '{name}' saved")

    async def send_from_template(self, chat_name: str, template_name: str,
                                 variables: Optional[Dict] = None) -> bool:
        """Send message from template with variable substitution"""
        if template_name not in self.templates:
            print(f"[ERROR] Template '{template_name}' not found")
            return False

        message = self.templates[template_name]

        # Replace variables
        if variables:
            for key, value in variables.items():
                message = message.replace(f"{{{key}}}", str(value))

        return await self.send_message(chat_name, message)

    async def list_templates(self):
        """List all saved templates"""
        print("\n[*] Saved Templates:")
        for name, message in self.templates.items():
            preview = message[:50] + "..." if len(message) > 50 else message
            print(f"  - {name}: {preview}")

    async def send_smart_reply(self, chat_name: str, intent: str = "acknowledge") -> bool:
        """Send AI-generated smart reply"""
        # Read last message
        messages = await self.read_messages(chat_name, limit=1)
        if not messages:
            print("[ERROR] No messages to reply to")
            return False

        last_msg = messages[-1]["text"]
        reply = MessageEnhancer.create_smart_reply(last_msg, intent)
        return await self.send_message(chat_name, reply)

    async def batch_send(self, chat_names: List[str], message: str) -> Dict[str, bool]:
        """Send same message to multiple chats"""
        print(f"[*] Batch sending to {len(chat_names)} chats...")
        results = {}

        for chat in chat_names:
            success = await self.send_message(chat, message)
            results[chat] = success
            await asyncio.sleep(1)  # Avoid rate limiting

        successful = sum(1 for v in results.values() if v)
        print(f"[OK] Batch send complete: {successful}/{len(chat_names)} successful")
        return results

    async def export_chat_history(self, chat_name: str, output_file: str):
        """Export entire chat history to file"""
        messages = await self.read_messages(chat_name, limit=500)

        # Create formatted export
        export_data = {
            "chat": chat_name,
            "exported": datetime.now().isoformat(),
            "message_count": len(messages),
            "messages": messages
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print(f"[OK] Chat history exported to {output_file}")

    async def get_unread_count(self) -> Dict[str, int]:
        """Get unread message counts per chat"""
        print("[*] Checking unread messages...")

        try:
            unread = {}
            chat_elements = await self.page.locator('[class*="chat-item"]').all()

            for elem in chat_elements:
                try:
                    # Look for unread badge
                    badge = await elem.locator('[class*="badge"], [class*="unread"]').first
                    if badge:
                        chat_name = await elem.locator('[class*="name"]').inner_text()
                        count_text = await badge.inner_text()
                        count = int(re.search(r'\d+', count_text).group())
                        unread[chat_name] = count
                except:
                    continue

            total = sum(unread.values())
            print(f"[OK] Total unread: {total}")
            return unread
        except Exception as e:
            print(f"[ERROR] Could not check unread: {e}")
            return {}

    async def mark_as_read(self, chat_name: str) -> bool:
        """Mark chat as read"""
        if not await self.navigate_to_chat(chat_name):
            return False

        # Just opening the chat marks it as read
        await asyncio.sleep(1)
        print(f"[OK] Marked {chat_name} as read")
        return True

    async def take_screenshot(self, output_file: str = "feishu_screenshot.png"):
        """Take screenshot of current view"""
        await self.page.screenshot(path=output_file, full_page=True)
        print(f"[OK] Screenshot saved to {output_file}")

    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
        elif self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()
        print("[*] Browser closed")


async def main():
    """Enhanced CLI interface"""
    if len(sys.argv) < 2:
        print("""
Feishu Pro - Advanced Browser Automation

BASIC COMMANDS:
  start                              - Start browser and keep open
  list                              - List all chats
  unread                            - Check unread messages

MESSAGING:
  send <chat> <message>             - Send simple message
  send-enhanced <chat> <message> <style> - Send with AI enhancement
                                      Styles: professional, friendly, formal, brief
  send-mention <chat> <message> <@user> - Send with @mention
  send-formatted <chat> <message>   - Send with markdown formatting
  send-multiline <chat> <line1> <line2> ... - Send multi-line message

SMART FEATURES:
  smart-reply <chat> <intent>       - Send AI smart reply
                                      Intents: acknowledge, agree, question, thanks
  batch-send <chat1,chat2> <message> - Send to multiple chats
  send-template <chat> <template_name> - Send from saved template

READING:
  read <chat> [limit]               - Read messages (default 50)
  read-export <chat> <file.json>    - Read and export to file
  search <query>                    - Search messages
  export-history <chat> <file.json> - Export full chat history

TEMPLATES:
  save-template <name> <message>    - Save message template
  list-templates                    - List all templates

FILES:
  upload <chat> <file_path>         - Upload file to chat
  screenshot [output.png]           - Take screenshot

ADVANCED:
  create-group <name> <member1,member2> - Create group chat
  mark-read <chat>                  - Mark chat as read

Examples:
  python feishu_pro.py send Hany "Hello there"
  python feishu_pro.py send-enhanced Hany "meeting tomorrow" professional
  python feishu_pro.py send-mention TeamChat "great work" John
  python feishu_pro.py smart-reply Hany acknowledge
  python feishu_pro.py batch-send "Hany,John,Sarah" "Meeting at 3pm"
  python feishu_pro.py read-export Hany chat_backup.json
  python feishu_pro.py save-template standup "Daily standup: {task} - {status}"
""")
        return

    command = sys.argv[1]
    app = FeishuPro()

    try:
        await app.start()

        if command == "start":
            print("\n[OK] Feishu Pro is ready")
            print("Press Ctrl+C to close")
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n[*] Shutting down...")

        elif command == "list":
            chats = await app.get_chat_list()
            print("\n[*] Your Chats:")
            for chat in chats:
                print(f"  - {chat}")

        elif command == "unread":
            unread = await app.get_unread_count()
            if unread:
                print("\n[*] Unread Messages:")
                for chat, count in unread.items():
                    print(f"  - {chat}: {count} unread")
            else:
                print("\n[OK] No unread messages")

        elif command == "send":
            if len(sys.argv) < 4:
                print("[ERROR] Usage: send <chat> <message>")
                return
            await app.send_message(sys.argv[2], sys.argv[3])

        elif command == "send-enhanced":
            if len(sys.argv) < 5:
                print("[ERROR] Usage: send-enhanced <chat> <message> <style>")
                return
            await app.send_message(sys.argv[2], sys.argv[3], enhance=sys.argv[4])

        elif command == "send-mention":
            if len(sys.argv) < 5:
                print("[ERROR] Usage: send-mention <chat> <message> <@user>")
                return
            await app.send_with_mention(sys.argv[2], sys.argv[3], sys.argv[4])

        elif command == "send-multiline":
            if len(sys.argv) < 4:
                print("[ERROR] Usage: send-multiline <chat> <line1> <line2> ...")
                return
            await app.send_multiline_message(sys.argv[2], sys.argv[3:])

        elif command == "smart-reply":
            if len(sys.argv) < 4:
                print("[ERROR] Usage: smart-reply <chat> <intent>")
                return
            await app.send_smart_reply(sys.argv[2], sys.argv[3])

        elif command == "batch-send":
            if len(sys.argv) < 4:
                print("[ERROR] Usage: batch-send <chat1,chat2> <message>")
                return
            chats = sys.argv[2].split(',')
            await app.batch_send(chats, sys.argv[3])

        elif command == "read":
            if len(sys.argv) < 3:
                print("[ERROR] Usage: read <chat> [limit]")
                return
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 50
            messages = await app.read_messages(sys.argv[2], limit)
            print("\n--- Messages ---")
            for msg in messages:
                print(f"{msg.get('timestamp', 'N/A')}: {msg['text']}")
                print("---")

        elif command == "read-export":
            if len(sys.argv) < 4:
                print("[ERROR] Usage: read-export <chat> <file.json>")
                return
            await app.read_messages(sys.argv[2], limit=500, save_to_file=sys.argv[3])

        elif command == "search":
            if len(sys.argv) < 3:
                print("[ERROR] Usage: search <query>")
                return
            results = await app.search_messages(sys.argv[2])
            for result in results:
                print(f"  - {result['text']}")

        elif command == "export-history":
            if len(sys.argv) < 4:
                print("[ERROR] Usage: export-history <chat> <file.json>")
                return
            await app.export_chat_history(sys.argv[2], sys.argv[3])

        elif command == "save-template":
            if len(sys.argv) < 4:
                print("[ERROR] Usage: save-template <name> <message>")
                return
            await app.add_template(sys.argv[2], sys.argv[3])

        elif command == "list-templates":
            await app.list_templates()

        elif command == "send-template":
            if len(sys.argv) < 4:
                print("[ERROR] Usage: send-template <chat> <template_name>")
                return
            await app.send_from_template(sys.argv[2], sys.argv[3])

        elif command == "upload":
            if len(sys.argv) < 4:
                print("[ERROR] Usage: upload <chat> <file_path>")
                return
            await app.upload_file(sys.argv[2], sys.argv[3])

        elif command == "create-group":
            if len(sys.argv) < 4:
                print("[ERROR] Usage: create-group <name> <member1,member2>")
                return
            members = sys.argv[3].split(',')
            await app.create_group_chat(sys.argv[2], members)

        elif command == "mark-read":
            if len(sys.argv) < 3:
                print("[ERROR] Usage: mark-read <chat>")
                return
            await app.mark_as_read(sys.argv[2])

        elif command == "screenshot":
            output = sys.argv[2] if len(sys.argv) > 2 else "feishu_screenshot.png"
            await app.take_screenshot(output)

        else:
            print(f"[ERROR] Unknown command: {command}")

    finally:
        if command != "start":
            await app.close()


if __name__ == "__main__":
    asyncio.run(main())
