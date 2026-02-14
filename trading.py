from __future__ import annotations

import math
from typing import Dict

from market_data import get_price
from portfolio import Portfolio


def execute_trade(portfolio: Portfolio, allocation: Dict[str, float]) -> None:
    """
    Execute a mock trade given a portfolio and target allocation.

    Behavior (Sprint 1):
    - Validate allocation weights sum to ~1.0
    - Use the portfolio's current cash as the source of funds
    - Buy each symbol according to its weight (no rebalancing / no selling)
    - Update portfolio state via portfolio.buy() only
    """
    total_weight = sum(allocation.values())
    if not math.isclose(total_weight, 1.0, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError(f"Allocation must sum to 1.0, but got {total_weight}.")

    starting_cash = portfolio.cash
    if starting_cash <= 0:
        raise ValueError("Portfolio cash must be greater than zero.")

    symbols = list(allocation.keys())
    for i, symbol in enumerate(symbols):
        weight = allocation[symbol]

        # Use the remainder cash for the last symbol to avoid tiny float drift.
        if i == len(symbols) - 1:
            allocated_cash = portfolio.cash
        else:
            allocated_cash = starting_cash * weight

        price = get_price(symbol)
        units = allocated_cash / price
        portfolio.buy(symbol, units, price)

