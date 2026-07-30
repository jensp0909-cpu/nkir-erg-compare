import pytest

from common.time_parse import format_seconds, parse_time


def test_parse_dutch_format():
    assert parse_time("06:02,0") == 362.0


def test_parse_dot_format():
    assert parse_time("6:02.0") == 362.0


def test_parse_no_fraction():
    assert parse_time("6:02") == 362.0


def test_parse_with_hours():
    assert parse_time("1:00:00") == 3600.0


def test_parse_blank_returns_none():
    assert parse_time("") is None
    assert parse_time(None) is None
    assert parse_time("   ") is None


def test_parse_invalid_raises():
    with pytest.raises(ValueError):
        parse_time("DNF")


def test_format_seconds_roundtrip():
    assert format_seconds(362.0) == "6:02.0"
