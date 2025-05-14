import sys
import uuid
from datetime import datetime
from .file import load_json, dump_json  # noqa
from .file import read_file  # noqa


def fmt_filename(input_string: str) -> str:
    """
    格式化文件名函数
    将输入字符串中的空格替换为下划线，并将所有字母转换为小写，
    适用于生成文件名，确保文件名符合命名规范。

    参数：
    input_string (str): 输入的字符串，表示需要格式化的文件名。

    返回：
    str: 格式化后的文件名。
    """

    if not isinstance(input_string, str):
        raise ValueError("输入必须是字符串类型")

    # 去除首尾空格后，转换为小写，再替换空格为下划线
    formatted_string = "_".join(input_string.strip().casefold().split())

    return formatted_string


def gen_filename_from_kwargs(utc_time=False, **kwargs):
    """
    根据函数的参数名称和对应的值生成文件名。
    """
    filename_parts = []

    for param, value in kwargs.items():
        # 将参数名称小写并替换空格为下划线，参数值直接加入
        filename_parts.append(f"{param.lower()}-{value}")
    if utc_time:
        time = datetime.now(datetime.timezone.utc)().strftime("%Y-%m-%dT%H-%M-%SZ")
    else:
        time = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    return (
        f"{time}_" + "_".join(filename_parts) + "_" + str(uuid.uuid4()).split("-")[-1]
    )


def fmt_args_to_short_command():
    """
    获取命令行参数并将其还原为终端命令
    """
    # 使用 sys.argv 获取命令行传入的所有参数
    command = " ".join(sys.argv[1:])  # 连接成字符串
    if not command:  # 如果命令为空，则返回None
        return ""
    return command


def fmt_args_to_command(args):
    """
    将解析后的命令行参数格式化为所需的字符串形式。
    """
    args = vars(args)
    result = []
    for key, value in args.items():
        if value is not None:
            result.append(f"--{key} {value}")
        else:
            result.append(key)
    return " ".join(result)
