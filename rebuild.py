import os
import sys
import glob
import shutil
import subprocess

def ensure_build_tools():
    """确保构建工具已安装"""
    required = ["build", "wheel", "twine"]
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            print(f"Installing missing package: {pkg}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])


def main():
    ensure_build_tools()
    try:
        # 清理旧的构建文件
        print("Cleaning old build files...")
        if os.path.exists('dist'):
            shutil.rmtree('dist')
        # if os.path.exists('build'):  # 注释掉的构建目录清理
        #     shutil.rmtree('build')
        # if os.path.exists('*.egg-info'):  # 注释掉的元数据清理
        #     os.remove(glob.glob('*.egg-info')[0])

        # 重新打包 Python 包
        print("Rebuilding package...")
        subprocess.run([sys.executable, "-m", "build"], check=True)

        # 设置文件路径模式
        pattern = os.path.join("dist", "ai4one-*-py3-none-any.whl")
        files = glob.glob(pattern)

        # 检查文件是否存在
        if not files:
            print(f"No matching .whl file found in pattern: {pattern}")
            return

        # 处理找到的所有匹配文件
        for whl_file in files:
            print(f"Found: {whl_file}")
            
            # 先卸载现有版本
            print("Uninstalling existing package...")
            subprocess.run(
                [sys.executable, "-m", "pip", "uninstall", "ai4one", "-y"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # 安装新版本
            print(f"Installing new version from: {whl_file}")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", whl_file],
                check=True
            )

        print(".whl file found and successfully reinstalled.")
    
    except subprocess.CalledProcessError as e:
        print(f"Error during execution: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)
    finally:
        input("Done! Press Enter to exit...")

if __name__ == "__main__":
    main()
    