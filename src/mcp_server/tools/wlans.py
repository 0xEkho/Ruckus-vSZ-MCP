"""
vSZ WLAN tools.

Covers WLAN listing, details, creation, update, deletion
and enable/disable operations within a zone.
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
)

logger = logging.getLogger(__name__)

V = API_VERSION


def register_tools(mcp: FastMCP) -> None:
    """Register all vSZ WLAN tools."""

    @mcp.tool()
    async def vsz_list_wlans(host: str, zone_id: str) -> str:
        """List all WLANs in a zone.

        Args:
            host: vSZ controller IP or hostname.
            zone_id: Zone UUID.
        """
        result = await api_get(host, f"/{V}/rkszones/{zone_id}/wlans")
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_get_wlan(host: str, zone_id: str, wlan_id: str) -> str:
        """Get WLAN configuration details.

        Args:
            host: vSZ controller IP or hostname.
            zone_id: Zone UUID.
            wlan_id: WLAN UUID.
        """
        result = await api_get(host, f"/{V}/rkszones/{zone_id}/wlans/{wlan_id}")
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_create_wlan(
        host: str,
        zone_id: str,
        name: str,
        ssid: str,
        security_type: str = "Open",
        encryption_method: Optional[str] = None,
        passphrase: Optional[str] = None,
        description: Optional[str] = None,
        vlan_id: Optional[int] = None,
    ) -> str:
        """Create a new WLAN in a zone.

        Args:
            host: vSZ controller IP or hostname.
            zone_id: Zone UUID.
            name: WLAN name.
            ssid: SSID to broadcast.
            security_type: Security type (Open, WPA2, WPA3, WPA23_Mixed, WEP).
            encryption_method: Encryption method (AES, TKIP_AES) for WPA.
            passphrase: PSK passphrase (required for WPA security).
            description: WLAN description.
            vlan_id: Access VLAN ID.
        """
        body: dict[str, Any] = {"name": name, "ssid": ssid}
        if description:
            body["description"] = description
        if vlan_id is not None:
            body["vlan"] = {"accessVlan": vlan_id}

        # Build encryption section
        encryption: dict[str, Any] = {"method": encryption_method or "AES"}
        if security_type != "Open":
            encryption["support80211w"] = "DISABLED"
            if passphrase:
                encryption["passphrase"] = passphrase
        body["encryption"] = encryption

        result = await api_post(host, f"/{V}/rkszones/{zone_id}/wlans", data=body)
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_update_wlan(
        host: str,
        zone_id: str,
        wlan_id: str,
        name: Optional[str] = None,
        ssid: Optional[str] = None,
        description: Optional[str] = None,
        vlan_id: Optional[int] = None,
    ) -> str:
        """Update WLAN configuration.

        Args:
            host: vSZ controller IP or hostname.
            zone_id: Zone UUID.
            wlan_id: WLAN UUID.
            name: New WLAN name.
            ssid: New SSID.
            description: New description.
            vlan_id: New access VLAN ID.
        """
        body: dict[str, Any] = {}
        if name:
            body["name"] = name
        if ssid:
            body["ssid"] = ssid
        if description is not None:
            body["description"] = description
        if vlan_id is not None:
            body["vlan"] = {"accessVlan": vlan_id}
        if not body:
            return "ERROR: No fields to update"
        result = await api_patch(
            host, f"/{V}/rkszones/{zone_id}/wlans/{wlan_id}", data=body
        )
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_delete_wlan(host: str, zone_id: str, wlan_id: str) -> str:
        """Delete a WLAN from a zone.

        Args:
            host: vSZ controller IP or hostname.
            zone_id: Zone UUID.
            wlan_id: WLAN UUID.
        """
        result = await api_delete(host, f"/{V}/rkszones/{zone_id}/wlans/{wlan_id}")
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_enable_disable_wlan(
        host: str, zone_id: str, wlan_id: str, enabled: bool
    ) -> str:
        """Enable or disable a WLAN.

        Args:
            host: vSZ controller IP or hostname.
            zone_id: Zone UUID.
            wlan_id: WLAN UUID.
            enabled: True to enable, False to disable.
        """
        # The vSZ API uses PATCH on the WLAN resource to toggle state
        body: dict[str, Any] = {"enabled": enabled}
        result = await api_patch(
            host, f"/{V}/rkszones/{zone_id}/wlans/{wlan_id}", data=body
        )
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)
