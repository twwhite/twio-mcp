import logging

from mcp.server.fastmcp import FastMCP

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

mcp = FastMCP("Unified MCP (TWIO)", host="0.0.0.0", port=8584)


@mcp.tool()
def tool_get_local_time(timezone: str = "America/Los_Angeles"):
    from .tools.time import get_local_time

    """Get current local time.

    Args:
        timezone: IANA timezone string. Default: America/Los_Angeles.
    Returns:
        Formatted time, e.g. "Tuesday, July 30, 2025 11:05 AM PDT".
    """

    return get_local_time(timezone)


def main():
    logger.debug("Starting MCP server...")
    mcp.run()


if __name__ == "__main__":
    main()
