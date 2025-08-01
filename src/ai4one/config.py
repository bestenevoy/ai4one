from dataclasses import field, dataclass, asdict  # noqa
from typing import Type, TypeVar, List, get_origin, Any, Dict  # noqa
from pathlib import Path

# from dataclasses_json import dataclass_json
# from simple_parsing import ArgumentParser
from simple_parsing.helpers import Serializable
import simple_parsing
import sys

T = TypeVar("T", bound="BaseConfig")

MUTABLE_TYPE_FACTORIES = {
    list: list,
    dict: dict,
    set: set,
    # str: str
}


def load_config(
    path: str,
):
    import tomllib as toml
    with open(path, mode="rb") as f:
        return toml.load(f)


def is_builtin_type(type_hint: Any) -> bool:
    return type(type_hint) is type


class BaseConfig(Serializable):
    """配置基类，可以实现自动解析命令行参数 argument_parser, rom_file/to_file

    一个支持 JSON, YAML, TOML 的多功能配置基类。
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
    ...     data: DataConfig
    ...     model: ModelConfig
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
        no_default_names = []
        sub_cls = []

        if not hasattr(cls, "__annotations__"):
            dataclass(cls)
            # dataclass_json(cls)
            return

        for name, type_hint in cls.__annotations__.copy().items():

            if type_hint is list:
                cls.__annotations__[name] = List[Any]
            elif type_hint is dict:
                cls.__annotations__[name] = Dict[Any, Any]
            elif type_hint is str:
                pass

            if isinstance(type_hint, type) and issubclass(type_hint, BaseConfig):
                # issubclass() arg 1 must be a class
                sub_cls.append((name, type_hint))
                setattr(cls, name, field(default_factory=type_hint))
                continue

            is_has = hasattr(cls, name)
            if not is_has:
                no_default_names.append(name)
                if not is_builtin_type(type_hint):
                    _type_ = get_origin(type_hint)
                    origin_value = _type_()
                else:
                    # 如果是内置类型
                    _type_ = type_hint
                    origin_value = type_hint()
                setattr(cls, name, field(default_factory=lambda n=origin_value: n))
            else:
                origin_value = getattr(cls, name)
                _type_ = type(origin_value)
                type_hint_o = get_origin(type_hint)

                if _type_ in MUTABLE_TYPE_FACTORIES:
                    # NOTE: 不能写成 lambda: origin_value
                    # 这样并没有捕获到当前的 origin_value，会被后面的值覆盖掉。
                    setattr(cls, name, field(default_factory=lambda n=origin_value: n))
                    continue
                elif type_hint_o is not _type_:
                    continue

        dataclass(cls)
        # dataclass_json(cls)
        cls.__no_default_names__ = no_default_names
        cls.__sub_cls__ = sub_cls

    def to_file(self, file_path: str, **kwargs):
        self.save(file_path, **kwargs)

    @classmethod
    def from_file(cls: Type[T], file_path: str) -> T:
        """
        从文件加载配置实例，根据文件扩展名自动选择格式。

        Args:
            file_path (str): 源文件路径 (e.g., 'config.json', 'config.yaml').

        Returns:
            一个填充了文件数据的配置类实例。
        """
        return cls.load(file_path)

    @classmethod
    def argument_parser(cls: Type[T], config_path_arg="config-file") -> T:

        ret = simple_parsing.parse(
            config_class=cls,
            args=" ".join(sys.argv[1:]),
            add_config_path_arg=config_path_arg,
        )
        cls.check_no_default_names(ret)
        return ret

    @classmethod
    def _collect_missing_fields(
        cls, instance: "BaseConfig", prefix: str = ""
    ) -> List[str]:
        """一个递归的辅助函数，用于收集所有缺失字段的完整路径。"""
        missing_paths = []

        # 1. 检查当前级别的必填字段
        # 我们假设 __no_default_names__ 存储了没有默认值的字段名
        for name in getattr(cls, "__no_default_names__", []):
            # 检查属性值是否为 "falsy" (e.g., None, 0, "", [])
            # 注意：如果 0 或 "" 是有效值，此检查可能需要调整
            if not getattr(instance, name, None):
                missing_paths.append(f"{prefix}{name}")

        # 2. 递归检查所有子配置
        # 我们假设 __sub_cls__ 存储了 (字段名, 子配置类) 的元组
        for name, sub_cls in getattr(cls, "__sub_cls__", []):
            sub_instance = getattr(instance, name)
            # 将当前字段名加入前缀，并递归调用
            sub_missing = sub_cls._collect_missing_fields(
                sub_instance, prefix=f"{prefix}{name}."
            )
            missing_paths.extend(sub_missing)

        return missing_paths

    @classmethod
    def check_no_default_names(cls: Type[T], cls_instance: T):
        """
        检查实例及其子实例中所有必填字段是否已提供。
        如果未提供，则打印一个包含所有缺失项的清晰错误信息，然后退出。
        """
        all_missing = cls._collect_missing_fields(cls_instance)

        if all_missing:
            # --- 错误信息主体部分 (与之前相同) ---
            error_header = "❌ Error: The following required configuration parameters are missing or empty:"
            error_list = "\n".join([f"  - {path}" for path in all_missing])
            error_footer = "\nPlease provide them via the command line or in your configuration file."
            import sys

            # --- 新增：动态生成命令行示例 ---
            try:
                # 尝试获取当前运行的脚本名
                script_name = Path(sys.argv[0]).name
            except (IndexError, AttributeError):
                script_name = "your_script.py"

            # 将缺失的路径转换为命令行参数格式
            # 例如 'data.path' -> '--data.path <VALUE>'
            example_args = [
                f"--{path.split('.')[-1]} <YOUR_{path.upper().replace('.', '_')}_VALUE>"
                for path in all_missing
            ]

            # 拼接成完整的命令
            example_command = f"python {script_name} " + " ".join(example_args)

            example_section = (
                f"\n💡 For example, you could provide the missing values like this:\n"
                f"   {example_command}"
            )

            # --- 组合成最终的完整信息 ---
            full_message = (
                f"\n{error_header}\n{error_list}\n{error_footer}\n{example_section}\n"
            )

            sys.exit(full_message)
