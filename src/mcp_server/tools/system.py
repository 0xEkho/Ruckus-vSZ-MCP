"""
vSZ System tools.

Covers system information, cluster status, controller list,
inventory and summary statistics.
"""
import json
import logging

from mcp.server.fastmcp import FastMCP

from mcp_server.api.client import API_VERSION, api_get

logger = logging.getLogger(__name__)

V = API_VERSION


def register_tools(mcp: FastMCP) -> None:
    """Register all vSZ system tools."""

    @mcp.tool()
    async def vsz_get_system_info(host: str) -> str:
        """Get vSZ controller system information (version, model, uptime).

        Args:
            host: vSZ controller IP or hostname.
        """
        result = await api_get(host, f"/{V}/controller")
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_get_system_summary(host: str) -> str:
        """Get system summary with AP count, client count and zone statistics.

        Tries /system/systemSummary first, falls back to /system/inventory.

        Args:
            host: vSZ controller IP or hostname.
        """
        result = await api_get(host, f"/{V}/system/systemSummary")
        if isinstance(result, str) and "404" in result:
            # Fallback for older vSZ versions
            result = await api_get(host, f"/{V}/system/inventory")
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_get_system_inventory(host: str) -> str:
        """Get system inventory with per-zone AP and client statistics.

        Args:
            host: vSZ controller IP or hostname.
        """
        result = await api_get(host, f"/{V}/system/inventory")
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_get_cluster_state(host: str) -> str:
        """Get cluster state including node status and roles.

        Args:
            host: vSZ controller IP or hostname.
        """
        result = await api_get(host, f"/{V}/cluster/state")
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_get_controller_list(host: str) -> str:
        """List all controllers in the cluster.

        Args:
            host: vSZ controller IP or hostname.
        """
        result = await api_get(host, f"/{V}/controller")
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)
