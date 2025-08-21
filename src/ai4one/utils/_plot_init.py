import matplotlib.pyplot as plt
import warnings
warnings.warn(
    "本模块（ai4one.utils._plot_init）将在 v0.4.0 被移除，请使用\n"
    "from ai4one.tools.plt import setup_fonts\n"
    "setup_fonts()\n",
    DeprecationWarning, stacklevel=2
)
plt.rcParams['font.family'] = ['SimHei', 'Microsoft YaHei', 'sans-serif']
