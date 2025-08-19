import os
import sys
import time

import typer
import subprocess
from rich import print

from ..tools.visual_call_graph import ProjectAnalyzer


app = typer.Typer(no_args_is_help=True)


@app.callback()
def callback():
    """
    Awesome AI CLI tool under development.
    """
    pass


@app.command(name="gpu")
def nvidia_info(
    refresh: bool = typer.Option(
        False, "--refresh", "-r", help="Enable real-time refresh"
    ),
    interval: float = typer.Option(
        2.0, "--interval", "-i", help="Refresh interval in seconds"
    ),
):
    """
    Check GPU driver information, PyTorch version, Python version, and Python executable path.

    Use --refresh or -r to enable real-time monitoring.
    Use --interval or -i to set the refresh interval (default: 2 seconds).
    """

    # 检查 nvidia-smi 是否存在
    def check_nvidia_smi():
        try:
            subprocess.run(
                ["nvidia-smi", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,  # 如果命令返回非零状态码会抛出异常
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    # 清屏函数，跨平台支持
    def clear_screen():
        os.system("cls" if os.name == "nt" else "clear")

    pytorch_info = ""
    try:
        import torch
        pytorch_info = f"PyTorch Version: {torch.__version__}\nCuda is available: {torch.cuda.is_available()}"
    except ImportError:
        pytorch_info = "[bold red]PyTorch is not installed.[/bold red]"

    # 获取 Python 版本和执行路径
    python_info = (
        f"Python Version: {sys.version}\nPython Executable Path: {sys.executable}"
    )

    # 显示 NVIDIA-SMI 信息的函数
    def show_gpu_info():
        result = subprocess.run(
            ["nvidia-smi"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # 返回文本（字符串）而不是字节
        )
        output = result.stdout
        error_output = result.stderr
        if result.returncode == 0:
            content = "\r\n".join(output.splitlines()[1:12])
            first_line = output.splitlines()[0]
            lenght = len(output.splitlines()[3])
            print("INFO".center(lenght, "="))
            print(f"Current Time: [green]{first_line}[/green]")
            print(content)
        else:
            print("NVIDIA-SMI Error Output:")
            print(error_output)

        if refresh:
            print(
                f"\n[italic cyan]Refreshing GPU info every {interval} seconds. Press Ctrl+C to exit.[/italic cyan]"
            )
    NOT_NS = "[bold red]Error: nvidia-smi not found. Please ensure NVIDIA drivers are installed.[/bold red]"
    # 是否需要实时刷新
    if refresh:
        try:
            if not check_nvidia_smi():
                print(NOT_NS)
                return
            while True:
                clear_screen()
                show_gpu_info()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n[bold green]GPU monitoring stopped.[/bold green]")
    else:
        if not check_nvidia_smi():
            print(NOT_NS)
        else:
            show_gpu_info()

        print("\n" + pytorch_info)
        print("\n" + python_info)


@app.command()
def test(name: str = typer.Option(None, "--name", "-n", help="this is a test param")):
    """
    this is test
    """
    print("It looks like it's correct.")


@app.command()
def callgraph(
    path: str = typer.Argument(
        ..., help="Path to the Python file or project directory to analyze."
    ),
    output: str = typer.Option(
        "call_graph.dot", "--output", "-o", help="Output path for the .dot file."
    ),
):
    """
    Generates a focused, intra-project function call graph.

    Analyzes a single Python file or an entire project directory and
    creates a .dot file representing the internal call structure.
    """
    target_path = os.path.abspath(path)
    print(f"🔍 Analyzing target: [bold cyan]{target_path}[/bold cyan]")

    project_root = None
    files_to_analyze = None

    if not os.path.exists(target_path):
        print(
            f"[bold red]Error:[/bold red] The provided path '{target_path}' does not exist."
        )
        raise typer.Exit(code=1)

    if os.path.isfile(target_path):
        # 如果是文件，项目根目录是其所在目录，分析列表只包含它自己
        print("Mode: Single File Analysis")
        project_root = os.path.dirname(target_path)
        files_to_analyze = [target_path]
    elif os.path.isdir(target_path):
        # 如果是目录，项目根目录就是它自己，分析列表由脚本自动发现
        print("Mode: Project Directory Analysis")
        project_root = target_path
        # files_to_analyze 保持为 None, 让 analyze 方法自己去发现
        files_to_analyze = None

    try:
        # 实例化并运行分析器
        analyzer = ProjectAnalyzer(project_root)
        analyzer.analyze(files_to_analyze=files_to_analyze)
        analyzer.generate_dot_file(output)  # 调用新的生成方法
        print(
            "\n[bold green]✨ Analysis complete! You can now render the DOT file with Graphviz:[/bold green]"
        )
        print(f"dot -Tpng {output} -o {os.path.splitext(output)[0]}.png")
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        import traceback

        traceback.print_exc()  # 打印详细的错误堆栈，便于调试
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
