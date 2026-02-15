# Robo-Advisor

Backend ของระบบ Robo-Advisor: risk profiling, portfolio model, trading engine และ backtesting ใช้ผ่าน CLI เท่านั้น ไม่มี frontend

## โหมดการใช้งาน

| โหมด | ไฟล์ | คำอธิบาย |
|------|------|----------|
| **Real-time Portfolio** | `main.py` | แบบสอบถามความเสี่ยง → เงินลงทุน → allocation → ซื้อ ETF ตามราคาปัจจุบัน → แสดงสรุปพอร์ต |
| **Backtest** | `backtest_runner.py` | แบบสอบถามความเสี่ยง → allocation → เงินลงทุน → เลือก rebalance frequency → รัน backtest ย้อนหลัง → แสดง report |

## Features

- **Risk questionnaire** – คำถาม 5 ข้อ → คะแนนความเสี่ยง → ระดับที่แนะนำ (low / medium / high) พร้อมตัวเลือก override และ confirmation
- **Capital input** – รับเงินลงทุนเริ่มต้นผ่าน CLI (validate, รองรับ comma)
- **Risk profiling** – แมประดับความเสี่ยงเป็น target ETF allocation (น้ำหนักรวม 1.0) ใช้กับทั้ง real-time และ backtest
- **Market data** – ราคาปัจจุบันจาก **yfinance** (`get_price`) และ historical สำหรับ backtest (`get_historical_prices`, `to_monthly_prices`, `calculate_monthly_returns`)
- **Portfolio model** – เงินสด + holdings, `buy()` / `sell()` พร้อม validation
- **Trading engine** – `execute_trade(portfolio, allocation)` จัดสรรเงินเข้า ETF ตามน้ำหนัก (real-time)
- **Backtest engine** – `run_backtest(monthly_returns, allocation, initial_capital, rebalance_frequency)` รองรับ Buy & Hold, Monthly (1), Semi-Annual (6), Annual (12)

## ETF universe

| Symbol | Description        |
|--------|--------------------|
| VTI    | US Total Stock     |
| VXUS   | International Stock |
| BND    | US Bond            |
| BNDX   | International Bond |
| VNQ    | Real Estate        |

## โครงสร้างโปรเจกต์

| ไฟล์ | บทบาท |
|------|--------|
| `main.py` | Orchestration real-time: questionnaire → capital → allocation → portfolio → execute_trade → สรุปพอร์ต |
| `backtest_runner.py` | Orchestration backtest: questionnaire → allocation → capital → เลือก rebalance → โหลดข้อมูล → run_backtest → print_report |
| `backtest_engine.py` | Logic backtest: `run_backtest()` track มูลค่าแต่ละ asset, rebalance ตาม frequency, คืน final_value, total_return, cagr, portfolio_history |
| `risk_questionnaire.py` | CLI แบบสอบถามความเสี่ยง; `run_questionnaire_cli()` คืน risk level (มี confirmation/override) |
| `capital_input.py` | รับเงินลงทุนเริ่มต้นผ่าน CLI; `run_capital_input_cli()`, `parse_initial_cash()` (pure) |
| `risk_profiling.py` | `get_allocation(risk_level)` → dict[symbol, weight]; ไม่มี pricing logic |
| `market_data.py` | `get_price(symbol)` ราคาปัจจุบัน; `get_historical_prices`, `to_monthly_prices`, `calculate_monthly_returns` สำหรับ backtest |
| `portfolio.py` | `Portfolio`, `init_portfolio()`, `buy()`/`sell()`, value/allocation helpers |
| `trading.py` | `execute_trade(portfolio, allocation)` ใช้ `portfolio.buy()` เท่านั้น |

## Requirements

- Python 3.x
- **yfinance** (Yahoo Finance)
- **pandas** (backtest และ market_data)

```bash
pip install yfinance pandas
```

## การรัน

### Real-time Portfolio (จัดพอร์ตตามราคาปัจจุบัน)

```bash
python main.py
```

Flow: แบบสอบถามความเสี่ยง → ยืนยันระดับ → กรอกเงินลงทุน → ระบบดึงราคาปัจจุบัน → จัดสรรซื้อ ETF → แสดงสรุปพอร์ต (ภาษาไทย)

### Backtest (ทดสอบย้อนหลัง)

```bash
python backtest_runner.py
```

Flow:

1. **Risk Assessment** – ตอบแบบสอบถามความเสี่ยง → ได้ risk level
2. **Allocation** – แสดงระดับความเสี่ยงและ Recommended Allocation (จาก risk_profiling)
3. **Capital** – กรอกเงินลงทุนเริ่มต้น
4. **Rebalance** – เลือก 0=Buy & Hold, 1=Monthly, 6=Semi-Annual, 12=Annual
5. **Summary** – แสดง Risk Level, Initial Capital, Rebalance Frequency
6. **Running Backtest** – โหลดข้อมูลย้อนหลัง (ช่วงที่กำหนดใน runner) → รัน backtest → แสดง report (Performance Summary, Key Insight, Monthly ล่าสุด 12 เดือน)

ผลลัพธ์ report แสดง Final Value, Total Return, CAGR, Max Drawdown, Best/Worst Year และ monthly return 12 เดือนล่าสุด
