from __future__ import annotations

import re
import time as _time
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Union


# ===== 基础内部工具 =====

def _local_tz():
    """获取本地时区对象（含偏移），用于生成感知时区的时间。"""
    return datetime.now().astimezone().tzinfo


def _aware_now(utc: bool = False) -> datetime:
    """返回当前时间（时区感知）。

    Args:
        utc: True 返回 UTC 时间，False 返回本地时间。
    """
    return datetime.now(timezone.utc) if utc else datetime.now().astimezone()


def _iso_format(dt: datetime, ms: bool = True) -> str:
    """将 datetime 格式化为 ISO 8601 字符串。

    - 对 UTC 时间，使用末尾 Z
    - 对本地时间，包含时区偏移
    """
    if ms:
        s = dt.isoformat(timespec="milliseconds")
    else:
        s = dt.isoformat(timespec="seconds")
    # 将 +00:00 规范化为 Z
    if dt.tzinfo is not None and dt.utcoffset() == timedelta(0):
        s = s.replace("+00:00", "Z")
    return s


# ===== 对外便捷 API（推荐给大模型） =====

def now_iso(utc: bool = True, ms: bool = True) -> str:
    """返回当前时间的 ISO 8601 字符串。

    Args:
        utc: 是否使用 UTC 时间（末尾 Z）。False 则返回本地时间并带偏移。
        ms: 是否包含毫秒。
    """
    return _iso_format(_aware_now(utc=utc), ms=ms)


def now_compact(utc: bool = True, ms: bool = False) -> str:
    """返回紧凑格式时间，用于日志/ID：YYYYMMDD-HHMMSS[.mmm]。

    Args:
        utc: True 则使用 UTC 时间。
        ms: 是否包含毫秒（3位）。
    """
    dt = _aware_now(utc=utc)
    base = dt.strftime("%Y%m%d-%H%M%S")
    if ms:
        milli = int(dt.microsecond / 1000)
        base = f"{base}.{milli:03d}"
    return base


def now_for_filename(utc: bool = True, ms: bool = False) -> str:
    """返回适合文件名的时间：YYYY-MM-DD_HH-MM-SS[.mmm]

    与 repo 中常见命名风格保持一致，避免文件系统不友好的字符。
    """
    dt = _aware_now(utc=utc)
    base = dt.strftime("%Y-%m-%d_%H-%M-%S")
    if ms:
        milli = int(dt.microsecond / 1000)
        base = f"{base}.{milli:03d}"
    return base


def timestamp() -> int:
    """返回当前 Unix 时间戳（秒，整数）。"""
    return int(_time.time())


def timestamp_ms() -> int:
    """返回当前 Unix 时间戳（毫秒，整数）。"""
    return int(_time.time() * 1000)


def ts_to_iso(ts: Union[int, float], utc: bool = True, ms: bool = True) -> str:
    """将时间戳转换为 ISO 字符串。

    Args:
        ts: Unix 时间戳（秒）。
        utc: True 用 UTC；False 用本地时区。
        ms: 是否包含毫秒。
    """
    tz = timezone.utc if utc else _local_tz()
    dt = datetime.fromtimestamp(float(ts), tz=tz)
    return _iso_format(dt, ms=ms)


# ===== 解析与格式化 =====

def parse_duration(s: Union[str, int, float]) -> float:
    """解析时长字符串为秒（float）。

    支持示例：
      - "90s" "2m" "1.5h" "2d" "800ms" "1h30m" "2m10s"
      - 纯数字视为秒
    """
    if isinstance(s, (int, float)):
        return float(s)

    text = str(s).strip().lower()
    if re.fullmatch(r"[+-]?\d+(?:\.\d+)?", text or ""):
        return float(text)

    # 支持组合，例如 "1h30m10s"，按单位逐个累计
    pattern = r"([+-]?\d+(?:\.\d+)?)(ms|s|m|h|d)"
    total = 0.0
    for num, unit in re.findall(pattern, text):
        val = float(num)
        if unit == "ms":
            total += val / 1000.0
        elif unit == "s":
            total += val
        elif unit == "m":
            total += val * 60
        elif unit == "h":
            total += val * 3600
        elif unit == "d":
            total += val * 86400
    if total == 0.0:
        raise ValueError(f"无法解析时长: {s}")
    return total


