"""
Unit tests for backtest_engine: run_backtest() only.
Uses mock monthly_returns (no real API/network).
"""

from __future__ import annotations

import pandas as pd
import pytest

from backtest_engine import run_backtest


REQUIRED_KEYS = {"portfolio_history", "final_value", "total_return", "cagr"}


def test_return_has_required_keys(
    mock_monthly_returns: pd.DataFrame,
    sample_allocation: dict[str, float],
) -> None:
    returns = mock_monthly_returns
    alloc = sample_allocation
    result = run_backtest(returns, alloc, initial_capital=100_000.0)
    for key in REQUIRED_KEYS:
        assert key in result, f"Missing key: {key}"


def test_initial_capital_positive_gives_positive_final_value(
    mock_monthly_returns: pd.DataFrame,
    sample_allocation: dict[str, float],
) -> None:
    returns = mock_monthly_returns
    alloc = sample_allocation
    result = run_backtest(returns, alloc, initial_capital=100_000.0)
    assert result["final_value"] > 0


def test_rebalance_frequency_none_works(
    mock_monthly_returns: pd.DataFrame,
    sample_allocation: dict[str, float],
) -> None:
    returns = mock_monthly_returns
    alloc = sample_allocation
    result = run_backtest(
        returns, alloc, initial_capital=10_000.0, rebalance_frequency=None
    )
    assert result["final_value"] > 0
    assert "total_return" in result
    assert "cagr" in result


def test_rebalance_frequency_twelve_works(
    mock_monthly_returns: pd.DataFrame,
    sample_allocation: dict[str, float],
) -> None:
    returns = mock_monthly_returns
    alloc = sample_allocation
    result = run_backtest(
        returns, alloc, initial_capital=10_000.0, rebalance_frequency=12
    )
    assert result["final_value"] > 0


def test_allocation_sum_not_one_raises(
    mock_monthly_returns: pd.DataFrame,
) -> None:
    returns = mock_monthly_returns
    bad_alloc = {"VTI": 0.5, "VXUS": 0.3}
    with pytest.raises(ValueError, match="sum to 1.0"):
        run_backtest(returns, bad_alloc, initial_capital=10_000.0)


def test_initial_capital_zero_raises(
    mock_monthly_returns: pd.DataFrame,
    sample_allocation: dict[str, float],
) -> None:
    returns = mock_monthly_returns
    alloc = sample_allocation
    with pytest.raises(ValueError, match="greater than 0"):
        run_backtest(returns, alloc, initial_capital=0)
    with pytest.raises(ValueError, match="greater than 0"):
        run_backtest(returns, alloc, initial_capital=-100)


def test_portfolio_history_length_matches_input(
    mock_monthly_returns: pd.DataFrame,
    sample_allocation: dict[str, float],
) -> None:
    returns = mock_monthly_returns
    alloc = sample_allocation
    result = run_backtest(returns, alloc, initial_capital=10_000.0)
    hist = result["portfolio_history"]
    assert len(hist) == len(returns)
    assert list(hist.index) == list(returns.index)
