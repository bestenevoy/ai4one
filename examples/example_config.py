from dataclasses_json import config
from ai4one.config import BaseConfig
from typing import Literal, List


# --- 使用示例 ---
class DataConfig(BaseConfig):
    name: str = "hello"
    folds: List[int]


class ModelConfig(BaseConfig):
    pass


class TrainConfig(BaseConfig):
    device: Literal["auto", "gpu", "cpu"] = "auto"


class Config(BaseConfig):

    data: DataConfig
    model: ModelConfig
    train: TrainConfig

    mode: Literal["train", "test", "predict"] = "train"


if __name__ == "__main__":

    config = Config.argument_parser()
    config.to_file("./ai4one_config.json")
    config.to_file("./ai4one_config.yaml")
    config.to_file("./ai4one_config.toml")

    cfg = Config.from_file("./ai4one_config.json")
    Config.from_file("./ai4one_config.yaml")
    Config.from_file("./ai4one_config.toml")

    print(cfg.data.name)
    print(cfg.data.folds)

    """
    uv run examples/example_config.py --device gpu --name ai4one --folds 2 3 --mode test
    or 
    python examples/example_config.py --device gpu --name ai4one --folds 2 3 --mode test
    """
