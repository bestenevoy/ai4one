
from ai4one.config import load_config

def test_add():
    config = load_config("./pyproject.toml")
    assert config["project"]["name"] == "ai4one"
