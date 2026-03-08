# AI4One Project Memory

## Project Overview

**AI4One** - AI Agent Toolkit with MCP servers and CLI tools.

- **Version**: 0.4.0
- **Python**: 3.10+
- **Package Manager**: uv

## Architecture

```
src/ai4one/
├── __init__.py        # Package entry: BaseConfig, Notifier
├── config.py          # Configuration system with CLI parsing
├── notifier.py        # Email notification (QQEmailNotifier)
│
├── cli/               # CLI commands
│   └── cli.py         # ai4one gpu, mcp, callgraph
│
├── mcp/               # MCP servers for AI agents
│   ├── local_file.py  # File operations (port 50001)
│   ├── todo.py        # Task management (port 50002)
│   ├── world_info.py  # Time/environment (port 50003)
│   └── web.py         # Web search/fetch (port 50004)
│
├── tools/             # Utility modules
│   ├── plt.py         # Matplotlib font configuration
│   ├── pytorch.py     # Device selection, seed, clipper
│   └── visual_call_graph.py  # Function call graph
│
├── agent/             # Agent framework
│   └── __init__.py    # Agent base class + attachment registry
│
└── utils/             # Helper utilities
    ├── file.py        # JSON/text file operations
    ├── func.py        # Function introspection
    └── chrono.py      # Time utilities
```

## MCP Servers

| Server | Port | Tools |
|--------|------|-------|
| file | 50001 | list_work_dir, mkdir, get_system_info, read_file, open_dir, write_file, delete_file, run_command |
| todo | 50002 | create_todo_list, list_todo_lists, get_todo_list, delete_todo_list, rename_todo_list, add_task, list_tasks, set_task_status, update_task, remove_task, clear_completed, search_tasks |
| world | 50003 | get_base_world_info |
| web | 50004 | web_search, web_search_news, web_fetch, web_fetch_links, url_info, url_encode, url_decode |

## Key Patterns

### MCP Server Template
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ai4one_xxx_server")

@mcp.tool()
def tool_name(arg: str) -> dict:
    """Tool description."""
    return {"result": "value"}

def run_server():
    import anyio
    args = parse_args()
    mcp.settings.port = args.port
    match args.transport:
        case "stdio": anyio.run(mcp.run_stdio_async)
        case "sse": anyio.run(lambda: mcp.run_sse_async(None))
        case "mcp": anyio.run(mcp.run_streamable_http_async)

if __name__ == "__main__":
    run_server()
```

### Configuration
- `BaseConfig` supports nested configs, CLI parsing via `argument_parser()`
- Serialization: JSON, YAML, TOML via `to_file()` / `from_file()`

### Utils/Chrono
- All functions return timezone-aware datetime or ISO strings
- `parse_datetime()` handles: "now", "today", "tomorrow", "+2h", ISO format, timestamps

## Dependencies

Core:
- mcp[cli] - MCP server framework
- typer - CLI framework
- requests - HTTP client
- simple-parsing - Config parsing

Web MCP:
- beautifulsoup4 - HTML parsing
- duckduckgo-search - Web search (no API key)
- lxml - XML/HTML parser

## CLI Commands

```bash
ai4one gpu              # GPU info
ai4one gpu -r -i 5      # Real-time refresh
ai4one callgraph ./src  # Generate call graph
ai4one mcp list         # List MCP servers
ai4one mcp start web    # Start web server
ai4one mcp info todo    # Server details
```

## Development

```bash
uv pip install -e ".[dev]"  # Install with dev deps
uv run pytest               # Run tests
uv build                    # Build package
python scripts/tag.py       # Create git tag from version
```
