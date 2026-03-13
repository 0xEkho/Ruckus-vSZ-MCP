"""Tests for MCP tools."""
import pytest
from unittest.mock import AsyncMock, patch
from mcp.server.fastmcp import FastMCP


@pytest.fixture
def mcp_instance():
    """Create a fresh FastMCP instance for testing."""
    instance = FastMCP("test-server")
    from mcp_server.tools.example import register_tools
    register_tools(instance)
    return instance


@pytest.mark.asyncio
async def test_echo_returns_message():
    """Test that echo tool returns the message prefixed with 'Echo: '."""
    mcp = FastMCP("test")
    from mcp_server.tools.example import register_tools
    register_tools(mcp)

    # Access the registered tool function directly
    tools = {t.name: t for t in await mcp.list_tools()}
    assert "echo" in tools

    result = await mcp.call_tool("echo", {"message": "hello"})
    assert len(result) > 0
    assert "hello" in result[0].text


@pytest.mark.asyncio
async def test_fetch_url_rejects_invalid_url():
    """Test that fetch_url returns an error for non-HTTP URLs."""
    mcp = FastMCP("test")
    from mcp_server.tools.example import register_tools
    register_tools(mcp)

    result = await mcp.call_tool("fetch_url", {"url": "ftp://example.com"})
    assert len(result) > 0
    assert "Error" in result[0].text


@pytest.mark.asyncio
async def test_fetch_url_handles_http_error():
    """Test that fetch_url handles HTTP errors gracefully."""
    import httpx
    mcp = FastMCP("test")
    from mcp_server.tools.example import register_tools
    register_tools(mcp)

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)

        mock_response = AsyncMock()
        mock_response.status_code = 404
        mock_client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "404", request=AsyncMock(), response=mock_response
            )
        )

        result = await mcp.call_tool("fetch_url", {"url": "https://example.com/notfound"})
        assert len(result) > 0
        assert "Error" in result[0].text
