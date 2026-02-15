"""
Unit tests for rebalancing logic inside run_backtest.
Uses mock data; tests rebalance_frequency behavior.
"""

from __future__ import annotations

import pandas as pd
import pytest

from backtest_engine import run_backtest


def test_rebalance_frequency_none_never_rebalances(
    mock_monthly_returns_24: pd.DataFrame,
    sample_allocation: dict[str, float],
) -> None:
    """Buy & Hold: ไม่ rebalance ดังนั้นผลลัพธ์ขึ้นกับ drift ตาม return เท่านั้น."""
    result_none = run_backtest(
        mock_monthly_returns_24,
        sample_allocation,
        initial_capital=100_000.0,
        rebalance_frequency=None,
    )
    assert result_none["final_value"] > 0
    assert "total_return" in result_none


def test_rebalance_frequency_12_works(
    mock_monthly_returns_24: pd.DataFrame,
    sample_allocation: dict[str, float],
) -> None:
    """Annual rebalance ครบ 2 รอบ (เดือน 12 และ 24)."""
    result = run_backtest(
        mock_monthly_returns_24,
        sample_allocation,
        initial_capital=100_000.0,
        rebalance_frequency=12,
    )
    assert result["final_value"] > 0
    assert len(result["portfolio_history"]) == 24


def test_rebalance_frequency_6_works(
    mock_monthly_returns_24: pd.DataFrame,
    sample_allocation: dict[str, float],
) -> None:
    """Semi-annual rebalance ครบ 4 รอบ."""
    result = run_backtest(
        mock_monthly_returns_24,
        sample_allocation,
        initial_capital=100_000.0,
        rebalance_frequency=6,
    )
    assert result["final_value"] > 0
    assert len(result["portfolio_history"]) == 24


def test_rebalance_invalid_frequency_raises(
    mock_monthly_returns_24: pd.DataFrame,
    sample_allocation: dict[str, float],
) -> None:
    with pytest.raises(ValueError, match="rebalance_frequency"):
        run_backtest(
            mock_monthly_returns_24,
            sample_allocation,
            initial_capital=100_000.0,
            rebalance_frequency=0,
        )
    with pytest.raises(ValueError, match="rebalance_frequency"):
        run_backtest(
            mock_monthly_returns_24,
            sample_allocation,
            initial_capital=100_000.0,
            rebalance_frequency=-1,
        )
