"""
Unit tests for pure utility functions (no CLI / no I/O).
"""

from __future__ import annotations

import pytest

from capital_input import parse_initial_cash


def test_parse_initial_cash_accepts_integer_string() -> None:
    assert parse_initial_cash("100000") == 100_000.0


def test_parse_initial_cash_accepts_comma() -> None:
    assert parse_initial_cash("100,000") == 100_000.0
    assert parse_initial_cash("1,000,000") == 1_000_000.0


def test_parse_initial_cash_strips_whitespace() -> None:
    assert parse_initial_cash("  50000  ") == 50_000.0


def test_parse_initial_cash_zero_raises() -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        parse_initial_cash("0")
    with pytest.raises(ValueError, match="greater than zero"):
        parse_initial_cash("-100")


def test_parse_initial_cash_invalid_raises() -> None:
    with pytest.raises(ValueError, match="valid number"):
        parse_initial_cash("abc")
    with pytest.raises(ValueError, match="valid number"):
        parse_initial_cash("12.34.56")


def test_parse_initial_cash_empty_raises() -> None:
    with pytest.raises(ValueError):
        parse_initial_cash("")
    with pytest.raises(ValueError):
        parse_initial_cash("   ")
