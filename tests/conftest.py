"""
Shared pytest fixtures for Robo-Advisor tests.

Mock data is deterministic: no external API, no network.
"""

from __future__ import annotations

import pandas as pd
import pytest

from portfolio import Portfolio, init_portfolio


@pytest.fixture
def sample_allocation() -> dict[str, float]:
    """Allocation ที่รวมกันเท่ากับ 1.0 ใช้กับ backtest และ trading."""
    return {"VTI": 0.5, "VXUS": 0.3, "BND": 0.2}


@pytest.fixture
def mock_monthly_returns() -> pd.DataFrame:
    """
    Mock monthly returns 12 เดือน, 3 tickers.
    ค่า predictable: ทุกเดือนทุก asset ได้ 1% (0.01).
    """
    dates = pd.date_range("2023-01-31", periods=12, freq="ME")
    data = {
        "VTI": [0.01] * 12,
        "VXUS": [0.01] * 12,
        "BND": [0.01] * 12,
    }
    return pd.DataFrame(data, index=dates)


@pytest.fixture
def mock_monthly_returns_24() -> pd.DataFrame:
    """Mock 24 เดือน สำหรับทดสอบ rebalance ครบ 2 รอบ (frequency=12)."""
    dates = pd.date_range("2022-01-31", periods=24, freq="ME")
    data = {
        "VTI": [0.02] * 24,
        "VXUS": [0.01] * 24,
        "BND": [0.005] * 24,
    }
    return pd.DataFrame(data, index=dates)


@pytest.fixture
def sample_portfolio() -> Portfolio:
    """Portfolio เริ่มต้นด้วยเงินสด 100,000."""
    return init_portfolio(100_000.0)
