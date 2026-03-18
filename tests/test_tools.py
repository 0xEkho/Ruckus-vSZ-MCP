"""Comprehensive tests for all vSZ MCP tool modules.

Tests cover:
- Tool registration for each module
- Nominal behavior with mocked API responses
- Error propagation (API returning error strings)
- Edge cases (empty updates, invalid JSON filters)
"""
import json

import pytest
from unittest.mock import AsyncMock, patch

from mcp.server.fastmcp import FastMCP

from mcp_server.tools import register_all_tools

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _text(result) -> str:
    """Extract text from call_tool result.

    mcp >=1.26 returns ``(content_list, raw_result)`` tuple.
    """
    content = result[0]  # list of TextContent
    return content[0].text


HOST = "10.0.0.1"
ZONE_ID = "zone-uuid-1234"
WLAN_ID = "wlan-uuid-5678"
AP_MAC = "AA:BB:CC:DD:EE:FF"
CLIENT_MAC = "11:22:33:44:55:66"
ALARM_ID = "alarm-uuid-0001"
DOMAIN_ID = "domain-uuid-0001"
SERVER_ID = "auth-server-uuid"
POOL_ID = "pool-uuid-0001"
CLIENT_ID = "blocked-client-uuid"
ROGUE_MAC = "99:88:77:66:55:44"


# ---------------------------------------------------------------------------
# Fixtures — one per module + one with all tools
# ---------------------------------------------------------------------------
@pytest.fixture
def mcp_all_tools():
    """FastMCP instance with ALL vSZ tools registered."""
    mcp = FastMCP("test-all")
    register_all_tools(mcp)
    return mcp


def _make_module_fixture(module_path: str):
    """Factory for per-module fixtures."""

    @pytest.fixture
    def _fix():
        mcp = FastMCP("test")
        mod = __import__(module_path, fromlist=["register_tools"])
        mod.register_tools(mcp)
        return mcp

    return _fix


mcp_system = _make_module_fixture("mcp_server.tools.system")
mcp_zones = _make_module_fixture("mcp_server.tools.zones")
mcp_aps = _make_module_fixture("mcp_server.tools.aps")
mcp_wlans = _make_module_fixture("mcp_server.tools.wlans")
mcp_clients = _make_module_fixture("mcp_server.tools.clients")
mcp_alarms = _make_module_fixture("mcp_server.tools.alarms")
mcp_domains = _make_module_fixture("mcp_server.tools.domains")
mcp_aaa = _make_module_fixture("mcp_server.tools.aaa")
mcp_dhcp = _make_module_fixture("mcp_server.tools.dhcp")
mcp_monitoring = _make_module_fixture("mcp_server.tools.monitoring")
mcp_block_clients = _make_module_fixture("mcp_server.tools.block_clients")
mcp_rogue = _make_module_fixture("mcp_server.tools.rogue")


# ===================================================================
# 1. REGISTRATION TESTS — every expected tool exists
# ===================================================================
EXPECTED_TOOLS = [
    # system
    "vsz_get_system_info",
    "vsz_get_system_summary",
    "vsz_get_system_inventory",
    "vsz_get_cluster_state",
    "vsz_get_controller_list",
    # zones
    "vsz_list_zones",
    "vsz_get_zone",
    "vsz_create_zone",
    "vsz_update_zone",
    "vsz_delete_zone",
    "vsz_list_zone_ap_groups",
    # aps
    "vsz_list_aps",
    "vsz_get_ap",
    "vsz_get_ap_operational",
    "vsz_update_ap",
    "vsz_delete_ap",
    "vsz_reboot_ap",
    "vsz_list_ap_lldp",
    "vsz_get_ap_radio",
    "vsz_query_aps",
    # wlans
    "vsz_list_wlans",
    "vsz_get_wlan",
    "vsz_create_wlan",
    "vsz_update_wlan",
    "vsz_delete_wlan",
    "vsz_enable_disable_wlan",
    # clients
    "vsz_list_clients",
    "vsz_get_client",
    "vsz_disconnect_client",
    "vsz_query_clients",
    # alarms
    "vsz_list_alarms",
    "vsz_get_alarm",
    "vsz_acknowledge_alarm",
    "vsz_clear_alarm",
    # domains
    "vsz_list_domains",
    "vsz_get_domain",
    "vsz_create_domain",
    # aaa
    "vsz_list_auth_servers",
    "vsz_get_auth_server",
    "vsz_test_aaa",
    # dhcp
    "vsz_list_dhcp_pools",
    "vsz_get_dhcp_pool",
    "vsz_list_vlan_pools",
    "vsz_get_vlan_pool",
    # monitoring
    "vsz_query",
    "vsz_get_ap_statistics",
    "vsz_get_wlan_statistics",
    # block_clients
    "vsz_list_blocked_clients",
    "vsz_block_client",
    "vsz_unblock_client",
    # rogue
    "vsz_list_rogue_aps",
    "vsz_mark_rogue",
]


async def test_all_tools_registered(mcp_all_tools):
    """Every tool from the canonical registry must be present."""
    tools = {t.name for t in await mcp_all_tools.list_tools()}
    for name in EXPECTED_TOOLS:
        assert name in tools, f"Tool '{name}' not registered"


async def test_total_tool_count(mcp_all_tools):
    """Exact total matches the canonical registry (no extras from prod modules)."""
    tools = await mcp_all_tools.list_tools()
    tool_names = {t.name for t in tools}
    for name in EXPECTED_TOOLS:
        assert name in tool_names


# Per-module registration spot-checks
async def test_system_tools_registered(mcp_system):
    names = {t.name for t in await mcp_system.list_tools()}
    assert names == {
        "vsz_get_system_info",
        "vsz_get_system_summary",
        "vsz_get_system_inventory",
        "vsz_get_cluster_state",
        "vsz_get_controller_list",
    }


async def test_zones_tools_registered(mcp_zones):
    names = {t.name for t in await mcp_zones.list_tools()}
    assert names == {
        "vsz_list_zones",
        "vsz_get_zone",
        "vsz_create_zone",
        "vsz_update_zone",
        "vsz_delete_zone",
        "vsz_list_zone_ap_groups",
    }


async def test_aps_tools_registered(mcp_aps):
    names = {t.name for t in await mcp_aps.list_tools()}
    assert names == {
        "vsz_list_aps",
        "vsz_get_ap",
        "vsz_get_ap_operational",
        "vsz_update_ap",
        "vsz_delete_ap",
        "vsz_reboot_ap",
        "vsz_list_ap_lldp",
        "vsz_get_ap_radio",
        "vsz_query_aps",
    }


async def test_wlans_tools_registered(mcp_wlans):
    names = {t.name for t in await mcp_wlans.list_tools()}
    assert names == {
        "vsz_list_wlans",
        "vsz_get_wlan",
        "vsz_create_wlan",
        "vsz_update_wlan",
        "vsz_delete_wlan",
        "vsz_enable_disable_wlan",
    }


