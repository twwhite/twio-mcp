import logging
from typing import Callable, TypedDict

import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.middleware.cors import CORSMiddleware

from twio_mcp.registry import REGISTRY

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

mcp = FastMCP(
    "Unified MCP (TWIO)",
    host="0.0.0.0",
    port=8584,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
        allowed_origins=["*"],
    ),
)


@mcp.tool()
def hub(command: str, kwargs: dict | None = None) -> str:
    """
    Central dispatch tool for all available capabilities.
    Always call with command='list' at the start of a session to discover
    available commands. Then call command='help' with the specific command
    name to get full usage details before invoking it.
    """
    if kwargs is None:
        kwargs = {}
    if command not in REGISTRY:
        available = ", ".join(REGISTRY.keys())
        return f"Unknown command '{command}'. Available: {available}"
    return REGISTRY[command](**kwargs)


def main():
    app = mcp.streamable_http_app()
    # Step 2: Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://chat2.timwhite.io"],
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["mcp-session-id"],
    )

    # Step 3: Run with uvicorn directly (not mcp.run)
    uvicorn.run(app, host="0.0.0.0", port=8584)


if __name__ == "__main__":
    main()
