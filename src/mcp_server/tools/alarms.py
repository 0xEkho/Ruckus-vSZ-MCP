"""
vSZ Alarm and Event tools.

Covers alarm listing, details, acknowledgement and clearing.
"""
import json
import logging

from mcp.server.fastmcp import FastMCP

from mcp_server.api.client import API_VERSION, api_post, api_put

logger = logging.getLogger(__name__)

V = API_VERSION


def register_tools(mcp: FastMCP) -> None:
    """Register all vSZ alarm tools."""

    @mcp.tool()
    async def vsz_list_alarms(host: str) -> str:
        """List active alarms on the vSZ controller.

        Args:
            host: vSZ controller IP or hostname.
        """
        result = await api_post(host, f"/{V}/alert/alarm/list", data={})
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_get_alarm(host: str, alarm_id: str) -> str:
        """Get details of a specific alarm.

        Fetches the alarm list and filters for the matching alarm ID,
        as the vSZ API does not expose a single-alarm GET endpoint.

        Args:
            host: vSZ controller IP or hostname.
            alarm_id: Alarm UUID (e.g. 'Alarm_303_...').
        """
        result = await api_post(host, f"/{V}/alert/alarm/list", data={})
        if isinstance(result, str):
            return result
        if isinstance(result, dict) and result.get("list"):
            for alarm in result["list"]:
                if alarm.get("id") == alarm_id or alarm.get("alarmUUID") == alarm_id:
                    return json.dumps(alarm, indent=2)
            return f"ERROR: Alarm '{alarm_id}' not found"
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_acknowledge_alarm(host: str, alarm_id: str) -> str:
        """Acknowledge an active alarm.

        Args:
            host: vSZ controller IP or hostname.
            alarm_id: Alarm UUID (e.g. 'Alarm_303_...').
        """
        result = await api_put(host, f"/{V}/alert/alarm/{alarm_id}/ack")
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_clear_alarm(host: str, alarm_id: str) -> str:
        """Clear (dismiss) an alarm.

        Args:
            host: vSZ controller IP or hostname.
            alarm_id: Alarm UUID (e.g. 'Alarm_303_...').
        """
        result = await api_put(host, f"/{V}/alert/alarm/{alarm_id}/clear")
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)
