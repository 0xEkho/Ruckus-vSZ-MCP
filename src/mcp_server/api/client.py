"""
Ruckus vSZ REST API client.

Provides an async httpx-based client for the vSZ public API
with automatic service-ticket authentication.

Credentials are read from environment variables (loaded from ``.env``
by ``server.py`` at startup):

- ``VSZ_USERNAME`` — API username
- ``VSZ_PASSWORD`` — API password

The ``host`` parameter is passed by each tool call, allowing
multi-controller management from a single MCP server.  The hosts
are listed in the model's system prompt.
"""

import logging
import os
import warnings
from typing import Any, Optional

import httpx

# Suppress SSL-related warnings for self-signed certs (verify=False)
warnings.filterwarnings("ignore", message=".*Unverified HTTPS.*")

# MCP STDIO transport: logging must go to stderr only
logger = logging.getLogger(__name__)

API_VERSION = "v11_1"
DEFAULT_TIMEOUT = 30.0


def _get_credentials() -> tuple[str, str, bool, float]:
    """Read vSZ credentials and connection settings from environment.

    Returns:
        (username, password, verify_ssl, timeout)

    Raises:
        RuntimeError: If required env vars are missing.
    """
    username = os.getenv("VSZ_USERNAME", "")
    password = os.getenv("VSZ_PASSWORD", "")
    if not username or not password:
        raise RuntimeError(
            "VSZ_USERNAME and VSZ_PASSWORD must be set in .env"
        )
    verify_ssl = os.getenv("VSZ_VERIFY_SSL", "false").lower() in ("true", "1", "yes")
    timeout = float(os.getenv("VSZ_TIMEOUT", str(DEFAULT_TIMEOUT)))
    return username, password, verify_ssl, timeout


async def _get_service_ticket(host: str) -> tuple[httpx.AsyncClient, str]:
    """Authenticate and return (client, service_ticket).

    Creates an httpx.AsyncClient and obtains a service ticket from
    the vSZ controller using credentials from ``.env``.

    Args:
        host: vSZ controller IP or hostname (without port).

    Returns:
        Tuple of (httpx.AsyncClient, service_ticket_string).

    Raises:
        RuntimeError: If env vars are missing.
        ValueError: If authentication fails.
    """
    username, password, verify_ssl, timeout = _get_credentials()
    base_url = f"https://{host}:8443/wsg/api/public"
    client = httpx.AsyncClient(
        base_url=base_url,
        verify=verify_ssl,
        timeout=timeout,
        headers={"Content-Type": "application/json;charset=UTF-8"},
    )
    try:
        resp = await client.post(
            f"/{API_VERSION}/serviceTicket",
            json={"username": username, "password": password},
        )
        resp.raise_for_status()
        data = resp.json()
        ticket = data.get("serviceTicket")
        if not ticket:
            await client.aclose()
            raise ValueError("No serviceTicket in response")
        logger.debug("Service ticket obtained from %s", host)
        return client, ticket
    except Exception:
        await client.aclose()
        raise


async def _api_request(
    host: str,
    method: str,
    endpoint: str,
    data: Optional[dict[str, Any]] = None,
    params: Optional[dict[str, Any]] = None,
) -> dict[str, Any] | list | str:
    """Execute a single authenticated API request.

    Handles the full lifecycle: authenticate → request → close.

    Args:
        host: vSZ controller IP or hostname.
        method: HTTP method (GET, POST, PUT, PATCH, DELETE).
        endpoint: API endpoint path (e.g., "/v11_1/rkszones").
        data: JSON body for POST/PUT/PATCH requests.
        params: Additional query parameters.

    Returns:
        Parsed JSON response (dict or list), or error string on failure.
    """
    try:
        client, ticket = await _get_service_ticket(host)
    except Exception as exc:
        logger.error("Authentication failed: %s", exc)
        return f"ERROR: Authentication failed — {exc}"
    try:
        query: dict[str, Any] = {"serviceTicket": ticket}
        if params:
            query.update(params)

        kwargs: dict[str, Any] = {"params": query}
        if data is not None and method in ("POST", "PUT", "PATCH"):
            kwargs["json"] = data

        resp = await client.request(method, endpoint, **kwargs)
        resp.raise_for_status()

        if resp.status_code == 204 or not resp.content:
            return {"success": True, "status_code": resp.status_code}

        return resp.json()
    except httpx.HTTPStatusError as exc:
        body = exc.response.text
        logger.error(
            "API %s %s → %s: %s", method, endpoint, exc.response.status_code, body
        )
        return f"ERROR: API {exc.response.status_code} — {body}"
    except Exception as exc:
        logger.error("Request error: %s", exc)
        return f"ERROR: {exc}"
    finally:
        await client.aclose()


# ── Convenience functions used by tool modules ──────────────────────


async def api_get(
    host: str, endpoint: str, params: Optional[dict[str, Any]] = None
) -> dict[str, Any] | list | str:
    """GET request to vSZ API."""
    return await _api_request(host, "GET", endpoint, params=params)


async def api_post(
    host: str,
    endpoint: str,
    data: Optional[dict[str, Any]] = None,
    params: Optional[dict[str, Any]] = None,
) -> dict[str, Any] | list | str:
    """POST request to vSZ API."""
    return await _api_request(host, "POST", endpoint, data=data, params=params)


async def api_put(
    host: str,
    endpoint: str,
    data: Optional[dict[str, Any]] = None,
    params: Optional[dict[str, Any]] = None,
) -> dict[str, Any] | list | str:
    """PUT request to vSZ API."""
    return await _api_request(host, "PUT", endpoint, data=data, params=params)


async def api_patch(
    host: str,
    endpoint: str,
    data: Optional[dict[str, Any]] = None,
    params: Optional[dict[str, Any]] = None,
) -> dict[str, Any] | list | str:
    """PATCH request to vSZ API."""
    return await _api_request(host, "PATCH", endpoint, data=data, params=params)


async def api_delete(
    host: str, endpoint: str, params: Optional[dict[str, Any]] = None
) -> dict[str, Any] | list | str:
    """DELETE request to vSZ API."""
    return await _api_request(host, "DELETE", endpoint, params=params)
