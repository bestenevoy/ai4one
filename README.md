# AI4One

**AI Agent Toolkit with MCP servers and CLI tools.**

AI4One provides essential utilities for building AI-powered applications:
- **MCP Servers**: Ready-to-use tools for AI agents
- **CLI Commands**: Direct access for humans
- **Shared Utilities**: Time, file, config handling

## Installation

```bash
pip install ai4one
```

Requires Python 3.10+.

## MCP Servers

MCP (Model Context Protocol) servers provide tools for AI agents:

```bash
# List available servers
ai4one mcp list

# Start a server
ai4one mcp start todo
ai4one mcp start web -t sse -p 8080
ai4one mcp start file --transport mcp

# Show server info
ai4one mcp info web
```

| Server | Description | Tools |
|--------|-------------|-------|
| `file` | File system operations | read, write, list, mkdir, run_command |
| `todo` | Task management | CRUD operations with UUID lists |
| `world` | Environment info | current time, system info |
| `web` | Web search & fetch | DuckDuckGo search, page extraction, URL utils |

### Web MCP Tools

```python
# Web search (no API key needed)
web_search("Python async tutorial", max_results=5)

# News search
web_search_news("AI news", max_results=5)

# Fetch page content
web_fetch("https://example.com/article", max_length=10000)

# Extract links
web_fetch_links("https://example.com", max_links=50)

# URL utilities
url_info("https://example.com/path?query=1")
url_encode("hello world")  # -> "hello%20world"
url_decode("hello%20world")  # -> "hello world"
```

## CLI Commands

```bash
# GPU info with PyTorch status
ai4one gpu
ai4one gpu -r -i 5  # refresh every 5 seconds

# Generate call graph
ai4one callgraph ./src -o graph.dot
```

## Configuration System

Type-safe configuration with CLI parsing and file serialization:

```python
from ai4one.config import BaseConfig

class ModelConfig(BaseConfig):
    name: str = "gpt-4"
    temperature: float = 0.7

class TrainConfig(BaseConfig):
    model: ModelConfig
    epochs: int = 10
    lr: float = 0.001

# Parse from command line: python train.py --epochs 20 --model.name gpt-4o
config = TrainConfig.argument_parser()
```

## Time Utilities

```python
from ai4one.utils import now_iso, parse_datetime, humanize_delta

# Current time
now_iso()  # "2024-01-15T10:30:00.123Z"

# Parse flexible datetime
parse_datetime("tomorrow")
parse_datetime("+2h")  # 2 hours from now

# Human-friendly durations
humanize_delta(3661)  # "1h1m1s"
```

## Plotting Fonts

Auto-configure matplotlib for Chinese + English:

```python
from ai4one.tools.plt import setup_fonts
setup_fonts(["Times New Roman", "SimHei"])
```

## Project Structure

```
ai4one/
├── config.py          # Configuration with CLI parsing
├── cli/               # CLI commands
│   └── cli.py         # ai4one gpu, mcp, callgraph
├── mcp/               # MCP servers
│   ├── file.py        # File operations
│   ├── todo.py        # Task management
│   ├── world.py       # Time/environment
│   └── web.py         # Web search & fetch
├── tools/             # PyTorch, plotting, call graph
├── agent/             # Agent framework
└── utils/             # Time, file utilities
```

## Development

```bash
git clone https://github.com/bestenevoy/ai4one.git
cd ai4one
uv pip install -e ".[dev]"

# Run tests
uv run pytest

# Validate MCP servers
python examples/mcp_validate.py
```

## License

MIT
