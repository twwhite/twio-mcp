# twio-mcp
Tim's MCP servers for personal use

Each command has a brief definition of:

> command:
> ( name,  short description,  longer mcp-style docstring )

The model calls the _List_ command on every chat start. The return is a list of text like:

> commands:
> - time - get the current time _(short descr.)_
> - calculate - do math operations using python _(short descr.)_

Then, the model can choose when to call _"help [command]"_ to receive the full docstring style help information to call the tool effectively.

This has been a huge QOL improvement for me because it let's the model choose to hot-swap MCP tools without taking up as much context.
