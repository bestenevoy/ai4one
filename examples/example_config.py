from ai4one.config import BaseConfig
from typing import Literal, List


# --- 使用示例 ---
class DataConfig(BaseConfig):
    name: str = "hello"
    folds: List[int]
    date: list[int]


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
    # config = Config.argument_parser(config_path_arg="config-file")  # default
    print("1".center(20, "="))
    print(config.data.name)
    print(config.data.folds)
    print(config.data.date)

    config.to_file("./ai4one_config.json")
    # config.to_file("./ai4one_config.yaml")
    # config.to_file("./ai4one_config.toml")

    cfg = Config.from_file("./ai4one_config.json")
    # Config.from_file("./ai4one_config.yaml")
    # Config.from_file("./ai4one_config.toml")
    print("2".center(20, "="))
    print(cfg.data.name)
    print(cfg.data.folds)
    print(cfg.data.date)

    """
    uv run examples/example_config.py --device gpu --name ai4one --folds 2 3 --mode test --date 1999 9 9
    or 
    python examples/example_config.py --device gpu --name ai4one --folds 2 3 --mode test --date 1999 9 9
    or
    uv run examples/example_config.py --config-file ./ai4one_config.yaml
    or
    uv run examples/example_config.py --config-file ./ai4one_config.yaml --name bestenevoy
    or
    uv run examples/example_config.py --config-file ./ai4one_config.yaml --date 2025 8 1
    """
