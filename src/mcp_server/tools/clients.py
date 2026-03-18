"""
vSZ Wireless Client tools.

Covers client listing, details, disconnection and query operations.
"""
import json
import logging
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from mcp_server.api.client import API_VERSION, api_post

logger = logging.getLogger(__name__)

V = API_VERSION


def register_tools(mcp: FastMCP) -> None:
    """Register all vSZ wireless-client tools."""

    @mcp.tool()
    async def vsz_list_clients(host: str) -> str:
        """List currently connected wireless clients.

        Uses the query API to retrieve the client table.

        Args:
            host: vSZ controller IP or hostname.
        """
        body: dict[str, Any] = {}
        result = await api_post(host, f"/{V}/query/client", data=body)
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_get_client(host: str, client_mac: str) -> str:
        """Get details of a specific wireless client by MAC address.

        Args:
            host: vSZ controller IP or hostname.
            client_mac: Client MAC address (e.g. "AB:CD:EF:12:34:56").
        """
        # Query API with fullTextSearch to find the client by MAC
        body: dict[str, Any] = {
            "fullTextSearch": {"type": "AND", "value": client_mac},
        }
        result = await api_post(host, f"/{V}/query/client", data=body)
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_disconnect_client(
        host: str, client_mac: str, ap_mac: str
    ) -> str:
        """Disconnect (deauthenticate) a wireless client.

        Requires both the client MAC and the AP MAC it is connected to.

        Args:
            host: vSZ controller IP or hostname.
            client_mac: Client MAC address.
            ap_mac: AP MAC address the client is associated with.
        """
        body = {"mac": client_mac, "apMac": ap_mac}
        result = await api_post(host, f"/{V}/clients/disconnect", data=body)
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_query_clients(
        host: str,
        filters: Optional[str] = None,
        full_text_search: Optional[str] = None,
    ) -> str:
        """Query wireless clients with advanced filters.

        Args:
            host: vSZ controller IP or hostname.
            filters: JSON string of filter criteria.
            full_text_search: Free-text search across client fields.
        """
        body: dict[str, Any] = {}
        if filters:
            try:
                body["filters"] = json.loads(filters)
            except json.JSONDecodeError:
                return "ERROR: 'filters' must be valid JSON"
        if full_text_search:
            body["fullTextSearch"] = {"type": "AND", "value": full_text_search}
        result = await api_post(host, f"/{V}/query/client", data=body)
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)
