#!/usr/bin/env python3
"""
MCP World Info tools for agents to get current world information.
- Provides current local time information
- Gets current location/region information
- Provides basic runtime environment details

Run this module to start a standalone MCP server, or import the tools into another server.
"""
from __future__ import annotations

import argparse
import platform
from datetime import datetime
from typing import Dict
import locale

from mcp.server.fastmcp import FastMCP


def parse_args():
    parser = argparse.ArgumentParser(description="MCP World Info Server")
    parser.add_argument(
        "--port", type=int, default=50003, help="Server port (default: 50003)"
    )
    parser.add_argument(
        "--host", default="0.0.0.0", help="Server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )
    parser.add_argument(
        "--transport","-t",
        default="stdio",
        choices=["stdio", "sse", "mcp", "streamable-http"],
        help="Transport protocol",
    )

    try:
        args = parser.parse_args()
    except SystemExit:

        class Args:
            port = 50003
            host = "0.0.0.0"
            log_level = "INFO"
            transport = "stdio"
        args = Args()
    return args


mcp = FastMCP("ai4one_world_info_server")


@mcp.tool()
def get_base_world_info() -> Dict[str, str]:
    """Get basic world information, primarily focused on current time details.

    Returns:
        Dictionary containing only core information: current time, timezone,
        weekday, system, python version, and language/country.
    """
    try:
        # Get time info
        now = datetime.now()

        # Get system info
        system = platform.system()
        release = platform.release()
        python_version = platform.python_version()

        # Get locale info
        try:
            current_locale = (
                locale.getlocale()[0] or locale.getdefaultlocale()[0] or "Unknown"
            )
            if current_locale and "_" in current_locale:
                language, country = current_locale.split("_", 1)
            else:
                language = current_locale or "Unknown"
                country = "Unknown"
        except:
            language = "Unknown"
            country = "Unknown"

        return {
            "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "timezone": "Local",
            "weekday": now.strftime("%A"),
            "system": f"{system} {release}",
            "python_version": python_version,
            "language_country": f"{language}/{country}",
        }
    except Exception as e:
        return {
            "error": f"Failed to get essential info: {str(e)}",
            "current_time": "Unknown",
            "system": "Unknown",
            "python_version": "Unknown",
        }


# Server runner
def run_server():
    import anyio

    args = parse_args()

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


if __name__ == "__main__":
    run_server()