import os
import sys
import time

import typer
import subprocess
from rich import print

app = typer.Typer(no_args_is_help=True)


@app.callback()
def callback():
    """
    Awesome AI CLI tool under development.
    """
    pass


@app.command(name="gpu")
def nvidia_info(
    refresh: bool = typer.Option(False, "--refresh", "-r", help="Enable real-time refresh"),
    interval: float = typer.Option(2.0, "--interval", "-i", help="Refresh interval in seconds")
):
    """
    Check GPU driver information, PyTorch version, Python version, and Python executable path.

    Use --refresh or -r to enable real-time monitoring.
    Use --interval or -i to set the refresh interval (default: 2 seconds).
    """

    # 清屏函数，跨平台支持
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')
        
    pytorch_info = ""
    try:
        import torch
        pytorch_info = f"PyTorch Version: {torch.__version__}\nCuda is available: {torch.cuda.is_available()}"
    except ImportError:
        pytorch_info = "[bold red]PyTorch is not installed.[/bold red]"
    
    # 获取 Python 版本和执行路径
    python_info = f"Python Version: {sys.version}\nPython Executable Path: {sys.executable}"
    
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
        
        # 打印 PyTorch 信息
        print("\n" + pytorch_info)
        # 打印 Python 信息
        print("\n" + python_info)
        
        if refresh:
            print(f"\n[italic cyan]Refreshing GPU info every {interval} seconds. Press Ctrl+C to exit.[/italic cyan]")
    
    # 是否需要实时刷新
    if refresh:
        try:
            while True:
                clear_screen()
                show_gpu_info()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n[bold green]GPU monitoring stopped.[/bold green]")
    else:
        show_gpu_info()


@app.command()
def test(name: str = typer.Option(None, "--name", "-n", help="this is a test param")):
    """
    this is test
    """
    print("It looks like it's correct.")


if __name__ == "__main__":
    app()
