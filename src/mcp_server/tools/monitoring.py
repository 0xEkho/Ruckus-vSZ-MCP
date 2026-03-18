"""
vSZ Monitoring and Query tools.

Covers generic query API, AP statistics and WLAN statistics.
"""
import json
import logging
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from mcp_server.api.client import API_VERSION, api_get, api_post

logger = logging.getLogger(__name__)

V = API_VERSION


def register_tools(mcp: FastMCP) -> None:
    """Register all vSZ monitoring / query tools."""

    @mcp.tool()
    async def vsz_query(
        host: str,
        query_type: str,
        filters: Optional[str] = None,
        full_text_search: Optional[str] = None,
        page: int = 1,
        limit: int = 100,
    ) -> str:
        """Run a generic vSZ query with optional filters.

        Supported query types: ap, client, wlan, dpsk, roguesInfoList, etc.

        Args:
            host: vSZ controller IP or hostname.
            query_type: Query type (ap, client, wlan, dpsk, roguesInfoList).
            filters: JSON string of filter criteria.
            full_text_search: Free-text search.
            page: Page number (1-indexed).
            limit: Results per page (max 1000).
        """
        body: dict[str, Any] = {
            "page": page,
            "limit": limit,
        }
        if filters:
            try:
                body["filters"] = json.loads(filters)
            except json.JSONDecodeError:
                return "ERROR: 'filters' must be valid JSON"
        if full_text_search:
            body["fullTextSearch"] = {"type": "AND", "value": full_text_search}
        result = await api_post(host, f"/{V}/query/{query_type}", data=body)
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_get_ap_statistics(host: str, ap_mac: str) -> str:
        """Get traffic statistics for a specific AP.

        Args:
            host: vSZ controller IP or hostname.
            ap_mac: AP MAC address.
        """
        result = await api_get(host, f"/{V}/aps/{ap_mac}/operational/summary")
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_get_wlan_statistics(
        host: str,
        wlan_name: Optional[str] = None,
    ) -> str:
        """Get statistics for WLANs via the query API.

        Returns WLAN statistics including client count, traffic and status.
        Optionally filter by WLAN name.

        Args:
            host: vSZ controller IP or hostname.
            wlan_name: WLAN name to filter (optional, returns all if omitted).
        """
        body: dict[str, Any] = {}
        if wlan_name:
            body["fullTextSearch"] = {"type": "AND", "value": wlan_name}
        result = await api_post(host, f"/{V}/query/wlan", data=body)
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)
