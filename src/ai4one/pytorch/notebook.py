import os
from pathlib import Path
from typing import Optional

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


def get_notebook_work_dir(_file_: Optional[Path] = None) -> Path:
    if _file_ is None:
        return Path(os.getcwd())
    return Path(_file_).parent
