"""
MCP Server - Main entry point.

This module initializes the FastMCP server and registers all tools,
resources, and prompts. Rename and adapt to your use case.
"""
import logging
import os
import sys

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables from .env file (if present)
load_dotenv()

# Configure logging to stderr ONLY (never stdout for STDIO transport)
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server — name and version read from environment
mcp = FastMCP(
    os.getenv("MCP_SERVER_NAME", "mcp-server"),
    version=os.getenv("MCP_SERVER_VERSION", "0.1.0"),
)

# Register tools, resources, and prompts by importing their modules
# Each module registers its primitives on the shared `mcp` instance
from mcp_server.tools.example import register_tools       # noqa: E402, F401
from mcp_server.resources.example import register_resources  # noqa: E402, F401
from mcp_server.prompts.example import register_prompts    # noqa: E402, F401

register_tools(mcp)
register_resources(mcp)
register_prompts(mcp)


def main() -> None:
    """Start the MCP server using the STDIO transport."""
    logger.info("Starting MCP server...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
