from dataclasses_json import config
from ai4one.config import BaseConfig, field
from marshmallow import fields, validate
from typing import Literal, List


# --- 使用示例 ---
class DataConfig(BaseConfig):
    name: str = "hahahah"
    folds: List[int] = field(default_factory=list)


class ModelConfig(BaseConfig):
    pass


class TrainConfig(BaseConfig):
    device: Literal["auto", "gpu", "cpu"] = field(
        default="auto",
        metadata=config(
            # 我们告诉 dataclasses-json，不要自己去猜这个字段怎么处理，
            # 直接使用我们提供的 marshmallow 字段。
            mm_field=fields.String(
                # 这个字段必须是一个字符串
                validate=validate.OneOf(
                    ["auto", "gpu", "cpu"]
                )  # 并且它的值必须是这三个选项之一
            )
        ),
    )


class Config(BaseConfig):

    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    train: TrainConfig = field(default_factory=TrainConfig)

    mode: Literal["train", "test", "predict"] = field(
        default="train",
        metadata=config(mm_field=str),
    )


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
