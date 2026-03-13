"""
Example MCP Resources.

Resources are application-driven data sources that provide context to LLMs.
They are identified by URIs and can contain text or binary data.

Best practices:
- Use clear, meaningful URIs (e.g., config://app, file:///path/to/file)
- Include MIME types for binary resources
- Resources should be read-only and stable
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)


def register_resources(mcp: Any) -> None:
    """Register all resources on the MCP server instance."""

    @mcp.resource("config://server-info")
    def server_info() -> str:
        """Provide basic server configuration information.

        Returns key metadata about this MCP server instance.
        """
        return (
            "Server: mcp-server\n"
            "Version: 0.1.0\n"
            "Transport: stdio\n"
            "Description: MCP Template Server\n"
        )

    @mcp.resource("docs://getting-started")
    def getting_started() -> str:
        """Getting started guide for using this MCP server.

        Returns a markdown-formatted guide.
        """
        return """# Getting Started

This MCP server exposes the following primitives:

## Tools
- `echo` — Echo a message back (test connectivity)
- `fetch_url` — Fetch content from a URL

## Resources
- `config://server-info` — Server metadata
- `docs://getting-started` — This document

## Prompts
- `summarize` — Summarize a block of text
"""
