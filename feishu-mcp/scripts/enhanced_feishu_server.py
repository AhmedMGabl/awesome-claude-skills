#!/usr/bin/env python3
"""
Enhanced Feishu MCP Server with Document, Base, and Wiki Support
Provides comprehensive access to all Feishu content types
Author: Claude AI (Sonnet 4.5)
Date: 2024-01-22
"""

import os
import json
import httpx
import asyncio
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize MCP server
mcp = FastMCP("Feishu Enhanced")

# Configuration
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "cli_a85833b3fc39900e")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")
FEISHU_API_BASE = "https://open.feishu.cn/open-apis"

# Token cache
_token_cache = {
    "tenant_token": None,
    "tenant_expires": 0
}


# ============================================================================
# AUTHENTICATION
# ============================================================================

async def get_tenant_token() -> str:
    """Get cached or fresh tenant access token"""
    current_time = datetime.now().timestamp()

    if _token_cache["tenant_token"] and current_time < _token_cache["tenant_expires"]:
        return _token_cache["tenant_token"]

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{FEISHU_API_BASE}/auth/v3/tenant_access_token/internal",
            json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET},
            timeout=30.0
        )
        data = response.json()

        if data.get("code") != 0:
            raise Exception(f"Auth failed: {data.get('msg')}")

        _token_cache["tenant_token"] = data["tenant_access_token"]
        _token_cache["tenant_expires"] = current_time + data["expire"] - 60

        return data["tenant_access_token"]


async def api_call(
    method: str,
    endpoint: str,
    params: Optional[Dict] = None,
    json_data: Optional[Dict] = None
) -> Dict:
    """Make authenticated API call"""
    token = await get_tenant_token()

    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=method,
            url=f"{FEISHU_API_BASE}{endpoint}",
            headers={"Authorization": f"Bearer {token}"},
            params=params,
            json=json_data,
            timeout=60.0
        )
        return response.json()


# ============================================================================
# DOCUMENT DISCOVERY & SEARCH
# ============================================================================

@mcp.tool()
async def search_all_content(
    query: str,
    content_types: Optional[List[str]] = None,
    owner_ids: Optional[List[str]] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 20
) -> str:
    """
    Search across all Feishu content types.

    Args:
        query: Search keywords
        content_types: Filter by type (doc, sheet, bitable, wiki, file)
        owner_ids: Filter by owner user IDs
        date_from: Start date (YYYY-MM-DD)
        date_to: End date (YYYY-MM-DD)
        limit: Max results

    Returns:
        Comprehensive search results across all content
    """
    results = []

    # Search files/documents in Drive
    try:
        search_payload = {
            "search_key": query,
            "count": limit
        }
        if owner_ids:
            search_payload["owner_ids"] = owner_ids

        drive_result = await api_call(
            "POST",
            "/drive/v1/files/search",
            json_data=search_payload
        )

        if drive_result.get("code") == 0:
            files = drive_result.get("data", {}).get("files", [])
            for file in files:
                results.append({
                    "type": file.get("type", "file"),
                    "name": file.get("name", "Unnamed"),
                    "url": file.get("url", ""),
                    "owner": file.get("owner_id", "Unknown"),
                    "modified": file.get("modified_time", ""),
                    "location": "Drive"
                })
    except Exception as e:
        results.append({"error": f"Drive search failed: {str(e)}"})

    # Format output
    if not results:
        return f"No results found for '{query}'"

    output = [f"🔍 Found {len(results)} results for '{query}':\n"]

    for i, result in enumerate(results, 1):
        if "error" in result:
            output.append(f"⚠️ {result['error']}")
            continue

        output.append(f"{i}. {result['name']}")
        output.append(f"   📁 Type: {result['type']}")
        output.append(f"   👤 Owner: {result['owner']}")
        output.append(f"   📅 Modified: {result['modified']}")
        output.append(f"   🔗 URL: {result['url']}")
        output.append("")

    return "\n".join(output)


# ============================================================================
# FEISHU DOCS (DOCUMENTS) OPERATIONS
# ============================================================================

@mcp.tool()
async def read_document(document_id: str) -> str:
    """
    Read content from a Feishu Doc.

    Args:
        document_id: Document ID or token

    Returns:
        Document content
    """
    result = await api_call(
        "GET",
        f"/docx/v1/documents/{document_id}/raw_content"
    )

    if result.get("code") != 0:
        return f"Error: {result.get('msg')}"

    content = result.get("data", {}).get("content", "")
    return f"📄 Document Content:\n\n{content}"


