# MCP Server Template 🤖

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![MCP](https://img.shields.io/badge/MCP-1.2.0%2B-green)
![uv](https://img.shields.io/badge/uv-latest-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

Template Python pour créer des serveurs **MCP (Model Context Protocol)** avec [FastMCP](https://github.com/modelcontextprotocol/python-sdk). Ce template fournit une structure de projet prête à l'emploi, avec des exemples fonctionnels d'outils, de ressources et de prompts, ainsi que les bonnes pratiques officielles intégrées dès le départ.

---

## 🚀 Démarrage rapide

### Pré-requis

- [Python 3.10+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — gestionnaire de projet et d'environnement virtuel

### Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/0xEkho/MCP-Template.git
cd MCP-Template

# 2. Copier le fichier de configuration
cp .env.example .env

# 3. Installer les dépendances (crée automatiquement le virtualenv)
uv sync

# 4. Lancer le serveur MCP
uv run mcp-server
```

---

## 📁 Structure du projet

```
MCP-Template/
├── .github/
│   ├── agents/                    # Agents Copilot spécialisés
│   │   ├── mcp-developer.agent.md
│   │   ├── mcp-documenter.agent.md
│   │   ├── mcp-scaffolder.agent.md
│   │   └── mcp-tester.agent.md
│   └── copilot-instructions.md    # Routage obligatoire vers les agents
├── src/
│   └── mcp_server/
│       ├── __init__.py
│       ├── server.py              # Point d'entrée : initialise FastMCP et enregistre les primitives
│       ├── tools/
│       │   ├── __init__.py
│       │   └── example.py         # Exemples d'outils (echo, fetch_url)
│       ├── resources/
│       │   ├── __init__.py
│       │   └── example.py         # Exemples de ressources (config://, docs://)
│       └── prompts/
│           ├── __init__.py
│           └── example.py         # Exemples de prompts (summarize)
├── tests/
│   ├── __init__.py
│   ├── test_tools.py
│   ├── test_resources.py
│   └── test_prompts.py
├── AGENTS.md                      # Vue d'ensemble des agents et best practices
├── LICENSE
├── .env.example                   # Variables d'environnement à copier vers .env
├── .python-version                # Version Python gérée par uv
├── pyproject.toml                 # Configuration du projet et des dépendances
└── README.md
```

---

## 📦 Primitives incluses par défaut

Ce template embarque des exemples fonctionnels et testés de chaque type de primitive MCP.
Supprime-les ou remplace-les par tes propres implémentations.

### 🔧 Tools — exécutés par le modèle
| Nom | Description |
|-----|-------------|
| `echo` | Renvoie un message en écho — utile pour tester la connectivité |
| `fetch_url` | Récupère le contenu textuel d'une URL HTTP/HTTPS |

### 📄 Resources — lues par l'application
| URI | Description |
|-----|-------------|
| `config://server-info` | Métadonnées du serveur (nom, version, transport) |
| `docs://getting-started` | Guide de démarrage en Markdown |

### 💬 Prompts — déclenchés par l'utilisateur
| Nom | Arguments | Description |
|-----|-----------|-------------|
| `summarize` | `text`, `language` (optionnel) | Génère un prompt pour résumer un texte dans la langue choisie |

---

## 🔧 Développement

### Ajouter un outil (tool)

Les outils sont des fonctions exécutables par le modèle. Créez un nouveau fichier dans `src/mcp_server/tools/` ou ajoutez une fonction dans un fichier existant.

```python
# src/mcp_server/tools/my_tools.py
import logging
from typing import Any

logger = logging.getLogger(__name__)


def register_tools(mcp: Any) -> None:
    """Register all tools on the MCP server instance."""

    @mcp.tool()
    async def add_numbers(a: float, b: float) -> str:
        """Add two numbers together and return the result.

        Args:
            a: The first number.
            b: The second number.
        """
        logger.info("add_numbers called: %s + %s", a, b)
        result = a + b
        return f"Result: {result}"
```

Ensuite, enregistrez le nouveau module dans `server.py` :

```python
# src/mcp_server/server.py
from mcp_server.tools.my_tools import register_tools as register_my_tools

register_my_tools(mcp)
```

### Ajouter une ressource (resource)

Les ressources sont des sources de données en lecture seule identifiées par des URI. Elles fournissent du contexte au modèle.

```python
# src/mcp_server/resources/my_resources.py
import logging
from typing import Any

logger = logging.getLogger(__name__)


def register_resources(mcp: Any) -> None:
    """Register all resources on the MCP server instance."""

    @mcp.resource("config://my-config")
    def my_config() -> str:
        """Provide application configuration as a resource.

        Returns key/value configuration for the current environment.
        """
        logger.info("my_config resource accessed")
        return (
            "env=production\n"
            "feature_x=enabled\n"
        )
```

### Ajouter un prompt

Les prompts sont des templates réutilisables qui structurent les interactions avec le modèle.

```python
# src/mcp_server/prompts/my_prompts.py
import logging
from typing import Any

from mcp.types import GetPromptResult, PromptMessage, TextContent

logger = logging.getLogger(__name__)


def register_prompts(mcp: Any) -> None:
    """Register all prompts on the MCP server instance."""

    @mcp.prompt()
    def review_code(code: str, language: str = "Python") -> GetPromptResult:
        """Generate a prompt asking the LLM to review a code snippet.

        Args:
            code: The source code to review.
            language: The programming language (default: Python).
        """
        logger.info("review_code prompt requested, language=%s", language)
        return GetPromptResult(
            description=f"Review the provided {language} code",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=(
                            f"Please review the following {language} code and suggest improvements.\n\n"
                            f"```{language.lower()}\n{code}\n```"
                        ),
                    ),
                )
            ],
        )
```

---

## 🧪 Tests

```bash
# Lancer tous les tests
uv run pytest

# Avec rapport de couverture de code
uv run pytest --cov=mcp_server

# Rapport de couverture en HTML
uv run pytest --cov=mcp_server --cov-report=html

# Lancer un fichier de test spécifique
uv run pytest tests/test_tools.py -v
```

---

## 🔍 Debug avec MCP Inspector

[MCP Inspector](https://github.com/modelcontextprotocol/inspector) est un outil interactif pour tester et inspecter un serveur MCP directement depuis le navigateur.

```bash
npx @modelcontextprotocol/inspector uv run mcp-server
```

Ouvrez ensuite l'URL affichée dans le terminal (généralement `http://localhost:5173`) pour explorer les outils, ressources et prompts exposés par votre serveur.

---

## ⚙️ Configuration Claude Desktop

Pour utiliser ce serveur dans [Claude Desktop](https://claude.ai/download), éditez le fichier `claude_desktop_config.json` :

- **macOS** : `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows** : `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "mon-serveur": {
      "command": "uv",
      "args": [
        "--directory",
        "/CHEMIN/ABSOLU/VERS/MCP-Template",
        "run",
        "mcp-server"
      ]
    }
  }
}
```

> ⚠️ Remplacez `/CHEMIN/ABSOLU/VERS/MCP-Template` par le chemin absolu réel vers ce projet sur votre machine.

---

## 📋 Bonnes pratiques

Ces bonnes pratiques sont issues des [spécifications officielles MCP](https://modelcontextprotocol.io/docs/concepts/architecture) et sont déjà appliquées dans ce template.

1. **Ne jamais écrire sur `stdout` avec le transport STDIO** — toute sortie sur `stdout` corromprait le protocole. Utilisez exclusivement `logging` vers `stderr` :
   ```python
   import sys
   logging.basicConfig(stream=sys.stderr)
   ```

2. **Retourner les erreurs dans le résultat d'un outil, ne pas lever d'exceptions** — renvoyez un message d'erreur explicite plutôt que de laisser une exception se propager :
   ```python
   if not url.startswith(("http://", "https://")):
       return "Error: URL must start with http:// or https://"
   ```

3. **Utiliser des type hints et des docstrings** — FastMCP génère automatiquement les schémas JSON à partir des annotations de type et des docstrings :
   ```python
   async def my_tool(name: str, count: int = 1) -> str:
       """Description de l'outil visible par le modèle."""
   ```

4. **Séparer Tools / Resources / Prompts en modules distincts** — un module par type de primitive favorise la lisibilité et la maintenabilité (voir la structure de ce template).

5. **Utiliser des variables d'environnement pour les secrets** — ne jamais mettre de clés API en dur dans le code. Utilisez `.env` (basé sur `.env.example`) et `python-dotenv` :
   ```python
   import os
   api_key = os.getenv("MY_API_KEY")
   ```

6. **Tester avec MCP Inspector avant d'intégrer dans un client** — validez le comportement de chaque outil, ressource et prompt de manière isolée avant de configurer Claude Desktop ou un autre client MCP.

---

## 🤖 Agents Copilot intégrés

Ce template embarque 4 agents Copilot spécialisés (`.github/agents/`) qui respectent automatiquement la séparation des responsabilités. Ils sont utilisables dans **Copilot CLI** et **VS Code Copilot Chat**.

| Agent | Domaine |
|-------|---------|
| `mcp-developer` | Code source : `src/mcp_server/` (tools, resources, prompts) |
| `mcp-tester` | Tests : `tests/` — ne modifie jamais `src/` |
| `mcp-scaffolder` | Config : `pyproject.toml`, `.gitignore`, `.env.example` |
| `mcp-documenter` | Docs : `README.md`, docstrings, `AGENTS.md` |

**Utilisation :**
```bash
# Sélectionner un agent dans Copilot CLI
/agent

# Ou directement dans un prompt
Use mcp-developer to add a tool that queries the GitHub API
```

> Le fichier `.github/copilot-instructions.md` impose la délégation automatique au bon agent à chaque prompt dans ce repo.

---

## 🔗 Ressources

- [MCP Documentation](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
- [Exemples officiels de serveurs MCP](https://github.com/modelcontextprotocol/servers)
- [uv — Documentation](https://docs.astral.sh/uv/)
