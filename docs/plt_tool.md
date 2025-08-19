## 📦 Font Tools - 自动配置 matplotlib 中英文字体
### 🎯 核心功能
- ✅ 自动检测系统字体
- ✅ 按需下载缺失字体（Times New Roman/SimSun/SimHei）
- ✅ 支持本地字体文件注册
- ✅ 跨平台兼容（Windows/Linux/macOS）
- ✅ 智能缓存管理
---
## 🚀 快速开始
### 基础用法
```python
from ai4one.tools.plt import setup_fonts
# 一键配置中英文字体
setup_fonts([
    "Times New Roman",          # 系统字体/自动下载
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
---
## 📁 字体管理方案
### 1. 内置字体（自动下载）
| 字体名 | 用途 | 自动下载文件名 |
|--------|------|----------------|
| `Times New Roman` | 英文衬线 | `TimesNewRoman.ttf` |
| `SimSun` | 中文宋体 | `SimSun.ttf` |
| `SimHei` | 中文黑体 | `SimHei.ttf` |

**下载位置**：`~/.ai4one/fonts/`

### 2. 自定义字体
#### 来源推荐
- Adobe 开源字体：https://github.com/adobe-fonts
- Google Fonts：https://fonts.google.com
#### 安装方式
```python
# 方式1：直接指定路径
setup_fonts(["/path/to/your/font.ttf"])
# 方式2：放入缓存目录
# 1. 将字体文件复制到 ~/.ai4one/fonts/
# 2. 使用文件名（可省略扩展名）
setup_fonts(["MyCustomFont"])
```
### 3. 缓存目录结构
```
~/.ai4one/fonts/
├── TimesNewRoman.ttf     # 自动下载
├── SimSun.ttf            # 自动下载
├── SimHei.ttf            # 自动下载
├── FiraCode-Regular.ttf  # 用户添加
└── MyCustomFont.otf      # 用户添加
```
---
## 🔧 API 参考
### `setup_fonts(fonts: List[str]) -> FontAutoConfig`
一键配置字体，返回配置器实例。
**参数**：
- `fonts`: 字体列表，支持：
  - 系统字体名称（如 `"Times New Roman"`）
  - 文件路径（相对或绝对）
  - 缓存目录中的字体名（可省略扩展名）
**返回**：
- `FontAutoConfig` 实例
---
## 💡 最佳实践
### 1. 生产环境建议
```python
# 推荐的字体配置顺序
fonts = [
    "Times New Roman",  # 优先英文
    "SimSun",           # 中文衬线
    "SimHei",           # 中文黑体（备用）
    "./assets/brand-font.ttf"  # 自定义品牌字体
]
fcfg = setup_fonts(fonts)
```
### 2. 离线环境部署
```python
# 1. 事先下载好字体文件
# 2. 放入缓存目录 ~/.ai4one/fonts/
# 3. 配置时直接使用字体名
setup_fonts(["Times New Roman", "SimSun"])
```