"""
vSZ Block Client tools.

Covers listing, blocking and unblocking wireless clients by MAC address.
"""
import json
import logging
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from mcp_server.api.client import API_VERSION, api_delete, api_post

logger = logging.getLogger(__name__)

V = API_VERSION


def register_tools(mcp: FastMCP) -> None:
    """Register all vSZ block-client tools."""

    @mcp.tool()
    async def vsz_list_blocked_clients(host: str) -> str:
        """List all blocked (blacklisted) clients.

        Args:
            host: vSZ controller IP or hostname.
        """
        result = await api_post(host, f"/{V}/blockClient/query", data={})
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_block_client(
        host: str,
        mac: str,
        description: Optional[str] = None,
    ) -> str:
        """Block (blacklist) a wireless client by MAC address.

        Args:
            host: vSZ controller IP or hostname.
            mac: Client MAC address to block.
            description: Reason for blocking.
        """
        body: dict[str, Any] = {"mac": mac}
        if description:
            body["description"] = description
        result = await api_post(host, f"/{V}/blockClient", data=body)
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_unblock_client(host: str, client_id: str) -> str:
        """Unblock (remove from blacklist) a client.

        Args:
            host: vSZ controller IP or hostname.
            client_id: Blocked client entry UUID.
        """
        result = await api_delete(host, f"/{V}/blockClient/{client_id}")
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)
