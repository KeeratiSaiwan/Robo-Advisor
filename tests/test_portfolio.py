"""
Unit tests for portfolio: Portfolio, init_portfolio, buy, sell, value, allocation.
No CLI, no I/O.
"""

from __future__ import annotations

import pytest

from portfolio import Portfolio, init_portfolio


def test_init_portfolio_sets_cash() -> None:
    p = init_portfolio(50_000.0)
    assert p.cash == 50_000.0
    assert p.holdings == {}


def test_initial_cash_negative_raises() -> None:
    with pytest.raises(ValueError, match="must not be negative"):
        Portfolio(cash=-100)


def test_buy_increases_holdings() -> None:
    p = init_portfolio(100_000.0)
    p.buy("VTI", 100.0, 250.0)
    assert p.holdings.get("VTI") == 100.0
    assert p.cash == 100_000.0 - 25_000.0


def test_calculate_portfolio_value() -> None:
    p = init_portfolio(10_000.0)
    p.buy("VTI", 20.0, 100.0)
    prices = {"VTI": 100.0}
    assert p.cash == 8_000.0
    assert p.holdings["VTI"] == 20.0
    assert p.calculate_portfolio_value(prices) == 10_000.0


def test_portfolio_value_not_negative_after_buy() -> None:
    p = init_portfolio(1000.0)
    p.buy("VTI", 2.0, 100.0)
    assert p.cash >= 0
    prices = {"VTI": 100.0}
    assert p.calculate_portfolio_value(prices) >= 0


def test_sell_decreases_holdings_increases_cash() -> None:
    p = init_portfolio(100_000.0)
    p.buy("VTI", 100.0, 250.0)
    p.sell("VTI", 40.0, 250.0)
    assert p.holdings.get("VTI") == 60.0
    assert p.cash == 100_000.0 - 25_000.0 + 40.0 * 250.0


def test_insufficient_cash_raises() -> None:
    p = init_portfolio(100.0)
    with pytest.raises(ValueError, match="Insufficient cash"):
        p.buy("VTI", 10.0, 100.0)


def test_sell_more_than_holdings_raises() -> None:
    p = init_portfolio(100_000.0)
    p.buy("VTI", 10.0, 100.0)
    with pytest.raises(ValueError, match="Insufficient holdings"):
        p.sell("VTI", 20.0, 100.0)


def test_buy_zero_units_raises() -> None:
    p = init_portfolio(100_000.0)
    with pytest.raises(ValueError, match="greater than zero"):
        p.buy("VTI", 0.0, 100.0)


def test_sell_zero_units_raises() -> None:
    p = init_portfolio(100_000.0)
    p.buy("VTI", 10.0, 100.0)
    with pytest.raises(ValueError, match="greater than zero"):
        p.sell("VTI", 0.0, 100.0)


def test_get_current_allocation() -> None:
    p = init_portfolio(10_000.0)
    p.buy("VTI", 50.0, 100.0)
    prices = {"VTI": 100.0}
    alloc = p.get_current_allocation(prices)
    total = sum(alloc.values())
    assert abs(total - 1.0) < 1e-9
    assert "VTI" in alloc
    assert "CASH" in alloc
