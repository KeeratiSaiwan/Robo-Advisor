from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


def init_portfolio(initial_cash: float) -> "Portfolio":
    """
    Factory function for creating a new empty portfolio with given initial cash.
    """
    return Portfolio(cash=initial_cash)


@dataclass
class Portfolio:
    """
    Simple in-memory portfolio model.

    Attributes:
        cash: Available cash balance (in base currency).
        holdings: Mapping asset symbol -> number of units held.
    """

    cash: float
    holdings: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.cash < 0:
            raise ValueError("Initial cash must not be negative.")

    def add_position(self, asset: str, amount: float) -> None:
        """
        Adjust holdings for a given asset by a signed amount.
        Positive amount increases position, negative amount decreases it.
        """
        current = self.holdings.get(asset, 0.0)
        new_amount = current + amount

        if new_amount < 0:
            raise ValueError(
                f"Cannot reduce holdings of {asset} below zero. "
                f"Current: {current}, change: {amount}"
            )

        if new_amount == 0:
            # Clean up zero positions for readability
            self.holdings.pop(asset, None)
        else:
            self.holdings[asset] = new_amount

    def buy(self, asset: str, units: float, price: float) -> None:
        """
        Buy an asset using available cash and update holdings.

        Rules:
        - units must be > 0
        - price must be > 0
        - cash must be sufficient (cannot go negative)
        """
        if units <= 0:
            raise ValueError("Buy units must be greater than zero.")
        if price <= 0:
            raise ValueError("Price must be greater than zero.")

        cost = units * price

        # Allow a tiny epsilon for floating-point arithmetic.
        eps = 1e-9
        if cost > self.cash + eps:
            raise ValueError(
                f"Insufficient cash to buy {units} of {asset} at {price}. "
                f"Required: {cost}, available: {self.cash}"
            )

        self.cash -= cost
        if abs(self.cash) < eps:
            self.cash = 0.0

        self.add_position(asset, units)

    def sell(self, asset: str, units: float, price: float) -> None:
        """
        Sell an asset and update holdings and cash.

        Rules:
        - units must be > 0
        - price must be > 0
        - holdings must be sufficient (cannot go below zero)
        """
        if units <= 0:
            raise ValueError("Sell units must be greater than zero.")
        if price <= 0:
            raise ValueError("Price must be greater than zero.")

        current_units = self.holdings.get(asset, 0.0)
        if units > current_units:
            raise ValueError(
                f"Insufficient holdings to sell {units} of {asset}. Current: {current_units}"
            )

        proceeds = units * price
        self.add_position(asset, -units)
        self.cash += proceeds

    def calculate_portfolio_value(self, prices: Dict[str, float]) -> float:
        """
        Calculate total portfolio value given a price mapping.

        The 'CASH' position is represented explicitly via self.cash and does
        not require a price entry.
        """
        value = self.cash
        for asset, units in self.holdings.items():
            if asset not in prices:
                raise KeyError(f"Missing price for asset '{asset}'")
            value += units * prices[asset]
        return value

    def get_current_allocation(self, prices: Dict[str, float]) -> Dict[str, float]:
        """
        Compute current allocation by asset (including CASH) as weights summing to 1.
        """
        total_value = self.calculate_portfolio_value(prices)
        if total_value == 0:
            # Avoid division by zero - no value means no allocation
            return {}

        allocation: Dict[str, float] = {}

        # CASH allocation
        if self.cash > 0:
            allocation["CASH"] = self.cash / total_value

        # Non-cash assets
        for asset, units in self.holdings.items():
            price = prices.get(asset)
            if price is None:
                raise KeyError(f"Missing price for asset '{asset}'")
            allocation[asset] = (units * price) / total_value

        return allocation

