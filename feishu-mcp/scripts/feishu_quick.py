#!/usr/bin/env python3
"""
Feishu Quick Send - Simple message sender
Uses existing browser without conflicts
"""

import asyncio
import sys
from playwright.async_api import async_playwright

async def send_message(chat_name: str, message: str):
    """Send message using a simple browser launch"""
    async with async_playwright() as p:
        # Launch browser (will use existing profile if available)
        browser = await p.chromium.launch(
            headless=False,
            channel="chrome"
        )

        context = await browser.new_context()
        page = await context.new_page()

        print(f"[*] Opening Feishu...")
        await page.goto("https://qcn9ppuir8al.feishu.cn/next/messenger/")

        # Wait for page to load
        print("[*] Waiting for page to load...")
        await asyncio.sleep(5)

        # Navigate to chat
        print(f"[*] Looking for chat: {chat_name}")
        try:
            # Try clicking visible chat
            await page.click(f'text="{chat_name}"', timeout=5000)
            await asyncio.sleep(2)
        except:
            # Try search
            print("[*] Searching for chat...")
            try:
                search = page.locator('input').first
                await search.click()
                await search.fill(chat_name)
                await asyncio.sleep(2)
                await page.click(f'text="{chat_name}"')
                await asyncio.sleep(2)
            except Exception as e:
                print(f"[ERROR] Could not find chat: {e}")
                await browser.close()
                return False

        # Send message
        print(f"[*] Sending message...")
        try:
            input_field = page.locator('[contenteditable="true"]').first
            await input_field.click()
            await asyncio.sleep(0.5)
            await input_field.fill(message)
            await asyncio.sleep(0.5)
            await page.keyboard.press('Enter')
            await asyncio.sleep(2)

            print(f"[OK] Message sent to {chat_name}!")

            # Keep browser open for a moment
            await asyncio.sleep(3)

        except Exception as e:
            print(f"[ERROR] Failed to send: {e}")
            await browser.close()
            return False

        await browser.close()
        return True

async def main():
    if len(sys.argv) < 3:
        print("""
Feishu Quick Send

Usage:
  python feishu_quick.py <chat_name> <message>

Example:
  python feishu_quick.py Hany "Hello!"
""")
        return

    chat_name = sys.argv[1]
    message = " ".join(sys.argv[2:])

    await send_message(chat_name, message)

if __name__ == "__main__":
    asyncio.run(main())
