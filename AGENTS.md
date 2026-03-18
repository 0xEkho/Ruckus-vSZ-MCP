# AGENTS.md — Ruckus vSZ MCP Server

> **INSTRUCTION OBLIGATOIRE** : Pour **tout prompt** dans ce projet, Copilot doit invoquer
> les **4 agents en parallèle**, sans exception. Chaque agent audite et agit sur son domaine.
> Ne jamais implémenter directement sans passer par les agents.

Ce fichier décrit les agents Copilot disponibles pour ce projet et leurs règles de collaboration.

## Vue d'ensemble du projet

Ce repo est un **serveur MCP (Model Context Protocol)** pour la gestion de contrôleurs Wi-Fi **Ruckus Virtual SmartZone (vSZ)** via leur API REST.
- Stack : Python ≥3.10 (runtime recommandé : 3.12), `uv`, `FastMCP` (mcp>=1.2.0), `httpx`
- Transport : STDIO (par défaut)
- API vSZ : `https://{host}:8443/wsg/api/public/v11_1`
- Auth : `serviceTicket` (acquis par appel, credentials depuis `.env` : `VSZ_USERNAME` / `VSZ_PASSWORD`)
- Paramètre tool : `host` uniquement (permet le multi-contrôleur depuis le system prompt)
- Préfixe outils : `vsz_`
- Structure : `src/mcp_server/{server.py, api/, tools/, resources/, prompts/}` + `tests/`
- **52 tools** répartis en **12 modules**

## Agents disponibles

| Agent | Fichier | Responsabilité |
|-------|---------|----------------|
| `mcp-scaffolder` | `.github/agents/mcp-scaffolder.agent.md` | Configuration projet (pyproject.toml, .gitignore, .env) |
| `mcp-developer` | `.github/agents/mcp-developer.agent.md` | Code source (api client, tools, resources, prompts) |
| `mcp-tester` | `.github/agents/mcp-tester.agent.md` | Tests pytest-asyncio |
| `mcp-documenter` | `.github/agents/mcp-documenter.agent.md` | README, docstrings, documentation |

## Règle d'or : invocation parallèle des 4 agents à chaque prompt

```
Chaque prompt → mcp-scaffolder + mcp-developer + mcp-tester + mcp-documenter (en parallèle)
```

Chaque agent vérifie son domaine même si la tâche ne le concerne pas directement.
Si rien à faire → l'agent répond "RAS" mais **doit être invoqué**.

## Flux de travail pour une nouvelle fonctionnalité

1. **mcp-scaffolder** : ajoute la dépendance si nécessaire
2. **mcp-developer** : implémente le tool dans `src/mcp_server/tools/`, enregistre dans `__init__.py`
3. **mcp-tester** : écrit les tests correspondants dans `tests/`
4. **mcp-documenter** : met à jour README.md (table des outils) et vérifie les docstrings

## Canonical Tool Registry (52 tools — 12 modules)

### System (5 tools) — `system.py`
- `vsz_get_system_info(host)` — Get vSZ system information (version, model, uptime)
- `vsz_get_system_summary(host)` — Get system summary with AP/client counts
- `vsz_get_system_inventory(host)` — Get per-zone AP and client statistics
- `vsz_get_cluster_state(host)` — Get cluster node status and roles
- `vsz_get_controller_list(host)` — List all controllers in the cluster

### Zones (6 tools) — `zones.py`
- `vsz_list_zones(host)` — List all zones
- `vsz_get_zone(host, zone_id)` — Get zone details
- `vsz_create_zone(host, name, ...)` — Create a new zone
- `vsz_update_zone(host, zone_id, ...)` — Update zone configuration
- `vsz_delete_zone(host, zone_id)` — Delete a zone
- `vsz_list_zone_ap_groups(host, zone_id)` — List AP groups in a zone

### Access Points (9 tools) — `aps.py`
- `vsz_list_aps(host)` — List all access points
- `vsz_get_ap(host, ap_mac)` — Get AP configuration details
- `vsz_get_ap_operational(host, ap_mac)` — Get AP operational info (uptime, clients, status)
- `vsz_update_ap(host, ap_mac, ...)` — Update AP configuration
- `vsz_delete_ap(host, ap_mac)` — Remove AP from management
- `vsz_reboot_ap(host, ap_mac)` — Reboot an access point
- `vsz_list_ap_lldp(host, ap_mac)` — Get AP LLDP neighbours (via /operational/neighbor endpoint)
- `vsz_get_ap_radio(host, ap_mac)` — Get AP radio configuration extracted from AP config endpoint (2.4G / 5G / 6G)
- `vsz_query_aps(host, ...)` — Query APs with filters

