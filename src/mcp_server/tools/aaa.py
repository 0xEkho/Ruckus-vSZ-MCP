"""
vSZ Authentication / AAA tools.

Covers authentication server listing, details and
AAA connectivity testing (RADIUS, TACACS+, AD, LDAP).
"""
import json
import logging
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from mcp_server.api.client import API_VERSION, api_get, api_post

logger = logging.getLogger(__name__)

V = API_VERSION


def register_tools(mcp: FastMCP) -> None:
    """Register all vSZ AAA / authentication tools."""

    @mcp.tool()
    async def vsz_list_auth_servers(host: str) -> str:
        """List all authentication (AAA) servers.

        Args:
            host: vSZ controller IP or hostname.
        """
        result = await api_get(host, f"/{V}/services/auth/radius")
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_get_auth_server(host: str, server_id: str) -> str:
        """Get details of a specific authentication server.

        Args:
            host: vSZ controller IP or hostname.
            server_id: Auth server UUID.
        """
        result = await api_get(host, f"/{V}/services/auth/radius/{server_id}")
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_test_aaa(
        host: str,
        server_type: str,
        server_ip: str,
        server_port: int,
        shared_secret: str,
        auth_protocol: str = "PAP",
        test_username: Optional[str] = None,
        test_password: Optional[str] = None,
    ) -> str:
        """Test AAA server connectivity.

        Sends a test authentication request to validate the RADIUS/TACACS+ server
        is reachable and credentials work.

        Args:
            host: vSZ controller IP or hostname.
            server_type: Server type (RADIUS, TACACS_PLUS).
            server_ip: AAA server IP address.
            server_port: AAA server port (e.g. 1812 for RADIUS).
            shared_secret: Shared secret for the AAA server.
            auth_protocol: Auth protocol (PAP, CHAP, PEAP).
            test_username: Username to test with.
            test_password: Password to test with.
        """
        body: dict[str, Any] = {
            "type": server_type,
            "ip": server_ip,
            "port": server_port,
            "sharedSecret": shared_secret,
            "authProtocol": auth_protocol,
        }
        if test_username:
            body["userName"] = test_username
        if test_password:
            body["password"] = test_password
        result = await api_post(host, f"/{V}/services/auth/test", data=body)
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)
