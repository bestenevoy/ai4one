# AI4One

**A lightweight, modular toolkit for building AI-powered applications.**

AI4One provides essential utilities for AI development: configuration management, MCP servers for agent tools, CLI commands, and time/file utilities.

## Installation

```bash
pip install ai4one
```

Requires Python 3.10+.

## Features

### Configuration System

Type-safe configuration with CLI parsing, file serialization (JSON/YAML/TOML), and nested config support.

```python
from ai4one.config import BaseConfig
from ai4one.utils import field

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

### MCP Servers

Built-in MCP (Model Context Protocol) servers for AI agents:

```bash
# List available servers
ai4one mcp list

# Start a server
ai4one mcp start todo
ai4one mcp start file -t sse -p 8080
ai4one mcp start world

# Server info
ai4one mcp info todo
```

| Server | Description | Tools |
|--------|-------------|-------|
| `file` | File system operations | read, write, list, mkdir, run_command |
| `todo` | Task management | CRUD operations with UUID lists |
| `world` | Environment info | current time, system info |

### CLI Commands

```bash
# GPU info with PyTorch status
ai4one gpu
ai4one gpu -r -i 5  # refresh every 5 seconds

# Generate call graph
ai4one callgraph ./src -o graph.dot
```

### Time Utilities

```python
from ai4one.utils import now_iso, parse_datetime, humanize_delta, sleep_until

# Current time
now_iso()  # "2024-01-15T10:30:00.123Z"

# Parse flexible datetime strings
parse_datetime("tomorrow")
parse_datetime("+2h")  # 2 hours from now
parse_datetime("2024-01-15 10:00")

# Human-friendly durations
humanize_delta(3661)  # "1h1m1s"

# Sleep until a specific time
sleep_until("tomorrow 09:00")
```

### Plotting Fonts

Auto-configure matplotlib for Chinese + English fonts:

```python
from ai4one.tools.plt import setup_fonts

setup_fonts(["Times New Roman", "SimHei"])
```

## Project Structure

```
ai4one/
├── config.py          # Configuration base class
├── cli/               # CLI commands (gpu, mcp, callgraph)
├── mcp/               # MCP servers (file, todo, world)
├── tools/             # PyTorch utils, plotting, call graph
├── agent/             # Agent framework base classes
├── utils/             # Time, file, and helper utilities
└── notifier.py        # Email notification
```

## Development

```bash
# Clone and install dev dependencies
git clone https://github.com/bestenevoy/ai4one.git
cd ai4one
uv pip install -e ".[dev]"

# Run tests
uv run pytest
```

## License

MIT
