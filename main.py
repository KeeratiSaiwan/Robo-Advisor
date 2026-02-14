from __future__ import annotations

from capital_input import run_capital_input_cli
from market_data import get_price
from portfolio import init_portfolio
from risk_profiling import get_allocation
from risk_questionnaire import run_questionnaire_cli
from trading import execute_trade


def main() -> None:
    # Header
    print("=== ระบบ Robo-Advisor ===")
    print()

    # ชั้น input layer (CLI) ที่แยกออกไปแล้ว
    risk_level = run_questionnaire_cli()
    cash = run_capital_input_cli()

    # Business logic orchestration
    allocation = get_allocation(risk_level)
    portfolio = init_portfolio(cash)
    execute_trade(portfolio, allocation)

    # แสดงผลลัพธ์เป็นภาษาไทย
    print("สรุปพอร์ตการลงทุน")
    print("----------------------------------------")
    print("สัญลักษณ์ | จำนวนหน่วย      | ราคา       | มูลค่า")
    print("----------------------------------------")

    total_value = 0.0
    for symbol in allocation.keys():
        units = portfolio.holdings.get(symbol, 0.0)
        price = get_price(symbol)
        value = units * price
        total_value += value
        print(f"{symbol:8s} | {units:14.4f} | {price:10.2f} | {value:12.2f}")

    print("----------------------------------------")
    print(f"เงินสดคงเหลือ: {portfolio.cash:,.2f} บาท")
    print(f"มูลค่าพอร์ตทั้งหมด: {total_value + portfolio.cash:,.2f} บาท")


if __name__ == "__main__":
    main()

