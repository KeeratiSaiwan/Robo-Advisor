from __future__ import annotations

import math
from typing import Dict

import pandas as pd


def _rebalance(
    asset_values: Dict[str, float],
    allocation: Dict[str, float],
) -> None:
    """
    ปรับสัดส่วนมูลค่าแต่ละ asset ให้ตรงกับ allocation (in-place).

    Args:
        asset_values: dict[ticker, value] มูลค่าปัจจุบันของแต่ละ asset.
        allocation: dict[ticker, weight] น้ำหนักเป้าหมาย (รวม 1.0).
    """
    total_value = sum(asset_values.values())
    for asset in asset_values:
        asset_values[asset] = total_value * allocation[asset]


def run_backtest(
    monthly_returns: pd.DataFrame,
    allocation: Dict[str, float],
    initial_capital: float,
    rebalance_frequency: int | None = None,
) -> Dict:
    """
    รัน backtest แบบรายเดือนจาก monthly returns และ allocation.

    Track มูลค่าแต่ละ asset แยกกัน และรองรับ rebalance ตามช่วงที่กำหนด
    (None = Buy-and-Hold, 12 = Annual, 6 = Semi-annual, 1 = Monthly).

    Args:
        monthly_returns: DataFrame ของ monthly returns (index = วันที่, columns = ticker).
        allocation: dict[ticker, weight] น้ำหนักรวมควรเท่ากับ 1.0.
        initial_capital: เงินลงทุนเริ่มต้น (ต้อง > 0).
        rebalance_frequency: จำนวนเดือนระหว่าง rebalance (None = ไม่ rebalance).

    Returns:
        dict ประกอบด้วย:
        - "portfolio_history": pd.Series มูลค่าพอร์ตแต่ละเดือน (index = เดือน).
        - "final_value": float มูลค่าพอร์ตสิ้นสุด.
        - "total_return": float คืนทุนรวมเป็นทศนิยม (เช่น 0.15 = 15%).
        - "cagr": float อัตราผลตอบแทนทบต้นรายปี (ทศนิยม).

    Raises:
        ValueError: ถ้า input ไม่ผ่าน validation.
    """
    if not isinstance(monthly_returns, pd.DataFrame):
        raise ValueError("monthly_returns must be a pandas DataFrame.")

    if monthly_returns.empty:
        raise ValueError("monthly_returns must not be empty.")

    if not allocation:
        raise ValueError("allocation must not be empty.")

    if initial_capital <= 0:
        raise ValueError("initial_capital must be greater than 0.")

    total_weight = sum(allocation.values())
    if not math.isclose(total_weight, 1.0, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError(f"Allocation must sum to 1.0, but got {total_weight}.")

    if rebalance_frequency is not None:
        if not isinstance(rebalance_frequency, int) or rebalance_frequency < 1:
            raise ValueError(
                "rebalance_frequency must be None or a positive integer."
            )

    allowed = set(monthly_returns.columns)
    for ticker in allocation:
        if ticker not in allowed:
            raise ValueError(
                f"Ticker '{ticker}' in allocation is not a column in monthly_returns."
            )

    # แบ่ง initial capital ตาม allocation
    asset_values: Dict[str, float] = {
        asset: initial_capital * weight for asset, weight in allocation.items()
    }

    history_values: list[float] = []
    month_counter = 0

    for date, row in monthly_returns.iterrows():
        # อัปเดตมูลค่าแต่ละ asset ตาม monthly return ของ asset นั้น
        for asset in asset_values:
            ret = row.get(asset, 0.0)
            if pd.isna(ret):
                ret = 0.0
            asset_values[asset] *= 1.0 + float(ret)

        month_counter += 1

        # Rebalance เมื่อถึงรอบ (ถ้ามีการตั้งค่า)
        if rebalance_frequency is not None and month_counter % rebalance_frequency == 0:
            _rebalance(asset_values, allocation)

        total = sum(asset_values.values())
        history_values.append(total)

    portfolio_history = pd.Series(history_values, index=monthly_returns.index)
    final_value = portfolio_history.iloc[-1]
    total_return = (final_value / initial_capital) - 1.0
    n_months = len(monthly_returns)
    years = n_months / 12.0
    cagr = (final_value / initial_capital) ** (1.0 / years) - 1.0 if years > 0 else 0.0

    return {
        "portfolio_history": portfolio_history,
        "final_value": float(final_value),
        "total_return": float(total_return),
        "cagr": float(cagr),
    }
