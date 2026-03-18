"""
Ruckus vSZ MCP Server — Main entry point.

Initialises FastMCP, registers all vSZ tools, then starts the
appropriate transport based on the ``MCP_TRANSPORT`` environment variable.

Supported transports
--------------------
``stdio``
    Default.  Suitable for direct LLM process integration (e.g. Claude
    Desktop).  API-key and IP filtering are **not** applicable.
``sse``
    HTTP + Server-Sent Events.  Suitable for web-based MCP clients and
    Docker deployments.
``streamable-http``
    Streamable HTTP transport (recommended for production HTTP deployments).

Security (HTTP transports only)
-------------------------------
When running with ``sse`` or ``streamable-http``:

* If ``MCP_API_KEY`` is set, every request must carry
  ``Authorization: Bearer <MCP_API_KEY>``.
* If ``MCP_ALLOWED_IPS`` is set (comma-separated CIDR list), requests from
  addresses outside the allowlist are rejected with HTTP 403.

Environment variables
---------------------
``MCP_TRANSPORT``          stdio | sse | streamable-http  (default: stdio)
``MCP_SERVER_NAME``        Server display name
``MCP_HOST``               Bind address for HTTP transports (default: 127.0.0.1)
``MCP_PORT``               Bind port for HTTP transports   (default: 8081)
``MCP_API_KEY``            Bearer token required on HTTP requests
``MCP_ALLOWED_IPS``        Comma-separated CIDR allowlist for client IPs
``LOG_LEVEL``              Python log level (default: INFO)
"""
import ipaddress
import logging
import os
import sys
from collections.abc import Callable
from typing import Any

from dotenv import load_dotenv

# load_dotenv FIRST — sub-modules must see .env values at import time.
load_dotenv()

from mcp.server.fastmcp import FastMCP  # noqa: E402

from mcp_server.tools import register_all_tools  # noqa: E402

# ---------------------------------------------------------------------------
# Logging — stderr ONLY, never stdout (stdout is reserved for STDIO transport)
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FastMCP instance — host/port are used by HTTP transports
# ---------------------------------------------------------------------------
mcp = FastMCP(
    os.getenv("MCP_SERVER_NAME", "ruckus-vsz-mcp"),
    host=os.getenv("MCP_HOST", "127.0.0.1"),
    port=int(os.getenv("MCP_PORT", "8081")),
)


# ---------------------------------------------------------------------------
# Pure-ASGI security middleware (streaming-safe: no response buffering)
# ---------------------------------------------------------------------------

