"""
Robo Advisor Backtest Runner — orchestration layer.

รับ risk level, allocation, capital และ rebalance frequency จาก user
แล้วรัน backtest และแสดง report (ไม่แก้ logic ใน backtest_engine)
"""

from __future__ import annotations

from typing import Dict

import pandas as pd

from backtest_engine import run_backtest
from capital_input import run_capital_input_cli
from market_data import (
    get_historical_prices,
    to_monthly_prices,
    calculate_monthly_returns,
)
from risk_profiling import get_allocation
from risk_questionnaire import run_questionnaire_cli


# ช่วง backtest (ใช้ร่วมกับ allocation จาก risk profiling)
BACKTEST_START = "2018-01-01"
BACKTEST_END = "2023-12-31"

REBALANCE_OPTIONS = {
    0: ("Buy & Hold", None),
    1: ("Monthly (1 month)", 1),
    6: ("Semi-Annual (6 months)", 6),
    12: ("Annual (12 months)", 12),
}


def _risk_level_display(risk_level: str) -> str:
    """แปลง risk level เป็นข้อความแสดงผล (low -> Low, medium -> Moderate, high -> High)."""
    r = risk_level.strip().lower()
    if r == "low":
        return "Low"
    if r == "medium":
        return "Moderate"
    if r == "high":
        return "High"
    return risk_level


def _print_allocation(allocation: Dict[str, float]) -> None:
    """แสดง allocation เป็นเปอร์เซ็นต์ อ่านง่าย."""
    print("Recommended Allocation:")
    for ticker, weight in sorted(allocation.items()):
        print(f"  {ticker}: {weight * 100:.0f}%")
    print()


def select_rebalance_frequency() -> tuple[str, int | None]:
    """
    ให้ผู้ใช้เลือก rebalance frequency จากเมนู.

    Returns:
        (strategy_display_name, rebalance_frequency)
        frequency เป็น None สำหรับ Buy & Hold ไม่เช่นนั้นเป็น 1, 6 หรือ 12
    """
    print("Select Rebalance Frequency:")
    print("  0 = Buy & Hold")
    print("  1 = Monthly (1 month)")
    print("  6 = Semi-Annual (6 months)")
    print("  12 = Annual (12 months)")
    print()

    valid = {0, 1, 6, 12}
    while True:
        raw = input("Your choice (0 / 1 / 6 / 12): ").strip()
        try:
            choice = int(raw)
        except ValueError:
            print("Please enter a number: 0, 1, 6, or 12.\n")
            continue
        if choice not in valid:
            print("Invalid choice. Enter 0, 1, 6, or 12.\n")
            continue
        label, freq = REBALANCE_OPTIONS[choice]
        print(f"Selected: {label}\n")
        return label, freq


def _compute_max_drawdown(portfolio_history: pd.Series, initial_capital: float) -> float:
    """คำนวณ Max Drawdown (ทศนิยม เช่น -0.15 = -15%)."""
    values = pd.Series([initial_capital] + portfolio_history.tolist())
    running_max = values.cummax()
    drawdown = (values - running_max) / running_max
    return float(drawdown.min())


def _compute_yearly_returns(
    portfolio_history: pd.Series,
    initial_capital: float,
) -> list[tuple[int, float]]:
    """คำนวณ return รายปี จาก portfolio_history. คืนค่า list of (year, return)."""
    hist = portfolio_history.sort_index()
    years = hist.index.year.unique()
    result: list[tuple[int, float]] = []
    prev_value = float(initial_capital)
    for year in sorted(years):
        year_data = hist[hist.index.year == year]
        if year_data.empty:
            continue
        end_value = float(year_data.iloc[-1])
        ret = (end_value - prev_value) / prev_value if prev_value > 0 else 0.0
        result.append((year, ret))
        prev_value = end_value
    return result


