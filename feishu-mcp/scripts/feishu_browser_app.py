#!/usr/bin/env python3
"""
Feishu Browser Automation App
Maintains persistent browser session for reliable Feishu operations
"""

import asyncio
import json
import sys
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

# Configuration
USER_DATA_DIR = Path.home() / ".feishu-browser-data"
FEISHU_URL = "https://qcn9ppuir8al.feishu.cn/next/messenger/"


class FeishuBrowser:
    def __init__(self):
        self.playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None

    async def start(self):
        """Start browser with persistent context"""
        print("Starting Feishu browser...")
        self.playwright = await async_playwright().start()

        # Use persistent context to maintain login
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            channel="chrome",
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage'
            ]
        )

        # Get or create page
        if len(self.context.pages) > 0:
            self.page = self.context.pages[0]
        else:
            self.page = await self.context.new_page()

        # Navigate to Feishu
        await self.page.goto(FEISHU_URL, wait_until='domcontentloaded')
        await asyncio.sleep(2)  # Give it time to load messenger UI
        print(f"Browser ready at: {self.page.url}")

    async def send_message(self, chat_name: str, message: str):
        """Send message to a chat"""
        print(f"Sending message to {chat_name}: {message}")

        # Search for chat
        await self.page.click('text=Search')
        await asyncio.sleep(0.5)

        # Type chat name
        await self.page.keyboard.type(chat_name)
        await asyncio.sleep(1)

        # Click on the chat
        await self.page.click(f'text={chat_name}')
        await asyncio.sleep(1)

        # Find and fill message input
        input_field = await self.page.locator('[contenteditable="true"]').first
        await input_field.click()
        await input_field.fill(message)

        # Send
        await self.page.keyboard.press('Enter')
        await asyncio.sleep(0.5)

        print(f"[OK] Message sent to {chat_name}")
        return True

    async def add_reaction(self, message_text: str, emoji: str = "👍"):
        """Add reaction to a message"""
        print(f"Adding reaction '{emoji}' to message: {message_text[:50]}...")

        try:
            # Find the message
            message = await self.page.locator(f'text="{message_text}"').last

            # Hover to show reaction button
            await message.hover()
            await asyncio.sleep(0.5)

            # Look for reaction button (usually appears on hover)
            # Try to find the emoji/reaction icon
            reaction_buttons = await self.page.locator('[class*="reaction"], [class*="emoji"]').all()

            if reaction_buttons:
                await reaction_buttons[0].click()
                await asyncio.sleep(0.3)

                # Select the emoji
                await self.page.click(f'text="{emoji}"')
                await asyncio.sleep(0.3)

                print(f"[OK] Reaction added")
                return True
            else:
                # Alternative: right-click on message
                await message.click(button='right')
                await asyncio.sleep(0.5)

                # Look for "Add Reaction" or emoji option
                try:
                    await self.page.click('text=/[Rr]eaction|[Ee]moji/')
                    await asyncio.sleep(0.3)
                    await self.page.click(f'text="{emoji}"')
                    print(f"[OK] Reaction added via context menu")
                    return True
                except:
                    print("Could not find reaction option in context menu")
                    return False

        except Exception as e:
            print(f"Error adding reaction: {e}")
            return False

    async def read_messages(self, chat_name: str, limit: int = 20):
        """Read recent messages from a chat"""
        print(f"Reading messages from {chat_name}...")

        # Navigate to chat
        await self.page.click(f'text="{chat_name}"')
        await asyncio.sleep(1)

        # Scroll up to load history
        for _ in range(3):
            await self.page.keyboard.press('PageUp')
            await asyncio.sleep(0.3)

        # Extract messages
        messages = []
        message_elements = await self.page.locator('[class*="message"]').all()

        for elem in message_elements[-limit:]:
            text = await elem.inner_text()
            messages.append(text)

        print(f"[OK] Read {len(messages)} messages")
        return messages

    async def close(self):
        """Close browser"""
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()
        print("Browser closed")


async def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("""
Feishu Browser Automation App

Usage:
  python feishu_browser_app.py start                          - Start browser and keep open
  python feishu_browser_app.py send <chat_name> <message>    - Send message
  python feishu_browser_app.py react <message_text> [emoji]  - Add reaction
  python feishu_browser_app.py read <chat_name>              - Read messages

Examples:
  python feishu_browser_app.py start
  python feishu_browser_app.py send Hany "Hello!"
  python feishu_browser_app.py react "sup" "👍"
  python feishu_browser_app.py read Hany
""")
        return

    command = sys.argv[1]
    browser = FeishuBrowser()

    try:
        await browser.start()

        if command == "start":
            print("\n[OK] Browser is ready and logged in")
            print("You can verify and keep this session open")
            print("Press Ctrl+C to close")

            # Keep running
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\nClosing...")

        elif command == "send":
            if len(sys.argv) < 4:
                print("Error: Usage: send <chat_name> <message>")
                return
            chat_name = sys.argv[2]
            message = sys.argv[3]
            await browser.send_message(chat_name, message)

        elif command == "react":
            if len(sys.argv) < 3:
                print("Error: Usage: react <message_text> [emoji]")
                return
            message_text = sys.argv[2]
            emoji = sys.argv[3] if len(sys.argv) > 3 else "👍"
            await browser.add_reaction(message_text, emoji)

        elif command == "read":
            if len(sys.argv) < 3:
                print("Error: Usage: read <chat_name>")
                return
            chat_name = sys.argv[2]
            messages = await browser.read_messages(chat_name)
            print("\n--- Messages ---")
            for msg in messages:
                print(msg)
                print("---")
        else:
            print(f"Unknown command: {command}")

    finally:
        if command != "start":
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
