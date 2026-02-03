"""Helpers for fetching market data."""

from __future__ import annotations

from typing import Iterable, List, Optional, Dict, Any

DATA_PROVIDER = "yfinance"


class DataSourceError(Exception):
    """Raised when a data source fails unexpectedly."""


def _load_yfinance():
    try:
        import yfinance as yf  # type: ignore
    except ImportError:  # pragma: no cover - depends on env
        return None
    return yf


def _format_quote(symbol: str, price: Optional[float], change_percent: Optional[float], message: str) -> Dict[str, Any]:
    return {
        "symbol": symbol,
        "price": price,
        "change_percent": change_percent,
        "message": message,
    }


def _get_latest_quote(symbol: str) -> Dict[str, Any]:
    yf = _load_yfinance()
    if yf is None:
        return _format_quote(symbol, None, None, "yfinance is not installed")

    try:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="2d")
    except Exception as exc:  # pragma: no cover - network/provider failure
        return _format_quote(symbol, None, None, f"failed to fetch data: {exc}")

    if history.empty:
        return _format_quote(symbol, None, None, "no data returned")

    # Use the last two rows to compute daily change.
    closes = history["Close"].dropna()
    if closes.empty:
        return _format_quote(symbol, None, None, "no closing price data")

    latest_price = float(closes.iloc[-1])
    if len(closes) < 2:
        return _format_quote(symbol, latest_price, None, "not enough data to compute change")

    previous_price = float(closes.iloc[-2])
    if previous_price == 0:
        return _format_quote(symbol, latest_price, None, "previous price is zero; cannot compute change")

    change_percent = ((latest_price - previous_price) / previous_price) * 100
    return _format_quote(symbol, latest_price, change_percent, "ok")


def get_index_quote(symbol: str) -> Dict[str, Any]:
    """Fetch a single index quote."""
    return _get_latest_quote(symbol)


def get_commodity_quote(symbol: str) -> Dict[str, Any]:
    """Fetch a single commodity quote."""
    return _get_latest_quote(symbol)


def get_stock_quotes(symbols: Iterable[str]) -> List[Dict[str, Any]]:
    """Fetch multiple stock quotes."""
    return [_get_latest_quote(symbol) for symbol in symbols]
