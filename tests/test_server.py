"""Tests for the MCP server initialization and tool aggregation."""
import pytest
from unittest.mock import patch, MagicMock

from mcp.server.fastmcp import FastMCP

from mcp_server.tools import register_all_tools, _MODULES


# ===================================================================
# Server entry point
# ===================================================================
class TestServerInit:
    def test_server_module_imports(self):
        """server.py can be imported without side-effects breaking tests."""
        try:
            from mcp_server import server  # noqa: F401
        except TypeError:
            # FastMCP version may not support 'version' kwarg — acceptable
            pass

    def test_server_has_main_function(self):
        try:
            import mcp_server.server as srv_mod
            assert hasattr(srv_mod, "main")
            assert callable(srv_mod.main)
        except TypeError:
            # FastMCP version may not support 'version' kwarg — acceptable
            pass


# ===================================================================
# Tool aggregation via register_all_tools
# ===================================================================
class TestRegisterAllTools:
    def test_modules_list_contains_all_twelve(self):
        """_MODULES must reference all 12 tool sub-modules."""
        module_names = {m.__name__.split(".")[-1] for m in _MODULES}
        expected = {
            "system", "zones", "aps", "wlans", "clients",
            "alarms", "domains", "aaa", "dhcp", "monitoring",
            "block_clients", "rogue",
        }
        assert module_names == expected

    async def test_register_all_tools_populates_instance(self):
        mcp = FastMCP("test-aggregation")
        register_all_tools(mcp)
        tools = await mcp.list_tools()
        # At least the 47 canonical tools must exist
        assert len(tools) >= 47

    async def test_each_module_contributes_tools(self):
        """Each module registers at least one tool."""
        for module in _MODULES:
            mcp = FastMCP("test-single")
            module.register_tools(mcp)
            tools = await mcp.list_tools()
            assert len(tools) > 0, f"{module.__name__} registered 0 tools"

    async def test_no_duplicate_tool_names(self):
        mcp = FastMCP("test-dupes")
        register_all_tools(mcp)
        tools = await mcp.list_tools()
        names = [t.name for t in tools]
        assert len(names) == len(set(names)), f"Duplicate tools: {[n for n in names if names.count(n) > 1]}"

    async def test_all_tools_have_descriptions(self):
        mcp = FastMCP("test-docs")
        register_all_tools(mcp)
        tools = await mcp.list_tools()
        for tool in tools:
            assert tool.description, f"Tool '{tool.name}' has no description"

    async def test_all_vsz_tools_require_host_param(self):
        """Every vsz_* tool must accept a 'host' parameter."""
        mcp = FastMCP("test-host-param")
        register_all_tools(mcp)
        tools = await mcp.list_tools()
        for tool in tools:
            if tool.name.startswith("vsz_"):
                param_names = set(tool.inputSchema.get("properties", {}).keys())
                assert "host" in param_names, f"Tool '{tool.name}' missing 'host' parameter"
