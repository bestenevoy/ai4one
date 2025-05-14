import os
from pathlib import Path
from .utils.file import get_work_dir

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


def get_notebook_work_dir() -> Path:
    return get_work_dir()
