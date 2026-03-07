"""AI4One CLI - Command line interface for AI development utilities."""

import os
import sys
import subprocess
from pathlib import Path

import typer
from rich import print
from rich.console import Console
from rich.table import Table

from ..tools.visual_call_graph import ProjectAnalyzer

app = typer.Typer(no_args_is_help=True, help="AI4One - AI Development Toolkit")
mcp_app = typer.Typer(
    help="MCP (Model Context Protocol) server management", no_args_is_help=True
)
app.add_typer(mcp_app, name="mcp")

console = Console()

# MCP Server configurations
MCP_SERVERS = {
    "file": {
        "description": "File system operations (read, write, list, etc.)",
        "tools": ["list_work_dir", "mkdir", "get_system_info", "read_file",
                  "open_dir", "write_file", "delete_file", "run_command"],
        "default_port": 50001,
    },
    "todo": {
        "description": "Todo list management with UUID support",
        "tools": ["create_todo_list", "list_todo_lists", "get_todo_list",
                  "delete_todo_list", "rename_todo_list", "add_task",
                  "list_tasks", "set_task_status", "update_task",
                  "remove_task", "clear_completed", "search_tasks"],
        "default_port": 50002,
    },
    "world": {
        "description": "World info: current time, system environment",
        "tools": ["get_base_world_info"],
        "default_port": 50003,
    },
}


@app.callback()
def callback():
    """AI4One - A modular AI development toolkit."""