async def test_clients_tools_registered(mcp_clients):
    names = {t.name for t in await mcp_clients.list_tools()}
    assert names == {
        "vsz_list_clients",
        "vsz_get_client",
        "vsz_disconnect_client",
        "vsz_query_clients",
    }


async def test_alarms_tools_registered(mcp_alarms):
    names = {t.name for t in await mcp_alarms.list_tools()}
    assert names == {
        "vsz_list_alarms",
        "vsz_get_alarm",
        "vsz_acknowledge_alarm",
        "vsz_clear_alarm",
    }


async def test_domains_tools_registered(mcp_domains):
    names = {t.name for t in await mcp_domains.list_tools()}
    assert names == {
        "vsz_list_domains",
        "vsz_get_domain",
        "vsz_create_domain",
    }


async def test_aaa_tools_registered(mcp_aaa):
    names = {t.name for t in await mcp_aaa.list_tools()}
    assert names == {
        "vsz_list_auth_servers",
        "vsz_get_auth_server",
        "vsz_test_aaa",
    }


async def test_dhcp_tools_registered(mcp_dhcp):
    names = {t.name for t in await mcp_dhcp.list_tools()}
    assert names == {
        "vsz_list_dhcp_pools",
        "vsz_get_dhcp_pool",
        "vsz_list_vlan_pools",
        "vsz_get_vlan_pool",
    }


async def test_monitoring_tools_registered(mcp_monitoring):
    names = {t.name for t in await mcp_monitoring.list_tools()}
    assert names == {
        "vsz_query",
        "vsz_get_ap_statistics",
        "vsz_get_wlan_statistics",
    }


async def test_block_clients_tools_registered(mcp_block_clients):
    names = {t.name for t in await mcp_block_clients.list_tools()}
    assert names == {
        "vsz_list_blocked_clients",
        "vsz_block_client",
        "vsz_unblock_client",
    }


async def test_rogue_tools_registered(mcp_rogue):
    names = {t.name for t in await mcp_rogue.list_tools()}
    assert names == {
        "vsz_list_rogue_aps",
        "vsz_mark_rogue",
    }


