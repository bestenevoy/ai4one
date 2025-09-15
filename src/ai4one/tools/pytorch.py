import torch
import random
import numpy as np


def get_device(num=None, debug=False, verbose=True):
    """自动选择可用设备（GPU/CPU），支持多卡和调试模式。
    
    Args:
        num (int, optional): 指定 GPU 编号。若为 None 或 CUDA 不可用，返回 CPU。
        debug (bool): 是否强制使用 CPU（用于调试）。
        verbose (bool): 是否打印设备信息（默认 True）。
    
    Returns:
        torch.device: 计算设备对象。
    """
    if debug:
        if verbose:
            print("Debug mode: Using CPU.")
        return torch.device('cpu')
    
    if not torch.cuda.is_available():
        if verbose:
            print("CUDA not available. Using CPU.")
        return torch.device('cpu')
    
    # 处理 GPU 选择逻辑
    if num is not None:
        if num < 0 or num >= torch.cuda.device_count():
            if verbose:
                print(f"Warning: GPU {num} not available. Using GPU 0 instead.")
            num = 0  # 回退到 GPU 0
        device = torch.device(f'cuda:{num}')
    else:
        num = 0
        device = torch.device('cuda')  # 默认当前 GPU（cuda:0）
    
    if verbose:
        print(f"Using device: {device} (GPU {num if num is not None else 0})")
        print(torch.cuda.get_device_name(num))
    return device


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
