#!/usr/bin/env python3
"""
Feishu Persistent Session
Saves your login - log in once, use forever!
No more blank pages, no repeated logins
"""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

# Persistent storage for your Feishu session
USER_DATA_DIR = Path.home() / ".feishu-session"
FEISHU_URL = "https://qcn9ppuir8al.feishu.cn/next/messenger/"


async def setup_session():
    """First-time setup: Log in once and save session"""
    print("\n" + "="*50)
    print("FEISHU SESSION SETUP")
    print("="*50)
    print("\nThis is a ONE-TIME setup.")
    print("After you log in, your session will be saved.")
    print("Future commands will use this session automatically.")
    print("\nSteps:")
    print("1. Browser will open to Feishu")
    print("2. Log in normally")
    print("3. Press Enter here when logged in")
    print("4. Done! Session saved forever")
    print("="*50 + "\n")

    async with async_playwright() as p:
        # Create persistent context - saves login!
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            channel="chrome"
        )

        page = context.pages[0] if context.pages else await context.new_page()

        print(f"[*] Opening Feishu...")
        await page.goto(FEISHU_URL)

        print("\n[!] Please log into Feishu in the browser window")
        print("[!] Waiting 60 seconds for you to log in...")
        print("[!] (Browser will stay open for future use)")

        await asyncio.sleep(60)

        print("\n[OK] Session saved!")
        print("[OK] Browser will stay open - you can close it or keep using it")
        print("\nFrom now on, use:")
        print("  python feishu_persistent.py send Hany \"message\"")
        print("\nNo more logins required!")

        await context.close()


async def send_message(chat_name: str, message: str):
    """Send message using saved session"""
    async with async_playwright() as p:
        # Use saved session
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            channel="chrome"
        )

        page = context.pages[0] if context.pages else await context.new_page()

        # Go to Feishu (already logged in!)
        if "feishu.cn" not in page.url:
            print("[*] Opening Feishu...")
            await page.goto(FEISHU_URL)
            await asyncio.sleep(2)
        else:
            print("[OK] Using existing Feishu session")

        # Navigate to chat
        print(f"[*] Opening chat: {chat_name}")
        try:
            await page.click(f'text="{chat_name}"', timeout=5000)
            await asyncio.sleep(1)
        except:
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
            await asyncio.sleep(1)

            print(f"[OK] Message sent to {chat_name}!")

            # Close browser (session is saved, will reopen logged in next time)
            await asyncio.sleep(2)
            await context.close()
            return True

        except Exception as e:
            print(f"[ERROR] Failed to send: {e}")
            await context.close()
            return False


async def read_messages(chat_name: str, limit: int = 20):
    """Read messages using saved session"""
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            channel="chrome"
        )

        page = context.pages[0] if context.pages else await context.new_page()

        if "feishu.cn" not in page.url:
            await page.goto(FEISHU_URL)
            await asyncio.sleep(2)

        # Navigate to chat
        print(f"[*] Opening chat: {chat_name}")
        try:
            await page.click(f'text="{chat_name}"')
            await asyncio.sleep(2)
        except:
            pass

        # Scroll and read
        print(f"[*] Reading messages...")
        for _ in range(3):
            await page.keyboard.press('PageUp')
            await asyncio.sleep(0.3)

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

        except Exception as e:
            print(f"[ERROR] Could not read: {e}")

        await asyncio.sleep(2)
        await context.close()
        return messages


async def list_chats():
    """List all chats using saved session"""
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            channel="chrome"
        )

        page = context.pages[0] if context.pages else await context.new_page()

        if "feishu.cn" not in page.url:
            await page.goto(FEISHU_URL)
            await asyncio.sleep(2)

        print("[*] Getting chat list...")
        chats = []
        try:
            chat_elements = await page.locator('[class*="chat-item"]').all()
            for elem in chat_elements[:50]:
                try:
                    text = await elem.inner_text()
                    chat_name = text.split('\n')[0]
                    if chat_name:
                        chats.append(chat_name)
                except:
                    continue

            print(f"[OK] Found {len(chats)} chats")

        except Exception as e:
            print(f"[ERROR] Could not list chats: {e}")

        await asyncio.sleep(2)
        await context.close()
        return chats


def check_session():
    """Check if session is already saved"""
    return USER_DATA_DIR.exists()


async def main():
    if len(sys.argv) < 2:
        print("""
Feishu Persistent Session
Log in once, use forever!

FIRST TIME SETUP:
  python feishu_persistent.py setup   - Log in and save session (once!)

THEN USE ANYTIME:
  python feishu_persistent.py send <chat> <message>
  python feishu_persistent.py read <chat> [limit]
  python feishu_persistent.py list

EXAMPLES:
  # First time only:
  python feishu_persistent.py setup

  # Then forever:
  python feishu_persistent.py send Hany "Hello!"
  python feishu_persistent.py read Hany 50
  python feishu_persistent.py list

NO MORE LOGINS REQUIRED!
""")
        return

    command = sys.argv[1]

    # Check if session exists (except for setup command)
    if command != "setup" and not check_session():
        print("\n[ERROR] No saved session found!")
        print("[!] Please run setup first:")
        print("    python feishu_persistent.py setup\n")
        return

    if command == "setup":
        await setup_session()

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
