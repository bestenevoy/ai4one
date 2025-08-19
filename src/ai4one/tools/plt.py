import os
import warnings
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from typing import Sequence, Union, List, Optional

"""
## 🚀 快速开始

### 基础用法

```python
from ai4one.tools.plt import setup_fonts
# 一键配置中英文字体
setup_fonts([
    "Times New Roman",          # 系统字体
    "./fonts/my-font.otf",      # 本地字体（相对路径）
    "/usr/share/fonts/arial.ttf", # 本地字体（绝对路径）
    "FiraCode-Regular",         # 缓存目录中的字体
])
```

### 高级用法

```python
from ai4one.tools.plt import FontAutoConfig
# 创建配置器实例
fcfg = FontAutoConfig()
# 获取字体路径
font_path = fcfg.get_font_path("SimHei")
print(f"字体路径: {font_path}")
```

### 默认字体

配置 `Times New Roman` `SimSun` `SimHei` 支持自动下载

详细使用文档见 docs/plt_tool.md
"""


FONT_MAP = {
    "Times New Roman": {
        "urls": [
            "https://db.onlinewebfonts.com/t/32441506567156636049eb850b53f02a.ttf",  # noqa Flake8(E501)
            "https://raw.githubusercontent.com/trishume/OpenTuringCompiler/master/stdlib-sfml/fonts/Times%20New%20Roman.ttf",  # noqa Flake8(E501)
        ],
        "filename": "TimesNewRoman.ttf",
    },
    "SimSun": {
        "urls": [
            "https://db.onlinewebfonts.com/t/b4a89f5837a3f561b244965550593f37.ttf",  # noqa Flake8(E501)
            "https://raw.githubusercontent.com/yanshengjia/link/master/thesis/font/simsun.ttf",  # noqa Flake8(E501)
        ],
        "filename": "SimSun.ttf",
    },
    "SimHei": {
        "urls": [
            "https://zihao-openmmlab.obs.cn-east-3.myhuaweicloud.com/20220716-mmclassification/dataset/SimHei.ttf",  # noqa Flake8(E501)
        ],
        "filename": "SimHei.ttf",
    },
}

CACHE_DIR = Path.home() / ".ai4one" / "fonts"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}  # noqa Flake8(E501)


class FontAutoConfig:
    def __init__(
        self,
        fonts: Optional[Sequence[str]] = None,
        font_dir: Optional[Union[Path, str]] = None,
    ):
        """
        fonts: 字体名称 或 绝对/相对路径列表
            提供下载配置的字体: ["Times New Roman", "SimSun", "SimHei"]
        font_dir: 字体缓存目录，默认 ~/.ai4one/fonts/
        """
        if not fonts:
            fonts = list(FONT_MAP.keys())

        if isinstance(font_dir, str):
            font_dir = Path(font_dir)
        if font_dir is None:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            font_dir = CACHE_DIR

        self.cache_fonts_dir = font_dir
        self.fonts = fonts

    def apply(self) -> None:
        families = []

        for font in self.fonts:
            path = self._resolve(font)
            if path is None:
                warnings.warn(f"字体未找到: {font}", UserWarning)
                continue
            name = self._register_font(path)
            families.append(name)

        # 把综合 family 列表也写进去，顺序即用户指定顺序
        if families:
            plt.rcParams["font.family"] = families
            plt.rcParams["axes.unicode_minus"] = False
        else:
            # 全部失败 -> 不破坏原环境
            warnings.warn("所有指定字体均不可用，保留 matplotlib 默认设置", UserWarning)

    # ---------- 内部工具 ----------
    def _resolve(self, font: str) -> str | None:
        """返回绝对路径或 None"""
        # 1. 绝对/相对路径
        if os.path.isfile(font):
            return os.path.abspath(font)

        # 2. 系统已注册字体
        try:
            return fm.findfont(font, fallback_to_default=False)
        except Exception:
            pass

        # 3. 默认配置字体
        if font in FONT_MAP:
            name = FONT_MAP[font]["filename"]
            cached = self.cache_fonts_dir / name
            if cached.exists():
                return str(cached)
            path = self._download(font)
            if path is None:
                return None
            return path

        # 4. 其他字体到 ~/.ai4one/fonts/ 目录再搜一次
        extra_dir = self.cache_fonts_dir
        for ext in ("*.ttf", "*.otf", "*.TTF", "*.OTF"):
            for fp in extra_dir.glob(ext):
                name = fm.FontProperties(fname=fp).get_name()
                if fp.stem.lower() == font.lower() or name == font:
                    return str(fp.resolve())
        return None

    def _register_font(self, path: str) -> str:
        """注册并返回内部名"""
        fm.fontManager.addfont(path)
        return fm.FontProperties(fname=path).get_name()

    def _download(self, name: str) -> str | None:
        import requests

        info = FONT_MAP[name]
        filename = info["filename"]
        for url in info["urls"]:
            try:
                print(f"下载 {name} 从 {url}")
                resp = requests.get(url, headers=HEADERS, timeout=30)
                resp.raise_for_status()
                dst = self.cache_fonts_dir / filename
                dst.write_bytes(resp.content)
                return str(dst)
            except Exception as e:
                warnings.warn(f"下载 {name} 失败（{url}）: {e}", UserWarning)
        return None

    def get_font_path(self, name: str) -> str | None:
        """
        按系统→缓存→下载的顺序返回指定字体的绝对路径。
        若找不到返回 None。
        """
        path = self._resolve(name)
        if path is None:
            return None
        return path


def setup_fonts(fonts: List[str] = []) -> "FontAutoConfig":
    """
    自动配置字体，根据系统字体、缓存字体、下载字体的顺序。
    """
    cfg = FontAutoConfig(fonts)
    cfg.apply()
    return cfg


if __name__ == "__main__":
    # 用户随意组合：系统字体名、绝对路径、相对路径
    user_list = [
        "Times New Roman",  # 系统
        "SimSun",  # 系统
        "SimHei",  # 系统
    ]

    cfg = setup_fonts(user_list)

    # 验证
    print("当前 font.family :", plt.rcParams["font.family"])

    # 绘图
    plt.figure(figsize=(4, 3))
    plt.plot([0, 1], [1, 4])
    plt.title("中国制造 Title Test 123")
    plt.xlabel("横轴 X-axis")
    plt.ylabel("纵轴 Y-axis")
    plt.savefig("test.png")
    plt.show()
