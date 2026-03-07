# tests/test_config.py
"""Tests for ai4one.config module."""

import json
import pytest
from dataclasses import field
from typing import List, Literal
from ai4one.config import load_config, BaseConfig


def test_load_config():
    """Test loading config from TOML file."""
    config = load_config("./pyproject.toml")
    assert config["project"]["name"] == "ai4one"


class SimpleConfig(BaseConfig):
    """Test config with basic types."""
    name: str
    value: int = 10
    test_list1: list
    test_list2: list = [1, 2, 3]
    test_list3: list[int] = [1, 2, 3]
    test_list4: List[int] = field(default_factory=lambda: [2025, 8, 1])
    test_list5: List[int] = [4, 5, 6]


class DataConfig(BaseConfig):
    """Nested config for testing."""
    path: str = "/data/default"
    batch_size: int = 32


class ModelConfig(BaseConfig):
    """Nested config for testing."""
    name: str = "default_model"
    layers: int = 4
    device: Literal["auto", "gpu", "cpu"] = "auto"


class NestedConfig(BaseConfig):
    """Config with nested configs."""
    data: DataConfig
    model: ModelConfig
    learning_rate: float = 0.01


class TestBaseConfig:
    """Tests for BaseConfig class."""

    def test_simple_config_defaults(self):
        """Test that config initializes with correct defaults."""
        config = SimpleConfig(name="test_item")
        assert config.name == "test_item"
        assert config.value == 10
        assert config.test_list1 == []
        assert config.test_list3 == [1, 2, 3]
        assert config.test_list4 == [2025, 8, 1]
        assert config.test_list5 == [4, 5, 6]

    def test_file_io_json(self, tmp_path):
        """Test to_file and from_file with JSON."""
        config_file = tmp_path / "config.json"
        original = SimpleConfig(name="io_test", value=99)

        original.to_file(config_file)
        assert config_file.exists()

        loaded = SimpleConfig.from_file(config_file)
        assert loaded.name == "io_test"
        assert loaded.value == 99

    def test_nested_config_io(self, tmp_path):
        """Test serialization of nested configs."""
        config_file = tmp_path / "nested.json"

        original = NestedConfig()
        original.data.batch_size = 128
        original.model.name = "CustomNet"

        original.to_file(config_file)
        loaded = NestedConfig.from_file(config_file)

        assert loaded.learning_rate == 0.01
        assert loaded.data.batch_size == 128
        assert loaded.model.name == "CustomNet"
        assert isinstance(loaded.data, DataConfig)
        assert isinstance(loaded.model, ModelConfig)

    def test_nested_config_equality(self, tmp_path):
        """Test that loaded config equals original."""
        config_file = tmp_path / "equality.json"
        original = NestedConfig()
        original.data.batch_size = 64
        original.to_file(config_file)

        loaded = NestedConfig.from_file(config_file)
        assert loaded == original
