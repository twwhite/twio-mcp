from typing import TypedDict


class CommandMeta(TypedDict):
    short: str
    detail: str
    kwargs: dict[str, str]
    example: str
