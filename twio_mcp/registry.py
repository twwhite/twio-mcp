from typing import Callable

from twio_mcp.commands import (
    CommandMeta,
    cmd_calculate,
    cmd_get_time,
    cmd_help,
    cmd_list,
)
from twio_mcp.commands.ext_mcp import ExternalMCPGateway
from twio_mcp.ext_mcp_config import EXTERNAL_SERVERS

COMMANDS: dict[str, CommandMeta] = {
    "list": {
        "short": "Show all available commands",
        "detail": "Lists every registered command with a one-line description. No kwargs. Call this first to orient yourself, then call help <command> for full usage details.",
        "kwargs": {},
        "example": '{"command": "list"}',
    },
    "help": {
        "short": 'Show usage for a command. Usage: {"command": "help", "kwargs": {"command": "<name>"}}',
        "detail": "Returns full description, kwargs, types, defaults, and an example call for the given command.",
        "kwargs": {
            "command": "str, required — the command name to get help for",
        },
        "example": '{"command": "help", "kwargs": {"command": "list"}}',
    },
    "get_time": {
        "short": "Get the current local time",
        "detail": "Returns the current local time for a given timezone.",
        "kwargs": {
            "timezone": "str, default='America/Los_Angeles' — IANA timezone string e.g. 'Europe/London'",
        },
        "example": '{"command": "get_time", "kwargs": {"timezone": "America/New_York"}}',
    },
    "calculate": {
        "short": "Evaluate a mathematical expression",
        "detail": "Evaluates arithmetic, algebraic, symbolic, calculus expressions using sympy. Supports solve(), diff(), integrate(), simplify(), limit() and more.",
        "kwargs": {
            "expression": "str, required — the expression to evaluate e.g. 'solve(x**2 - 4, x)'",
        },
        "example": '{"command": "calculate", "kwargs": {"expression": "solve(x**2 - 4, x)"}}',
    },
}

REGISTRY: dict[str, Callable] = {
    "list": cmd_list,
    "help": cmd_help,
    "get_time": cmd_get_time,
    "calculate": cmd_calculate,
}
# ---------------------------------------------------------------------------
# Auto-register external MCP servers from config
# ---------------------------------------------------------------------------

for _server in EXTERNAL_SERVERS:
    _name = _server["name"]
    _url = _server["url"]
    _transport = _server.get("transport", "http")
    _command_name = f"ext_{_name}"
    _gateway = ExternalMCPGateway(name=_name, url=_url, transport=_transport)

    COMMANDS[_command_name] = {
        "short": f'External MCP gateway. Usage: {{"command": "ext_{_name}", "kwargs": {{"action": "list"}}}}',
        "detail": (
            f"External MCP gateway for {_name} ({_url}).\n"
            f"  actions:\n"
            f"    list    — show all tools on this server\n"
            f"    help    — show usage for a specific tool. kwargs: tool (str)\n"
            f"    invoke  — call a tool. kwargs: tool (str), kwargs (dict)"
        ),
        "kwargs": {
            "action": "str, default='list' — one of: list, help, invoke",
            "tool": "str, optional — tool name for help and invoke actions",
            "kwargs": "dict, optional — arguments to pass to the tool on invoke",
        },
        "example": f'{{"command": "ext_{_name}", "kwargs": {{"action": "list"}}}}',
    }
    REGISTRY[_command_name] = _gateway
