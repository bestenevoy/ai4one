"""Tests for ai4one.utils module."""

import time
import pytest
from ai4one.utils import (
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
    tic,
    toc,
    day_bounds,
    week_bounds,
    load_json,
    dump_json,
    fmt_filename,
)


class TestChrono:
    """Tests for chrono time utilities."""

    def test_now_iso(self):
        """Test ISO time format."""
        result = now_iso()
        assert "T" in result
        assert result.endswith("Z") or "+" in result

    def test_now_iso_utc(self):
        """Test UTC ISO time."""
        result = now_iso(utc=True)
        assert result.endswith("Z")

    def test_now_compact(self):
        """Test compact time format."""
        result = now_compact()
        assert "-" in result
        assert len(result) >= 15  # YYYYMMDD-HHMMSS

    def test_now_for_filename(self):
        """Test filename-safe time format."""
        result = now_for_filename()
        assert "-" in result
        assert "_" in result

    def test_timestamp(self):
        """Test Unix timestamp."""
        ts = timestamp()
        assert isinstance(ts, int)
        assert ts > 1700000000  # After 2023

    def test_timestamp_ms(self):
        """Test millisecond timestamp."""
        ts = timestamp_ms()
        assert isinstance(ts, int)
        assert ts > 1700000000000

    def test_ts_to_iso(self):
        """Test timestamp to ISO conversion."""
        ts = 1700000000
        result = ts_to_iso(ts)
        assert "2023" in result

    def test_parse_duration_seconds(self):
        """Test parsing duration in seconds."""
        assert parse_duration("30s") == 30
        assert parse_duration("90s") == 90

    def test_parse_duration_minutes(self):
        """Test parsing duration in minutes."""
        assert parse_duration("2m") == 120
        assert parse_duration("1.5m") == 90

    def test_parse_duration_hours(self):
        """Test parsing duration in hours."""
        assert parse_duration("1h") == 3600
        assert parse_duration("2h") == 7200

    def test_parse_duration_combined(self):
        """Test parsing combined duration."""
        assert parse_duration("1h30m") == 5400
        assert parse_duration("2m10s") == 130

    def test_parse_duration_number(self):
        """Test parsing raw number as seconds."""
        assert parse_duration(60) == 60
        assert parse_duration("60") == 60

    def test_parse_datetime_keywords(self):
        """Test parsing datetime keywords."""
        from datetime import datetime

        now = parse_datetime("now")
        assert isinstance(now, datetime)

        today = parse_datetime("today")
        assert today.hour == 0
        assert today.minute == 0

    def test_parse_datetime_iso(self):
        """Test parsing ISO datetime."""
        from datetime import datetime

        result = parse_datetime("2024-01-15T10:30:00Z")
        assert isinstance(result, datetime)
        assert result.year == 2024

    def test_humanize_delta_seconds(self):
        """Test humanizing seconds."""
        assert humanize_delta(30) == "30s"
        assert humanize_delta(90) == "1m30s"

    def test_humanize_delta_hours(self):
        """Test humanizing hours."""
        assert humanize_delta(3600) == "1h"
        assert humanize_delta(3661) == "1h1m1s"  # 1h + 1m + 1s

    def test_humanize_delta_ms(self):
        """Test humanizing milliseconds."""
        assert humanize_delta(0.5) == "500ms"

    def test_tic_toc(self):
        """Test timer functions."""
        t0 = tic()
        time.sleep(0.1)
        elapsed = toc(t0)
        assert elapsed >= 0.1
        assert elapsed < 1.0

    def test_toc_formatted(self):
        """Test formatted toc output."""
        t0 = tic()
        time.sleep(0.1)
        result = toc(t0, fmt=True)
        assert isinstance(result, str)
        assert "s" in result or "ms" in result

    def test_day_bounds(self):
        """Test day bounds."""
        start, end = day_bounds()
        assert "T00:00:00" in start or "00:00" in start

    def test_week_bounds(self):
        """Test week bounds."""
        start, end = week_bounds()
        assert start < end


class TestFile:
    """Tests for file utilities."""

    def test_fmt_filename(self):
        """Test filename formatting."""
        assert fmt_filename("Hello World") == "hello_world"
        assert fmt_filename("Test File Name") == "test_file_name"
        assert fmt_filename("UPPERCASE") == "uppercase"

    def test_fmt_filename_invalid(self):
        """Test filename with invalid input."""
        with pytest.raises(ValueError):
            fmt_filename(123)  # type: ignore

    def test_json_roundtrip(self, tmp_path):
        """Test JSON write and read."""
        data = {"name": "test", "value": 42, "items": [1, 2, 3]}
        file_path = tmp_path / "test.json"

        assert dump_json(data, file_path) is True
        loaded = load_json(file_path)
        assert loaded == data

    def test_load_json_missing_file(self):
        """Test loading missing JSON file."""
        result = load_json("/nonexistent/path/file.json")
        assert result is None
