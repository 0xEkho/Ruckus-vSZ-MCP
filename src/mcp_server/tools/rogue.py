"""
vSZ Rogue AP tools.

Covers listing detected rogue APs and marking/classifying them.
"""
import json
import logging
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from mcp_server.api.client import API_VERSION, api_post

logger = logging.getLogger(__name__)

V = API_VERSION


def register_tools(mcp: FastMCP) -> None:
    """Register all vSZ rogue-AP tools."""

    @mcp.tool()
    async def vsz_list_rogue_aps(
        host: str,
        filters: Optional[str] = None,
    ) -> str:
        """List detected rogue access points.

        Args:
            host: vSZ controller IP or hostname.
            filters: JSON string of filter criteria.
        """
        body: dict[str, Any] = {}
        if filters:
            try:
                body["filters"] = json.loads(filters)
            except json.JSONDecodeError:
                return "ERROR: 'filters' must be valid JSON"
        result = await api_post(host, f"/{V}/query/roguesInfoList", data=body)
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_mark_rogue(
        host: str,
        rogue_mac: str,
        classification: str = "Rogue",
    ) -> str:
        """Mark or classify a rogue AP.

        Args:
            host: vSZ controller IP or hostname.
            rogue_mac: Rogue AP MAC address.
            classification: Classification label (Rogue, Known, Malicious, Ignore).
        """
        action_map = {
            "Known": "markKnown",
            "Malicious": "markMalicious",
            "Ignore": "markIgnore",
            "Rogue": "markRogue",
        }
        action = action_map.get(classification)
        if not action:
            return f"ERROR: Invalid classification '{classification}'. Use: Rogue, Known, Malicious, Ignore"
        body: dict[str, Any] = {"rogueAPMac": rogue_mac}
        result = await api_post(
            host, f"/{V}/rogue/{action}", data=body
        )
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)
