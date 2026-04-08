from typing import Callable

from twio_mcp.commands import CommandMeta, cmd_get_time, cmd_help, cmd_list

COMMANDS: dict[str, CommandMeta] = {
    "list": {
        "short": "Show all available commands",
        "detail": "Lists every registered command with a one-line description. No kwargs. Call this first to orient yourself, then call help <command> for full usage details.",
        "kwargs": {},
        "example": '{"command": "list"}',
    },
    "help": {
        "short": "Show detailed usage for a specific command",
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
}

REGISTRY: dict[str, Callable] = {
    "list": cmd_list,
    "help": cmd_help,
    "get_time": cmd_get_time,
}
