# Ruckus Virtual SmartZone — MCP Server 🔌

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![MCP](https://img.shields.io/badge/MCP-1.2.0%2B-green)
![uv](https://img.shields.io/badge/uv-latest-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

> **Model Context Protocol server** for Ruckus Virtual SmartZone (vSZ) wireless controller management.
> Exposes **52 tools** across 12 modules to query and manage APs, WLANs, zones, clients, alarms, and more — directly from an LLM.

---

## 🚀 Quick Start

### Prerequisites

- [Python ≥ 3.10](https://www.python.org/downloads/) (recommended: 3.12)
- [uv](https://docs.astral.sh/uv/) package manager
- Access to a Ruckus vSZ controller (API port 8443)

### Installation

```bash
git clone https://github.com/0xEkho/Ruckus-vSZ-MCP.git
cd Ruckus-vSZ-MCP
cp .env.example .env    # Set VSZ_USERNAME & VSZ_PASSWORD
uv sync
```

### Run

```bash
uv run ruckus-vsz-mcp
```

### Test with MCP Inspector

```bash
npx @modelcontextprotocol/inspector uv run ruckus-vsz-mcp
```
### Docker (SSE / streamable-http)

```bash
cp .env.example .env    # Set VSZ_USERNAME, VSZ_PASSWORD, MCP_TRANSPORT=sse
docker compose up -d
docker compose logs -f
```

The server listens on port **8081** by default (configurable via `MCP_PORT`).
---

## � Architecture & Connection Model

```
┌─────────────┐   STDIO    ┌──────────────────┐   HTTPS/8443   ┌────────────┐
│  LLM Client │ ◄────────► │  MCP Server      │ ◄────────────► │  vSZ #1    │
│  (Claude…)  │            │  ruckus-vsz-mcp  │                └────────────┘
└─────────────┘            │                  │   HTTPS/8443   ┌────────────┐
                           │  ┌─── .env ────┐ │ ◄────────────► │  vSZ #2    │
                           │  │ VSZ_USERNAME │ │                └────────────┘
                           │  │ VSZ_PASSWORD │ │
                           │  └─────────────┘ │
                           └──────────────────┘
```

| Parameter | Source | Scope |
|-----------|--------|-------|
| `host` | Tool parameter | Per-call — enables multi-controller from system prompt |
| `VSZ_USERNAME` | `.env` file | Shared across all controllers |
| `VSZ_PASSWORD` | `.env` file | Shared across all controllers |

- **API base URL** : `https://{host}:8443/wsg/api/public/v11_1`
- **Authentication** : `serviceTicket` acquired automatically on each tool call via `POST /v11_1/serviceTicket`
- **Transport** : STDIO (default)
- **SSL** : Verification disabled by default (vSZ uses self-signed certificates) — configurable via `VSZ_VERIFY_SSL`

---

## 🔧 MCP Client Configuration

### Claude Desktop

Edit `claude_desktop_config.json`:

- **macOS** : `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows** : `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ruckus-vsz": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/Ruckus-vSZ-MCP", "run", "ruckus-vsz-mcp"]
    }
  }
}
```

### VS Code (GitHub Copilot)

In `.vscode/mcp.json` :

```json
{
  "servers": {
    "ruckus-vsz": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/Ruckus-vSZ-MCP", "run", "ruckus-vsz-mcp"]
    }
  }
}
```

> ⚠️ Replace `/absolute/path/to/Ruckus-vSZ-MCP` with the absolute path to this project on your machine.

### Docker / Remote (SSE)

If the server runs in Docker or on a remote machine, use the SSE URL:

```json
{
  "mcpServers": {
    "ruckus-vsz": {
      "url": "http://localhost:8081/sse"
    }
  }
}
```

### System Prompt Example

Add the vSZ hosts to the model's system prompt so the LLM knows which controller(s) to target:

```
You have access to a Ruckus vSZ MCP server.
Available controllers:
- Production: host = "vsz-prod.example.com"
- Lab: host = "10.0.1.100"

