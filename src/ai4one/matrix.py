import numpy as np
from numpy.typing import ArrayLike


def fill_zero_by_matrix(x: ArrayLike, y: ArrayLike):
    """
    使用 y 中非零的值来填充 x 中的零值
    """
    return np.where(x == 0, y, x)