### WLANs (6 tools) — `wlans.py`
- `vsz_list_wlans(host, zone_id)` — List WLANs in a zone
- `vsz_get_wlan(host, zone_id, wlan_id)` — Get WLAN configuration details
- `vsz_create_wlan(host, zone_id, name, ssid, ...)` — Create a new WLAN
- `vsz_update_wlan(host, zone_id, wlan_id, ...)` — Update WLAN configuration
- `vsz_delete_wlan(host, zone_id, wlan_id)` — Delete a WLAN
- `vsz_enable_disable_wlan(host, zone_id, wlan_id, enabled)` — Enable or disable a WLAN

### Clients (4 tools) — `clients.py`
- `vsz_list_clients(host)` — List connected wireless clients
- `vsz_get_client(host, client_mac)` — Get client details by MAC
- `vsz_disconnect_client(host, client_mac, ap_mac)` — Disconnect a wireless client (requires AP MAC)
- `vsz_query_clients(host, ...)` — Query clients with filters

### Alarms (4 tools) — `alarms.py`
- `vsz_list_alarms(host)` — List active alarms
- `vsz_get_alarm(host, alarm_id)` — Get alarm details (fetches alarm list and filters for matching ID)
- `vsz_acknowledge_alarm(host, alarm_id)` — Acknowledge an alarm (PUT ack endpoint)
- `vsz_clear_alarm(host, alarm_id)` — Clear an alarm (PUT clear endpoint)

### Domains (3 tools) — `domains.py`
- `vsz_list_domains(host)` — List all administration domains
- `vsz_get_domain(host, domain_id)` — Get domain details
- `vsz_create_domain(host, name, ...)` — Create a new domain

### Authentication / AAA (3 tools) — `aaa.py`
- `vsz_list_auth_servers(host)` — List authentication (RADIUS) servers
- `vsz_get_auth_server(host, server_id)` — Get auth server details
- `vsz_test_aaa(host, server_type, server_ip, server_port, shared_secret, ...)` — Test AAA server connectivity

### DHCP & Network (4 tools) — `dhcp.py`
- `vsz_list_dhcp_pools(host, zone_id)` — List DHCP pools in a zone
- `vsz_get_dhcp_pool(host, zone_id, pool_id)` — Get DHCP pool details
- `vsz_list_vlan_pools(host)` — List VLAN pooling profiles (POST query endpoint)
- `vsz_get_vlan_pool(host, pool_id)` — Get VLAN pool details

### Monitoring & Query (3 tools) — `monitoring.py`
- `vsz_query(host, query_type, ...)` — Generic query with filters (ap, client, wlan, dpsk, roguesInfoList)
- `vsz_get_ap_statistics(host, ap_mac)` — Get AP traffic statistics
- `vsz_get_wlan_statistics(host, wlan_name=None)` — Get WLAN statistics via query API (optional name filter)

### Block Clients (3 tools) — `block_clients.py`
- `vsz_list_blocked_clients(host)` — List blocked (blacklisted) clients (POST query endpoint)
- `vsz_block_client(host, mac, ...)` — Block a client by MAC address
- `vsz_unblock_client(host, client_id)` — Unblock a client

### Rogue APs (2 tools) — `rogue.py`
- `vsz_list_rogue_aps(host, ...)` — List detected rogue access points
- `vsz_mark_rogue(host, rogue_mac, ...)` — Mark/classify a rogue AP (Rogue, Known, Malicious, Ignore)

## Best practices MCP — règles non négociables

1. ⛔ **Jamais de `print()` sans `file=sys.stderr`** pour les serveurs STDIO
2. ⛔ **Jamais lever d'exception** depuis un outil pour signaler une erreur métier → retourner un string d'erreur
3. ✅ **Type hints** sur tous les paramètres d'outils → schéma généré automatiquement
4. ✅ **Docstrings** sur chaque primitive → description MCP générée automatiquement
5. ✅ **Credentials dans `.env`** (`VSZ_USERNAME`, `VSZ_PASSWORD`) — seul `host` est paramètre d’outil
6. ✅ **Tester avec MCP Inspector** : `npx @modelcontextprotocol/inspector uv run ruckus-vsz-mcp`

## Commandes de référence

```bash
uv sync                          # installer les dépendances
uv run ruckus-vsz-mcp            # lancer le serveur MCP
uv run pytest                    # lancer les tests
uv run pytest --cov=mcp_server   # avec couverture
```