Credentials are pre-configured in the server's .env file.
Always specify the host parameter when calling vsz_* tools.
```

---

## 🛠 Available Tools (52)

### System — `system.py` (5 tools)

| Tool | Signature | Description |
|------|-----------|-------------|
| `vsz_get_system_info` | `(host)` | Get vSZ system information (version, model, uptime) |
| `vsz_get_system_summary` | `(host)` | Get system summary with AP/client counts |
| `vsz_get_system_inventory` | `(host)` | Get per-zone AP and client statistics |
| `vsz_get_cluster_state` | `(host)` | Get cluster node status and roles |
| `vsz_get_controller_list` | `(host)` | List all controllers in the cluster |

### Zones — `zones.py` (6 tools)

| Tool | Signature | Description |
|------|-----------|-------------|
| `vsz_list_zones` | `(host)` | List all zones |
| `vsz_get_zone` | `(host, zone_id)` | Get zone details |
| `vsz_create_zone` | `(host, name, ...)` | Create a new zone |
| `vsz_update_zone` | `(host, zone_id, ...)` | Update zone configuration |
| `vsz_delete_zone` | `(host, zone_id)` | Delete a zone |
| `vsz_list_zone_ap_groups` | `(host, zone_id)` | List AP groups in a zone |

### Access Points — `aps.py` (9 tools)

| Tool | Signature | Description |
|------|-----------|-------------|
| `vsz_list_aps` | `(host)` | List all access points |
| `vsz_get_ap` | `(host, ap_mac)` | Get AP configuration details |
| `vsz_get_ap_operational` | `(host, ap_mac)` | Get AP operational info (uptime, clients, status) |
| `vsz_update_ap` | `(host, ap_mac, ...)` | Update AP configuration |
| `vsz_delete_ap` | `(host, ap_mac)` | Remove AP from management |
| `vsz_reboot_ap` | `(host, ap_mac)` | Reboot an access point |
| `vsz_list_ap_lldp` | `(host, ap_mac)` | Get AP LLDP neighbours (via /operational/neighbor endpoint) |
| `vsz_get_ap_radio` | `(host, ap_mac)` | Get AP radio configuration extracted from AP config endpoint (2.4G / 5G / 6G) |
| `vsz_query_aps` | `(host, ...)` | Query APs with filters |

### WLANs — `wlans.py` (6 tools)

| Tool | Signature | Description |
|------|-----------|-------------|
| `vsz_list_wlans` | `(host, zone_id)` | List WLANs in a zone |
| `vsz_get_wlan` | `(host, zone_id, wlan_id)` | Get WLAN configuration details |
| `vsz_create_wlan` | `(host, zone_id, name, ssid, ...)` | Create a new WLAN |
| `vsz_update_wlan` | `(host, zone_id, wlan_id, ...)` | Update WLAN configuration |
| `vsz_delete_wlan` | `(host, zone_id, wlan_id)` | Delete a WLAN |
| `vsz_enable_disable_wlan` | `(host, zone_id, wlan_id, enabled)` | Enable or disable a WLAN |

### Clients — `clients.py` (4 tools)

| Tool | Signature | Description |
|------|-----------|-------------|
| `vsz_list_clients` | `(host)` | List connected wireless clients |
| `vsz_get_client` | `(host, client_mac)` | Get client details by MAC |
| `vsz_disconnect_client` | `(host, client_mac, ap_mac)` | Disconnect a wireless client (requires AP MAC) |
| `vsz_query_clients` | `(host, ...)` | Query clients with filters |

### Alarms — `alarms.py` (4 tools)

| Tool | Signature | Description |
|------|-----------|-------------|
| `vsz_list_alarms` | `(host)` | List active alarms |
| `vsz_get_alarm` | `(host, alarm_id)` | Get alarm details (fetches list and filters for matching ID) |
| `vsz_acknowledge_alarm` | `(host, alarm_id)` | Acknowledge an alarm (PUT ack endpoint) |
| `vsz_clear_alarm` | `(host, alarm_id)` | Clear an alarm (PUT clear endpoint) |

### Domains — `domains.py` (3 tools)

| Tool | Signature | Description |
|------|-----------|-------------|
| `vsz_list_domains` | `(host)` | List all administration domains |
| `vsz_get_domain` | `(host, domain_id)` | Get domain details |
| `vsz_create_domain` | `(host, name, ...)` | Create a new domain |

### Authentication / AAA — `aaa.py` (3 tools)

| Tool | Signature | Description |
|------|-----------|-------------|
| `vsz_list_auth_servers` | `(host)` | List authentication (RADIUS) servers |
| `vsz_get_auth_server` | `(host, server_id)` | Get auth server details |
| `vsz_test_aaa` | `(host, server_type, server_ip, server_port, shared_secret, ...)` | Test AAA server connectivity |

### DHCP & Network — `dhcp.py` (4 tools)

| Tool | Signature | Description |
|------|-----------|-------------|
| `vsz_list_dhcp_pools` | `(host, zone_id)` | List DHCP pools in a zone |
| `vsz_get_dhcp_pool` | `(host, zone_id, pool_id)` | Get DHCP pool details |
| `vsz_list_vlan_pools` | `(host)` | List VLAN pooling profiles (POST query endpoint) |
| `vsz_get_vlan_pool` | `(host, pool_id)` | Get VLAN pool details |

### Monitoring & Query — `monitoring.py` (3 tools)

| Tool | Signature | Description |
|------|-----------|-------------|
| `vsz_query` | `(host, query_type, ...)` | Generic query with filters (ap, client, wlan, dpsk, roguesInfoList) |
| `vsz_get_ap_statistics` | `(host, ap_mac)` | Get AP traffic statistics |
| `vsz_get_wlan_statistics` | `(host, wlan_name=None)` | Get WLAN statistics via query API (optional name filter) |

### Block Clients — `block_clients.py` (3 tools)

| Tool | Signature | Description |
|------|-----------|-------------|
| `vsz_list_blocked_clients` | `(host)` | List blocked (blacklisted) clients (POST query endpoint) |
| `vsz_block_client` | `(host, mac, ...)` | Block a client by MAC address |
| `vsz_unblock_client` | `(host, client_id)` | Unblock a client |

### Rogue APs — `rogue.py` (2 tools)

| Tool | Signature | Description |
|------|-----------|-------------|
| `vsz_list_rogue_aps` | `(host, ...)` | List detected rogue access points |
| `vsz_mark_rogue` | `(host, rogue_mac, ...)` | Mark/classify a rogue AP (Rogue, Known, Malicious, Ignore) |

---

## 📁 Project Structure

```
Ruckus-vSZ-MCP/
├── src/
│   └── mcp_server/
│       ├── __init__.py
│       ├── server.py              # FastMCP entry point (STDIO transport)
│       ├── api/
│       │   ├── __init__.py
│       │   └── client.py          # Async httpx vSZ API client (auth from .env)
│       ├── tools/                 # 52 MCP tools — one module per vSZ API domain
│       │   ├── __init__.py        # register_all_tools() — aggregates 12 modules
│       │   ├── system.py          # System info, cluster, inventory (5)
│       │   ├── zones.py           # Zone CRUD, AP groups (6)
│       │   ├── aps.py             # AP management, radio, LLDP, query (9)
│       │   ├── wlans.py           # WLAN CRUD, enable/disable (6)
│       │   ├── clients.py         # Client listing, disconnect, query (4)
│       │   ├── alarms.py          # Alarm list, details, ack, clear (4)
│       │   ├── domains.py         # Domain management (3)
│       │   ├── aaa.py             # AAA server listing, test (3)
│       │   ├── dhcp.py            # DHCP/VLAN pool management (4)
│       │   ├── monitoring.py      # Generic query, statistics (3)
│       │   ├── block_clients.py   # Client blacklist management (3)
│       │   └── rogue.py           # Rogue AP detection (2)
│       ├── resources/
│       │   └── example.py
│       └── prompts/
│           └── example.py
├── tests/
│   ├── test_server.py
│   ├── test_tools.py
│   ├── test_resources.py
│   └── test_prompts.py
├── .env.example                   # Environment template (credentials, settings)
├── pyproject.toml
├── AGENTS.md
└── README.md
```

---

## 🧪 Testing

```bash
uv run pytest                                       # Run all 130 tests
uv run pytest -v                                    # Verbose output
uv run pytest --cov=mcp_server                      # With coverage
uv run pytest --cov=mcp_server --cov-report=html    # HTML coverage report
uv run pytest tests/test_tools.py -v                # Single test file
```

---

## 🔐 Security Notes

- **Credentials** are stored in `.env` (`VSZ_USERNAME`, `VSZ_PASSWORD`) — never hardcoded
- **SSL verification** is disabled by default (vSZ uses self-signed certificates) — enable via `VSZ_VERIFY_SSL=true`
- **Service tickets** expire after 24 hours — acquired fresh on each tool call
- **`host`** is the only connection parameter exposed to the LLM — credentials remain server-side

---

## 📜 MCP Rules (non-negotiable)

1. ⛔ **Never `print()` without `file=sys.stderr`** — STDIO transport requires clean stdout
   ```python
   import sys
   logging.basicConfig(stream=sys.stderr)
   ```

2. ⛔ **Never raise exceptions from MCP tools** — return error strings instead
   ```python
   try:
       result = await api_get(host, "/v11_1/aps")
   except Exception as e:
       return f"Error: {e}"
   ```

3. ✅ **Type hints on all parameters** — FastMCP generates JSON schemas automatically
   ```python
   async def vsz_list_aps(host: str) -> str:
   ```

4. ✅ **Docstrings on every tool** — auto-generates MCP descriptions
   ```python
   """List all access points managed by the vSZ controller.

   Args:
       host: vSZ controller IP or hostname.
   """
   ```

5. ✅ **Credentials in `.env`** — `host` is the only tool parameter for connection
6. ✅ **Test with MCP Inspector** : `npx @modelcontextprotocol/inspector uv run ruckus-vsz-mcp`

---

## 🔧 Development

### Add a new vSZ tool

1. Create a module in `src/mcp_server/tools/` (e.g., `firmware.py`)
2. Implement `register_tools(mcp)` with `@mcp.tool()` decorated functions
3. Import and register in `src/mcp_server/tools/__init__.py`
4. Add tests in `tests/`
5. Update this README

**Example:**

```python
# src/mcp_server/tools/firmware.py
import json
import logging

