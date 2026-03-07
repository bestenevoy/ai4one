"""Tests for ai4one.cli module."""

from typer.testing import CliRunner
from ai4one.cli import app

runner = CliRunner()


def test_mcp_list():
    """Test mcp list command."""
    result = runner.invoke(app, ["mcp", "list"])
    assert result.exit_code == 0
    assert "file" in result.stdout
    assert "todo" in result.stdout
    assert "world" in result.stdout


def test_mcp_info():
    """Test mcp info command."""
    result = runner.invoke(app, ["mcp", "info", "todo"])
    assert result.exit_code == 0
    assert "todo" in result.stdout.lower()
    assert "create_todo_list" in result.stdout


def test_mcp_info_world():
    """Test mcp info command for world server."""
    result = runner.invoke(app, ["mcp", "info", "world"])
    assert result.exit_code == 0
    assert "world" in result.stdout.lower()


def test_callgraph_missing_path():
    """Test callgraph with missing path."""
    result = runner.invoke(app, ["callgraph", "/nonexistent/path"])
    assert result.exit_code != 0 or "does not exist" in result.stdout.lower()
