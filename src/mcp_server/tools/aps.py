"""
vSZ Access Point tools.

Covers AP listing, details, operational info, configuration,
radio info, LLDP neighbours, reboot and query.
"""
import json
import logging
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from mcp_server.api.client import (
    API_VERSION,
    api_delete,
    api_get,
    api_patch,
    api_post,
    api_put,
)

logger = logging.getLogger(__name__)

V = API_VERSION


def register_tools(mcp: FastMCP) -> None:
    """Register all vSZ access-point tools."""

    @mcp.tool()
    async def vsz_list_aps(host: str) -> str:
        """List all access points managed by the vSZ controller.

        Args:
            host: vSZ controller IP or hostname.
        """
        result = await api_get(host, f"/{V}/aps")
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_get_ap(host: str, ap_mac: str) -> str:
        """Get configuration details of a specific access point.

        Args:
            host: vSZ controller IP or hostname.
            ap_mac: AP MAC address (e.g. "AB:CD:EF:12:34:56").
        """
        result = await api_get(host, f"/{V}/aps/{ap_mac}")
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_get_ap_operational(host: str, ap_mac: str) -> str:
        """Get operational information of an AP (uptime, clients, status).

        Args:
            host: vSZ controller IP or hostname.
            ap_mac: AP MAC address.
        """
        result = await api_get(host, f"/{V}/aps/{ap_mac}/operational/summary")
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_update_ap(
        host: str,
        ap_mac: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        zone_id: Optional[str] = None,
        ap_group_id: Optional[str] = None,
        location: Optional[str] = None,
        gps_latitude: Optional[float] = None,
        gps_longitude: Optional[float] = None,
    ) -> str:
        """Update access point configuration.

        Args:
            host: vSZ controller IP or hostname.
            ap_mac: AP MAC address.
            name: New AP name.
            description: New AP description.
            zone_id: Move AP to a different zone (UUID).
            ap_group_id: Assign AP to a different AP group (UUID).
            location: AP location string.
            gps_latitude: GPS latitude.
            gps_longitude: GPS longitude.
        """
        body: dict = {}
        if name:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if zone_id:
            body["zoneId"] = zone_id
        if ap_group_id:
            body["apGroupId"] = ap_group_id
        if location:
            body["location"] = location
        if gps_latitude is not None and gps_longitude is not None:
            body["gps"] = {"latitude": gps_latitude, "longitude": gps_longitude}
        if not body:
            return "ERROR: No fields to update"
        result = await api_patch(host, f"/{V}/aps/{ap_mac}", data=body)
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_delete_ap(host: str, ap_mac: str) -> str:
        """Remove an access point from vSZ management.

        Args:
            host: vSZ controller IP or hostname.
            ap_mac: AP MAC address.
        """
        result = await api_delete(host, f"/{V}/aps/{ap_mac}")
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_reboot_ap(host: str, ap_mac: str) -> str:
        """Reboot an access point.

        Args:
            host: vSZ controller IP or hostname.
            ap_mac: AP MAC address.
        """
        result = await api_put(host, f"/{V}/aps/{ap_mac}/reboot")
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_list_ap_mesh_neighbors(host: str, ap_mac: str) -> str:
        """Get mesh neighbor APs discovered by an AP (mesh topology).

        Args:
            host: vSZ controller IP or hostname.
            ap_mac: AP MAC address.
        """
        result = await api_get(host, f"/{V}/aps/{ap_mac}/operational/neighbor")
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_list_ap_lldp_neighbors(host: str, ap_mac: str) -> str:
        """Get LLDP neighbor devices discovered by an AP (switches, phones, etc.).

        Returns the list of LLDP neighbors with chassis ID, system name,
        port description, capabilities, management IP and power info.

        Args:
            host: vSZ controller IP or hostname.
            ap_mac: AP MAC address (e.g. 00:33:58:07:70:E0).
        """
        result = await api_get(host, f"/{V}/aps/{ap_mac}/apLldpNeighbors")
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_get_ap_radio(host: str, ap_mac: str) -> str:
        """Get radio configuration of an AP (2.4G / 5G / 6G).

        Returns the radioConfig section from the AP configuration endpoint.

        Args:
            host: vSZ controller IP or hostname.
            ap_mac: AP MAC address.
        """
        result = await api_get(host, f"/{V}/aps/{ap_mac}")
        if isinstance(result, str):
            return result
        # Extract radio-related fields
        radio_info: dict = {}
        if isinstance(result, dict):
            for key in ("radioConfig", "wifi24Channel", "wifi50Channel", "wifi6gChannel"):
                if key in result:
                    radio_info[key] = result[key]
            if not radio_info:
                radio_info = result
        return json.dumps(radio_info, indent=2)

    @mcp.tool()
    async def vsz_query_aps(
        host: str,
        filters: Optional[str] = None,
        full_text_search: Optional[str] = None,
    ) -> str:
        """Query access points with filters.

        Uses the vSZ query API to search APs by criteria.

        Note: DOMAIN-type filters may return 403 depending on the API
        account privileges. Prefer full_text_search when possible.

        Args:
            host: vSZ controller IP or hostname.
            filters: JSON string of filter criteria (e.g. '[{"type":"ZONE","value":"..."}]').
            full_text_search: Free-text search across AP fields (recommended).
        """
        body: dict[str, Any] = {}
        if filters:
            try:
                body["filters"] = json.loads(filters)
            except json.JSONDecodeError:
                return "ERROR: 'filters' must be valid JSON"
        if full_text_search:
            body["fullTextSearch"] = {"type": "AND", "value": full_text_search}
        result = await api_post(host, f"/{V}/query/ap", data=body)
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)