from mcp.server.fastmcp import FastMCP
from mcp_server.api.client import API_VERSION, api_get

logger = logging.getLogger(__name__)
V = API_VERSION


def register_tools(mcp: FastMCP) -> None:
    """Register firmware management tools."""

    @mcp.tool()
    async def vsz_list_firmware(host: str) -> str:
        """List available firmware versions on the vSZ controller.

        Args:
            host: vSZ controller IP or hostname.
        """
        result = await api_get(host, f"/{V}/firmware")
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2)
```

---

## 🤖 Copilot Agents

This project includes 4 specialized Copilot agents (`.github/agents/`) for automated development workflows.

| Agent | Domain |
|-------|--------|
| `mcp-developer` | Source code: `src/mcp_server/` (tools, resources, prompts) |
| `mcp-tester` | Tests: `tests/` — never modifies `src/` |
| `mcp-scaffolder` | Config: `pyproject.toml`, `.gitignore`, `.env.example` |
| `mcp-documenter` | Docs: `README.md`, docstrings, `AGENTS.md` |

> `.github/copilot-instructions.md` enforces automatic delegation to the correct agent on every prompt.

---

## 🔗 Resources

- [MCP Documentation](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
- [Ruckus vSZ API Reference](https://docs.commscope.com/bundle/vsz-apidocs-public-611)
- [uv — Documentation](https://docs.astral.sh/uv/)

---

## 📝 License

MIT