class _SecurityMiddleware:
    """ASGI middleware enforcing API-key and IP-allowlist checks.

    Implemented as a pure ASGI callable so that streaming responses
    (SSE, chunked HTTP) pass through without any buffering.

    Args:
        app: The inner ASGI application to wrap.
        api_key: Expected Bearer token value, or empty string to skip check.
        allowed_networks: List of network objects. Empty list skips the IP check.
    """

    def __init__(
        self,
        app: Any,
        api_key: str,
        allowed_networks: list[ipaddress.IPv4Network | ipaddress.IPv6Network],
    ) -> None:
        self.app = app
        self.api_key = api_key
        self.allowed_networks = allowed_networks

    async def __call__(
        self,
        scope: dict,
        receive: Callable,
        send: Callable,
    ) -> None:
        """Handle an ASGI request."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # --- IP allowlist check ---
        if self.allowed_networks:
            client = scope.get("client")
            client_host: str | None = client[0] if client else None

            if not client_host:
                await self._respond(scope, send, 403, "Forbidden: no client IP")
                return
            try:
                client_ip = ipaddress.ip_address(client_host)
                if not any(client_ip in net for net in self.allowed_networks):
                    logger.warning("Rejected request from %s: not in MCP_ALLOWED_IPS", client_host)
                    await self._respond(scope, send, 403, "Forbidden: IP not allowed")
                    return
            except ValueError:
                await self._respond(scope, send, 403, "Forbidden: invalid client IP")
                return

        # --- API-key check ---
        if self.api_key:
            headers: dict[bytes, bytes] = dict(scope.get("headers", []))
            auth_bytes = headers.get(b"authorization", b"")
            auth_header = auth_bytes.decode("latin-1", errors="replace")

            if not auth_header.startswith("Bearer "):
                await self._respond(scope, send, 401, "Unauthorized: missing Bearer token")
                return

            token = auth_header[len("Bearer "):].strip()
            if token != self.api_key:
                await self._respond(scope, send, 401, "Unauthorized: invalid API key")
                return

        await self.app(scope, receive, send)

    @staticmethod
    async def _respond(
        scope: dict,
        send: Callable,
        status: int,
        body: str,
    ) -> None:
        """Send a minimal HTTP error response."""
        encoded = body.encode()
        await send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": [
                    (b"content-type", b"text/plain; charset=utf-8"),
                    (b"content-length", str(len(encoded)).encode()),
                ],
            }
        )
        await send({"type": "http.response.body", "body": encoded, "more_body": False})


def _build_allowed_networks() -> list[ipaddress.IPv4Network | ipaddress.IPv6Network]:
    """Parse ``MCP_ALLOWED_IPS`` into a list of network objects."""
    raw = os.getenv("MCP_ALLOWED_IPS", "").strip()
    if not raw:
        return []

    networks: list[ipaddress.IPv4Network | ipaddress.IPv6Network] = []
    for cidr in raw.split(","):
        cidr = cidr.strip()
        if not cidr:
            continue
        try:
            networks.append(ipaddress.ip_network(cidr, strict=False))
        except ValueError:
            logger.warning("Invalid CIDR in MCP_ALLOWED_IPS: %r — entry ignored", cidr)
    return networks


def _apply_security(app: Any) -> Any:
    """Wrap *app* with security middleware when auth is configured.

    If neither ``MCP_API_KEY`` nor ``MCP_ALLOWED_IPS`` are set the original
    app is returned unchanged (zero overhead).
    """
    api_key = os.getenv("MCP_API_KEY", "").strip()
    allowed_networks = _build_allowed_networks()

    if not api_key and not allowed_networks:
        logger.debug("No MCP_API_KEY / MCP_ALLOWED_IPS configured — security middleware skipped")
        return app

    logger.info(
        "Security middleware enabled: api_key=%s, allowed_networks=%d entries",
        "yes" if api_key else "no",
        len(allowed_networks),
    )
    return _SecurityMiddleware(app, api_key, allowed_networks)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Start the MCP server with the transport selected by ``MCP_TRANSPORT``.

    * ``stdio``           → run directly (blocks until stdin closes)
    * ``sse``             → start uvicorn with SSE Starlette app
    * ``streamable-http`` → start uvicorn with Streamable-HTTP Starlette app
    """
    register_all_tools(mcp)

    transport = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()
    logger.info("Starting Ruckus vSZ MCP server (transport=%s)…", transport)

    if transport == "stdio":
        mcp.run(transport="stdio")
        return

    if transport not in ("sse", "streamable-http"):
        logger.error(
            "Unknown MCP_TRANSPORT=%r — expected stdio, sse or streamable-http",
            transport,
        )
        sys.exit(1)

    # HTTP transports: build Starlette app, apply security, serve via uvicorn.
    import anyio
    import uvicorn

    async def _serve() -> None:
        if transport == "sse":
            mcp_app = mcp.sse_app()
        else:
            mcp_app = mcp.streamable_http_app()

        secured_app = _apply_security(mcp_app)

        config = uvicorn.Config(
            secured_app,
            host=mcp.settings.host,
            port=mcp.settings.port,
            log_level=os.getenv("LOG_LEVEL", "info").lower(),
        )
        server = uvicorn.Server(config)
        logger.info(
            "Uvicorn listening on %s:%d (transport=%s)",
            mcp.settings.host,
            mcp.settings.port,
            transport,
        )
        await server.serve()

    anyio.run(_serve)


if __name__ == "__main__":
    main()
