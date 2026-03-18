"""
vSZ Zone management tools.

Covers zone CRUD operations and AP group listing per zone.
"""
import json
import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP

from mcp_server.api.client import API_VERSION, api_delete, api_get, api_patch, api_post

logger = logging.getLogger(__name__)

V = API_VERSION


def register_tools(mcp: FastMCP) -> None:
    """Register all vSZ zone tools."""

    @mcp.tool()
    async def vsz_list_zones(host: str) -> str:
        """List all zones configured on the vSZ controller.

        Args:
            host: vSZ controller IP or hostname.
        """
        result = await api_get(host, f"/{V}/rkszones")
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_get_zone(host: str, zone_id: str) -> str:
        """Get detailed information about a specific zone.

        Args:
            host: vSZ controller IP or hostname.
            zone_id: Zone UUID.
        """
        result = await api_get(host, f"/{V}/rkszones/{zone_id}")
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_create_zone(
        host: str,
        name: str,
        description: Optional[str] = None,
        domain_id: Optional[str] = None,
        country_code: Optional[str] = None,
    ) -> str:
        """Create a new zone on the vSZ controller.

        Args:
            host: vSZ controller IP or hostname.
            name: Zone name.
            description: Optional zone description.
            domain_id: Optional domain UUID to associate.
            country_code: Optional two-letter country code (e.g. "FR").
        """
        body: dict = {"name": name}
        if description:
            body["description"] = description
        if domain_id:
            body["domainId"] = domain_id
        if country_code:
            body["countryCode"] = country_code
        result = await api_post(host, f"/{V}/rkszones", data=body)
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_update_zone(
        host: str,
        zone_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> str:
        """Update an existing zone's configuration.

        Args:
            host: vSZ controller IP or hostname.
            zone_id: Zone UUID.
            name: New name for the zone.
            description: New description for the zone.
        """
        body: dict = {}
        if name:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if not body:
            return "ERROR: No fields to update"
        result = await api_patch(host, f"/{V}/rkszones/{zone_id}", data=body)
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_delete_zone(host: str, zone_id: str) -> str:
        """Delete a zone from the vSZ controller.

        Args:
            host: vSZ controller IP or hostname.
            zone_id: Zone UUID.
        """
        result = await api_delete(host, f"/{V}/rkszones/{zone_id}")
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_list_zone_ap_groups(host: str, zone_id: str) -> str:
        """List AP groups configured in a specific zone.

        Args:
            host: vSZ controller IP or hostname.
            zone_id: Zone UUID.
        """
        result = await api_get(host, f"/{V}/rkszones/{zone_id}/apgroups")
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)
