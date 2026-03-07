"""Utility functions for ai4one."""

import sys
import uuid
from datetime import datetime

from .file import load_json, dump_json, read_file, get_work_dir
from .func import get_current_function_name
from .chrono import (
    now_iso,
    now_compact,
    now_for_filename,
    timestamp,
    timestamp_ms,
    ts_to_iso,
    parse_duration,
    parse_datetime,
    humanize_delta,
    ago,
    sleep_for,
    sleep_until,
    tic,
    toc,
    day_bounds,
    week_bounds,
)


def fmt_filename(input_string: str) -> str:
    """Format a string as a valid filename (lowercase, underscores for spaces)."""
    if not isinstance(input_string, str):
        raise ValueError("Input must be a string")
    return "_".join(input_string.strip().casefold().split())


def gen_filename_from_kwargs(utc_time: bool = False, **kwargs) -> str:
    """Generate a unique filename from keyword arguments with timestamp."""
    parts = [f"{k.lower()}-{v}" for k, v in kwargs.items()]
    if utc_time:
        ts = datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    else:
        ts = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    return f"{ts}_" + "_".join(parts) + "_" + uuid.uuid4().hex[:8]


def fmt_args_to_short_command() -> str:
    """Get command line arguments as a short command string."""
    return " ".join(sys.argv[1:])


def fmt_args_to_command(args) -> str:
    """Format parsed arguments back to command line string."""
    result = []
    for key, value in vars(args).items():
        if value is not None:
            result.append(f"--{key} {value}")
        else:
            result.append(key)
    return " ".join(result)


__all__ = [
    # file
    "load_json",
    "dump_json",
    "read_file",
    "get_work_dir",
    # func
    "get_current_function_name",
    "fmt_filename",
    "gen_filename_from_kwargs",
    "fmt_args_to_short_command",
    "fmt_args_to_command",
    # chrono
    "now_iso",
    "now_compact",
    "now_for_filename",
    "timestamp",
    "timestamp_ms",
    "ts_to_iso",
    "parse_duration",
    "parse_datetime",
    "humanize_delta",
    "ago",
    "sleep_for",
    "sleep_until",
    "tic",
    "toc",
    "day_bounds",
    "week_bounds",
]
