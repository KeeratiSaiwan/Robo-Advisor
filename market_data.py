from __future__ import annotations

from typing import List

import pandas as pd
import yfinance as yf


def get_historical_prices(
    tickers: List[str],
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """
    ดึงราคาปิดปรับแล้ว (Adj Close) ย้อนหลังหลาย ticker สำหรับ backtesting.

    ใช้ yfinance.download() ดึงข้อมูลช่วง start_date ถึง end_date
    คืนค่าเฉพาะคอลัมน์ Adj Close เรียงวันที่เก่าไปใหม่ และ dropna.

    Args:
        tickers: รายการสัญลักษณ์ (เช่น ["VTI", "VXUS", "BND"]).
        start_date: วันที่เริ่ม (รูปแบบที่ yfinance รองรับ เช่น "YYYY-MM-DD").
        end_date: วันที่สิ้นสุด (รวมถึงวันนี้).

    Returns:
        DataFrame ที่ index เป็นวันที่ (datetime), columns เป็นชื่อ ticker,
        ค่าเป็น Adj Close เรียงจากเก่าไปใหม่ และไม่มี missing values.

    Raises:
        ValueError: ถ้า tickers ว่าง หรือข้อมูลที่ดึงได้ว่างหลัง dropna.
        ConnectionError: ถ้าเกิดข้อผิดพลาดจากการเชื่อมต่อ/ดึงข้อมูล.
    """
    if not tickers:
        raise ValueError("tickers must be a non-empty list.")

    tickers = [str(t).strip().upper() for t in tickers if str(t).strip()]
    if not tickers:
        raise ValueError("tickers must contain at least one valid symbol.")

    start = str(start_date).strip()
    end = str(end_date).strip()
    if not start or not end:
        raise ValueError("start_date and end_date must be non-empty strings.")

    try:
        raw = yf.download(
            tickers,
            start=start,
            end=end,
            progress=False,
            auto_adjust=False,
            threads=True,
        )
    except Exception as exc:
        raise ConnectionError(
            "Failed to download historical data. Check network and date range."
        ) from exc

    if raw is None or raw.empty:
        raise ValueError(
            "No historical price data returned. Check tickers and date range."
        )

    # ดึงเฉพาะ Adj Close: กรณี 1 ticker ได้ Series, หลาย ticker ได้ DataFrame
    adj = raw["Adj Close"].copy()
    if isinstance(adj, pd.Series):
        adj = adj.to_frame(name=tickers[0])

    adj = adj.dropna()
    adj = adj.sort_index(ascending=True)

    if adj.empty:
        raise ValueError(
            "No rows left after dropping missing values. Check tickers and dates."
        )

    return adj


def to_monthly_prices(daily_prices: pd.DataFrame) -> pd.DataFrame:
    """
    แปลง daily prices เป็น month-end prices (ราคาปิดวันสุดท้ายของแต่ละเดือน).

    ใช้ resample("ME").last() เพื่อดึงแถววันสุดท้ายของแต่ละเดือน เรียงวันที่
    จากเก่าไปใหม่ และลบแถวที่มี missing values.

    Args:
        daily_prices: DataFrame ของราคารายวัน index ต้องเป็น DatetimeIndex,
            columns เป็น ticker.

    Returns:
        DataFrame ของราคาปิดสิ้นเดือน (month-end) เรียงจากเก่าไปใหม่ ไม่มี NaN.

    Raises:
        ValueError: ถ้า input ไม่ใช่ DataFrame, ว่าง หรือผลลัพธ์หลัง resample/dropna ว่าง.
    """
    if not isinstance(daily_prices, pd.DataFrame):
        raise ValueError("daily_prices must be a pandas DataFrame.")

    if daily_prices.empty:
        raise ValueError("daily_prices must not be empty.")

    monthly = daily_prices.resample("ME").last()
    monthly = monthly.dropna()
    monthly = monthly.sort_index(ascending=True)

    if monthly.empty:
        raise ValueError(
            "Result of to_monthly_prices is empty after resample and dropna."
        )

    return monthly


def calculate_monthly_returns(monthly_prices: pd.DataFrame) -> pd.DataFrame:
    """
    คำนวณ monthly returns (เปอร์เซ็นต์การเปลี่ยนแปลงรายเดือน) จากราคาปิดสิ้นเดือน.

    ใช้ pct_change() เพื่อคำนวณ (price_t - price_{t-1}) / price_{t-1}
    แถวแรกจะได้ NaN จึง dropna() ออก.

    Args:
        monthly_prices: DataFrame ของราคาปิดสิ้นเดือน (เช่น จาก to_monthly_prices)
            index เป็นวันที่, columns เป็น ticker.

    Returns:
        DataFrame ของ monthly returns (ค่าเป็นทศนิยม เช่น 0.01 = 1%)
        ไม่มี NaN.

    Raises:
        ValueError: ถ้า input ไม่ใช่ DataFrame, ว่าง หรือผลลัพธ์หลัง dropna ว่าง.
    """
    if not isinstance(monthly_prices, pd.DataFrame):
        raise ValueError("monthly_prices must be a pandas DataFrame.")

    if monthly_prices.empty:
        raise ValueError("monthly_prices must not be empty.")

    returns = monthly_prices.pct_change()
    returns = returns.dropna()
    returns = returns.sort_index(ascending=True)

    if returns.empty:
        raise ValueError(
            "Result of calculate_monthly_returns is empty after dropna."
        )

    return returns


def get_price(symbol: str) -> float:
    """
    Fetch the latest closing price for a given symbol from Yahoo Finance.

    Uses yfinance to download 1-day history and returns the most recent
    closing price. Suitable for ETFs and stocks supported by Yahoo Finance.

    Args:
        symbol: Ticker symbol (e.g. "VTI", "VXUS", "BND").

    Returns:
        Latest closing price as a float.

    Raises:
        ValueError: If no price data is available (empty history or invalid symbol).
        ConnectionError: If a network/connection error occurs while fetching data.
    """
    if not symbol or not str(symbol).strip():
        raise ValueError("Symbol must be a non-empty string.")

    symbol = str(symbol).strip().upper()

    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
    except Exception as exc:
        raise ConnectionError(
            f"Failed to fetch data for '{symbol}'. Check network and try again."
        ) from exc

    if data is None or data.empty:
        raise ValueError(
            f"No price data available for symbol '{symbol}'. "
            "Symbol may be invalid or delisted."
        )

    # Latest row = most recent trading day; 'Close' is the closing price.
    close_series = data["Close"]
    if close_series is None or close_series.empty:
        raise ValueError(f"No closing price found for symbol '{symbol}'.")

    latest_close = float(close_series.iloc[-1])
    if latest_close <= 0:
        raise ValueError(f"Invalid closing price for '{symbol}': {latest_close}.")

    return latest_close
