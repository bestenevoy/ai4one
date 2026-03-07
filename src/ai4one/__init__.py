"""AI4One - A lightweight, modular toolkit for building AI-powered applications."""

from .config import BaseConfig
from .notifier import Notifier, QQEmailNotifier

__version__ = "0.3.2"

__all__ = [
    "BaseConfig",
    "Notifier",
    "QQEmailNotifier",
]