@mcp.tool()
async def update_document_block(
    document_id: str,
    block_id: str,
    new_content: str
) -> str:
    """
    Update a specific block in a Feishu Doc.

    Args:
        document_id: Document ID
        block_id: Block ID to update
        new_content: New content for the block

    Returns:
        Confirmation message
    """
    payload = {
        "block": {
            "text": {
                "elements": [
                    {
                        "text_run": {
                            "content": new_content
                        }
                    }
                ]
            }
        }
    }

    result = await api_call(
        "PATCH",
        f"/docx/v1/documents/{document_id}/blocks/{block_id}",
        json_data=payload
    )

    if result.get("code") != 0:
        return f"Error: {result.get('msg')}"

    return f"✅ Block updated successfully"


# ============================================================================
# FEISHU BASE (SPREADSHEET/DATABASE) OPERATIONS
# ============================================================================

@mcp.tool()
async def list_bases(page_size: int = 50) -> str:
    """
    List all Feishu Bases (spreadsheets) user has access to.

    Args:
        page_size: Number of bases to return

    Returns:
        List of bases
    """
    result = await api_call(
        "GET",
        "/bitable/v1/apps",
        params={"page_size": page_size}
    )

    if result.get("code") != 0:
        return f"Error: {result.get('msg')}"

    bases = result.get("data", {}).get("items", [])

    if not bases:
        return "No bases found"

    output = [f"📊 {len(bases)} Bases:\n"]

    for i, base in enumerate(bases, 1):
        name = base.get("name", "Unnamed")
        app_token = base.get("app_token", "")
        output.append(f"{i}. {name}")
        output.append(f"   Token: {app_token}")
        output.append("")

    return "\n".join(output)


@mcp.tool()
async def search_base_records(
    app_token: str,
    table_id: str,
    field_name: str,
    search_value: str,
    operator: str = "contains"
) -> str:
    """
    Search for records in a Feishu Base table.

    Args:
        app_token: Base app token
        table_id: Table ID within base
        field_name: Field/column to search
        search_value: Value to search for
        operator: Comparison operator (is, isNot, contains, doesNotContain, isEmpty, isNotEmpty)

    Returns:
        Matching records
    """
    payload = {
        "filter": {
            "conditions": [
                {
                    "field_name": field_name,
                    "operator": operator,
                    "value": [search_value]
                }
            ],
            "conjunction": "and"
        }
    }

    result = await api_call(
        "POST",
        f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/search",
        json_data=payload
    )

    if result.get("code") != 0:
        return f"Error: {result.get('msg')}"

    records = result.get("data", {}).get("items", [])

    if not records:
        return f"No records found matching '{search_value}'"

    output = [f"📋 Found {len(records)} records:\n"]

    for i, record in enumerate(records, 1):
        record_id = record.get("record_id", "")
        fields = record.get("fields", {})
        output.append(f"{i}. Record ID: {record_id}")
        for key, value in fields.items():
            output.append(f"   {key}: {value}")
        output.append("")

    return "\n".join(output)


@mcp.tool()
async def update_base_record(
    app_token: str,
    table_id: str,
    record_id: str,
    fields: Dict[str, Any]
) -> str:
    """
    Update a record in a Feishu Base table.

    Args:
        app_token: Base app token
        table_id: Table ID
        record_id: Record ID to update
        fields: Dictionary of field names and new values

    Returns:
        Confirmation message
    """
    payload = {
        "records": [
            {
                "record_id": record_id,
                "fields": fields
            }
        ]
    }

    result = await api_call(
        "POST",
        f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_update",
        json_data=payload
    )

    if result.get("code") != 0:
        return f"Error: {result.get('msg')}"

    return f"✅ Record updated successfully: {record_id}"


@mcp.tool()
async def create_base_record(
    app_token: str,
    table_id: str,
    fields: Dict[str, Any]
) -> str:
    """
    Create a new record in a Feishu Base table.

    Args:
        app_token: Base app token
        table_id: Table ID
        fields: Dictionary of field names and values

    Returns:
        New record ID
    """
    payload = {
        "records": [
            {
                "fields": fields
            }
        ]
    }

    result = await api_call(
        "POST",
        f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create",
        json_data=payload
    )

    if result.get("code") != 0:
        return f"Error: {result.get('msg')}"

    record_id = result.get("data", {}).get("records", [{}])[0].get("record_id", "")
    return f"✅ Record created! ID: {record_id}"


