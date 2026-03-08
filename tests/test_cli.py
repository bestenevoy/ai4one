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
    assert "web" in result.stdout


def test_mcp_info_file():
    """Test mcp info command for file server."""
    result = runner.invoke(app, ["mcp", "info", "file"])
    assert result.exit_code == 0
    assert "file" in result.stdout.lower()


def test_mcp_info_todo():
    """Test mcp info command for todo server."""
    result = runner.invoke(app, ["mcp", "info", "todo"])
    assert result.exit_code == 0
    assert "todo" in result.stdout.lower()
    assert "create_todo_list" in result.stdout


def test_mcp_info_world():
    """Test mcp info command for world server."""
    result = runner.invoke(app, ["mcp", "info", "world"])
    assert result.exit_code == 0
    assert "world" in result.stdout.lower()


def test_mcp_info_web():
    """Test mcp info command for web server."""
    result = runner.invoke(app, ["mcp", "info", "web"])
    assert result.exit_code == 0
    assert "web" in result.stdout.lower()
    assert "web_search" in result.stdout


def test_mcp_info_unknown():
    """Test mcp info with unknown server."""
    result = runner.invoke(app, ["mcp", "info", "unknown"])
    assert result.exit_code != 0


def test_callgraph_missing_path():
    """Test callgraph with missing path."""
    result = runner.invoke(app, ["callgraph", "/nonexistent/path"])
    assert result.exit_code != 0 or "does not exist" in result.stdout.lower()
