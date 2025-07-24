# tests/test_config.py

from ai4one.config import load_config, BaseConfig
from unittest.mock import patch
from dataclasses import field


# 从您的源码中导入被测试的类
def test_add():
    config = load_config("./pyproject.toml")
    assert config["project"]["name"] == "ai4one"


# --- 定义用于测试的配置类 ---

class SimpleConfig(BaseConfig):
    name: str
    value: int = 10

class DataConfig(BaseConfig):
    path: str = "/data/default"
    batch_size: int = 32

class ModelConfig(BaseConfig):
    name: str = "default_model"
    layers: int = 4

class NestedConfig(BaseConfig):
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    learning_rate: float = 0.01


# --- 测试类 ---

class TestBaseConfig:

    def test_inheritance_and_serialization(self):
        config = SimpleConfig(name="test_item")
        assert config.name == "test_item"
        assert config.value == 10

        # 验证 to_json() 方法是否存在且工作正常
        json_str = config.to_json()
        assert '"name": "test_item"' in json_str
        assert '"value": 10' in json_str

    def test_file_io_cycle(self, tmp_path):
        """测试 to_file 和 from_file 的完整读写循环。
        
        `tmp_path` 是一个 pytest fixture，提供一个临时的目录对象。
        """
        config_file = tmp_path / "config.json"
        original_config = SimpleConfig(name="cycle_test", value=99)

        original_config.to_file(config_file)
        assert config_file.exists()

        loaded_config = SimpleConfig.from_file(config_file)

        assert loaded_config == original_config

    def test_nested_config_io(self, tmp_path):
        """测试对嵌套配置的序列化和文件I/O。"""
        config_file = tmp_path / "nested_config.json"
        
        original_config = NestedConfig()
        original_config.data.batch_size = 128
        original_config.model.name = "CustomNet"

        original_config.to_file(config_file)
        
        loaded_config = NestedConfig.from_file(config_file)

        assert loaded_config.learning_rate == 0.01
        assert loaded_config.data.batch_size == 128
        assert loaded_config.model.name == "CustomNet"
        
        assert isinstance(loaded_config.data, DataConfig)
        assert isinstance(loaded_config.model, ModelConfig)

        assert loaded_config == original_config
    
    def test_argument_parser_override(self):
        """测试 argument_parser 是否能正确地被命令行参数覆盖。"""
        # 模拟命令行输入: python script.py --learning_rate 0.5 --path /new/path
        cli_args = [
            "script.py", # 第一个参数总是脚本名
            "--learning_rate",
            "0.5",
            "--path",
            "/new/path",
        ]

        with patch("sys.argv", cli_args):
            parsed_config = NestedConfig.argument_parser()

        assert parsed_config.model.name == "default_model"
        
        assert parsed_config.learning_rate == 0.5
        assert parsed_config.data.path == "/new/path"