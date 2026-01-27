#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify Feishu Enhanced MCP server starts properly
Run this before restarting Claude Code to catch any issues
"""

import sys
import subprocess
import os

def check_python_version():
    """Check Python version is 3.8+"""
    print("[*] Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"[OK] Python {version.major}.{version.minor}.{version.micro} OK")
        return True
    else:
        print(f"[FAIL] Python {version.major}.{version.minor} is too old. Need 3.8+")
        return False


def check_dependencies():
    """Check required packages are installed"""
    print("\n[*] Checking dependencies...")
    required = [("httpx", "httpx"), ("fastmcp", "fastmcp"), ("python-dotenv", "dotenv")]
    missing = []

    for display_name, import_name in required:
        try:
            __import__(import_name)
            print(f"[OK] {display_name} installed")
        except ImportError:
            print(f"[FAIL] {display_name} NOT installed")
            missing.append(display_name)

    if missing:
        print(f"\n[WARN] Install missing packages:")
        print(f"   pip install {' '.join(missing)}")
        return False

    return True


def check_server_file():
    """Check server.py exists and is readable"""
    print("\n[*] Checking server file...")
    server_path = os.path.join(os.path.dirname(__file__), "server.py")

    if not os.path.exists(server_path):
        print(f"[FAIL] server.py not found at: {server_path}")
        return False

    size = os.path.getsize(server_path)
    if size < 10000:
        print(f"[WARN] server.py seems too small ({size} bytes)")
        return False

    print(f"[OK] server.py exists ({size} bytes)")
    return True


def check_credentials():
    """Check credentials are configured"""
    print("\n[*] Checking credentials...")

    # Check in .mcp.json
    mcp_json_path = os.path.join(os.path.dirname(__file__), ".mcp.json")
    if os.path.exists(mcp_json_path):
        with open(mcp_json_path, 'r') as f:
            content = f.read()
            if "cli_a85833b3fc39900e" in content:
                print("[OK] App ID found in .mcp.json")
            else:
                print("[WARN] App ID not found in .mcp.json")

            if "FEISHU_APP_SECRET" in content and "your_secret" not in content.lower():
                print("[OK] App Secret configured in .mcp.json")
            else:
                print("[WARN] App Secret might not be configured")

    return True


def test_import_server():
    """Try to import the server module"""
    print("\n[*] Testing server import...")

    try:
        # Add current directory to path
        sys.path.insert(0, os.path.dirname(__file__))

        # Try importing (don't actually run it)
        import importlib.util
        server_path = os.path.join(os.path.dirname(__file__), "server.py")

        spec = importlib.util.spec_from_file_location("server", server_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            print("[OK] Server module can be loaded")
            return True
        else:
            print("[FAIL] Could not load server module")
            return False

    except Exception as e:
        print(f"[FAIL] Import failed: {str(e)}")
        return False


def check_tool_count():
    """Count MCP tools in server.py"""
    print("\n[*] Checking MCP tools...")

    server_path = os.path.join(os.path.dirname(__file__), "server.py")
    with open(server_path, 'r', encoding='utf-8') as f:
        content = f.read()
        tool_count = content.count("@mcp.tool()")

        expected_tools = [
            "search_all_content",
            "read_document",
            "update_document_block",
            "list_bases",
            "search_base_records",
            "update_base_record",
            "create_base_record",
            "search_wiki",
            "read_wiki_page",
            "track_document",
            "test_enhanced_connection"
        ]

        found_tools = []
        missing_tools = []

        for tool in expected_tools:
            if f"async def {tool}" in content:
                found_tools.append(tool)
            else:
                missing_tools.append(tool)

        print(f"[OK] Found {len(found_tools)}/{len(expected_tools)} tools")

        if missing_tools:
            print(f"[WARN] Missing tools: {', '.join(missing_tools)}")
            return False

        return True


def main():
    print("=" * 60)
    print("Feishu Enhanced MCP Server - Pre-Restart Test")
    print("=" * 60)

    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Server File", check_server_file),
        ("Credentials", check_credentials),
        ("Server Import", test_import_server),
        ("MCP Tools", check_tool_count),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"[FAIL] {name} check crashed: {e}")
            results.append((name, False))

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    all_passed = True
    for name, result in results:
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n[OK] ALL CHECKS PASSED!")
        print("\n[>>>] Ready to restart Claude Code")
        print("\nNext steps:")
        print("1. Close Claude Code completely")
        print("2. Restart Claude Code")
        print("3. Test with: 'Test Feishu MCP connection'")
        return 0
    else:
        print("\n[WARN] SOME CHECKS FAILED")
        print("\nFix the issues above before restarting Claude Code")
        return 1


if __name__ == "__main__":
    sys.exit(main())
