# AI4One Project Memory

## Project Overview

**AI4One** is a lightweight, modular Python toolkit for building AI-powered applications.

- **Version**: 0.3.2
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
│   └── cli.py         # ai4one gpu, ai4one mcp, ai4one callgraph
│
├── mcp/               # MCP servers for AI agents
│   ├── todo.py        # Task management (port 50002)
│   ├── local_file.py  # File operations (port 50001)
│   └── world_info.py  # Time/environment info (port 50003)
│
├── tools/             # Utility modules
│   ├── plt.py         # Matplotlib font configuration
│   ├── pytorch.py     # Device selection, seed, clipper
│   └── visual_call_graph.py  # Function call graph generator
│
├── agent/             # Agent framework
│   └── __init__.py    # Agent base class with attachment registry
│
└── utils/             # Helper utilities
    ├── file.py        # JSON/text file operations
    ├── func.py        # Function introspection
    └── chrono.py      # Time utilities (now_iso, parse_datetime, etc.)
```

## Key Patterns

### Configuration
- `BaseConfig` supports nested configs, CLI parsing via `argument_parser()`
- Serialization: JSON, YAML, TOML via `to_file()` / `from_file()`

### MCP Servers
- Use FastMCP from `mcp.server.fastmcp`
- Transport: stdio, sse, mcp, streamable-http
- CLI: `ai4one mcp start <server> -t <transport> -p <port>`

### Utils/Chrono
- All functions return timezone-aware datetime or ISO strings
- `parse_datetime()` handles: "now", "today", "tomorrow", "+2h", ISO format, timestamps

## Scripts

- `scripts/tag.py` - Auto-create git tag from pyproject.toml version

## Development

```bash
uv pip install -e ".[dev]"  # Install with dev deps
uv run pytest               # Run tests
uv build                    # Build package
```
