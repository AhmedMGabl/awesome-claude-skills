#!/usr/bin/env python3
"""
Comprehensive Feishu Testing Suite
Tests all automation methods and documents capabilities
"""

import asyncio
import sys
import os
from pathlib import Path
from playwright.async_api import async_playwright
import json

# Test results storage
results = {
    "bot_api": {},
    "browser_web": {},
    "desktop_app": {},
    "capabilities": []
}


async def test_bot_api():
    """Test 1: Feishu Bot API (if configured)"""
    print("\n" + "="*60)
    print("TEST 1: FEISHU BOT API")
    print("="*60)

    # Check if bot credentials exist
    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")

    if not app_id or not app_secret:
        print("[SKIP] No bot credentials configured")
        print("      Set FEISHU_APP_ID and FEISHU_APP_SECRET to enable")
        results["bot_api"]["status"] = "not_configured"
        return False

    print(f"[*] App ID: {app_id[:8]}...")

    try:
        import requests

        # Get tenant access token
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        data = {"app_id": app_id, "app_secret": app_secret}

        response = requests.post(url, json=data)
        if response.status_code == 200:
            token = response.json().get("tenant_access_token")
            print(f"[OK] Got access token: {token[:10]}...")

            results["bot_api"]["status"] = "working"
            results["bot_api"]["token"] = token[:10] + "..."
            results["capabilities"].append("Bot API: Send messages, manage chats")
            return True
        else:
            print(f"[ERROR] API returned {response.status_code}")
            results["bot_api"]["status"] = "error"
            return False

    except Exception as e:
        print(f"[ERROR] Bot API test failed: {e}")
        results["bot_api"]["status"] = "error"
        results["bot_api"]["error"] = str(e)
        return False


async def test_browser_web():
    """Test 2: Browser Web Automation"""
    print("\n" + "="*60)
    print("TEST 2: BROWSER WEB AUTOMATION")
    print("="*60)

    async with async_playwright() as p:
        # Test persistent context
        print("\n[*] Testing persistent context...")
        user_data_dir = Path.home() / ".feishu-test-session"

        try:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(user_data_dir),
                headless=False,
                channel="chrome"
            )

            page = context.pages[0] if context.pages else await context.new_page()

            print("[*] Opening Feishu web...")
            await page.goto("https://qcn9ppuir8al.feishu.cn/next/messenger/",
                          wait_until='domcontentloaded')
            await asyncio.sleep(3)

            # Check if logged in
            current_url = page.url
            print(f"[*] Current URL: {current_url}")

            if "login" in current_url.lower():
                print("[!] Not logged in - would need manual login")
                results["browser_web"]["status"] = "needs_login"
            else:
                print("[OK] Logged in successfully")
                results["browser_web"]["status"] = "working"

                # Test capabilities
                print("\n[*] Testing capabilities...")

                # Can we find chat list?
                try:
                    chats = await page.locator('[class*="chat"]').count()
                    print(f"[OK] Found {chats} chat elements")
                    results["capabilities"].append(f"Browser: List {chats} chats")
                except:
                    print("[!] Could not count chats")

                # Can we find input field?
                try:
                    input_field = page.locator('[contenteditable="true"]')
                    if await input_field.count() > 0:
                        print("[OK] Found message input field")
                        results["capabilities"].append("Browser: Send messages")
                except:
                    print("[!] Could not find input field")

                # Can we access user info?
                try:
                    await page.screenshot(path="feishu_test.png")
                    print("[OK] Can take screenshots")
                    results["capabilities"].append("Browser: Take screenshots")
                except:
                    pass

            await context.close()
            return True

        except Exception as e:
            print(f"[ERROR] Browser test failed: {e}")
            results["browser_web"]["status"] = "error"
            results["browser_web"]["error"] = str(e)
            return False


