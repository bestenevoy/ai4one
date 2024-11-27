import torch
import random
import numpy as np


class NoneNegClipper(object):
    """
    这个 NoneNegClipper 类定义了一个权重裁剪器，用于确保神经网络中某些权重不会变成负数。
    具体来说，该类会在模型训练过程中将权重强制修正为非负数，保证所有权重值都大于或等于零。
    """

    def __init__(self):
        super(NoneNegClipper, self).__init__()

    def __call__(self, module):
        if hasattr(module, "weight"):
            w = module.weight.data
            a = torch.relu(torch.neg(w))
            w.add_(a)


# ---------------------------------------------------#
#   设置种子
# ---------------------------------------------------#
def seed_everything(seed=24):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
