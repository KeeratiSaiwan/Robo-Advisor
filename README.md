# Robo-Advisor (Sprint 1)

Backend ของระบบ Robo-Advisor: risk profiling, portfolio model และ trading engine ใช้ผ่าน CLI เท่านั้น ไม่มี frontend

## Features

- **Risk questionnaire** – คำถาม 5 ข้อ → คะแนนความเสี่ยง → ระดับที่แนะนำ (low / medium / high) พร้อมตัวเลือก override และ confirmation จากผู้ใช้
- **Capital input** – รับเงินลงทุนเริ่มต้นผ่าน CLI (มีการ validate รองรับการใส่ comma)
- **Risk profiling** – แมประดับความเสี่ยงเป็น target ETF allocation (น้ำหนักรวม 1.0)
- **Market data** – ราคาปิดล่าสุดจาก **yfinance** (Yahoo Finance)
- **Portfolio model** – เงินสด + holdings มี `buy()` / `sell()` พร้อม validation (ห้าม cash/holdings ติดลบ)
- **Trading engine** – `execute_trade(portfolio, allocation)` จัดสรรเงินใน portfolio เข้า ETF ตามน้ำหนัก

## ETF universe

| Symbol | Description        |
|--------|--------------------|
| VTI    | US Total Stock     |
| VXUS   | International Stock |
| BND    | US Bond            |
| BNDX   | International Bond |
| VNQ    | Real Estate        |

## Project structure

| File | Role |
|------|------|
| `main.py` | Orchestration: questionnaire → capital → allocation → portfolio → execute_trade → print summary |
| `risk_questionnaire.py` | CLI risk questionnaire; `run_questionnaire_cli()` คืนระดับความเสี่ยง (มี confirmation/override) |
| `capital_input.py` | รับเงินลงทุนเริ่มต้นผ่าน CLI; `run_capital_input_cli()` → float; `parse_initial_cash()` (pure) |
| `risk_profiling.py` | `get_allocation(risk_level)` → dict[symbol, weight]; ไม่มี pricing logic |
| `market_data.py` | `get_price(symbol)` → ราคาปิดล่าสุดจาก yfinance; จัดการ connection และ empty data |
| `portfolio.py` | `Portfolio` (cash, holdings), `init_portfolio()`, `buy()`/`sell()`, ฟังก์ชันช่วยคำนวณ value/allocation |
| `trading.py` | `execute_trade(portfolio, allocation)` – ตรวจน้ำหนักรวม ~1.0 ใช้เฉพาะ `portfolio.buy()` |

## Requirements

- Python 3.x
- **yfinance** (ข้อมูลจาก Yahoo Finance)

```bash
pip install yfinance
```

## การรัน

```bash
python main.py
```

Flow:

1. **Risk questionnaire** – ตอบคำถาม 5 ข้อ (อายุ ระยะเวลาลงทุน ความมั่นคงรายได้ ประสบการณ์ ปฏิกิริยาต่อ drawdown)
2. **Confirmation** – ใช้ระดับที่ระบบแนะนำ หรือ override เป็น low / medium / high แล้วยืนยัน
3. **Capital** – กรอกเงินลงทุนเริ่มต้น
4. **Execution** – ระบบดึงราคาปัจจุบัน สร้าง allocation และ "ซื้อ" ETF เข้า portfolio
5. **Summary** – ตารางสัญลักษณ์ จำนวนหน่วย ราคา มูลค่า เงินสดคงเหลือ และมูลค่าพอร์ตทั้งหมด (ข้อความภาษาไทย)

ผลลัพธ์แสดงเป็นภาษาไทย (เช่น สรุปพอร์ตการลงทุน มูลค่าพอร์ตทั้งหมด) ยังไม่มี logic rebalancing หรือขายใน Sprint 1
