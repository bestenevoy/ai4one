import shutil
import subprocess
import os

def clear_dist():
    """Remove the dist/ directory if it exists."""
    dist_path = "dist"
    if os.path.exists(dist_path):
        shutil.rmtree(dist_path)
        print("Cleared dist/ directory")
    else:
        print("No dist/ directory found")

def build_package():
    """Run uv build."""
    print("Building package with uv...")
    subprocess.run(["uv", "build"], check=True)
    print("Build completed")

def main():
    try:
        clear_dist()
        build_package()
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