# ===================================================================
# 2. SYSTEM TOOLS — nominal + error
# ===================================================================
class TestSystemTools:
    async def test_get_system_info_success(self, mcp_system):
        mock_data = {"version": "6.1.1", "model": "vSZ-H", "uptime": 12345}
        with patch("mcp_server.tools.system.api_get", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_system.call_tool("vsz_get_system_info", {"host": HOST})
        parsed = json.loads(_text(result))
        assert parsed["version"] == "6.1.1"

    async def test_get_system_info_error(self, mcp_system):
        with patch("mcp_server.tools.system.api_get", new_callable=AsyncMock, return_value="ERROR: Auth failed"):
            result = await mcp_system.call_tool("vsz_get_system_info", {"host": HOST})
        assert "ERROR" in _text(result)

    async def test_get_system_summary_success(self, mcp_system):
        mock_data = {"totalAPs": 50, "totalClients": 200}
        with patch("mcp_server.tools.system.api_get", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_system.call_tool("vsz_get_system_summary", {"host": HOST})
        parsed = json.loads(_text(result))
        assert parsed["totalAPs"] == 50

    async def test_get_system_inventory_success(self, mcp_system):
        mock_data = {"list": [{"zoneName": "HQ", "apCount": 10}]}
        with patch("mcp_server.tools.system.api_get", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_system.call_tool("vsz_get_system_inventory", {"host": HOST})
        parsed = json.loads(_text(result))
        assert len(parsed["list"]) == 1

    async def test_get_cluster_state_success(self, mcp_system):
        mock_data = {"clusterState": "IN_SERVICE", "nodeCount": 2}
        with patch("mcp_server.tools.system.api_get", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_system.call_tool("vsz_get_cluster_state", {"host": HOST})
        parsed = json.loads(_text(result))
        assert parsed["clusterState"] == "IN_SERVICE"

    async def test_get_controller_list_success(self, mcp_system):
        mock_data = {"list": [{"id": "ctrl-1", "name": "Primary"}]}
        with patch("mcp_server.tools.system.api_get", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_system.call_tool("vsz_get_controller_list", {"host": HOST})
        parsed = json.loads(_text(result))
        assert parsed["list"][0]["name"] == "Primary"

    async def test_system_api_get_called_with_correct_endpoint(self, mcp_system):
        mock_get = AsyncMock(return_value={"ok": True})
        with patch("mcp_server.tools.system.api_get", mock_get):
            await mcp_system.call_tool("vsz_get_system_info", {"host": HOST})
        mock_get.assert_called_once_with(HOST, "/v11_1/controller")

    async def test_cluster_state_api_endpoint(self, mcp_system):
        mock_get = AsyncMock(return_value={"ok": True})
        with patch("mcp_server.tools.system.api_get", mock_get):
            await mcp_system.call_tool("vsz_get_cluster_state", {"host": HOST})
        mock_get.assert_called_once_with(HOST, "/v11_1/cluster/state")


# ===================================================================
# 3. ZONE TOOLS — CRUD + error
# ===================================================================
class TestZoneTools:
    async def test_list_zones_success(self, mcp_zones):
        mock_data = {"list": [{"id": ZONE_ID, "name": "HQ"}]}
        with patch("mcp_server.tools.zones.api_get", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_zones.call_tool("vsz_list_zones", {"host": HOST})
        parsed = json.loads(_text(result))
        assert parsed["list"][0]["name"] == "HQ"

    async def test_get_zone_success(self, mcp_zones):
        mock_data = {"id": ZONE_ID, "name": "Branch"}
        with patch("mcp_server.tools.zones.api_get", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_zones.call_tool("vsz_get_zone", {"host": HOST, "zone_id": ZONE_ID})
        parsed = json.loads(_text(result))
        assert parsed["id"] == ZONE_ID

    async def test_get_zone_error(self, mcp_zones):
        with patch("mcp_server.tools.zones.api_get", new_callable=AsyncMock, return_value="ERROR: Not found"):
            result = await mcp_zones.call_tool("vsz_get_zone", {"host": HOST, "zone_id": "bad"})
        assert "ERROR" in _text(result)

    async def test_create_zone_minimal(self, mcp_zones):
        mock_data = {"id": "new-zone-id"}
        mock_post = AsyncMock(return_value=mock_data)
        with patch("mcp_server.tools.zones.api_post", mock_post):
            result = await mcp_zones.call_tool("vsz_create_zone", {"host": HOST, "name": "NewZone"})
        parsed = json.loads(_text(result))
        assert parsed["id"] == "new-zone-id"
        call_args = mock_post.call_args
        assert call_args[1]["data"]["name"] == "NewZone"

    async def test_create_zone_full_params(self, mcp_zones):
        mock_post = AsyncMock(return_value={"id": "z1"})
        with patch("mcp_server.tools.zones.api_post", mock_post):
            await mcp_zones.call_tool("vsz_create_zone", {
                "host": HOST, "name": "Z1", "description": "Test",
                "domain_id": "d1", "country_code": "FR",
            })
        body = mock_post.call_args[1]["data"]
        assert body["name"] == "Z1"
        assert body["description"] == "Test"
        assert body["domainId"] == "d1"
        assert body["countryCode"] == "FR"

    async def test_update_zone_success(self, mcp_zones):
        mock_patch = AsyncMock(return_value={"success": True})
        with patch("mcp_server.tools.zones.api_patch", mock_patch):
            result = await mcp_zones.call_tool("vsz_update_zone", {
                "host": HOST, "zone_id": ZONE_ID, "name": "Renamed",
            })
        parsed = json.loads(_text(result))
        assert parsed["success"] is True

    async def test_update_zone_no_fields_returns_error(self, mcp_zones):
        result = await mcp_zones.call_tool("vsz_update_zone", {
            "host": HOST, "zone_id": ZONE_ID,
        })
        assert "ERROR" in _text(result)

    async def test_delete_zone_success(self, mcp_zones):
        mock_del = AsyncMock(return_value={"success": True, "status_code": 204})
        with patch("mcp_server.tools.zones.api_delete", mock_del):
            result = await mcp_zones.call_tool("vsz_delete_zone", {"host": HOST, "zone_id": ZONE_ID})
        mock_del.assert_called_once_with(HOST, f"/v11_1/rkszones/{ZONE_ID}")

    async def test_list_zone_ap_groups(self, mcp_zones):
        mock_data = {"list": [{"id": "grp1", "name": "Default"}]}
        with patch("mcp_server.tools.zones.api_get", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_zones.call_tool("vsz_list_zone_ap_groups", {
                "host": HOST, "zone_id": ZONE_ID,
            })
        parsed = json.loads(_text(result))
        assert parsed["list"][0]["name"] == "Default"


# ===================================================================
# 4. AP TOOLS
# ===================================================================
class TestAPTools:
    async def test_list_aps_success(self, mcp_aps):
        mock_data = {"list": [{"mac": AP_MAC, "name": "AP-Lobby"}]}
        with patch("mcp_server.tools.aps.api_get", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_aps.call_tool("vsz_list_aps", {"host": HOST})
        parsed = json.loads(_text(result))
        assert parsed["list"][0]["mac"] == AP_MAC

    async def test_get_ap_success(self, mcp_aps):
        mock_data = {"mac": AP_MAC, "zoneId": ZONE_ID}
        with patch("mcp_server.tools.aps.api_get", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_aps.call_tool("vsz_get_ap", {"host": HOST, "ap_mac": AP_MAC})
        parsed = json.loads(_text(result))
        assert parsed["mac"] == AP_MAC

    async def test_get_ap_error(self, mcp_aps):
        with patch("mcp_server.tools.aps.api_get", new_callable=AsyncMock, return_value="ERROR: 404"):
            result = await mcp_aps.call_tool("vsz_get_ap", {"host": HOST, "ap_mac": "bad"})
        assert "ERROR" in _text(result)

    async def test_get_ap_operational(self, mcp_aps):
        mock_data = {"uptime": 86400, "clients": 5, "status": "Online"}
        with patch("mcp_server.tools.aps.api_get", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_aps.call_tool("vsz_get_ap_operational", {"host": HOST, "ap_mac": AP_MAC})
        parsed = json.loads(_text(result))
        assert parsed["status"] == "Online"

    async def test_update_ap_with_name(self, mcp_aps):
        mock_patch = AsyncMock(return_value={"success": True})
        with patch("mcp_server.tools.aps.api_patch", mock_patch):
            result = await mcp_aps.call_tool("vsz_update_ap", {
                "host": HOST, "ap_mac": AP_MAC, "name": "AP-Floor2",
            })
        body = mock_patch.call_args[1]["data"]
        assert body["name"] == "AP-Floor2"

    async def test_update_ap_with_gps(self, mcp_aps):
        mock_patch = AsyncMock(return_value={"success": True})
        with patch("mcp_server.tools.aps.api_patch", mock_patch):
            await mcp_aps.call_tool("vsz_update_ap", {
                "host": HOST, "ap_mac": AP_MAC,
                "gps_latitude": 48.8566, "gps_longitude": 2.3522,
            })
        body = mock_patch.call_args[1]["data"]
        assert body["gps"]["latitude"] == 48.8566
        assert body["gps"]["longitude"] == 2.3522

    async def test_update_ap_no_fields_returns_error(self, mcp_aps):
        result = await mcp_aps.call_tool("vsz_update_ap", {"host": HOST, "ap_mac": AP_MAC})
        assert "ERROR" in _text(result)

    async def test_delete_ap(self, mcp_aps):
        mock_del = AsyncMock(return_value={"success": True, "status_code": 204})
        with patch("mcp_server.tools.aps.api_delete", mock_del):
            await mcp_aps.call_tool("vsz_delete_ap", {"host": HOST, "ap_mac": AP_MAC})
        mock_del.assert_called_once_with(HOST, f"/v11_1/aps/{AP_MAC}")

    async def test_reboot_ap(self, mcp_aps):
        mock_put = AsyncMock(return_value={"success": True, "status_code": 204})
        with patch("mcp_server.tools.aps.api_put", mock_put):
            await mcp_aps.call_tool("vsz_reboot_ap", {"host": HOST, "ap_mac": AP_MAC})
        mock_put.assert_called_once_with(HOST, f"/v11_1/aps/{AP_MAC}/reboot")

    async def test_list_ap_lldp(self, mcp_aps):
        mock_data = {"list": [{"chassisId": "switch-01"}]}
        with patch("mcp_server.tools.aps.api_get", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_aps.call_tool("vsz_list_ap_lldp", {"host": HOST, "ap_mac": AP_MAC})
        parsed = json.loads(_text(result))
        assert parsed["list"][0]["chassisId"] == "switch-01"

    async def test_get_ap_radio(self, mcp_aps):
        mock_data = {"radioConfig": {"radio24g": {"channel": 6}, "radio5g": {"channel": 36}}}
        with patch("mcp_server.tools.aps.api_get", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_aps.call_tool("vsz_get_ap_radio", {"host": HOST, "ap_mac": AP_MAC})
        parsed = json.loads(_text(result))
        assert parsed["radioConfig"]["radio24g"]["channel"] == 6

    async def test_get_ap_radio_uses_ap_endpoint(self, mcp_aps):
        """Verify uses GET /aps/{mac} (not a separate radio endpoint)."""
        mock_get = AsyncMock(return_value={"radioConfig": {}})
        with patch("mcp_server.tools.aps.api_get", mock_get):
            await mcp_aps.call_tool("vsz_get_ap_radio", {"host": HOST, "ap_mac": AP_MAC})
        mock_get.assert_called_once_with(HOST, f"/v11_1/aps/{AP_MAC}")

    async def test_get_ap_radio_no_radio_config(self, mcp_aps):
        """AP without radioConfig key falls back to full response."""
        mock_data = {"mac": AP_MAC, "name": "AP-NoRadio"}
        with patch("mcp_server.tools.aps.api_get", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_aps.call_tool("vsz_get_ap_radio", {"host": HOST, "ap_mac": AP_MAC})
        parsed = json.loads(_text(result))
        assert parsed["mac"] == AP_MAC

    async def test_query_aps_with_text_search(self, mcp_aps):
        mock_data = {"list": [{"mac": AP_MAC}], "totalCount": 1}
        mock_post = AsyncMock(return_value=mock_data)
        with patch("mcp_server.tools.aps.api_post", mock_post):
            result = await mcp_aps.call_tool("vsz_query_aps", {
                "host": HOST, "full_text_search": "lobby",
            })
        body = mock_post.call_args[1]["data"]
        assert body["fullTextSearch"]["value"] == "lobby"

    async def test_query_aps_with_valid_filters(self, mcp_aps):
        mock_post = AsyncMock(return_value={"list": [], "totalCount": 0})
        filters_json = json.dumps([{"type": "DOMAIN", "value": "d1"}])
        # Call the tool function directly to bypass SDK pre_parse_json
        # which converts JSON array strings to lists for Optional[str] params
        tool_fn = mcp_aps._tool_manager._tools["vsz_query_aps"].fn
        with patch("mcp_server.tools.aps.api_post", mock_post):
            await tool_fn(host=HOST, filters=filters_json)
        body = mock_post.call_args[1]["data"]
        assert body["filters"][0]["type"] == "DOMAIN"

    async def test_query_aps_invalid_filters_json(self, mcp_aps):
        result = await mcp_aps.call_tool("vsz_query_aps", {
            "host": HOST, "filters": "not-valid-json{",
        })
        assert "ERROR" in _text(result)


# ===================================================================
# 5. WLAN TOOLS
# ===================================================================
class TestWLANTools:
    async def test_list_wlans(self, mcp_wlans):
        mock_data = {"list": [{"id": WLAN_ID, "name": "Corp-WiFi"}]}
        with patch("mcp_server.tools.wlans.api_get", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_wlans.call_tool("vsz_list_wlans", {
                "host": HOST, "zone_id": ZONE_ID,
            })
        parsed = json.loads(_text(result))
        assert parsed["list"][0]["name"] == "Corp-WiFi"

    async def test_get_wlan(self, mcp_wlans):
        mock_data = {"id": WLAN_ID, "ssid": "Guest"}
        with patch("mcp_server.tools.wlans.api_get", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_wlans.call_tool("vsz_get_wlan", {
                "host": HOST, "zone_id": ZONE_ID, "wlan_id": WLAN_ID,
            })
        parsed = json.loads(_text(result))
        assert parsed["ssid"] == "Guest"

    async def test_create_wlan_open(self, mcp_wlans):
        mock_post = AsyncMock(return_value={"id": "new-wlan"})
        with patch("mcp_server.tools.wlans.api_post", mock_post):
            result = await mcp_wlans.call_tool("vsz_create_wlan", {
                "host": HOST, "zone_id": ZONE_ID,
                "name": "Guest", "ssid": "Guest-WiFi",
            })
        body = mock_post.call_args[1]["data"]
        assert body["name"] == "Guest"
        assert body["ssid"] == "Guest-WiFi"
        assert "encryption" in body

    async def test_create_wlan_wpa2(self, mcp_wlans):
        mock_post = AsyncMock(return_value={"id": "new-wlan"})
        with patch("mcp_server.tools.wlans.api_post", mock_post):
            await mcp_wlans.call_tool("vsz_create_wlan", {
                "host": HOST, "zone_id": ZONE_ID,
                "name": "Secure", "ssid": "Secure-WiFi",
                "security_type": "WPA2",
                "passphrase": "s3cret!!",
            })
        body = mock_post.call_args[1]["data"]
        assert body["encryption"]["passphrase"] == "s3cret!!"

    async def test_create_wlan_with_vlan(self, mcp_wlans):
        mock_post = AsyncMock(return_value={"id": "new-wlan"})
        with patch("mcp_server.tools.wlans.api_post", mock_post):
            await mcp_wlans.call_tool("vsz_create_wlan", {
                "host": HOST, "zone_id": ZONE_ID,
                "name": "IOT", "ssid": "IOT-Net",
                "vlan_id": 100,
            })
        body = mock_post.call_args[1]["data"]
        assert body["vlan"]["accessVlan"] == 100

    async def test_update_wlan_success(self, mcp_wlans):
        mock_patch = AsyncMock(return_value={"success": True})
        with patch("mcp_server.tools.wlans.api_patch", mock_patch):
            result = await mcp_wlans.call_tool("vsz_update_wlan", {
                "host": HOST, "zone_id": ZONE_ID,
                "wlan_id": WLAN_ID, "name": "Renamed",
            })
        parsed = json.loads(_text(result))
        assert parsed["success"] is True

    async def test_update_wlan_no_fields_returns_error(self, mcp_wlans):
        result = await mcp_wlans.call_tool("vsz_update_wlan", {
            "host": HOST, "zone_id": ZONE_ID, "wlan_id": WLAN_ID,
        })
        assert "ERROR" in _text(result)

    async def test_delete_wlan(self, mcp_wlans):
        mock_del = AsyncMock(return_value={"success": True, "status_code": 204})
        with patch("mcp_server.tools.wlans.api_delete", mock_del):
            await mcp_wlans.call_tool("vsz_delete_wlan", {
                "host": HOST, "zone_id": ZONE_ID, "wlan_id": WLAN_ID,
            })
        mock_del.assert_called_once_with(HOST, f"/v11_1/rkszones/{ZONE_ID}/wlans/{WLAN_ID}")

    async def test_enable_disable_wlan(self, mcp_wlans):
        mock_patch = AsyncMock(return_value={"success": True})
        with patch("mcp_server.tools.wlans.api_patch", mock_patch):
            await mcp_wlans.call_tool("vsz_enable_disable_wlan", {
                "host": HOST, "zone_id": ZONE_ID,
                "wlan_id": WLAN_ID, "enabled": False,
            })
        body = mock_patch.call_args[1]["data"]
        assert body["enabled"] is False


# ===================================================================
# 6. CLIENT TOOLS
# ===================================================================
class TestClientTools:
    async def test_list_clients(self, mcp_clients):
        mock_data = {"list": [{"mac": CLIENT_MAC, "ssid": "Corp"}], "totalCount": 1}
        with patch("mcp_server.tools.clients.api_post", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_clients.call_tool("vsz_list_clients", {"host": HOST})
        parsed = json.loads(_text(result))
        assert parsed["totalCount"] == 1

    async def test_get_client(self, mcp_clients):
        mock_data = {"list": [{"mac": CLIENT_MAC}], "totalCount": 1}
        mock_post = AsyncMock(return_value=mock_data)
        with patch("mcp_server.tools.clients.api_post", mock_post):
            result = await mcp_clients.call_tool("vsz_get_client", {
                "host": HOST, "client_mac": CLIENT_MAC,
            })
        body = mock_post.call_args[1]["data"]
        assert body["fullTextSearch"]["value"] == CLIENT_MAC

    async def test_disconnect_client(self, mcp_clients):
        mock_post = AsyncMock(return_value={"success": True, "status_code": 204})
        with patch("mcp_server.tools.clients.api_post", mock_post):
            await mcp_clients.call_tool("vsz_disconnect_client", {
                "host": HOST, "client_mac": CLIENT_MAC,
                "ap_mac": AP_MAC,
            })
        body = mock_post.call_args[1]["data"]
        assert body["mac"] == CLIENT_MAC
        assert body["apMac"] == AP_MAC

    async def test_query_clients_with_text_search(self, mcp_clients):
        mock_post = AsyncMock(return_value={"list": [], "totalCount": 0})
        with patch("mcp_server.tools.clients.api_post", mock_post):
            await mcp_clients.call_tool("vsz_query_clients", {
                "host": HOST, "full_text_search": "laptop",
            })
        body = mock_post.call_args[1]["data"]
        assert body["fullTextSearch"]["value"] == "laptop"

    async def test_query_clients_invalid_filters(self, mcp_clients):
        result = await mcp_clients.call_tool("vsz_query_clients", {
            "host": HOST, "filters": "{{invalid",
        })
        assert "ERROR" in _text(result)

    async def test_query_clients_valid_filters(self, mcp_clients):
        mock_post = AsyncMock(return_value={"list": [], "totalCount": 0})
        filters_json = json.dumps([{"type": "ZONE", "value": ZONE_ID}])
        # Call the tool function directly to bypass SDK pre_parse_json
        tool_fn = mcp_clients._tool_manager._tools["vsz_query_clients"].fn
        with patch("mcp_server.tools.clients.api_post", mock_post):
            await tool_fn(host=HOST, filters=filters_json)
        body = mock_post.call_args[1]["data"]
        assert body["filters"][0]["type"] == "ZONE"

    async def test_list_clients_error(self, mcp_clients):
        with patch("mcp_server.tools.clients.api_post", new_callable=AsyncMock, return_value="ERROR: timeout"):
            result = await mcp_clients.call_tool("vsz_list_clients", {"host": HOST})
        assert "ERROR" in _text(result)

    async def test_disconnect_client_endpoint_and_method(self, mcp_clients):
        """Verify disconnect uses POST /clients/disconnect with mac + apMac body."""
        mock_post = AsyncMock(return_value={"success": True})
        with patch("mcp_server.tools.clients.api_post", mock_post):
            await mcp_clients.call_tool("vsz_disconnect_client", {
                "host": HOST, "client_mac": CLIENT_MAC, "ap_mac": AP_MAC,
            })
        mock_post.assert_called_once_with(
            HOST, "/v11_1/clients/disconnect", data={"mac": CLIENT_MAC, "apMac": AP_MAC}
        )

    async def test_disconnect_client_error(self, mcp_clients):
        with patch("mcp_server.tools.clients.api_post", new_callable=AsyncMock, return_value="ERROR: AP not found"):
            result = await mcp_clients.call_tool("vsz_disconnect_client", {
                "host": HOST, "client_mac": CLIENT_MAC, "ap_mac": AP_MAC,
            })
        assert "ERROR" in _text(result)


# ===================================================================
# 7. ALARM TOOLS
# ===================================================================
class TestAlarmTools:
    async def test_list_alarms(self, mcp_alarms):
        mock_data = {"list": [{"id": ALARM_ID, "severity": "Critical"}]}
        with patch("mcp_server.tools.alarms.api_post", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_alarms.call_tool("vsz_list_alarms", {"host": HOST})
        parsed = json.loads(_text(result))
        assert parsed["list"][0]["severity"] == "Critical"

    async def test_get_alarm(self, mcp_alarms):
        mock_data = {"list": [{"id": ALARM_ID, "category": "AP", "severity": "Major"}]}
        with patch("mcp_server.tools.alarms.api_post", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_alarms.call_tool("vsz_get_alarm", {
                "host": HOST, "alarm_id": ALARM_ID,
            })
        parsed = json.loads(_text(result))
        assert parsed["severity"] == "Major"

    async def test_acknowledge_alarm(self, mcp_alarms):
        mock_put = AsyncMock(return_value={"success": True, "status_code": 204})
        with patch("mcp_server.tools.alarms.api_put", mock_put):
            await mcp_alarms.call_tool("vsz_acknowledge_alarm", {
                "host": HOST, "alarm_id": ALARM_ID,
            })
        mock_put.assert_called_once_with(HOST, f"/v11_1/alert/alarm/{ALARM_ID}/ack")

    async def test_clear_alarm(self, mcp_alarms):
        mock_put = AsyncMock(return_value={"success": True, "status_code": 204})
        with patch("mcp_server.tools.alarms.api_put", mock_put):
            await mcp_alarms.call_tool("vsz_clear_alarm", {
                "host": HOST, "alarm_id": ALARM_ID,
            })
        mock_put.assert_called_once_with(HOST, f"/v11_1/alert/alarm/{ALARM_ID}/clear")

    async def test_list_alarms_error(self, mcp_alarms):
        with patch("mcp_server.tools.alarms.api_post", new_callable=AsyncMock, return_value="ERROR: 500"):
            result = await mcp_alarms.call_tool("vsz_list_alarms", {"host": HOST})
        assert "ERROR" in _text(result)

    async def test_get_alarm_not_found(self, mcp_alarms):
        """Alarm ID not present in the returned list."""
        mock_data = {"list": [{"id": "other-alarm", "severity": "Minor"}]}
        with patch("mcp_server.tools.alarms.api_post", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_alarms.call_tool("vsz_get_alarm", {
                "host": HOST, "alarm_id": "nonexistent-id",
            })
        assert "not found" in _text(result)

    async def test_get_alarm_matches_by_alarmUUID(self, mcp_alarms):
        """Alarm can be found by alarmUUID field as well as id."""
        mock_data = {"list": [{"id": "other", "alarmUUID": ALARM_ID, "severity": "Critical"}]}
        with patch("mcp_server.tools.alarms.api_post", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_alarms.call_tool("vsz_get_alarm", {
                "host": HOST, "alarm_id": ALARM_ID,
            })
        parsed = json.loads(_text(result))
        assert parsed["severity"] == "Critical"

    async def test_get_alarm_error_propagation(self, mcp_alarms):
        with patch("mcp_server.tools.alarms.api_post", new_callable=AsyncMock, return_value="ERROR: Auth failed"):
            result = await mcp_alarms.call_tool("vsz_get_alarm", {
                "host": HOST, "alarm_id": ALARM_ID,
            })
        assert "ERROR" in _text(result)

    async def test_acknowledge_alarm_endpoint(self, mcp_alarms):
        """Verify acknowledge uses PUT /alert/alarm/{id}/ack (not /acknowledge)."""
        mock_put = AsyncMock(return_value={"success": True})
        with patch("mcp_server.tools.alarms.api_put", mock_put):
            await mcp_alarms.call_tool("vsz_acknowledge_alarm", {
                "host": HOST, "alarm_id": ALARM_ID,
            })
        endpoint = mock_put.call_args[0][1]
        assert endpoint.endswith("/ack")
        assert "/acknowledge" not in endpoint

    async def test_clear_alarm_uses_put_not_delete(self, mcp_alarms):
        """Verify clear uses PUT /alert/alarm/{id}/clear (not DELETE)."""
        mock_put = AsyncMock(return_value={"success": True})
        with patch("mcp_server.tools.alarms.api_put", mock_put):
            await mcp_alarms.call_tool("vsz_clear_alarm", {
                "host": HOST, "alarm_id": ALARM_ID,
            })
        mock_put.assert_called_once()


# ===================================================================
# 8. DOMAIN TOOLS
# ===================================================================
class TestDomainTools:
    async def test_list_domains(self, mcp_domains):
        mock_data = {"list": [{"id": DOMAIN_ID, "name": "Admin"}]}
        with patch("mcp_server.tools.domains.api_get", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_domains.call_tool("vsz_list_domains", {"host": HOST})
        parsed = json.loads(_text(result))
        assert parsed["list"][0]["name"] == "Admin"

    async def test_get_domain(self, mcp_domains):
        mock_data = {"id": DOMAIN_ID, "name": "Admin"}
        with patch("mcp_server.tools.domains.api_get", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_domains.call_tool("vsz_get_domain", {
                "host": HOST, "domain_id": DOMAIN_ID,
            })
        parsed = json.loads(_text(result))
        assert parsed["id"] == DOMAIN_ID

    async def test_create_domain_minimal(self, mcp_domains):
        mock_post = AsyncMock(return_value={"id": "new-dom"})
        with patch("mcp_server.tools.domains.api_post", mock_post):
            result = await mcp_domains.call_tool("vsz_create_domain", {
                "host": HOST, "name": "SubDomain",
            })
        body = mock_post.call_args[1]["data"]
        assert body["name"] == "SubDomain"
        assert "parentDomainId" not in body

    async def test_create_domain_full(self, mcp_domains):
        mock_post = AsyncMock(return_value={"id": "new-dom"})
        with patch("mcp_server.tools.domains.api_post", mock_post):
            await mcp_domains.call_tool("vsz_create_domain", {
                "host": HOST, "name": "Child",
                "description": "Child domain",
                "parent_domain_id": DOMAIN_ID,
            })
        body = mock_post.call_args[1]["data"]
        assert body["parentDomainId"] == DOMAIN_ID
        assert body["description"] == "Child domain"

    async def test_list_domains_error(self, mcp_domains):
        with patch("mcp_server.tools.domains.api_get", new_callable=AsyncMock, return_value="ERROR: Auth failed"):
            result = await mcp_domains.call_tool("vsz_list_domains", {"host": HOST})
        assert "ERROR" in _text(result)


# ===================================================================
# 9. AAA TOOLS
# ===================================================================
class TestAAATools:
    async def test_list_auth_servers(self, mcp_aaa):
        mock_data = {"list": [{"id": SERVER_ID, "name": "RADIUS-1"}]}
        with patch("mcp_server.tools.aaa.api_get", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_aaa.call_tool("vsz_list_auth_servers", {"host": HOST})
        parsed = json.loads(_text(result))
        assert parsed["list"][0]["name"] == "RADIUS-1"

    async def test_get_auth_server(self, mcp_aaa):
        mock_data = {"id": SERVER_ID, "ip": "10.0.1.10", "port": 1812}
        with patch("mcp_server.tools.aaa.api_get", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_aaa.call_tool("vsz_get_auth_server", {
                "host": HOST, "server_id": SERVER_ID,
            })
        parsed = json.loads(_text(result))
        assert parsed["port"] == 1812

    async def test_test_aaa_minimal(self, mcp_aaa):
        mock_post = AsyncMock(return_value={"result": "SUCCESS"})
        with patch("mcp_server.tools.aaa.api_post", mock_post):
            result = await mcp_aaa.call_tool("vsz_test_aaa", {
                "host": HOST,
                "server_type": "RADIUS",
                "server_ip": "10.0.1.10",
                "server_port": 1812,
                "shared_secret": "secret123",
            })
        body = mock_post.call_args[1]["data"]
        assert body["type"] == "RADIUS"
        assert body["port"] == 1812
        assert body["sharedSecret"] == "secret123"
        assert body["authProtocol"] == "PAP"

    async def test_test_aaa_with_credentials(self, mcp_aaa):
        mock_post = AsyncMock(return_value={"result": "SUCCESS"})
        with patch("mcp_server.tools.aaa.api_post", mock_post):
            await mcp_aaa.call_tool("vsz_test_aaa", {
                "host": HOST,
                "server_type": "RADIUS",
                "server_ip": "10.0.1.10",
                "server_port": 1812,
                "shared_secret": "secret",
                "test_username": "testuser",
                "test_password": "testpass",
            })
        body = mock_post.call_args[1]["data"]
        assert body["userName"] == "testuser"
        assert body["password"] == "testpass"

    async def test_test_aaa_error(self, mcp_aaa):
        with patch("mcp_server.tools.aaa.api_post", new_callable=AsyncMock, return_value="ERROR: Connection refused"):
            result = await mcp_aaa.call_tool("vsz_test_aaa", {
                "host": HOST,
                "server_type": "RADIUS",
                "server_ip": "10.0.1.10",
                "server_port": 1812,
                "shared_secret": "s",
            })
        assert "ERROR" in _text(result)


# ===================================================================
# 10. DHCP / VLAN TOOLS
# ===================================================================
class TestDHCPTools:
    async def test_list_dhcp_pools(self, mcp_dhcp):
        mock_data = {"list": [{"id": POOL_ID, "name": "DHCP-1"}]}
        with patch("mcp_server.tools.dhcp.api_get", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_dhcp.call_tool("vsz_list_dhcp_pools", {
                "host": HOST, "zone_id": ZONE_ID,
            })
        parsed = json.loads(_text(result))
        assert parsed["list"][0]["name"] == "DHCP-1"

    async def test_get_dhcp_pool(self, mcp_dhcp):
        mock_data = {"id": POOL_ID, "subnetAddress": "192.168.1.0"}
        mock_get = AsyncMock(return_value=mock_data)
        with patch("mcp_server.tools.dhcp.api_get", mock_get):
            result = await mcp_dhcp.call_tool("vsz_get_dhcp_pool", {
                "host": HOST, "zone_id": ZONE_ID, "pool_id": POOL_ID,
            })
        mock_get.assert_called_once_with(
            HOST, f"/v11_1/rkszones/{ZONE_ID}/dhcpSite/dhcpProfile/{POOL_ID}"
        )
        parsed = json.loads(_text(result))
        assert parsed["subnetAddress"] == "192.168.1.0"

    async def test_list_vlan_pools(self, mcp_dhcp):
        mock_data = {"list": [{"id": POOL_ID, "name": "VLAN-Pool-1"}]}
        with patch("mcp_server.tools.dhcp.api_post", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_dhcp.call_tool("vsz_list_vlan_pools", {
                "host": HOST,
            })
        parsed = json.loads(_text(result))
        assert parsed["list"][0]["name"] == "VLAN-Pool-1"

    async def test_get_vlan_pool(self, mcp_dhcp):
        mock_data = {"id": POOL_ID, "vlanMembers": [10, 20, 30]}
        mock_get = AsyncMock(return_value=mock_data)
        with patch("mcp_server.tools.dhcp.api_get", mock_get):
            result = await mcp_dhcp.call_tool("vsz_get_vlan_pool", {
                "host": HOST, "pool_id": POOL_ID,
            })
        mock_get.assert_called_once_with(
            HOST, f"/v11_1/vlanpoolings/{POOL_ID}"
        )

    async def test_dhcp_error_propagation(self, mcp_dhcp):
        with patch("mcp_server.tools.dhcp.api_get", new_callable=AsyncMock, return_value="ERROR: timeout"):
            result = await mcp_dhcp.call_tool("vsz_list_dhcp_pools", {
                "host": HOST, "zone_id": ZONE_ID,
            })
        assert "ERROR" in _text(result)

    async def test_list_vlan_pools_uses_post_query(self, mcp_dhcp):
        """Verify list_vlan_pools uses POST /vlanpoolings/query (no zone_id)."""
        mock_post = AsyncMock(return_value={"list": []})
        with patch("mcp_server.tools.dhcp.api_post", mock_post):
            await mcp_dhcp.call_tool("vsz_list_vlan_pools", {"host": HOST})
        mock_post.assert_called_once_with(HOST, "/v11_1/vlanpoolings/query", data={})

    async def test_list_vlan_pools_error(self, mcp_dhcp):
        with patch("mcp_server.tools.dhcp.api_post", new_callable=AsyncMock, return_value="ERROR: 500"):
            result = await mcp_dhcp.call_tool("vsz_list_vlan_pools", {"host": HOST})
        assert "ERROR" in _text(result)

    async def test_get_vlan_pool_no_zone_id(self, mcp_dhcp):
        """Verify get_vlan_pool uses GET /vlanpoolings/{pool_id} without zone_id."""
        mock_get = AsyncMock(return_value={"id": POOL_ID})
        with patch("mcp_server.tools.dhcp.api_get", mock_get):
            await mcp_dhcp.call_tool("vsz_get_vlan_pool", {
                "host": HOST, "pool_id": POOL_ID,
            })
        mock_get.assert_called_once_with(HOST, f"/v11_1/vlanpoolings/{POOL_ID}")


# ===================================================================
# 11. MONITORING / QUERY TOOLS
# ===================================================================
class TestMonitoringTools:
    async def test_query_generic(self, mcp_monitoring):
        mock_data = {"list": [{"id": "1"}], "totalCount": 1}
        mock_post = AsyncMock(return_value=mock_data)
        with patch("mcp_server.tools.monitoring.api_post", mock_post):
            result = await mcp_monitoring.call_tool("vsz_query", {
                "host": HOST, "query_type": "ap",
            })
        mock_post.assert_called_once()
        body = mock_post.call_args[1]["data"]
        assert body["page"] == 1
        assert body["limit"] == 100

    async def test_query_with_pagination(self, mcp_monitoring):
        mock_post = AsyncMock(return_value={"list": [], "totalCount": 0})
        with patch("mcp_server.tools.monitoring.api_post", mock_post):
            await mcp_monitoring.call_tool("vsz_query", {
                "host": HOST, "query_type": "client",
                "page": 3, "limit": 50,
            })
        body = mock_post.call_args[1]["data"]
        assert body["page"] == 3
        assert body["limit"] == 50

    async def test_query_with_text_search(self, mcp_monitoring):
        mock_post = AsyncMock(return_value={"list": [], "totalCount": 0})
        with patch("mcp_server.tools.monitoring.api_post", mock_post):
            await mcp_monitoring.call_tool("vsz_query", {
                "host": HOST, "query_type": "ap",
                "full_text_search": "lobby",
            })
        body = mock_post.call_args[1]["data"]
        assert body["fullTextSearch"]["value"] == "lobby"

    async def test_query_invalid_filters(self, mcp_monitoring):
        result = await mcp_monitoring.call_tool("vsz_query", {
            "host": HOST, "query_type": "ap", "filters": "bad{json",
        })
        assert "ERROR" in _text(result)

    async def test_get_ap_statistics(self, mcp_monitoring):
        mock_data = {"txBytes": 1000000, "rxBytes": 500000}
        mock_get = AsyncMock(return_value=mock_data)
        with patch("mcp_server.tools.monitoring.api_get", mock_get):
            result = await mcp_monitoring.call_tool("vsz_get_ap_statistics", {
                "host": HOST, "ap_mac": AP_MAC,
            })
        mock_get.assert_called_once_with(HOST, f"/v11_1/aps/{AP_MAC}/operational/summary")
        parsed = json.loads(_text(result))
        assert parsed["txBytes"] == 1000000

    async def test_get_wlan_statistics(self, mcp_monitoring):
        mock_data = {"list": [{"name": "TestSSID", "clientCount": 15}], "totalCount": 1}
        mock_post = AsyncMock(return_value=mock_data)
        with patch("mcp_server.tools.monitoring.api_post", mock_post):
            result = await mcp_monitoring.call_tool("vsz_get_wlan_statistics", {
                "host": HOST,
            })
        mock_post.assert_called_once()

    async def test_get_wlan_statistics_with_name_filter(self, mcp_monitoring):
        """Verify wlan_name is passed as fullTextSearch."""
        mock_post = AsyncMock(return_value={"list": [], "totalCount": 0})
        with patch("mcp_server.tools.monitoring.api_post", mock_post):
            await mcp_monitoring.call_tool("vsz_get_wlan_statistics", {
                "host": HOST, "wlan_name": "Corp-WiFi",
            })
        body = mock_post.call_args[1]["data"]
        assert body["fullTextSearch"]["value"] == "Corp-WiFi"

    async def test_get_wlan_statistics_uses_post_query_wlan(self, mcp_monitoring):
        """Verify endpoint is POST /query/wlan (not zone-based)."""
        mock_post = AsyncMock(return_value={"list": []})
        with patch("mcp_server.tools.monitoring.api_post", mock_post):
            await mcp_monitoring.call_tool("vsz_get_wlan_statistics", {"host": HOST})
        mock_post.assert_called_once_with(HOST, "/v11_1/query/wlan", data={})

    async def test_query_error_propagation(self, mcp_monitoring):
        with patch("mcp_server.tools.monitoring.api_post", new_callable=AsyncMock, return_value="ERROR: Auth failed"):
            result = await mcp_monitoring.call_tool("vsz_query", {
                "host": HOST, "query_type": "ap",
            })
        assert "ERROR" in _text(result)


# ===================================================================
# 12. BLOCK CLIENT TOOLS
# ===================================================================
class TestBlockClientTools:
    async def test_list_blocked_clients(self, mcp_block_clients):
        mock_data = {"list": [{"id": CLIENT_ID, "mac": CLIENT_MAC}]}
        with patch("mcp_server.tools.block_clients.api_post", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_block_clients.call_tool("vsz_list_blocked_clients", {"host": HOST})
        parsed = json.loads(_text(result))
        assert parsed["list"][0]["mac"] == CLIENT_MAC

    async def test_list_blocked_clients_uses_post_query(self, mcp_block_clients):
        """Verify uses POST /blockClient/query (not GET)."""
        mock_post = AsyncMock(return_value={"list": []})
        with patch("mcp_server.tools.block_clients.api_post", mock_post):
            await mcp_block_clients.call_tool("vsz_list_blocked_clients", {"host": HOST})
        mock_post.assert_called_once_with(HOST, "/v11_1/blockClient/query", data={})

    async def test_list_blocked_clients_error(self, mcp_block_clients):
        with patch("mcp_server.tools.block_clients.api_post", new_callable=AsyncMock, return_value="ERROR: 500"):
            result = await mcp_block_clients.call_tool("vsz_list_blocked_clients", {"host": HOST})
        assert "ERROR" in _text(result)

    async def test_block_client_minimal(self, mcp_block_clients):
        mock_post = AsyncMock(return_value={"id": CLIENT_ID})
        with patch("mcp_server.tools.block_clients.api_post", mock_post):
            result = await mcp_block_clients.call_tool("vsz_block_client", {
                "host": HOST, "mac": CLIENT_MAC,
            })
        body = mock_post.call_args[1]["data"]
        assert body["mac"] == CLIENT_MAC
        assert "description" not in body

    async def test_block_client_with_description(self, mcp_block_clients):
        mock_post = AsyncMock(return_value={"id": CLIENT_ID})
        with patch("mcp_server.tools.block_clients.api_post", mock_post):
            await mcp_block_clients.call_tool("vsz_block_client", {
                "host": HOST, "mac": CLIENT_MAC,
                "description": "Abuse detected",
            })
        body = mock_post.call_args[1]["data"]
        assert body["description"] == "Abuse detected"

    async def test_unblock_client(self, mcp_block_clients):
        mock_del = AsyncMock(return_value={"success": True, "status_code": 204})
        with patch("mcp_server.tools.block_clients.api_delete", mock_del):
            await mcp_block_clients.call_tool("vsz_unblock_client", {
                "host": HOST, "client_id": CLIENT_ID,
            })
        mock_del.assert_called_once_with(HOST, f"/v11_1/blockClient/{CLIENT_ID}")

    async def test_block_client_error(self, mcp_block_clients):
        with patch("mcp_server.tools.block_clients.api_post", new_callable=AsyncMock, return_value="ERROR: 409"):
            result = await mcp_block_clients.call_tool("vsz_block_client", {
                "host": HOST, "mac": CLIENT_MAC,
            })
        assert "ERROR" in _text(result)


# ===================================================================
# 13. ROGUE AP TOOLS
# ===================================================================
class TestRogueTools:
    async def test_list_rogue_aps(self, mcp_rogue):
        mock_data = {"list": [{"mac": ROGUE_MAC, "ssid": "EvilTwin"}], "totalCount": 1}
        with patch("mcp_server.tools.rogue.api_post", new_callable=AsyncMock, return_value=mock_data):
            result = await mcp_rogue.call_tool("vsz_list_rogue_aps", {"host": HOST})
        parsed = json.loads(_text(result))
        assert parsed["list"][0]["ssid"] == "EvilTwin"

    async def test_list_rogue_aps_with_filters(self, mcp_rogue):
        mock_post = AsyncMock(return_value={"list": [], "totalCount": 0})
        filters_json = json.dumps([{"type": "ZONE", "value": ZONE_ID}])
        # Call the tool function directly to bypass SDK pre_parse_json
        tool_fn = mcp_rogue._tool_manager._tools["vsz_list_rogue_aps"].fn
        with patch("mcp_server.tools.rogue.api_post", mock_post):
            await tool_fn(host=HOST, filters=filters_json)
        body = mock_post.call_args[1]["data"]
        assert body["filters"][0]["type"] == "ZONE"

    async def test_list_rogue_aps_invalid_filters(self, mcp_rogue):
        result = await mcp_rogue.call_tool("vsz_list_rogue_aps", {
            "host": HOST, "filters": "not{json",
        })
        assert "ERROR" in _text(result)

    async def test_mark_rogue_default_classification(self, mcp_rogue):
        mock_post = AsyncMock(return_value={"success": True})
        with patch("mcp_server.tools.rogue.api_post", mock_post):
            result = await mcp_rogue.call_tool("vsz_mark_rogue", {
                "host": HOST, "rogue_mac": ROGUE_MAC,
            })
        mock_post.assert_called_once_with(
            HOST, "/v11_1/rogue/markRogue", data={"rogueAPMac": ROGUE_MAC}
        )

    async def test_mark_rogue_custom_classification(self, mcp_rogue):
        mock_post = AsyncMock(return_value={"success": True})
        with patch("mcp_server.tools.rogue.api_post", mock_post):
            await mcp_rogue.call_tool("vsz_mark_rogue", {
                "host": HOST, "rogue_mac": ROGUE_MAC,
                "classification": "Malicious",
            })
        mock_post.assert_called_once_with(
            HOST, "/v11_1/rogue/markMalicious", data={"rogueAPMac": ROGUE_MAC}
        )

    async def test_mark_rogue_error(self, mcp_rogue):
        with patch("mcp_server.tools.rogue.api_post", new_callable=AsyncMock, return_value="ERROR: Not found"):
            result = await mcp_rogue.call_tool("vsz_mark_rogue", {
                "host": HOST, "rogue_mac": "bad-mac",
            })
        assert "ERROR" in _text(result)

    async def test_mark_rogue_invalid_classification(self, mcp_rogue):
        result = await mcp_rogue.call_tool("vsz_mark_rogue", {
            "host": HOST, "rogue_mac": ROGUE_MAC,
            "classification": "BadValue",
        })
        assert "ERROR" in _text(result)