@app.command(name="gpu")
def nvidia_info(
    refresh: bool = typer.Option(False, "--refresh", "-r", help="Enable real-time refresh"),
    interval: float = typer.Option(2.0, "--interval", "-i", help="Refresh interval in seconds"),
):
    """Check GPU info, PyTorch version, Python version and executable path.

    Use --refresh or -r to enable real-time monitoring.
    """
    def check_nvidia_smi():
        try:
            subprocess.run(
                ["nvidia-smi", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def clear_screen():
        os.system("cls" if os.name == "nt" else "clear")

    pytorch_info = ""
    try:
        import torch
        pytorch_info = f"PyTorch Version: {torch.__version__}\nCUDA available: {torch.cuda.is_available()}"
    except ImportError:
        pytorch_info = "[bold red]PyTorch is not installed.[/bold red]"

    python_info = f"Python Version: {sys.version}\nPython Executable: {sys.executable}"

    def show_gpu_info():
        result = subprocess.run(
            ["nvidia-smi"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode == 0:
            lines = result.stdout.splitlines()
            content = "\r\n".join(lines[1:12])
            first_line = lines[0]
            width = len(lines[3]) if len(lines) > 3 else 50
            print("INFO".center(width, "="))
            print(f"Current Time: [green]{first_line}[/green]")
            print(content)
        else:
            print("NVIDIA-SMI Error Output:")
            print(result.stderr)

        if refresh:
            print(f"\n[italic cyan]Refreshing every {interval}s. Press Ctrl+C to exit.[/italic cyan]")

    if refresh:
        if not check_nvidia_smi():
            print("[bold red]Error: nvidia-smi not found. Install NVIDIA drivers.[/bold red]")
            return
        try:
            while True:
                clear_screen()
                show_gpu_info()
                import time
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n[bold green]GPU monitoring stopped.[/bold green]")
    else:
        if check_nvidia_smi():
            show_gpu_info()
        else:
            print("[bold red]Error: nvidia-smi not found. Install NVIDIA drivers.[/bold red]")
        print("\n" + pytorch_info)
        print("\n" + python_info)


@app.command()
def callgraph(
    path: str = typer.Argument(..., help="Path to Python file or project directory"),
    output: str = typer.Option("call_graph.dot", "--output", "-o", help="Output .dot file path"),
):
    """Generate a focused intra-project function call graph.

    Creates a .dot file that can be rendered with Graphviz: dot -Tpng call_graph.dot -o graph.png
    """
    target_path = os.path.abspath(path)
    print(f"Analyzing: [bold cyan]{target_path}[/bold cyan]")

    if not os.path.exists(target_path):
        print(f"[bold red]Error:[/bold red] Path '{target_path}' does not exist.")
        raise typer.Exit(code=1)

    if os.path.isfile(target_path):
        print("Mode: Single File Analysis")
        project_root = os.path.dirname(target_path)
        files_to_analyze = [target_path]
    else:
        print("Mode: Project Directory Analysis")
        project_root = target_path
        files_to_analyze = None

    try:
        analyzer = ProjectAnalyzer(project_root)
        analyzer.analyze(files_to_analyze=files_to_analyze)
        analyzer.generate_dot_file(output)
        print(f"\n[bold green]Done! Render with:[/bold green] dot -Tpng {output} -o {os.path.splitext(output)[0]}.png")
    except Exception as e:
        print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@mcp_app.command("list")
def list_servers():
    """List available MCP servers."""
    import ai4one.mcp
    mcp_dir = Path(ai4one.mcp.__file__).parent

    table = Table(title="Available MCP Servers")
    table.add_column("Server", style="cyan")
    table.add_column("Description", style="green")
    table.add_column("Port", style="yellow")
    table.add_column("Status", style="dim")

    for name, config in MCP_SERVERS.items():
        script = mcp_dir / f"{name if name != 'file' else 'local_file'}.py"
        status = "✅" if script.exists() else "❌"
        table.add_row(name, config["description"], str(config["default_port"]), status)

    console.print(table)


@mcp_app.command("start")
def start_server(
    server: str = typer.Argument(..., help=f"Server name: {', '.join(MCP_SERVERS.keys())}"),
    port: int = typer.Option(None, "--port", "-p", help="Port for HTTP transports"),
    transport: str = typer.Option("stdio", "--transport", "-t",
                                   help="Transport: stdio, sse, mcp, streamable-http"),
):
    """Start an MCP server.

    Examples:
        ai4one mcp start file
        ai4one mcp start todo -t sse -p 8080
        ai4one mcp start world -t mcp
    """
    if server not in MCP_SERVERS:
        console.print(f"[red]Error: Unknown server '{server}'. Available: {', '.join(MCP_SERVERS.keys())}[/red]")
        raise typer.Exit(code=1)

    import ai4one.mcp
    mcp_dir = Path(ai4one.mcp.__file__).parent
    config = MCP_SERVERS[server]

    # Map server names to script filenames
    script_map = {"file": "local_file", "todo": "todo", "world": "world_info"}
    script_path = mcp_dir / f"{script_map[server]}.py"

    if not script_path.exists():
        console.print(f"[red]Error: Script not found: {script_path}[/red]")
        raise typer.Exit(code=1)

    console.print(f"Starting [cyan]{server}[/cyan] server...")
    console.print(f"Transport: {transport}")

    if transport in ["sse", "mcp", "streamable-http"]:
        if not port:
            port = config["default_port"]
        console.print(f"Port: {port}")
        console.print(f"[green]URL: http://localhost:{port}/{transport}[/green]")

    # Import and run the server
    try:
        if server == "todo":
            from ai4one.mcp.todo import run_server
        elif server == "file":
            from ai4one.mcp.local_file import run_server
        elif server == "world":
            from ai4one.mcp.world_info import run_server

        original_argv = sys.argv.copy()
        sys.argv = [script_path.name, "--transport", transport]
        if transport in ["sse", "mcp", "streamable-http"] and port:
            sys.argv.extend(["--port", str(port)])

        print("Press Ctrl+C to stop")
        run_server()
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)


@mcp_app.command("info")
def server_info(server: str = typer.Argument(..., help=f"Server name: {', '.join(MCP_SERVERS.keys())}")):
    """Show detailed information about an MCP server."""
    if server not in MCP_SERVERS:
        console.print(f"[red]Error: Unknown server '{server}'. Available: {', '.join(MCP_SERVERS.keys())}[/red]")
        raise typer.Exit(code=1)

    import ai4one.mcp
    mcp_dir = Path(ai4one.mcp.__file__).parent
    config = MCP_SERVERS[server]
    script_map = {"file": "local_file", "todo": "todo", "world": "world_info"}
    script_path = mcp_dir / f"{script_map[server]}.py"

    # Info table
    table = Table(title=f"MCP Server: {server}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Name", server)
    table.add_row("Description", config["description"])
    table.add_row("Script", str(script_path))
    table.add_row("Default Port", str(config["default_port"]))
    table.add_row("Status", "✅ Available" if script_path.exists() else "❌ Not Found")
    table.add_row("Tools", str(len(config["tools"])))
    console.print(table)

    # Tools table
    tools_table = Table(title="Tools")
    tools_table.add_column("Name", style="yellow")
    for tool in config["tools"]:
        tools_table.add_row(tool)
    console.print(tools_table)

    # Usage
    console.print(f"\n[bold]Usage:[/bold] ai4one mcp start {server}")


if __name__ == "__main__":
    app()