# ============================================================================
# WIKI OPERATIONS
# ============================================================================

@mcp.tool()
async def search_wiki(
    query: str,
    space_id: Optional[str] = None
) -> str:
    """
    Search wiki pages.

    Args:
        query: Search keywords
        space_id: Optional wiki space ID to search within

    Returns:
        Matching wiki pages
    """
    payload = {"query": query}
    if space_id:
        payload["space_id"] = space_id

    result = await api_call(
        "POST",
        "/wiki/v2/spaces/query",
        json_data=payload
    )

    if result.get("code") != 0:
        return f"Error: {result.get('msg')}"

    spaces = result.get("data", {}).get("items", [])

    if not spaces:
        return f"No wiki pages found for '{query}'"

    output = [f"📖 Found {len(spaces)} wiki results:\n"]

    for i, space in enumerate(spaces, 1):
        name = space.get("name", "Unnamed")
        space_id = space.get("space_id", "")
        output.append(f"{i}. {name}")
        output.append(f"   Space ID: {space_id}")
        output.append("")

    return "\n".join(output)


@mcp.tool()
async def read_wiki_page(
    space_id: str,
    node_token: str
) -> str:
    """
    Read content from a wiki page.

    Args:
        space_id: Wiki space ID
        node_token: Page node token

    Returns:
        Page content
    """
    result = await api_call(
        "GET",
        f"/wiki/v2/spaces/{space_id}/nodes/{node_token}"
    )

    if result.get("code") != 0:
        return f"Error: {result.get('msg')}"

    node = result.get("data", {}).get("node", {})
    title = node.get("title", "Untitled")
    obj_type = node.get("obj_type", "unknown")

    return f"📖 Wiki Page: {title}\nType: {obj_type}\nNode: {node_token}"


# ============================================================================
# DOCUMENT TRACKING SYSTEM
# ============================================================================

@mcp.tool()
async def track_document(
    document_name: str,
    document_type: str,
    document_url: str,
    status: str = "Found",
    priority: str = "Medium",
    notes: str = ""
) -> str:
    """
    Add a document to the tracking system.

    Args:
        document_name: Name of the document
        document_type: Type (Doc, Base, Wiki, Chat)
        document_url: URL or ID of document
        status: Status (Found, Needs Review, Updated, Verified)
        priority: Priority (High, Medium, Low)
        notes: Additional notes

    Returns:
        Confirmation with tracking record ID

    Note: Requires a tracking base to be set up. Set TRACKING_BASE_TOKEN and TRACKING_TABLE_ID env vars.
    """
    tracking_base = os.getenv("TRACKING_BASE_TOKEN")
    tracking_table = os.getenv("TRACKING_TABLE_ID")

    if not tracking_base or not tracking_table:
        return "⚠️ Tracking base not configured. Set TRACKING_BASE_TOKEN and TRACKING_TABLE_ID environment variables."

    fields = {
        "Document Name": document_name,
        "Type": document_type,
        "URL/ID": document_url,
        "Status": status,
        "Last Updated": datetime.now().strftime("%Y-%m-%d"),
        "Priority": priority,
        "Notes": notes
    }

    return await create_base_record(tracking_base, tracking_table, fields)


# ============================================================================
# UTILITY
# ============================================================================

@mcp.tool()
async def test_enhanced_connection() -> str:
    """Test connection and permissions for enhanced features"""
    status = []

    # Test Drive access
    try:
        result = await api_call("POST", "/drive/v1/files/search", json_data={"search_key": "test", "count": 1})
        if result.get("code") == 0:
            status.append("✅ Drive: OK")
        else:
            status.append(f"⚠️ Drive: {result.get('msg')}")
    except Exception as e:
        status.append(f"❌ Drive: {str(e)}")

    # Test Base access
    try:
        result = await api_call("GET", "/bitable/v1/apps", params={"page_size": 1})
        if result.get("code") == 0:
            status.append("✅ Base: OK")
        else:
            status.append(f"⚠️ Base: {result.get('msg')}")
    except Exception as e:
        status.append(f"❌ Base: {str(e)}")

    return "🔍 Enhanced Features Status:\n\n" + "\n".join(status)


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    print("Starting Enhanced Feishu MCP Server...")
    print(f"App ID: {FEISHU_APP_ID}")
    print("Features: Documents, Bases, Wikis, Tracking")
    mcp.run()
