#!/usr/bin/env python3
"""
MCP TodoList tools for agents to track task state with CRUD and UUID-based lists.
- Each TodoList gets a UUID at creation for subsequent operations
- Data is persisted as JSON files under a configurable data directory
- Exposes MCP tools for create/read/update/delete of lists and tasks

Run this module to start a standalone MCP server, or import the tools into another server.
"""
from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

from mcp.server.fastmcp import FastMCP

# Data directory setup (separate from local_file.py work_dir)
DATA_DIR: Path = Path("~/ai4one/mcp/todo_store/").expanduser()


def parse_args():
    parser = argparse.ArgumentParser(description="MCP Todo Server")
    parser.add_argument("--port", type=int, default=50002, help="Server port (default: 50002)")
    parser.add_argument("--host", default="0.0.0.0", help="Server host (default: 0.0.0.0)")
    parser.add_argument(
        "--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging level"
    )
    parser.add_argument(
        "--data-dir",
        default="~/ai4one/mcp/todo_store/",
        help="Directory to persist todo lists (default: ~/ai4one/mcp/todo_store/)",
    )
    parser.add_argument(
        "--transport",
        default="stdio",
        choices=["stdio", "sse", "mcp", "streamable-http"],
        help="Transport protocol",
    )

    try:
        args = parser.parse_args()
    except SystemExit:
        class Args:
            port = 50002
            host = "0.0.0.0"
            log_level = "INFO"
            data_dir = "~/ai4one/mcp/todo_store/"
            transport = "stdio"
        args = Args()
    return args


def setup_data_dir(args) -> None:
    global DATA_DIR
    DATA_DIR = Path(args.data_dir).expanduser()
    DATA_DIR.mkdir(parents=True, exist_ok=True)


mcp = FastMCP("ai4one_todo_server")


def _now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


ALLOWED_STATUSES = {"pending", "in_progress", "completed", "blocked"}
ALLOWED_PRIORITIES = {"low", "medium", "high"}


@dataclass
class Task:
    id: str
    content: str
    status: str = "pending"
    priority: str = "medium"
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)
    metadata: Dict = field(default_factory=dict)


@dataclass
class TodoList:
    id: str
    name: str
    description: Optional[str] = None
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)
    tasks: List[Task] = field(default_factory=list)


# Storage helpers

def _list_path(list_id: str) -> Path:
    return DATA_DIR / f"{list_id}.json"


def _save_list(todo: TodoList) -> None:
    path = _list_path(todo.id)
    data = asdict(todo)
    # dataclasses asdict will convert Task dataclasses recursively
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _load_list(list_id: str) -> TodoList:
    path = _list_path(list_id)
    if not path.exists():
        raise FileNotFoundError(f"TodoList '{list_id}' not found")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    tasks = [Task(**t) for t in data.get("tasks", [])]
    return TodoList(
        id=data["id"],
        name=data["name"],
        description=data.get("description"),
        created_at=data.get("created_at", _now_iso()),
        updated_at=data.get("updated_at", _now_iso()),
        tasks=tasks,
    )


def _validate_status(status: Optional[str]) -> None:
    if status is None:
        return
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"Invalid status '{status}', allowed: {sorted(ALLOWED_STATUSES)}")


def _validate_priority(priority: Optional[str]) -> None:
    if priority is None:
        return
    if priority not in ALLOWED_PRIORITIES:
        raise ValueError(f"Invalid priority '{priority}', allowed: {sorted(ALLOWED_PRIORITIES)}")


# MCP tools

@mcp.tool()
def create_todo_list(name: str, description: Optional[str] = None) -> dict:
    """Create a new todo list and return its UUID and metadata."""
    list_id = str(uuid4())
    todo = TodoList(id=list_id, name=name, description=description)
    _save_list(todo)
    return {"id": todo.id, "name": todo.name, "description": todo.description, "created_at": todo.created_at}


@mcp.tool()
def list_todo_lists() -> List[dict]:
    """List all todo lists (summary)."""
    items: List[dict] = []
    for p in DATA_DIR.glob("*.json"):
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            items.append(
                {
                    "id": data.get("id", p.stem),
                    "name": data.get("name", p.stem),
                    "description": data.get("description"),
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                    "task_count": len(data.get("tasks", [])),
                }
            )
        except Exception:
            # skip corrupted files
            continue
    return sorted(items, key=lambda x: (x.get("updated_at") or "", x.get("created_at") or ""), reverse=True)


