#!/usr/bin/env python3
"""
Feishu CDP Controller
Uses Chrome DevTools Protocol to control your existing browser session
No blank pages, works with your logged-in Feishu tab
"""

import asyncio
import sys
from playwright.async_api import async_playwright

CDP_URL = "http://localhost:9222"

async def find_feishu_page(browser):
    """Find the Feishu page in existing tabs"""
    for context in browser.contexts:
        for page in context.pages:
            if "feishu.cn" in page.url:
                return page
    return None

async def send_message(chat_name: str, message: str):
    """Send message using existing browser session"""
    async with async_playwright() as p:
        try:
            # Connect to existing Chrome
            browser = await p.chromium.connect_over_cdp(CDP_URL)
            print(f"[OK] Connected to Chrome (remote debugging)")
        except Exception as e:
            print(f"[ERROR] Could not connect to Chrome: {e}")
            print("\nPlease run: start_chrome_debug.bat")
            return False

        # Find Feishu page
        page = await find_feishu_page(browser)
        if not page:
            print("[ERROR] Feishu not found in any tab")
            print("Please open: https://qcn9ppuir8al.feishu.cn/next/messenger/")
            return False

        print(f"[OK] Found Feishu at: {page.url}")

        # Bring to front
        await page.bring_to_front()
        await asyncio.sleep(0.5)

        # Navigate to chat if needed
        print(f"[*] Opening chat: {chat_name}")
        try:
            # Try clicking visible chat
            await page.click(f'text="{chat_name}"', timeout=3000)
            await asyncio.sleep(1)
        except:
            # Already open or not visible, continue
            print("[*] Chat may already be open")

        # Send message
        print(f"[*] Sending: {message}")
        try:
            input_field = page.locator('[contenteditable="true"]').first
            await input_field.click()
            await asyncio.sleep(0.3)
            await input_field.fill(message)
            await asyncio.sleep(0.3)
            await page.keyboard.press('Enter')
            await asyncio.sleep(0.5)

            print(f"[OK] Message sent to {chat_name}!")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to send: {e}")
            return False

async def read_messages(chat_name: str, limit: int = 20):
    """Read messages from chat"""
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(CDP_URL)
        except:
            print("[ERROR] Could not connect. Run: start_chrome_debug.bat")
            return []

        page = await find_feishu_page(browser)
        if not page:
            print("[ERROR] Feishu not found")
            return []

        await page.bring_to_front()

        # Navigate to chat
        print(f"[*] Opening chat: {chat_name}")
        try:
            await page.click(f'text="{chat_name}"')
            await asyncio.sleep(2)
        except:
            pass

        # Scroll up
        print("[*] Reading messages...")
        for _ in range(3):
            await page.keyboard.press('PageUp')
            await asyncio.sleep(0.3)

        # Extract messages
        messages = []
        try:
            message_elements = await page.locator('[class*="message"]').all()
            for elem in message_elements[-limit:]:
                try:
                    text = await elem.inner_text()
                    messages.append(text)
                except:
                    continue

            print(f"[OK] Read {len(messages)} messages")
            return messages

        except Exception as e:
            print(f"[ERROR] Could not read messages: {e}")
            return []

async def list_chats():
    """List all visible chats"""
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(CDP_URL)
        except:
            print("[ERROR] Could not connect. Run: start_chrome_debug.bat")
            return []

        page = await find_feishu_page(browser)
        if not page:
            print("[ERROR] Feishu not found")
            return []

        await page.bring_to_front()
        await asyncio.sleep(1)

        print("[*] Getting chat list...")
        chats = []
        try:
            chat_elements = await page.locator('[class*="chat-item"], [class*="conversation"]').all()
            for elem in chat_elements[:50]:  # Limit to first 50
                try:
                    text = await elem.inner_text()
                    chat_name = text.split('\n')[0]
                    if chat_name and len(chat_name) > 0:
                        chats.append(chat_name)
                except:
                    continue

            print(f"[OK] Found {len(chats)} chats")
            return chats

        except Exception as e:
            print(f"[ERROR] Could not get chats: {e}")
            return []

async def check_connection():
    """Test if Chrome remote debugging is working"""
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(CDP_URL)
            print("[OK] Connected to Chrome successfully!")

            page = await find_feishu_page(browser)
            if page:
                print(f"[OK] Feishu found at: {page.url}")
                print("[OK] Setup is working perfectly!")
                return True
            else:
                print("[!] Chrome connected but Feishu not found")
                print("[*] Please open: https://qcn9ppuir8al.feishu.cn/next/messenger/")
                return False

        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            print("\nTroubleshooting:")
            print("1. Run: start_chrome_debug.bat")
            print("2. Make sure Chrome is open")
            print("3. Check that port 9222 is not blocked")
            return False

async def main():
    if len(sys.argv) < 2:
        print("""
Feishu CDP Controller
Uses Chrome DevTools Protocol - no blank pages!

SETUP:
  Run start_chrome_debug.bat first, then use these commands

COMMANDS:
  test                           - Test connection
  send <chat> <message>          - Send message
  read <chat> [limit]            - Read messages (default 20)
  list                           - List all chats

EXAMPLES:
  python feishu_cdp.py test
  python feishu_cdp.py send Hany "Hello!"
  python feishu_cdp.py read Hany 50
  python feishu_cdp.py list
""")
        return

    command = sys.argv[1]

    if command == "test":
        await check_connection()

    elif command == "send":
        if len(sys.argv) < 4:
            print("[ERROR] Usage: send <chat> <message>")
            return
        chat_name = sys.argv[2]
        message = " ".join(sys.argv[3:])
        await send_message(chat_name, message)

    elif command == "read":
        if len(sys.argv) < 3:
            print("[ERROR] Usage: read <chat> [limit]")
            return
        chat_name = sys.argv[2]
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
        messages = await read_messages(chat_name, limit)

        if messages:
            print("\n--- Messages ---")
            for msg in messages:
                print(msg)
                print("---")

    elif command == "list":
        chats = await list_chats()
        if chats:
            print("\n--- Your Chats ---")
            for chat in chats:
                print(f"  - {chat}")

    else:
        print(f"[ERROR] Unknown command: {command}")
        print("Run without arguments to see help")

if __name__ == "__main__":
    asyncio.run(main())