def parse_datetime(
    s: Union[str, int, float], *, tz: str = "local"
) -> datetime:
    """解析常见日期时间表示，返回时区感知的 datetime。

    Args:
        s: 字符串或（秒）时间戳；支持：
           - "now" / "today" / "yesterday" / "tomorrow"
           - 相对时长："-2h" "+30m"（基于当前时间）
           - ISO8601（含 Z/偏移）
           - 常见格式："YYYY-MM-DD HH:MM:SS"、"YYYY/MM/DD"、"YYYYMMDD" 等
           - 纯数字：自动识别秒/毫秒级时间戳
        tz: "utc" 或 "local"，当输入为无时区信息的日期字符串时使用该默认时区。
    """
    def default_tzinfo():
        return timezone.utc if tz == "utc" else _local_tz()

    if isinstance(s, (int, float)):
        # 认为是秒级时间戳
        return datetime.fromtimestamp(float(s), tz=default_tzinfo())

    text = str(s).strip()
    lower = text.lower()

    # 关键词
    if lower == "now":
        return _aware_now(utc=(tz == "utc"))
    if lower == "today":
        base = _aware_now(utc=(tz == "utc")).replace(hour=0, minute=0, second=0, microsecond=0)
        return base
    if lower == "yesterday":
        base = _aware_now(utc=(tz == "utc")).replace(hour=0, minute=0, second=0, microsecond=0)
        return base - timedelta(days=1)
    if lower == "tomorrow":
        base = _aware_now(utc=(tz == "utc")).replace(hour=0, minute=0, second=0, microsecond=0)
        return base + timedelta(days=1)

    # 相对时长：以当前时间为基准
    if re.fullmatch(r"[+-].+", lower):
        seconds = parse_duration(lower)
        return _aware_now(utc=(tz == "utc")) + timedelta(seconds=seconds)

    # 可能是纯数字时间戳（秒/毫秒）
    if re.fullmatch(r"\d{10,16}", lower):
        val = float(lower)
        if val > 1e12:  # 毫秒
            val /= 1000.0
        return datetime.fromtimestamp(val, tz=default_tzinfo())

    # ISO8601，兼容 Z
    iso_candidate = lower.replace("z", "+00:00") if lower.endswith("z") else text
    try:
        dt = datetime.fromisoformat(iso_candidate)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=default_tzinfo())
        return dt
    except Exception:
        pass

    # 常见格式列表（无 tz 的按 tz 赋值）
    fmts = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%Y%m%d",
    ]
    for fmt in fmts:
        try:
            dt = datetime.strptime(text, fmt)
            return dt.replace(tzinfo=default_tzinfo())
        except Exception:
            continue

    raise ValueError(f"无法解析日期时间: {s}")


def humanize_delta(delta: Union[timedelta, float, int], max_units: int = 3) -> str:
    """将时长友好化为紧凑字符串，如 2d3h4m、3h2m、5s、800ms。

    Args:
        delta: timedelta 或 秒数。
        max_units: 最多显示的单位数量（例如 2 -> 2h30m）。
    """
    if isinstance(delta, timedelta):
        total_ms = int(delta.total_seconds() * 1000)
    else:
        total_ms = int(float(delta) * 1000)

    if total_ms < 1000:
        return f"{total_ms}ms"

    seconds = total_ms // 1000
    ms = total_ms % 1000

    parts = []
    days, seconds = divmod(seconds, 86400)
    if days:
        parts.append(f"{days}d")
    hours, seconds = divmod(seconds, 3600)
    if hours:
        parts.append(f"{hours}h")
    minutes, seconds = divmod(seconds, 60)
    if minutes:
        parts.append(f"{minutes}m")
    if seconds:
        parts.append(f"{seconds}s")
    if ms and not parts:
        parts.append(f"{ms}ms")

    return "".join(parts[:max_units]) if parts else "0s"


