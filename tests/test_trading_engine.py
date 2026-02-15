"""
Unit tests for trading: execute_trade().
Mocks market_data.get_price to avoid network/API.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from portfolio import init_portfolio
from trading import execute_trade


def test_execute_trade_updates_portfolio(
    sample_allocation: dict[str, float],
    sample_portfolio,
) -> None:
    prices = {"VTI": 100.0, "VXUS": 50.0, "BND": 75.0}

    with patch("trading.get_price", side_effect=lambda s: prices[s]):
        execute_trade(sample_portfolio, sample_allocation)

    assert sample_portfolio.cash >= 0
    for symbol in sample_allocation:
        assert symbol in sample_portfolio.holdings
        assert sample_portfolio.holdings[symbol] >= 0


def test_execute_trade_allocation_sum_not_one_raises(
    sample_portfolio,
) -> None:
    bad_alloc = {"VTI": 0.6, "VXUS": 0.3}
    with pytest.raises(ValueError, match="sum to 1.0"):
        execute_trade(sample_portfolio, bad_alloc)


def test_zero_cash_raises(
    sample_allocation: dict[str, float],
) -> None:
    zero_portfolio = init_portfolio(0.0)
    with pytest.raises(ValueError, match="greater than zero"):
        execute_trade(zero_portfolio, sample_allocation)


def test_negative_quantity_via_portfolio_buy() -> None:
    """Trading ใช้ portfolio.buy; buy รับ units > 0 เท่านั้น."""
    from portfolio import Portfolio

    p = init_portfolio(10_000.0)
    with pytest.raises(ValueError, match="greater than zero"):
        p.buy("VTI", -10.0, 100.0)