def _format_pct(value: float) -> str:
    """จัดรูปแบบเปอร์เซ็นต์ 2 ตำแหน่ง พร้อมเครื่องหมาย + / -."""
    pct = value * 100
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.2f}%"


def _fmt_date(d) -> str:
    """แปลง datetime เป็นสตริง YYYY-MM-DD."""
    return d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d)[:10]


def print_report(
    strategy_name: str,
    result: dict,
    initial_capital: float,
) -> None:
    """
    แสดงผล backtest เป็น report อ่านง่ายแบบ financial report สำหรับ user.
    """
    hist = result["portfolio_history"].sort_index()
    start_str = _fmt_date(hist.index[0])
    end_str = _fmt_date(hist.index[-1])
    max_dd = _compute_max_drawdown(hist, initial_capital)
    yearly = _compute_yearly_returns(hist, initial_capital)

    best_year, best_return = (max(yearly, key=lambda x: x[1]) if yearly else (0, 0.0))
    worst_year, worst_return = (min(yearly, key=lambda x: x[1]) if yearly else (0, 0.0))

    prev_val = initial_capital
    monthly_ret_list: list[tuple] = []
    for date, val in hist.items():
        ret = (val - prev_val) / prev_val if prev_val > 0 else 0.0
        monthly_ret_list.append((date, ret))
        prev_val = val
    last_12 = monthly_ret_list[-12:] if len(monthly_ret_list) >= 12 else monthly_ret_list

    print("=" * 50)
    print(f"Strategy: {strategy_name}")
    print(f"Period: {start_str} – {end_str}")
    print(f"Initial Capital: {initial_capital:,.0f} บาท")
    print("=" * 50)
    print()

    print("[ Performance Summary ]")
    print("-" * 40)
    print(f"Final Value        : {result['final_value']:>12,.2f} บาท")
    print(f"Total Return       : {_format_pct(result['total_return'])}")
    print(f"CAGR               : {_format_pct(result['cagr'])}")
    print(f"Max Drawdown       : {_format_pct(max_dd)}")
    print()

    print("[ Key Insight ]")
    print("-" * 40)
    print(f"Best Year           : {best_year} ({_format_pct(best_return)})")
    print(f"Worst Year          : {worst_year} ({_format_pct(worst_return)})")
    print()

    print("[ Monthly - Last 12 months ]")
    print("-" * 40)
    for date, ret in last_12:
        dt_str = date.strftime("%Y-%m") if hasattr(date, "strftime") else str(date)[:7]
        print(f"{dt_str}  {_format_pct(ret)}")
    print("=" * 50)
    print()


def main() -> None:
    """Orchestrate Risk Assessment → Allocation → Capital → Rebalance choice → Backtest → Report."""
    print("=== Risk Assessment ===")
    print()

    risk_level = run_questionnaire_cli()
    allocation = get_allocation(risk_level)

    print("Your Risk Level:", _risk_level_display(risk_level))
    print()
    _print_allocation(allocation)

    print("Enter Initial Capital:")
    initial_capital = run_capital_input_cli()

    strategy_name, rebalance_frequency = select_rebalance_frequency()

    print("--- Summary ---")
    print(f"Risk Level          : {_risk_level_display(risk_level)}")
    print(f"Initial Capital     : {initial_capital:,.0f} บาท")
    print(f"Rebalance Frequency : {strategy_name}")
    print()
    print("Running Backtest...")
    print()

    tickers = list(allocation.keys())
    daily = get_historical_prices(
        tickers=tickers,
        start_date=BACKTEST_START,
        end_date=BACKTEST_END,
    )
    monthly_prices = to_monthly_prices(daily)
    monthly_returns = calculate_monthly_returns(monthly_prices)

    result = run_backtest(
        monthly_returns=monthly_returns,
        allocation=allocation,
        initial_capital=initial_capital,
        rebalance_frequency=rebalance_frequency,
    )

    print_report(strategy_name, result, initial_capital)


if __name__ == "__main__":
    main()
