#!/usr/bin/env python3
"""
Simple Feishu Browser Control
Uses the already-open Feishu web session
"""

import asyncio
import sys
from playwright.async_api import async_playwright


async def add_reaction_to_message(message_text, emoji="👍"):
    """Add reaction to a message in the currently open Feishu tab"""
    async with async_playwright() as p:
        # Connect to existing Chrome via CDP
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")

        # Get the active context and page
        contexts = browser.contexts
        if not contexts:
            print("Error: No browser contexts found. Make sure Feishu is open in Chrome.")
            return False

        context = contexts[0]
        pages = context.pages

        # Find Feishu page
        feishu_page = None
        for page in pages:
            if "feishu.cn" in page.url:
                feishu_page = page
                break

        if not feishu_page:
            print("Error: Feishu page not found. Make sure you have Feishu open.")
            return False

        print(f"Connected to Feishu at: {feishu_page.url}")

        try:
            # Find the message containing the text
            message_locator = feishu_page.locator(f'text="{message_text}"').last

            # Hover over the message to show reaction options
            await message_locator.hover()
            print(f"Hovering over message: {message_text}")
            await asyncio.sleep(1)

            # Try to find and click reaction button
            # Feishu usually shows emoji/reaction button on hover
            try:
                # Look for emoji or reaction icons (common class patterns)
                reaction_btn = feishu_page.locator('[class*="emoji"], [class*="reaction"], [aria-label*="eaction"]').first
                if await reaction_btn.is_visible(timeout=2000):
                    await reaction_btn.click()
                    await asyncio.sleep(0.5)

                    # Select emoji
                    emoji_btn = feishu_page.locator(f'text="{emoji}"').first
                    await emoji_btn.click(timeout=2000)
                    print(f"[OK] Reaction '{emoji}' added!")
                    return True
            except:
                pass

            # Alternative: Right-click context menu
            try:
                await message_locator.click(button='right')
                await asyncio.sleep(0.5)

                # Look for reaction option
                await feishu_page.click('text=/[Rr]eaction|[Ee]moji/')
                await asyncio.sleep(0.3)
                await feishu_page.click(f'text="{emoji}"')
                print(f"[OK] Reaction '{emoji}' added via context menu!")
                return True
            except:
                print("Could not find reaction option. Try manually.")
                return False

        except Exception as e:
            print(f"Error: {e}")
            return False


async def send_message(chat_name, message):
    """Send a message to a chat"""
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        pages = context.pages

        feishu_page = None
        for page in pages:
            if "feishu.cn" in page.url:
                feishu_page = page
                break

        if not feishu_page:
            print("Error: Feishu page not found")
            return False

        print(f"Sending message to {chat_name}...")

        # Navigate to messenger if not there
        if "messenger" not in feishu_page.url:
            await feishu_page.goto("https://qcn9ppuir8al.feishu.cn/next/messenger/")
            await asyncio.sleep(2)

        # Click on chat
        await feishu_page.click(f'text="{chat_name}"')
        await asyncio.sleep(1)

        # Type message
        input_field = feishu_page.locator('[contenteditable="true"]').first
        await input_field.click()
        await input_field.fill(message)
        await feishu_page.keyboard.press('Enter')
        await asyncio.sleep(0.5)

        print(f"[OK] Message sent to {chat_name}")
        return True


async def main():
    if len(sys.argv) < 2:
        print("""
Simple Feishu Browser Control

Prerequisites:
  1. Open Chrome with remote debugging: chrome.exe --remote-debugging-port=9222
  2. Navigate to Feishu Messenger and login
  3. Keep the browser open

Usage:
  python feishu_simple.py react <message_text> [emoji]
  python feishu_simple.py send <chat_name> <message>

Examples:
  python feishu_simple.py react "sup" "👍"
  python feishu_simple.py send "Hany" "Hello!"
""")
        return

    command = sys.argv[1]

    if command == "react":
        if len(sys.argv) < 3:
            print("Usage: react <message_text> [emoji]")
            return
        message_text = sys.argv[2]
        emoji = sys.argv[3] if len(sys.argv) > 3 else "👍"
        await add_reaction_to_message(message_text, emoji)

    elif command == "send":
        if len(sys.argv) < 4:
            print("Usage: send <chat_name> <message>")
            return
        chat_name = sys.argv[2]
        message = sys.argv[3]
        await send_message(chat_name, message)

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    asyncio.run(main())
