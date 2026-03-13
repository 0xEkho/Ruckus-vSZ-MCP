"""Tests for MCP resources."""
import pytest
from mcp.server.fastmcp import FastMCP


@pytest.fixture
def mcp_with_resources():
    """Create a FastMCP instance with resources registered."""
    instance = FastMCP("test-server")
    from mcp_server.resources.example import register_resources
    register_resources(instance)
    return instance


@pytest.mark.asyncio
async def test_server_info_resource_exists(mcp_with_resources):
    """Test that config://server-info resource is registered."""
    resources = await mcp_with_resources.list_resources()
    uris = [str(r.uri) for r in resources]
    assert "config://server-info" in uris


@pytest.mark.asyncio
async def test_getting_started_resource_exists(mcp_with_resources):
    """Test that docs://getting-started resource is registered."""
    resources = await mcp_with_resources.list_resources()
    uris = [str(r.uri) for r in resources]
    assert "docs://getting-started" in uris


@pytest.mark.asyncio
async def test_server_info_content(mcp_with_resources):
    """Test that server-info resource returns expected content."""
    result = await mcp_with_resources.read_resource("config://server-info")
    # read_resource returns content as string or list; normalize to string
    content = result if isinstance(result, str) else str(result)
    assert "mcp-server" in content
    assert "0.1.0" in content