@mcp.tool()
def get_todo_list(list_id: str) -> dict:
    """Get a full todo list by UUID."""
    todo = _load_list(list_id)
    return asdict(todo)


@mcp.tool()
def delete_todo_list(list_id: str) -> str:
    """Delete a todo list by UUID."""
    path = _list_path(list_id)
    if not path.exists():
        return f"TodoList '{list_id}' not found"
    os.remove(path)
    return "Success"


@mcp.tool()
def rename_todo_list(list_id: str, name: str, description: Optional[str] = None) -> dict | str:
    """Rename or update the description of a todo list."""
    try:
        todo = _load_list(list_id)
        todo.name = name
        if description is not None:
            todo.description = description
        todo.updated_at = _now_iso()
        _save_list(todo)
        return asdict(todo)
    except FileNotFoundError as e:
        return str(e)


@mcp.tool()
def add_task(list_id: str, content: str, priority: str = "medium") -> dict | str:
    """Add a task to a todo list; returns the created task."""
    try:
        _validate_priority(priority)
        todo = _load_list(list_id)
        task = Task(id=str(uuid4()), content=content, priority=priority)
        todo.tasks.append(task)
        todo.updated_at = _now_iso()
        _save_list(todo)
        return asdict(task)
    except (FileNotFoundError, ValueError) as e:
        return str(e)


@mcp.tool()
def list_tasks(list_id: str, status: Optional[str] = None) -> List[dict] | str:
    """List tasks in a todo list, optionally filtered by status."""
    try:
        _validate_status(status)
        todo = _load_list(list_id)
        tasks = [asdict(t) for t in todo.tasks if status is None or t.status == status]
        return tasks
    except (FileNotFoundError, ValueError) as e:
        return str(e)


@mcp.tool()
def set_task_status(list_id: str, task_id: str, status: str) -> dict | str:
    """Update the status of a task."""
    try:
        _validate_status(status)
        todo = _load_list(list_id)
        for t in todo.tasks:
            if t.id == task_id:
                t.status = status
                t.updated_at = _now_iso()
                todo.updated_at = t.updated_at
                _save_list(todo)
                return asdict(t)
        return f"Task '{task_id}' not found"
    except (FileNotFoundError, ValueError) as e:
        return str(e)


@mcp.tool()
def update_task(
    list_id: str,
    task_id: str,
    content: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
) -> dict | str:
    """Update task fields: content, status, priority."""
    try:
        _validate_status(status)
        _validate_priority(priority)
        todo = _load_list(list_id)
        for t in todo.tasks:
            if t.id == task_id:
                if content is not None:
                    t.content = content
                if status is not None:
                    t.status = status
                if priority is not None:
                    t.priority = priority
                t.updated_at = _now_iso()
                todo.updated_at = t.updated_at
                _save_list(todo)
                return asdict(t)
        return f"Task '{task_id}' not found"
    except (FileNotFoundError, ValueError) as e:
        return str(e)


@mcp.tool()
def remove_task(list_id: str, task_id: str) -> str:
    """Remove a task from a todo list."""
    try:
        todo = _load_list(list_id)
        before = len(todo.tasks)
        todo.tasks = [t for t in todo.tasks if t.id != task_id]
        after = len(todo.tasks)
        if before == after:
            return f"Task '{task_id}' not found"
        todo.updated_at = _now_iso()
        _save_list(todo)
        return "Success"
    except FileNotFoundError as e:
        return str(e)


@mcp.tool()
def clear_completed(list_id: str) -> dict | str:
    """Remove all completed tasks; returns removed count and remaining count."""
    try:
        todo = _load_list(list_id)
        before = len(todo.tasks)
        todo.tasks = [t for t in todo.tasks if t.status != "completed"]
        removed = before - len(todo.tasks)
        todo.updated_at = _now_iso()
        _save_list(todo)
        return {"removed": removed, "remaining": len(todo.tasks)}
    except FileNotFoundError as e:
        return str(e)


# Optional: search tasks
@mcp.tool()
def search_tasks(list_id: str, query: str) -> List[dict] | str:
    """Search tasks by substring in content (case-insensitive)."""
    try:
        todo = _load_list(list_id)
        q = query.lower()
        return [asdict(t) for t in todo.tasks if q in t.content.lower()]
    except FileNotFoundError as e:
        return str(e)


# Server runner (similar options to local_file.py)

def run_server():
    import anyio

    args = parse_args()
    setup_data_dir(args)

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