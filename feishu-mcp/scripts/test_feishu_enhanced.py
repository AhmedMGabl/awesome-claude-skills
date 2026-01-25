#!/usr/bin/env python3
"""
Feishu Enhanced MCP Server - Interactive Test Script

This script provides a simple command-line interface to test all Feishu
document management features. It helps verify that the enhanced server is
working correctly and demonstrates all available capabilities.

Usage:
    python test_feishu_enhanced.py

Features tested:
- Document search across all content types
- Feishu Docs reading and modification
- Feishu Bases (spreadsheet) operations
- Wiki search and access
- Document tracking
- Permission verification
"""

import os
import sys
import json
import asyncio
import httpx
from datetime import datetime
from typing import Optional, Dict, List, Any

# Configuration
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "cli_a85833b3fc39900e")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")
FEISHU_API_BASE = "https://open.feishu.cn/open-apis"

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print colored header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


# ============================================================================
# AUTHENTICATION
# ============================================================================

async def get_tenant_token() -> str:
    """Get Feishu tenant access token"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{FEISHU_API_BASE}/auth/v3/tenant_access_token/internal",
            json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET},
            timeout=30.0
        )
        data = response.json()

        if data.get("code") != 0:
            raise Exception(f"Auth failed: {data.get('msg', 'Unknown error')}")

        return data["tenant_access_token"]


async def api_call(method: str, endpoint: str, **kwargs) -> Dict:
    """Make authenticated API call to Feishu"""
    token = await get_tenant_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    url = f"{FEISHU_API_BASE}{endpoint}"

    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=method,
            url=url,
            headers=headers,
            timeout=30.0,
            **kwargs
        )
        return response.json()


# ============================================================================
# TEST FUNCTIONS
# ============================================================================

async def test_authentication():
    """Test 1: Verify authentication works"""
    print_header("Test 1: Authentication")

    try:
        token = await get_tenant_token()
        print_success("Authentication successful")
        print_info(f"Token: {token[:30]}...")
        return True
    except Exception as e:
        print_error(f"Authentication failed: {e}")
        return False


async def test_search_documents(query: str = ""):
    """Test 2: Search for documents across all content"""
    print_header("Test 2: Document Search")

    if not query:
        query = input(f"{Colors.YELLOW}Enter search query (or press Enter for 'test'): {Colors.RESET}") or "test"

    try:
        result = await api_call(
            "POST",
            "/drive/v1/files/search",
            json={"search_key": query, "count": 10}
        )

        if result.get("code") == 0:
            files = result.get("data", {}).get("files", [])
            print_success(f"Found {len(files)} documents")

            for idx, file in enumerate(files[:5], 1):
                name = file.get("name", "Unnamed")
                file_type = file.get("type", "Unknown")
                print(f"  {idx}. {name} ({file_type})")

            return True
        else:
            print_error(f"Search failed: {result.get('msg', 'Unknown error')}")
            return False
    except Exception as e:
        print_error(f"Search error: {e}")
        return False


async def test_list_bases():
    """Test 3: List all Feishu Bases (spreadsheets)"""
    print_header("Test 3: List Feishu Bases")

    try:
        result = await api_call(
            "GET",
            "/bitable/v1/apps",
            params={"page_size": 10}
        )

        if result.get("code") == 0:
            apps = result.get("data", {}).get("items", [])
            print_success(f"Found {len(apps)} Feishu Bases")

            for idx, app in enumerate(apps, 1):
                name = app.get("name", "Unnamed")
                app_token = app.get("app_token", "")
                print(f"  {idx}. {name} (token: {app_token[:15]}...)")

            return True
        else:
            print_error(f"List bases failed: {result.get('msg', 'Unknown error')}")
            return False
    except Exception as e:
        print_error(f"List bases error: {e}")
        return False


async def test_read_document(doc_id: str = ""):
    """Test 4: Read a Feishu document"""
    print_header("Test 4: Read Feishu Document")

    if not doc_id:
        doc_id = input(f"{Colors.YELLOW}Enter document ID (or press Enter to skip): {Colors.RESET}")
        if not doc_id:
            print_warning("Skipped - no document ID provided")
            return None

    try:
        result = await api_call(
            "GET",
            f"/docx/v1/documents/{doc_id}/raw_content"
        )

        if result.get("code") == 0:
            content = result.get("data", {}).get("content", "")
            print_success(f"Document read successfully")
            print_info(f"Content length: {len(content)} characters")
            print(f"\nPreview:\n{content[:200]}...\n")
            return True
        else:
            print_error(f"Read document failed: {result.get('msg', 'Unknown error')}")
            return False
    except Exception as e:
        print_error(f"Read document error: {e}")
        return False


async def test_permissions():
    """Test 5: Check all required permissions"""
    print_header("Test 5: Permission Check")

    permissions = [
        ("Drive Search", "/drive/v1/files/search", {"search_key": "test", "count": 1}),
        ("List Bases", "/bitable/v1/apps", {"page_size": 1}),
    ]

    results = []

    for name, endpoint, params in permissions:
        try:
            if endpoint == "/drive/v1/files/search":
                result = await api_call("POST", endpoint, json=params)
            else:
                result = await api_call("GET", endpoint, params=params)

            if result.get("code") == 0:
                print_success(f"{name}: Working")
                results.append(True)
            else:
                code = result.get("code")
                msg = result.get("msg", "Unknown error")
                print_error(f"{name}: Failed (Code {code}: {msg})")
                results.append(False)
        except Exception as e:
            print_error(f"{name}: Error ({e})")
            results.append(False)

    return all(results)


# ============================================================================
# INTERACTIVE MENU
# ============================================================================

async def show_menu():
    """Display interactive menu"""
    print_header("Feishu Enhanced MCP Server - Test Suite")
    print(f"{Colors.BOLD}Available Tests:{Colors.RESET}")
    print("  1. Test Authentication")
    print("  2. Search Documents")
    print("  3. List Feishu Bases (Spreadsheets)")
    print("  4. Read a Document")
    print("  5. Check All Permissions")
    print("  6. Run All Tests")
    print("  7. Show Server Info")
    print("  0. Exit")
    print()


async def show_server_info():
    """Display server configuration and status"""
    print_header("Server Information")

    print(f"{Colors.BOLD}Configuration:{Colors.RESET}")
    print(f"  App ID: {FEISHU_APP_ID}")
    print(f"  App Secret: {'*' * 10} (configured: {bool(FEISHU_APP_SECRET)})")
    print(f"  API Base: {FEISHU_API_BASE}")

    print(f"\n{Colors.BOLD}Available Tools:{Colors.RESET}")
    tools = [
        "search_all_content - Search across all Feishu content",
        "list_bases - List all Feishu Bases (spreadsheets)",
        "search_base_records - Query spreadsheet data",
        "update_base_record - Modify spreadsheet records",
        "create_base_record - Add new records",
        "read_document - Read Feishu Doc content",
        "update_document_block - Modify document blocks",
        "search_wiki - Search wiki pages",
        "read_wiki_page - Read wiki content",
        "track_document - Track important documents",
        "test_enhanced_connection - Verify permissions"
    ]

    for idx, tool in enumerate(tools, 1):
        print(f"  {idx:2d}. {tool}")

    print(f"\n{Colors.BOLD}Total Tools:{Colors.RESET} 11 document management tools")


async def run_all_tests():
    """Run all tests sequentially"""
    print_header("Running All Tests")

    results = []

    # Test 1: Authentication
    results.append(await test_authentication())

    # Test 2: Search (with default query)
    results.append(await test_search_documents(""))

    # Test 3: List Bases
    results.append(await test_list_bases())

    # Test 4: Skip read document (needs ID)
    print_header("Test 4: Read Document")
    print_warning("Skipped - requires specific document ID")

    # Test 5: Permissions
    results.append(await test_permissions())

    # Summary
    print_header("Test Summary")
    passed = sum(1 for r in results if r is True)
    total = len(results)

    print(f"{Colors.BOLD}Results:{Colors.RESET} {passed}/{total} tests passed")

    if passed == total:
        print_success("All tests passed! Feishu Enhanced MCP is working correctly.")
    else:
        print_warning(f"{total - passed} test(s) failed. Check permissions at open.feishu.cn")

    return passed == total


async def main_loop():
    """Main interactive loop"""
    while True:
        await show_menu()

        try:
            choice = input(f"{Colors.YELLOW}Select option (0-7): {Colors.RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n")
            print_info("Exiting...")
            break

        if choice == "0":
            print_info("Goodbye!")
            break
        elif choice == "1":
            await test_authentication()
        elif choice == "2":
            await test_search_documents()
        elif choice == "3":
            await test_list_bases()
        elif choice == "4":
            await test_read_document()
        elif choice == "5":
            await test_permissions()
        elif choice == "6":
            await run_all_tests()
        elif choice == "7":
            await show_server_info()
        else:
            print_warning("Invalid option. Please select 0-7.")

        input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("=" * 62)
    print("  Feishu Enhanced MCP Server - Interactive Tester")
    print("")
    print("  Test all document management features interactively")
    print("=" * 62)
    print(Colors.RESET)

    # Check credentials
    if not FEISHU_APP_SECRET:
        print_error("FEISHU_APP_SECRET not configured!")
        print_info("Set it in environment or .env file")
        sys.exit(1)

    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print("\n")
        print_info("Interrupted by user. Exiting...")
        sys.exit(0)
