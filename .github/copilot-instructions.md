# Copilot Instructions — MCP Template

Ce fichier est lu automatiquement par Copilot CLI et VS Code Copilot à chaque session dans ce repo.

## RÈGLE ABSOLUE : Délégation obligatoire aux agents spécialisés

Pour **toute tâche** dans ce projet, tu **DOIS** déléguer au bon agent spécialisé.
Tu ne dois **JAMAIS** implémenter directement du code, des tests ou de la documentation sans passer par l'agent approprié.

## Table de routage obligatoire

| Tâche demandée | Agent à utiliser OBLIGATOIREMENT |
|----------------|----------------------------------|
| Ajouter / modifier un tool, resource ou prompt | **mcp-developer** |
| Modifier `server.py`, la structure `src/` | **mcp-developer** |
| Écrire ou modifier des tests dans `tests/` | **mcp-tester** |
| Modifier `pyproject.toml`, `.gitignore`, `.env.example` | **mcp-scaffolder** |
| Mettre à jour `README.md`, docstrings, `AGENTS.md` | **mcp-documenter** |
| Tâche multi-domaines | Déléguer à **chaque agent concerné**, dans l'ordre : scaffolder → developer → tester → documenter |

## Protocole de réponse

Pour chaque prompt reçu, tu dois :

1. **Identifier** quel(s) agent(s) est concerné
2. **Annoncer** explicitement : *"Je délègue cette tâche à [nom-agent]"*
3. **Utiliser** l'agent via le tool `task` avec `agent_type` approprié
4. **Ne jamais** bypasser les agents pour écrire du code directement

## Rappels MCP non négociables

Ces règles doivent être rappelées et vérifiées par les agents :

- ⛔ Jamais `print()` sans `file=sys.stderr` (transport STDIO)
- ⛔ Jamais lever d'exception depuis un outil MCP → retourner une string d'erreur
- ✅ Type hints sur tous les paramètres
- ✅ Docstrings sur chaque primitive (tool, resource, prompt)
- ✅ Secrets uniquement dans `.env` (jamais hardcodés)
