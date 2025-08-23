import os
import sys
import time
import threading
import signal
from pathlib import Path

import typer
import subprocess
from rich import print
from rich.console import Console
from rich.table import Table

from ..tools.visual_call_graph import ProjectAnalyzer


app = typer.Typer(no_args_is_help=True)
mcp_app = typer.Typer(help="MCP (Model Context Protocol) server management commands", no_args_is_help=True)
app.add_typer(mcp_app, name="mcp")

console = Console()


@app.callback()
def callback():
    """
    Awesome AI CLI tool under development.
    """
    pass


@app.command(name="gpu")
def nvidia_info(
    refresh: bool = typer.Option(
        False, "--refresh", "-r", help="Enable real-time refresh"
    ),
    interval: float = typer.Option(
        2.0, "--interval", "-i", help="Refresh interval in seconds"
    ),
):
    """
    Check GPU driver information, PyTorch version, Python version, and Python executable path.

    Use --refresh or -r to enable real-time monitoring.
    Use --interval or -i to set the refresh interval (default: 2 seconds).
    """

    # 检查 nvidia-smi 是否存在
    def check_nvidia_smi():
        try:
            subprocess.run(
                ["nvidia-smi", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,  # 如果命令返回非零状态码会抛出异常
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    # 清屏函数，跨平台支持
    def clear_screen():
        os.system("cls" if os.name == "nt" else "clear")

    pytorch_info = ""
    try:
        import torch
        pytorch_info = f"PyTorch Version: {torch.__version__}\nCuda is available: {torch.cuda.is_available()}"
    except ImportError:
        pytorch_info = "[bold red]PyTorch is not installed.[/bold red]"

    # 获取 Python 版本和执行路径
    python_info = (
        f"Python Version: {sys.version}\nPython Executable Path: {sys.executable}"
    )

    # 显示 NVIDIA-SMI 信息的函数
    def show_gpu_info():
        result = subprocess.run(
            ["nvidia-smi"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # 返回文本（字符串）而不是字节
        )
        output = result.stdout
        error_output = result.stderr
        if result.returncode == 0:
            content = "\r\n".join(output.splitlines()[1:12])
            first_line = output.splitlines()[0]
            lenght = len(output.splitlines()[3])
            print("INFO".center(lenght, "="))
            print(f"Current Time: [green]{first_line}[/green]")
            print(content)
        else:
            print("NVIDIA-SMI Error Output:")
            print(error_output)

        if refresh:
            print(
                f"\n[italic cyan]Refreshing GPU info every {interval} seconds. Press Ctrl+C to exit.[/italic cyan]"
            )
    NOT_NS = "[bold red]Error: nvidia-smi not found. Please ensure NVIDIA drivers are installed.[/bold red]"
    # 是否需要实时刷新
    if refresh:
        try:
            if not check_nvidia_smi():
                print(NOT_NS)
                return
            while True:
                clear_screen()
                show_gpu_info()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n[bold green]GPU monitoring stopped.[/bold green]")
    else:
        if not check_nvidia_smi():
            print(NOT_NS)
        else:
            show_gpu_info()

        print("\n" + pytorch_info)
        print("\n" + python_info)


@app.command()
def test(name: str = typer.Option(None, "--name", "-n", help="this is a test param")):
    """
    this is test
    """
    print("It looks like it's correct.")


@app.command()
def callgraph(
    path: str = typer.Argument(
        ..., help="Path to the Python file or project directory to analyze."
    ),
    output: str = typer.Option(
        "call_graph.dot", "--output", "-o", help="Output path for the .dot file."
    ),
):
    """
    Generates a focused, intra-project function call graph.

    Analyzes a single Python file or an entire project directory and
    creates a .dot file representing the internal call structure.
    """
    target_path = os.path.abspath(path)
    print(f"🔍 Analyzing target: [bold cyan]{target_path}[/bold cyan]")

    project_root = None
    files_to_analyze = None

    if not os.path.exists(target_path):
        print(
            f"[bold red]Error:[/bold red] The provided path '{target_path}' does not exist."
        )
        raise typer.Exit(code=1)

    if os.path.isfile(target_path):
        # 如果是文件，项目根目录是其所在目录，分析列表只包含它自己
        print("Mode: Single File Analysis")
        project_root = os.path.dirname(target_path)
        files_to_analyze = [target_path]
    elif os.path.isdir(target_path):
        # 如果是目录，项目根目录就是它自己，分析列表由脚本自动发现
        print("Mode: Project Directory Analysis")
        project_root = target_path
        # files_to_analyze 保持为 None, 让 analyze 方法自己去发现
        files_to_analyze = None

    try:
        # 实例化并运行分析器
        analyzer = ProjectAnalyzer(project_root)
        analyzer.analyze(files_to_analyze=files_to_analyze)
        analyzer.generate_dot_file(output)  # 调用新的生成方法
        print(
            "\n[bold green]✨ Analysis complete! You can now render the DOT file with Graphviz:[/bold green]"
        )
        print(f"dot -Tpng {output} -o {os.path.splitext(output)[0]}.png")
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        import traceback

        traceback.print_exc()  # 打印详细的错误堆栈，便于调试
        raise typer.Exit(code=1)


# MCP Server Management Commands
@mcp_app.command("list")
def list_servers():
    """
    List available MCP servers.
    """
    table = Table(title="Available MCP Servers")
    table.add_column("Server", style="cyan")
    table.add_column("Description", style="green")
    table.add_column("Script Path", style="yellow")
    
    # Get MCP scripts directory using package path
    import ai4one.mcp
    mcp_dir = Path(ai4one.mcp.__file__).parent
    
    servers = [
        {
            "name": "file",
            "description": "File system operations (read, write, list, etc.)",
            "script": mcp_dir / "local_file.py"
        },
        {
            "name": "todo", 
            "description": "Todo list management with UUID support",
            "script": mcp_dir / "todo.py"
        }
    ]
    
    for server in servers:
        status = "✅" if server["script"].exists() else "❌"
        table.add_row(
            f"{status} {server['name']}",
            server["description"],
            str(server["script"])
        )
    
    console.print(table)


@mcp_app.command("start")
def start_server(
    server: str = typer.Argument(..., help="Server name: file or todo"),
    port: int = typer.Option(None, "--port", "-p", help="Port for HTTP-based transports (optional)"),
    transport: str = typer.Option("stdio", "--transport", "-t", help="Transport type: stdio, sse, mcp, or streamable-http")
):
    """
    Start a specific MCP server.
    
    Examples:
    - ai4one mcp start file
    - ai4one mcp start todo --transport sse --port 8080
    - ai4one mcp start todo --transport mcp --port 50002
    """
    # Get MCP scripts directory using package path
    import ai4one.mcp
    mcp_dir = Path(ai4one.mcp.__file__).parent
    
    server_configs = {
        "file": {
            "script": mcp_dir / "local_file.py",
            "description": "File Service MCP Server"
        },
        "todo": {
            "script": mcp_dir / "todo.py",
            "description": "Todo Service MCP Server"
        }
    }
    
    if server not in server_configs:
        console.print(f"[red]Error: Unknown server '{server}'. Available: {', '.join(server_configs.keys())}[/red]")
        raise typer.Exit(code=1)
    
    config = server_configs[server]
    script_path = config["script"]
    
    console.print(f"[green]🚀 Starting {config['description']}...[/green]")
    console.print(f"[cyan]Transport: {transport}[/cyan]")
    
    # Set default port if not provided for HTTP-based transports
    if transport in ["sse", "mcp", "streamable-http"] and not port:
        default_port = 50001 if server == "file" else 50002
        port = default_port
        console.print(f"[cyan]Using default port: {port}[/cyan]")
    elif port:
        console.print(f"[cyan]Port: {port}[/cyan]")
    
    try:
        # Try to import and run the server directly
        if server == "todo":
            from ai4one.mcp.todo import run_server as todo_run_server
            
            # Prepare arguments for the server
            original_argv = sys.argv.copy()
            sys.argv = ["todo.py", "--transport", transport]
            
            if transport in ["sse", "mcp", "streamable-http"] and port:
                sys.argv.extend(["--port", str(port)])
            
            if transport in ["sse", "mcp", "streamable-http"]:
                console.print(f"[green]Server will be available at: http://localhost:{port}/{transport}[/green]")
            
            console.print(f"[yellow]Press Ctrl+C to stop the server[/yellow]")
            
            try:
                todo_run_server()
            finally:
                sys.argv = original_argv
                
        elif server == "file":
            from ai4one.mcp.local_file import run_server as file_run_server
            
            # Prepare arguments for the server
            original_argv = sys.argv.copy()
            sys.argv = ["local_file.py", "--transport", transport]
            
            if transport in ["sse", "mcp", "streamable-http"] and port:
                sys.argv.extend(["--port", str(port)])
            
            if transport in ["sse", "mcp", "streamable-http"]:
                console.print(f"[green]Server will be available at: http://localhost:{port}/{transport}[/green]")
            
            console.print(f"[yellow]Press Ctrl+C to stop the server[/yellow]")
            
            try:
                file_run_server()
            finally:
                sys.argv = original_argv
                
    except ImportError:
        # Fallback to script execution if import fails
        if not script_path.exists():
            console.print(f"[red]Error: Script not found: {script_path}[/red]")
            raise typer.Exit(code=1)
        
        # Build command
        cmd = [sys.executable, str(script_path)]
        
        # Add transport argument
        cmd.extend(["--transport", transport])
        
        # Add port argument for HTTP-based transports
        if transport in ["sse", "mcp", "streamable-http"] and port:
            cmd.extend(["--port", str(port)])
        
        console.print(f"[green]Running command: {' '.join(cmd)}[/green]")
        
        if transport in ["sse", "mcp", "streamable-http"]:
            console.print(f"[green]Server will be available at: http://localhost:{port}/{transport}[/green]")
        
        console.print(f"[yellow]Press Ctrl+C to stop the server[/yellow]")
        
        # Run the server
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        console.print(f"\n[yellow]Server stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error starting server: {e}[/red]")
        raise typer.Exit(code=1)


@mcp_app.command("validate")
def validate_servers():
    """
    Validate both MCP servers by running the validation script.
    """
    project_root = Path(__file__).parent.parent.parent.parent
    validate_script = project_root / "examples" / "mcp_validate.py"
    
    if not validate_script.exists():
        console.print(f"[red]Error: Validation script not found: {validate_script}[/red]")
        raise typer.Exit(code=1)
    
    console.print(f"[green]🔍 Running MCP server validation...[/green]")
    
    try:
        result = subprocess.run(
            [sys.executable, str(validate_script)],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            console.print(result.stdout)
            console.print(f"[green]✅ All MCP servers validated successfully![/green]")
        else:
            console.print(f"[red]❌ Validation failed:[/red]")
            console.print(result.stdout)
            console.print(result.stderr)
            raise typer.Exit(code=1)
            
    except Exception as e:
        console.print(f"[red]Error running validation: {e}[/red]")
        raise typer.Exit(code=1)


@mcp_app.command("info")
def server_info(
    server: str = typer.Argument(..., help="Server name: file or todo")
):
    """
    Show detailed information about a specific MCP server.
    """
    # Get MCP scripts directory using package path
    import ai4one.mcp
    mcp_dir = Path(ai4one.mcp.__file__).parent
    
    server_configs = {
        "file": {
            "script": mcp_dir / "local_file.py",
            "description": "File system operations MCP server",
            "tools": ["list_work_dir", "mkdir", "get_system_info", "read_file", "open_dir", "write_file", "delete_file", "run_command"]
        },
        "todo": {
            "script": mcp_dir / "todo.py",
            "description": "Todo list management MCP server with UUID support",
            "tools": ["create_todo_list", "list_todo_lists", "get_todo_list", "delete_todo_list", "rename_todo_list", "add_task", "list_tasks", "set_task_status", "update_task", "remove_task", "clear_completed", "search_tasks"]
        }
    }
    
    if server not in server_configs:
        console.print(f"[red]Error: Unknown server '{server}'. Available: {', '.join(server_configs.keys())}[/red]")
        raise typer.Exit(code=1)
    
    config = server_configs[server]
    
    # Create info table
    table = Table(title=f"MCP Server Info: {server}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Name", server)
    table.add_row("Description", config["description"])
    table.add_row("Script Path", str(config["script"]))
    table.add_row("Status", "✅ Available" if config["script"].exists() else "❌ Not Found")
    table.add_row("Tool Count", str(len(config["tools"])))
    
    console.print(table)
    
    # Show tools
    tools_table = Table(title="Available Tools")
    tools_table.add_column("Tool Name", style="yellow")
    
    for tool in config["tools"]:
        tools_table.add_row(tool)
    
    console.print(tools_table)
    
    # Usage examples
    console.print(f"\n[bold]Usage Examples:[/bold]")
    console.print(f"[cyan]Start server:[/cyan] ai4one mcp start {server}")
    console.print(f"[cyan]Validate server:[/cyan] ai4one mcp validate")
    
    if server == "file":
        console.print(f"[cyan]Example client connection:[/cyan]")
        console.print(f"  python -c \"from mcp import ClientSession, StdioServerParameters; import asyncio; asyncio.run(ClientSession(StdioServerParameters(command='python', args=['{config['script']}'])).run())\"")
    

if __name__ == "__main__":
    app()
