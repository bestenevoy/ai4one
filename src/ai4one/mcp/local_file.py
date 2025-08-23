#!/usr/bin/env python3
"""
Example MCP Server using the new simplified pattern.
This demonstrates how to create a new AI4S tool with tools defined at module level.
"""
import argparse
import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP

work_dir: Path = Path(__file__).parent / "work_dir"


def parse_args():
    """Parse command line arguments for MCP server."""
    parser = argparse.ArgumentParser(description="MCP Server")
    parser.add_argument("--port", type=int, default=50001, help="Server port (default: 50001)")
    parser.add_argument("--host", default="0.0.0.0", help="Server host (default: 0.0.0.0)")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging level (default: INFO)")
    parser.add_argument("--work-dir", default="~/ai4one/mcp/work_dir/", help="Work directory (default: ~/ai4one/mcp/work_dir/)")
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse", "mcp", "streamable-http"], help="Transport protocol (default: sse)")

    try:
        args = parser.parse_args()
    except SystemExit:

        class Args:
            port = 50001
            host = "0.0.0.0"
            log_level = "INFO"
            work_dir = "~/ai4one/mcp/work_dir/"
            transport = "stdio"

        args = Args()

    return args


def setup_work_dir(args):
    global work_dir
    work_dir = Path(args.work_dir).expanduser()
    work_dir.mkdir(parents=True, exist_ok=True)


mcp = FastMCP("ai4one_file_server")


def run_server():
    import anyio

    args = parse_args()
    setup_work_dir(args)

    mcp.settings.port = args.port
    mcp.settings.host = args.host

    match args.transport:
        case "stdio":
            anyio.run(mcp.run_stdio_async)
        case "sse":
            mount_path = None
            print(f"Server URL: http://{args.host}:{args.port}/{args.transport}")
            anyio.run(lambda: mcp.run_sse_async(mount_path))
        case "mcp":
            print(f"Server URL: http://{args.host}:{args.port}/{args.transport}")
            anyio.run(mcp.run_streamable_http_async)


# Define tools at module level
@mcp.tool()
def list_work_dir() -> dict:
    """
    List work space files.

    Returns:
        A dictionary containing the list of work space files
    """
    return {"work_dir": os.listdir(work_dir)}


@mcp.tool()
def mkdir(dir_name: str) -> str:
    """
    Make a dirctery at work space.

    Args:
        dir_name: dirctery name.
    Returns:
        Success or failure.
    """
    try:
        os.mkdir(work_dir / dir_name)
        return "Success"
    except Exception as e:
        return f"Failure: {e}"


@mcp.tool()
def get_system_info() -> str:
    """
    Get system info.

    Returns:
        Windows or Linux.
    """
    return "Windows" if os.name == "nt" else "Linux"


@mcp.tool()
def read_file(file_path: str) -> str:
    """
    Read file.

    Args:
        file_path: File which root path at work space.

    Returns:
        File content.
    """
    content = ""
    try:
        file_path = os.path.join(work_dir, file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Failure: {e}"


@mcp.tool()
def open_dir(file_path: str) -> list[str] | str:
    """
    Open dirctery which root path at work space.

    Args:
        file_path: Dirctery which root path at work space.

    Returns:
        Files and directories in the specified path string.
    """
    try:
        file_path = os.path.join(str(work_dir), file_path)
        return os.listdir(file_path)
    except Exception as e:
        return f"Failure: {e}"


@mcp.tool()
def write_file(file_path: str, content: str) -> str:
    """
    Write file at work space.

    Args:
        file_path: File which root path at work space.
        content: Content to write.

    Returns:
        Success or failure.
    """
    file_path = work_dir / file_path  # type: ignore
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return "Success"
    except Exception as e:
        return f"Failure: {e}"


@mcp.tool()
def delete_file(file_path: str) -> str:
    """
    Delete file or dirctery at work space.

    Args:
        file_path: File or dirctery which root path at work space.

    Returns:
        Success or failure.
    """
    try:
        file_path = os.path.join(work_dir, file_path)
        os.remove(file_path)
        return "Success"
    except Exception as e:
        return f"Failure: {e}"


@mcp.tool()
def run_command(command: str) -> str:
    """
    Run command at work space.

    Args:
        command: Command to run.

    Returns:
        Command output.
    """
    import subprocess

    origin = os.getcwd()
    try:
        os.chdir(work_dir)
        output = subprocess.getoutput(command)
        os.chdir(origin)
        return output
    except Exception as e:
        os.chdir(origin)
        return f"Failure: {e}"


if __name__ == "__main__":
    # Get transport type from environment variable, default to SSE
    run_server()
