from __future__ import annotations

import json
from typing import Any

import httpx


def _pretty_schema(schema: dict) -> list[str]:
    """Convert a JSON Schema properties dict to readable lines."""
    lines = []
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    if not properties:
        return ["    kwargs: none"]
    for prop_name, prop_schema in properties.items():
        prop_type = prop_schema.get("type", "any")
        prop_desc = prop_schema.get("description", "")
        req = "required" if prop_name in required else "optional"
        lines.append(f"    {prop_name:20s} {prop_type}, {req} — {prop_desc}")
    return lines


class ExternalMCPGateway:
    def __init__(self, name: str, url: str, transport: str = "http"):
        self.name = name
        self.url = url.rstrip("/")
        self.transport = transport
        self._tools_cache: dict[str, Any] | None = None

    def _rpc(self, method: str, params: dict = {}) -> Any:
        """Send a JSON-RPC 2.0 request to the remote MCP server."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params,
        }
        if self.transport == "sse":
            return self._rpc_sse(payload)
        return self._rpc_http(payload)

    def _get_session_id(self, client: httpx.Client) -> str:
        """Initialize a session and return the session ID."""
        payload = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "twio-mcp-hub", "version": "0.1.0"},
            },
        }
        response = client.post(
            f"{self.url}/mcp",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
        )
        response.raise_for_status()
        session_id = response.headers.get("mcp-session-id")
        if not session_id:
            raise RuntimeError("Server did not return a session ID on initialize")
        return session_id

    def _rpc_http(self, payload: dict) -> Any:
        try:
            with httpx.Client(timeout=30.0) as client:
                session_id = self._get_session_id(client)
                response = client.post(
                    f"{self.url}/mcp",
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json, text/event-stream",
                        "mcp-session-id": session_id,
                    },
                )
                response.raise_for_status()
                content_type = response.headers.get("content-type", "")

                # Server may respond with SSE even on HTTP transport
                if "text/event-stream" in content_type:
                    for line in response.text.splitlines():
                        if line.startswith("data:"):
                            raw = line[len("data:") :].strip()
                            if not raw or raw == "[DONE]":
                                continue
                            try:
                                parsed = json.loads(raw)
                                if "result" in parsed:
                                    return parsed["result"]
                                if "error" in parsed:
                                    raise RuntimeError(
                                        parsed["error"].get(
                                            "message", "Unknown RPC error"
                                        )
                                    )
                            except json.JSONDecodeError:
                                continue
                    return None

                # Standard JSON response
                data = response.json()
                if "error" in data:
                    raise RuntimeError(
                        data["error"].get("message", "Unknown RPC error")
                    )
                return data.get("result")

        except httpx.HTTPError as e:
            raise RuntimeError(f"HTTP error contacting {self.name}: {e}")

    def _rpc_sse(self, payload: dict) -> Any:
        """
        For SSE transport: POST the JSON-RPC message and collect the streamed response.
        SSE MCP servers emit newline-delimited 'data:' events.
        """
        try:
            with httpx.Client(timeout=30.0) as client:
                with client.stream(
                    "POST",
                    f"{self.url}/sse",
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "text/event-stream",
                    },
                ) as response:
                    response.raise_for_status()
                    result_data = None
                    for line in response.iter_lines():
                        if line.startswith("data:"):
                            raw = line[len("data:") :].strip()
                            try:
                                parsed = json.loads(raw)
                                if "result" in parsed:
                                    result_data = parsed["result"]
                                    break
                                if "error" in parsed:
                                    raise RuntimeError(
                                        parsed["error"].get(
                                            "message", "Unknown RPC error"
                                        )
                                    )
                            except json.JSONDecodeError:
                                continue
                    return result_data
        except httpx.HTTPError as e:
            raise RuntimeError(f"SSE error contacting {self.name}: {e}")

    def _get_tools(self) -> dict[str, Any]:
        """Fetch and cache the tools list from the remote server."""
        if self._tools_cache is None:
            result = self._rpc("tools/list")
            tools = result.get("tools", []) if result else []
            self._tools_cache = {tool["name"]: tool for tool in tools}
        return self._tools_cache

    def _action_list(self) -> str:
        try:
            tools = self._get_tools()
        except RuntimeError as e:
            return f"Error fetching tools from {self.name}: {e}"
        if not tools:
            return f"No tools found on {self.name}."
        lines = [f"Available tools on ext_{self.name}:\n"]
        for tool_name, tool in tools.items():
            desc = tool.get("description", "No description.").splitlines()[0]
            lines.append(f"  {tool_name:24s} {desc}")
        return "\n".join(lines)

    def _action_help(self, tool: str | None = None) -> str:
        if not tool:
            return (
                f"ext_{self.name}: External MCP gateway\n\n"
                f"  actions:\n"
                f"    {'list':20s} Show all tools on this server\n"
                f"    {'help':20s} Show usage for a specific tool. kwargs: tool (str)\n"
                f"    {'invoke':20s} Call a tool. kwargs: tool (str), kwargs (dict)\n\n"
                f"  Call with action='list' to see available tools."
            )
        try:
            tools = self._get_tools()
        except RuntimeError as e:
            return f"Error fetching tools from {self.name}: {e}"
        if tool not in tools:
            return f"Unknown tool '{tool}' on {self.name}. Call action='list' to see available tools."
        t = tools[tool]
        desc = t.get("description", "No description.")
        input_schema = t.get("inputSchema", {})
        lines = [
            f"{tool}",
            f"  {desc}",
            "",
            "  kwargs:",
        ]
        lines += _pretty_schema(input_schema)
        lines += [
            "",
            "  example:",
            f'    {{"command": "ext_{self.name}", "kwargs": {{"action": "invoke", "tool": "{tool}", "kwargs": {{...}}}}}}',
        ]
        return "\n".join(lines)

    def _action_invoke(self, tool: str | None = None, kwargs: dict = {}) -> str:
        if not tool:
            return "invoke requires a 'tool' kwarg. Call action='list' to see available tools."
        try:
            result = self._rpc("tools/call", {"name": tool, "arguments": kwargs})
        except RuntimeError as e:
            return f"Error invoking '{tool}' on {self.name}: {e}"
        if result is None:
            return "Tool returned no result."
        # MCP tools/call returns a 'content' list of typed blocks
        content = result.get("content", [])
        parts = []
        for block in content:
            if block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "\n".join(parts) if parts else str(result)

    def __call__(
        self, action: str = "list", tool: str | None = None, kwargs: dict = {}, **_
    ) -> str:
        if action == "list":
            return self._action_list()
        if action == "help":
            return self._action_help(tool)
        if action == "invoke":
            return self._action_invoke(tool, kwargs)
        return f"Unknown action '{action}'. Available actions: list, help, invoke."
