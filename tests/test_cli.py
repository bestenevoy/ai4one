from typer.testing import CliRunner

from ai4one.cli import app

runner = CliRunner()


def test_app():
    result = runner.invoke(app, ["gpu"])
    assert result.exit_code == 0
    assert "INFO" in result.stdout or "NVIDIA" in result.stdout
