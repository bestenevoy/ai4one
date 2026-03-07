#!/usr/bin/env python3
"""
tag.py
在本地仓库根目录执行：
    python tag.py
即可根据 pyproject.toml 的 version 生成并推送 tag。
"""
import subprocess
import sys
from pathlib import Path

try:
    import tomllib          # Python 3.11+
except ImportError:
    # 兼容 3.10 及以下
    try:
        import tomli as tomllib
    except ImportError:
        print("需要 tomli（pip install tomli）在 Python<3.11 运行")
        sys.exit(1)

def cmd(c: str) -> str:
    """执行 shell 命令并返回 stdout，失败即抛异常"""
    return subprocess.check_output(c, shell=True, text=True).strip()

def main() -> None:
    # 1. 解析 pyproject.toml
    data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    version = data["project"]["version"]
    tag = f"v{version}"

    # 2. 如果 tag 已存在就退出
    try:
        cmd(f"git rev-parse {tag}")
        print(f"Tag {tag} 已存在，无需重复创建。")
        return
    except subprocess.CalledProcessError:
        pass

    # 3. 创建并推送
    cmd(f"git tag {tag}")
    cmd(f"git push origin {tag}")
    print(f"✅ 已创建并推送 tag：{tag}")

if __name__ == "__main__":
    main()