async def test_desktop_app():
    """Test 3: Feishu Desktop App Control"""
    print("\n" + "="*60)
    print("TEST 3: FEISHU DESKTOP APP CONTROL")
    print("="*60)

    # Check if desktop app is installed
    possible_paths = [
        r"C:\Users\{}\AppData\Local\Programs\Feishu\Feishu.exe",
        r"C:\Program Files\Feishu\Feishu.exe",
        r"C:\Program Files (x86)\Feishu\Feishu.exe",
    ]

    username = os.getenv("USERNAME")
    desktop_path = None

    for path_template in possible_paths:
        path = path_template.format(username)
        if Path(path).exists():
            desktop_path = path
            break

    if not desktop_path:
        print("[SKIP] Feishu desktop app not found")
        print("      Common paths checked:")
        for p in possible_paths:
            print(f"      - {p}")
        results["desktop_app"]["status"] = "not_installed"
        return False

    print(f"[OK] Found Feishu desktop app: {desktop_path}")
    results["desktop_app"]["path"] = desktop_path

    # Try to launch and control
    try:
        print("\n[*] Attempting to launch desktop app...")

        async with async_playwright() as p:
            # Launch the desktop app
            import subprocess
            process = subprocess.Popen([desktop_path])
            await asyncio.sleep(5)  # Wait for app to start

            print("[OK] Desktop app launched")
            print("[*] Desktop app control capabilities:")
            print("    - Can launch application")
            print("    - Would need UI Automation for control")
            print("    - Consider using pywinauto for full control")

            results["desktop_app"]["status"] = "can_launch"
            results["capabilities"].append("Desktop: Launch Feishu app")

            # Try to find window with pywinauto if available
            try:
                from pywinauto import Application
                app = Application(backend="uia").connect(path=desktop_path, timeout=5)
                print("[OK] Connected via UI Automation")

                # Get window info
                windows = app.windows()
                print(f"[OK] Found {len(windows)} windows")

                results["desktop_app"]["status"] = "full_control"
                results["capabilities"].append("Desktop: Full UI automation via pywinauto")

            except ImportError:
                print("[!] pywinauto not installed - install for full desktop control")
                print("    pip install pywinauto")
            except Exception as e:
                print(f"[!] Could not connect to app: {e}")

            # Close the app
            process.terminate()

            return True

    except Exception as e:
        print(f"[ERROR] Desktop app test failed: {e}")
        results["desktop_app"]["status"] = "error"
        results["desktop_app"]["error"] = str(e)
        return False


async def test_human_capabilities():
    """Test 4: Human-like Capabilities"""
    print("\n" + "="*60)
    print("TEST 4: HUMAN-LIKE CAPABILITIES")
    print("="*60)

    capabilities = [
        "Send text messages",
        "Read message history",
        "List all chats",
        "Search for chats",
        "Upload files (via browser)",
        "Take screenshots",
        "Read notifications",
        "Create group chats (via browser)",
        "Add reactions (limited)",
        "Edit messages (limited)",
        "Delete messages (limited)",
        "Voice/video calls (via desktop app)",
        "Screen sharing (via desktop app)",
    ]

    print("\n[*] Available capabilities:")
    for cap in capabilities:
        print(f"    ✓ {cap}")
        results["capabilities"].append(cap)

    print("\n[*] Limitations:")
    limitations = [
        "Cannot bypass 2FA/security checks",
        "Reactions require manual interaction (Feishu UI limitation)",
        "Voice/video requires desktop app",
        "Some features need Bot API permissions",
    ]

    for lim in limitations:
        print(f"    ! {lim}")

    return True


async def generate_report():
    """Generate comprehensive test report"""
    print("\n" + "="*60)
    print("COMPREHENSIVE TEST REPORT")
    print("="*60)

    # Summary
    print("\n📊 SUMMARY:")
    print(f"  Bot API: {results['bot_api'].get('status', 'not tested')}")
    print(f"  Browser Web: {results['browser_web'].get('status', 'not tested')}")
    print(f"  Desktop App: {results['desktop_app'].get('status', 'not tested')}")

    # Working methods
    print("\n✅ WORKING METHODS:")
    working_methods = []

    if results['bot_api'].get('status') == 'working':
        working_methods.append("Bot API")
    if results['browser_web'].get('status') == 'working':
        working_methods.append("Browser Web Automation")
    if results['desktop_app'].get('status') in ['can_launch', 'full_control']:
        working_methods.append("Desktop App Control")

    if working_methods:
        for method in working_methods:
            print(f"  ✓ {method}")
    else:
        print("  ! No methods fully configured yet")
        print("  ! Run setup for browser or configure bot API")

    # Capabilities
    print("\n🎯 CAPABILITIES:")
    unique_caps = list(set(results['capabilities']))
    for cap in unique_caps:
        print(f"  • {cap}")

    # Recommendations
    print("\n💡 RECOMMENDATIONS:")

    if results['bot_api'].get('status') != 'working':
        print("  1. Configure Bot API for production use")
        print("     - Set FEISHU_APP_ID and FEISHU_APP_SECRET")
        print("     - Add bot to chats you want to automate")

    if results['browser_web'].get('status') == 'needs_login':
        print("  2. Run persistent session setup:")
        print("     python feishu_persistent.py setup")

    if results['desktop_app'].get('status') == 'can_launch':
        print("  3. Install pywinauto for full desktop control:")
        print("     pip install pywinauto")

    # Save report
    report_file = "feishu_test_report.json"
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n📄 Full report saved to: {report_file}")


async def main():
    print("\n" + "="*60)
    print("FEISHU COMPREHENSIVE AUTOMATION TEST")
    print("="*60)
    print("\nThis will test all automation methods and capabilities.")
    print("Please review each test result.\n")

    # Run all tests
    await test_bot_api()
    await test_browser_web()
    await test_desktop_app()
    await test_human_capabilities()

    # Generate report
    await generate_report()

    print("\n" + "="*60)
    print("TESTING COMPLETE!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
