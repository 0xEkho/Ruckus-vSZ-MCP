"""
vSZ DHCP and VLAN network tools.

Covers DHCP pool and VLAN pool listing and details within zones.
"""
import json
import logging

from mcp.server.fastmcp import FastMCP

from mcp_server.api.client import API_VERSION, api_get, api_post

logger = logging.getLogger(__name__)

V = API_VERSION


def register_tools(mcp: FastMCP) -> None:
    """Register all vSZ DHCP / VLAN tools."""

    @mcp.tool()
    async def vsz_list_dhcp_pools(host: str, zone_id: str) -> str:
        """List DHCP pools configured in a zone.

        Args:
            host: vSZ controller IP or hostname.
            zone_id: Zone UUID.
        """
        result = await api_get(
            host, f"/{V}/rkszones/{zone_id}/dhcpSite/dhcpProfile"
        )
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_get_dhcp_pool(host: str, zone_id: str, pool_id: str) -> str:
        """Get details of a specific DHCP pool.

        Args:
            host: vSZ controller IP or hostname.
            zone_id: Zone UUID.
            pool_id: DHCP pool UUID.
        """
        result = await api_get(
            host, f"/{V}/rkszones/{zone_id}/dhcpSite/dhcpProfile/{pool_id}"
        )
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_list_vlan_pools(host: str) -> str:
        """List VLAN pooling profiles.

        Uses POST /vlanpoolings query endpoint.

        Args:
            host: vSZ controller IP or hostname.
        """
        result = await api_post(host, f"/{V}/vlanpoolings/query", data={})
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_get_vlan_pool(host: str, pool_id: str) -> str:
        """Get details of a specific VLAN pool.

        Args:
            host: vSZ controller IP or hostname.
            pool_id: VLAN pool UUID.
        """
        result = await api_get(
            host, f"/{V}/vlanpoolings/{pool_id}"
        )
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)
