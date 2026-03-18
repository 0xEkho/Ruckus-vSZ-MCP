"""
vSZ Domain tools.

Covers domain listing, details and creation.
"""
import json
import logging
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from mcp_server.api.client import API_VERSION, api_get, api_post

logger = logging.getLogger(__name__)

V = API_VERSION


def register_tools(mcp: FastMCP) -> None:
    """Register all vSZ domain tools."""

    @mcp.tool()
    async def vsz_list_domains(host: str) -> str:
        """List all administration domains.

        Args:
            host: vSZ controller IP or hostname.
        """
        result = await api_get(host, f"/{V}/domains")
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_get_domain(host: str, domain_id: str) -> str:
        """Get details of a specific domain.

        Args:
            host: vSZ controller IP or hostname.
            domain_id: Domain UUID.
        """
        result = await api_get(host, f"/{V}/domains/{domain_id}")
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def vsz_create_domain(
        host: str,
        name: str,
        description: Optional[str] = None,
        parent_domain_id: Optional[str] = None,
    ) -> str:
        """Create a new administration domain.

        Args:
            host: vSZ controller IP or hostname.
            name: Domain name.
            description: Domain description.
            parent_domain_id: Parent domain UUID (for sub-domains).
        """
        body: dict[str, Any] = {"name": name}
        if description:
            body["description"] = description
        if parent_domain_id:
            body["parentDomainId"] = parent_domain_id
        result = await api_post(host, f"/{V}/domains", data=body)
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)
