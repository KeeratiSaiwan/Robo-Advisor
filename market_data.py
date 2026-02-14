from __future__ import annotations

import yfinance as yf


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
