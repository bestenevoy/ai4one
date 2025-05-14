import os
import json
from pathlib import Path
from typing import Optional


def load_json(file_path, encoding="utf-8"):
    """
    Load data from a JSON file.

    Args:
        file_path (str): Path to the JSON file to be loaded.

    Returns:
        dict or list: The data loaded from the JSON file.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    try:
        with open(file_path, "r", encoding=encoding) as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: File '{file_path}' contains invalid JSON data.")
        return None


def dump_json(data, file_path, indent=2):
    """
    Save data to a JSON file.

    Args:
        data (dict or list): The data to be saved to the JSON file.
        file_path (str): Path where the JSON file will be saved.
        indent (int, optional): Number of spaces for indentation in the JSON file. Defaults to 4.

    Returns:
        bool: True if data was successfully saved, False otherwise.

    Raises:
        TypeError: If the data is not JSON serializable.
    """
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=indent)
        return True
    except TypeError as e:
        print(f"Error: Could not serialize data to JSON. {str(e)}")
        return False
    except Exception as e:
        print(f"Error: Failed to write to file '{file_path}'. {str(e)}")
        return False


def read_file(path: str, encoding: str = "utf8", lines: Optional[int] = None) -> str:
    """读取文件内容（始终返回字符串）

    Args:
        path: 文件路径
        encoding: 文件编码 (默认utf8)
        lines: 读取行数(None读全部，n读指定行数)

    Returns:
        拼接后的字符串（保留换行符）

    Raises:
        FileNotFoundError: 文件不存在
        UnicodeDecodeError: 编码错误
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"文件不存在: {path}")

    with open(path, "r", encoding=encoding) as f:
        if lines is None:
            return f.read()

        # 读取指定行数并拼接为字符串
        return "".join(line for i, line in enumerate(f) if i < lines)


def get_work_dir(_file_: Optional[Path] = None) -> Path:
    if _file_ is None:
        return Path(os.getcwd())
    return Path(_file_).parent
