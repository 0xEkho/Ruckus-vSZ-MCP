# AGENTS.md — MCP Template

> **INSTRUCTION OBLIGATOIRE** : Pour toute tâche dans ce projet, Copilot doit déléguer
> au bon agent spécialisé (voir table ci-dessous). Ne jamais implémenter directement
> sans passer par l'agent approprié.

Ce fichier décrit les agents Copilot disponibles pour ce projet et leurs règles de collaboration.

## Vue d'ensemble du projet

Ce repo est un **template Python pour créer des serveurs MCP** (Model Context Protocol).
- Stack : Python 3.12, `uv`, `FastMCP` (mcp>=1.2.0)
- Transport : STDIO (par défaut)
- Structure : `src/mcp_server/{server.py, tools/, resources/, prompts/}` + `tests/`

## Agents disponibles

| Agent | Fichier | Responsabilité |
|-------|---------|----------------|
| `mcp-scaffolder` | `.github/agents/mcp-scaffolder.agent.md` | Configuration projet (pyproject.toml, .gitignore, .env) |
| `mcp-developer` | `.github/agents/mcp-developer.agent.md` | Code source (tools, resources, prompts) |
| `mcp-tester` | `.github/agents/mcp-tester.agent.md` | Tests pytest-asyncio |
| `mcp-documenter` | `.github/agents/mcp-documenter.agent.md` | README, docstrings, documentation |

## Règle d'or : séparation des responsabilités

```
pyproject.toml / .gitignore / .env.example  →  mcp-scaffolder
src/mcp_server/**                           →  mcp-developer
tests/**                                    →  mcp-tester
README.md / AGENTS.md / docstrings          →  mcp-documenter
```

## Flux de travail pour une nouvelle fonctionnalité

1. **mcp-scaffolder** : ajoute la dépendance si nécessaire
2. **mcp-developer** : implémente le tool/resource/prompt dans `src/`
3. **mcp-tester** : écrit les tests correspondants dans `tests/`
4. **mcp-documenter** : met à jour README.md et vérifie les docstrings

## Best practices MCP — règles non négociables

1. ⛔ **Jamais de `print()` sans `file=sys.stderr`** pour les serveurs STDIO
2. ⛔ **Jamais lever d'exception** depuis un outil pour signaler une erreur métier → retourner un string d'erreur
3. ✅ **Type hints** sur tous les paramètres d'outils → schéma généré automatiquement
4. ✅ **Docstrings** sur chaque primitive → description MCP générée automatiquement
5. ✅ **Variables d'environnement** pour tous les secrets (`.env`, jamais hardcodé)
6. ✅ **Tester avec MCP Inspector** : `npx @modelcontextprotocol/inspector uv run mcp-server`

## Commandes de référence

```bash
uv sync                    # installer les dépendances
uv run mcp-server          # lancer le serveur MCP
uv run pytest              # lancer les tests
uv run pytest --cov=mcp_server  # avec couverture
```