def ago(x: Union[datetime, float, int], *, now: Optional[datetime] = None) -> str:
    """返回类似 "3m ago"/"2h ago" 的相对时间描述（紧凑）。"""
    if now is None:
        now = _aware_now(utc=True)
    if isinstance(x, datetime):
        dt = x.astimezone(timezone.utc)
    else:
        dt = datetime.fromtimestamp(float(x), tz=timezone.utc)
    delta = now - dt
    h = humanize_delta(delta, max_units=1)
    return f"{h} ago"


# ===== 睡眠与等待 =====

def sleep_for(duration: Union[str, int, float]) -> None:
    """睡眠指定时长（支持字符串）。例如："1.5s"、"2m"、"1h30m"。"""
    seconds = parse_duration(duration)
    if seconds <= 0:
        return
    _time.sleep(seconds)


def sleep_until(target: Union[str, int, float, datetime], *, tz: str = "local") -> float:
    """睡眠直到目标时间，返回实际睡眠秒数。

    Args:
        target: 目标时间，支持 parse_datetime 的全部输入；数字视为秒级时间戳。
        tz: 当 target 为无时区信息字符串时使用的默认时区。
    """
    if isinstance(target, (int, float)):
        t_dt = datetime.fromtimestamp(float(target), tz=timezone.utc if tz == "utc" else _local_tz())
    else:
        t_dt = parse_datetime(target, tz=tz)

    now = _aware_now(utc=False)
    seconds = (t_dt - now).total_seconds()
    if seconds > 0:
        _time.sleep(seconds)
        return seconds
    return 0.0


# ===== 简易计时器 =====

def tic() -> float:
    """开始计时，返回起始时间戳（perf_counter）。"""
    return _time.perf_counter()


def toc(t0: float, *, fmt: bool = False) -> Union[float, str]:
    """结束计时，返回耗时秒数；若 fmt=True 则返回人类友好字符串。"""
    elapsed = _time.perf_counter() - t0
    return humanize_delta(elapsed) if fmt else elapsed


# ===== 常见边界 =====

def day_bounds(dt: Optional[Union[str, datetime]] = None, *, tz: str = "local") -> Tuple[str, str]:
    """返回某一天的 [起, 止) ISO 区间（含起始，不含结束）。

    Args:
        dt: 为 None 表示今天；字符串/时间支持 parse_datetime；
        tz: 默认时区（当 dt 为无 tz 字符串时）。
    Returns:
        (start_iso, end_iso)
    """
    base = parse_datetime("today" if dt is None else dt, tz=tz)
    start = base.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return _iso_format(start), _iso_format(end)


def week_bounds(dt: Optional[Union[str, datetime]] = None, *, tz: str = "local", week_start: int = 1) -> Tuple[str, str]:
    """返回某一周的 [起, 止) ISO 区间（含起始，不含结束）。

    Args:
        dt: 参考日期；None 表示当前日期；
        tz: 默认时区；
        week_start: 一周起始，1=周一，0=周日。
    """
    ref = parse_datetime("now" if dt is None else dt, tz=tz)
    weekday = (ref.weekday() + 1) % 7  # 0=周一 -> 0..6
    if week_start == 0:
        # 以周日为一周开始
        days_from_start = (weekday + 1) % 7
    else:
        # 以周一为一周开始
        days_from_start = weekday
    start = ref.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_from_start)
    end = start + timedelta(days=7)
    return _iso_format(start), _iso_format(end)


__all__ = [
    # now / formatters
    "now_iso",
    "now_compact",
    "now_for_filename",
    "timestamp",
    "timestamp_ms",
    "ts_to_iso",
    # parse
    "parse_duration",
    "parse_datetime",
    # humanize
    "humanize_delta",
    "ago",
    # sleep/wait
    "sleep_for",
    "sleep_until",
    # timer
    "tic",
    "toc",
    # ranges
    "day_bounds",
    "week_bounds",
]