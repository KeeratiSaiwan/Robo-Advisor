"""
Unit tests for risk_profiling: get_allocation() only.
No CLI, no I/O.
"""

from __future__ import annotations

import math

import pytest

from risk_profiling import get_allocation


def test_get_allocation_returns_dict() -> None:
    for level in ("low", "medium", "high"):
        result = get_allocation(level)
        assert isinstance(result, dict)
        assert all(isinstance(k, str) and isinstance(v, (int, float)) for k, v in result.items())


def test_allocation_sums_to_one() -> None:
    for level in ("low", "medium", "high"):
        result = get_allocation(level)
        total = sum(result.values())
        assert math.isclose(total, 1.0, rel_tol=1e-9, abs_tol=1e-9)


def test_high_risk_has_more_equity_than_low() -> None:
    low = get_allocation("low")
    high = get_allocation("high")
    vti_low = low.get("VTI", 0) + low.get("VXUS", 0)
    vti_high = high.get("VTI", 0) + high.get("VXUS", 0)
    assert vti_high > vti_low


def test_moderate_between_low_and_high() -> None:
    low = get_allocation("low")
    med = get_allocation("medium")
    high = get_allocation("high")
    equity_low = low.get("VTI", 0) + low.get("VXUS", 0)
    equity_med = med.get("VTI", 0) + med.get("VXUS", 0)
    equity_high = high.get("VTI", 0) + high.get("VXUS", 0)
    assert equity_low <= equity_med <= equity_high


def test_invalid_risk_level_raises() -> None:
    with pytest.raises(ValueError, match="Invalid risk level"):
        get_allocation("invalid")
    with pytest.raises(ValueError, match="Invalid risk level"):
        get_allocation("")
    with pytest.raises(ValueError, match="Invalid risk level"):
        get_allocation("x")


def test_risk_level_case_insensitive() -> None:
    a1 = get_allocation("low")
    a2 = get_allocation("LOW")
    a3 = get_allocation("Low")
    assert a1 == a2 == a3
