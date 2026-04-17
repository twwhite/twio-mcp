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

    CALLING CONVENTION:
      Every call requires a 'command' string. Optional arguments are passed
      via the 'kwargs' dict — never as top-level arguments.

      Correct:   {"command": "help", "kwargs": {"command": "get_time"}}
      Incorrect: {"command": "help", "command": "get_time"}

    WORKFLOW:
      1. Call {"command": "list"} to see all available commands.
      2. Call {"command": "help", "kwargs": {"command": "<name>"}} for full usage.
      3. Call the command with its required kwargs.

    EXTERNAL GATEWAYS (ext_* commands):
      These proxy to external MCP servers. They are NOT invoked via a top-level
      'invoke' command. Call them directly with an 'action' kwarg:
      {"command": "ext_searxng", "kwargs": {"action": "list"}}
      {"command": "ext_searxng", "kwargs": {"action": "invoke", "tool": "search", "kwargs": {"query": "..."}}}
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
        allow_origins=["https://chat2.sudotim.com"],
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["mcp-session-id"],
    )

    # Step 3: Run with uvicorn directly (not mcp.run)
    uvicorn.run(app, host="0.0.0.0", port=8584)


if __name__ == "__main__":
    main()
