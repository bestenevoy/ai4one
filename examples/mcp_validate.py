#!/usr/bin/env python3
"""
MCP Server Validation Script

Validates that all MCP servers are working correctly.

Usage:
    python examples/mcp_validate.py
"""
import asyncio
import os
import sys
import json
from pathlib import Path
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src" / "ai4one" / "mcp"

SERVERS = {
    "file": str(SRC_DIR / "local_file.py"),
    "todo": str(SRC_DIR / "todo.py"),
    "world": str(SRC_DIR / "world_info.py"),
    "web": str(SRC_DIR / "web.py"),
}


class MCPValidator:
    def __init__(self):
        self.exit_stack = AsyncExitStack()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.exit_stack.aclose()

    async def connect_to_server(self, server_path: str, server_name: str):
        """Connect to MCP server."""
        print(f"\n  Connecting to {server_name}...")
        print(f"    Script: {server_path}")

        if not os.path.exists(server_path):
            raise FileNotFoundError(f"Server script not found: {server_path}")

        server_params = StdioServerParameters(command="python", args=[server_path], env=None)

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport

        session = await self.exit_stack.enter_async_context(ClientSession(stdio, write))
        await session.initialize()

        print(f"    Connected successfully")
        return session

    async def validate_file_server(self):
        """Validate file server."""
        print("\n[FILE SERVER]")
        try:
            session = await self.connect_to_server(SERVERS["file"], "file")

            tools_response = await session.list_tools()
            tools = [tool.name for tool in tools_response.tools]
            print(f"    Tools: {tools}")

            expected = {"list_work_dir", "mkdir", "get_system_info", "read_file",
                        "open_dir", "write_file", "delete_file", "run_command"}
            missing = expected - set(tools)
            if missing:
                print(f"    Missing tools: {missing}")
                return False

            result = await session.call_tool("get_system_info", {})
            content = result.content[0].text
            print(f"    System: {content}")

            print("  PASSED")
            return True
        except Exception as e:
            print(f"  FAILED: {e}")
            return False

    async def validate_todo_server(self):
        """Validate todo server."""
        print("\n[TODO SERVER]")
        try:
            session = await self.connect_to_server(SERVERS["todo"], "todo")

            tools_response = await session.list_tools()
            tools = [tool.name for tool in tools_response.tools]
            print(f"    Tools: {tools}")

            expected = {"create_todo_list", "list_todo_lists", "get_todo_list",
                        "delete_todo_list", "rename_todo_list", "add_task",
                        "list_tasks", "set_task_status", "update_task",
                        "remove_task", "clear_completed", "search_tasks"}
            missing = expected - set(tools)
            if missing:
                print(f"    Missing tools: {missing}")
                return False

            # Create test list
            result = await session.call_tool("create_todo_list", {
                "name": "Validation Test",
                "description": "Test list for validation"
            })
            list_data = json.loads(result.content[0].text)
            list_id = list_data["id"]
            print(f"    Created list: {list_id}")

            # Add task
            result = await session.call_tool("add_task", {
                "list_id": list_id,
                "content": "Test task",
                "priority": "high"
            })
            print(f"    Added task")

            # Cleanup
            await session.call_tool("delete_todo_list", {"list_id": list_id})
            print(f"    Cleaned up")

            print("  PASSED")
            return True
        except Exception as e:
            print(f"  FAILED: {e}")
            return False

    async def validate_world_server(self):
        """Validate world info server."""
        print("\n[WORLD INFO SERVER]")
        try:
            session = await self.connect_to_server(SERVERS["world"], "world")

            tools_response = await session.list_tools()
            tools = [tool.name for tool in tools_response.tools]
            print(f"    Tools: {tools}")

            expected = {"get_base_world_info"}
            missing = expected - set(tools)
            if missing:
                print(f"    Missing tools: {missing}")
                return False

            result = await session.call_tool("get_base_world_info", {})
            content = json.loads(result.content[0].text)
            print(f"    Current time: {content.get('current_time', 'N/A')}")
            print(f"    System: {content.get('system', 'N/A')}")

            print("  PASSED")
            return True
        except Exception as e:
            print(f"  FAILED: {e}")
            return False

    async def validate_web_server(self):
        """Validate web server."""
        print("\n[WEB SERVER]")
        try:
            session = await self.connect_to_server(SERVERS["web"], "web")

            tools_response = await session.list_tools()
            tools = [tool.name for tool in tools_response.tools]
            print(f"    Tools: {tools}")

            expected = {"web_search", "web_search_news", "web_fetch",
                        "web_fetch_links", "url_info", "url_encode", "url_decode"}
            missing = expected - set(tools)
            if missing:
                print(f"    Missing tools: {missing}")
                return False

            # Test url_encode
            result = await session.call_tool("url_encode", {"text": "hello world"})
            encoded = result.content[0].text
            print(f"    URL encode: 'hello world' -> {encoded}")

            # Test url_decode
            result = await session.call_tool("url_decode", {"encoded": encoded})
            decoded = result.content[0].text
            print(f"    URL decode: {encoded} -> '{decoded}'")

            # Test url_info (quick check, no full fetch)
            result = await session.call_tool("url_info", {"url": "https://example.com"})
            info = json.loads(result.content[0].text)
            print(f"    URL info: {info.get('domain', 'N/A')}")

            print("  PASSED")
            return True
        except Exception as e:
            print(f"  FAILED: {e}")
            return False

    async def run_validation(self):
        """Run full validation."""
        print("=" * 50)
        print("MCP Server Validation")
        print("=" * 50)

        results = {
            "file": await self.validate_file_server(),
            "todo": await self.validate_todo_server(),
            "world": await self.validate_world_server(),
            "web": await self.validate_web_server(),
        }

        print("\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        for name, passed in results.items():
            status = "PASS" if passed else "FAIL"
            print(f"  {name}: {status}")

        all_passed = all(results.values())
        print("\n" + ("ALL TESTS PASSED" if all_passed else "SOME TESTS FAILED"))
        return all_passed


async def main():
    try:
        async with MCPValidator() as validator:
            success = await validator.run_validation()
            sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nValidation interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    if not (PROJECT_ROOT / "pyproject.toml").exists():
        print("Error: Run this script from the project root directory")
        sys.exit(1)
    asyncio.run(main())
