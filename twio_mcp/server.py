import logging

import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.middleware.cors import CORSMiddleware

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
def tool_get_local_time(timezone: str = "America/Los_Angeles"):
    from twio_mcp.tools.time import get_local_time

    """Get current local time.

    Args:
        timezone: IANA timezone string. Default: America/Los_Angeles.
    Returns:
        Formatted time, e.g. "Tuesday, July 30, 2025 11:05 AM PDT".
    """

    return get_local_time(timezone)


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
