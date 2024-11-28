# mycli/cli.py
import typer
import subprocess
from rich import print

app = typer.Typer()


@app.command(name="gpu")
def nvidia_info():
    """查看 gpu 驱动信息 和 pytorch 版本"""
    result = subprocess.run(
        ["nvidia-smi"],
        stdout=subprocess.PIPE,  # 捕获标准输出
        stderr=subprocess.PIPE,  # 捕获错误输出
        text=True,  # 返回文本（字符串）而不是字节
    )
    output = result.stdout
    error_output = result.stderr
    if result.returncode == 0:
        content = "\r\n".join(output.splitlines()[1:12])  # 截取前5行
        first_line = output.splitlines()[0]
        lenght = len(output.splitlines()[3])
        print("INFO".center(lenght, "="))
        print(f"Current Time: [green]{first_line}[/green]")
        print(content)
    else:
        print("NVIDIA-SMI Error Output:")
        print(error_output)
    try:
        import torch
    except ImportError:
        print("[bold red]PyTorch is not installed.[/bold red]")
    else:
        print("PyTorch Version:", torch.__version__)
        print("Cuda is available:", torch.cuda.is_available())


@app.command()
def test(name: str = typer.Option(None, "--name", "-n", help="测试参数")):
    """this is test"""
    print("It looks like it's correct.")


if __name__ == "__main__":
    app()
