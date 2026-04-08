from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from twio_mcp.registry import COMMANDS


def cmd_list(**kwargs) -> str:
    from twio_mcp.registry import COMMANDS

    lines = ["Available commands:\n"]
    for name, meta in COMMANDS.items():
        lines.append(f"  {name:22s} {meta['short']}")
    return "\n".join(lines)


def cmd_help(command: str | None = None, **kwargs) -> str:
    from twio_mcp.registry import COMMANDS

    if not command:
        return 'Usage: help requires a command name. Example: {"command": "help", "kwargs": {"command": "list"}}'
    if command not in COMMANDS:
        return f"Unknown command '{command}'. Call list to see available commands."

    meta = COMMANDS[command]
    lines = [
        f"{command}",
        f"  {meta['detail']}",
        "",
    ]

    if meta["kwargs"]:
        lines.append("  kwargs:")
        for arg, desc in meta["kwargs"].items():
            lines.append(f"    {arg:20s} — {desc}")
    else:
        lines.append("  kwargs: none")

    lines += ["", "  example:", f"    {meta['example']}"]
    return "\n".join(lines)
