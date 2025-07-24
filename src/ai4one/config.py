from dataclasses import field, dataclass  # noqa
from typing import Type, TypeVar, List  # noqa

import tomllib
from dataclasses_json import dataclass_json
from simple_parsing import ArgumentParser


T = TypeVar("T", bound="BaseConfig")


def load_config(
    path: str,
):
    with open(path, mode="rb") as f:
        return tomllib.load(f)


class BaseConfig:
    """配置基类，可以实现自动解析命令行参数 argument_parser, rom_file/to_file, from_json/to_json

    通过继承此类，任何子类都会自动成为一个强大的配置对象，无需手动添加装饰器。

    核心特性:
    1.  **@dataclass 功能**: 自动生成 `__init__`, `__repr__` 等标准方法。
    2.  **JSON 序列化**: 通过 `dataclasses-json` 自动获得与 JSON 互相转换的能力
        (`to_json()`, `from_json()`)，并完美支持嵌套配置。
    3.  **文件 I/O**: 提供便捷的 `to_file()` 和 `from_file()` 方法，用于读写 JSON 配置文件。
    4.  **命令行集成**: `argument_parser()` 方法能自动将配置字段暴露为命令行参数，
        轻松实现默认值覆盖。
    5.  **类型安全**: 所有方法都具备严格的类型提示，确保静态分析和IDE自动补全的准确性。

    ---
    ### 使用示例 1: 基础用法与文件操作

    定义一个简单的配置类，设置其字段和默认值。

    >>> class DatabaseConfig(BaseConfig):
    ...     host: str = "localhost"
    ...     port: int = 5432
    ...     user: str
    
    保存和加载配置。

    >>> db_conf = DatabaseConfig(user="admin")
    >>> db_conf.to_file("db.json")
    >>> loaded_conf = DatabaseConfig.from_file("db.json")
    >>> print(loaded_conf.user)
    admin

    ---
    ### 使用示例 2: 嵌套配置 (Hierarchical Configuration)

    这是管理复杂项目配置的推荐方式。首先定义各个子配置。

    >>> class DataConfig(BaseConfig):
    ...     path: str = "/data/set"
    ...     batch_size: int = 64
    >>>
    >>> class ModelConfig(BaseConfig):
    ...     name: str = "ResNet50"
    ...     embedding_dim: int = 256
    
    然后，将它们组合成一个主配置类。使用 `dataclasses.field` 和 `default_factory`
    来确保每个子配置都能被正确初始化。

    >>> from dataclasses import field
    >>>
    >>> class MainConfig(BaseConfig):
    ...     data: DataConfig = field(default_factory=DataConfig)
    ...     model: ModelConfig = field(default_factory=ModelConfig)
    ...     learning_rate: float = 0.001

    主配置可以作为一个整体进行序列化和反序列化。

    >>> main_conf = MainConfig()
    >>> print(main_conf.model.name)
    ResNet50
    >>> main_conf.to_file("config.json")
    
    ---
    ### 使用示例 3: 命令行参数解析

    `argument_parser()` 方法允许你用命令行参数覆盖文件或代码中的默认配置。

    >>> # 在你的 Python 脚本 (例如: train.py) 中:
    >>> # config = MainConfig.argument_parser()
    >>> # print(config.learning_rate)
    >>> # print(config.data.batch_size)

    然后你可以在终端中运行脚本并传入参数：

    .. code-block:: shell

        # 使用默认值运行
        # python train.py
        # 输出: 0.001
        # 输出: 64

        # 从命令行覆盖参数
        # python train.py --learning_rate 0.1 --batch_size 128
        # 输出: 0.1
        # 输出: 128
    """

    def __init_subclass__(cls: Type, **kwargs):
        super().__init_subclass__(**kwargs)

        dataclass(cls)
        dataclass_json(cls)

    def to_file(self, file_path: str):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.to_json(indent=2, ensure_ascii=False))

    @classmethod
    def from_file(cls: Type[T], file_path: str) -> T:
        with open(file_path, "r", encoding="utf-8") as f:
            cfg2 = cls.schema().loads(f.read())
        return cfg2

    @classmethod
    def argument_parser(cls: Type[T]) -> T:
        parser = ArgumentParser()
        parser.add_arguments(cls, dest="config")
        args = parser.parse_args()
        return args.config
