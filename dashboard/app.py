import time
from typing import Dict, List

import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf

INDEX_TICKERS = {
    "WTI Crude": "CL=F",
    "Dow Jones": "^DJI",
    "S&P 500": "^GSPC",
}

DEFAULT_STOCKS = [
    "AAPL",
    "MSFT",
    "AMZN",
    "GOOGL",
    "NVDA",
    "META",
    "TSLA",
    "JPM",
    "XOM",
    "JNJ",
]


@st.cache_data(ttl=300)
def fetch_latest_prices(tickers: List[str]) -> pd.DataFrame:
    data = yf.download(
        tickers=" ".join(tickers),
        period="5d",
        interval="1d",
        group_by="ticker",
        auto_adjust=False,
        progress=False,
        threads=True,
    )
    if data.empty:
        return pd.DataFrame(columns=["ticker", "price", "change"])

    results = []
    if isinstance(data.columns, pd.MultiIndex):
        for ticker in tickers:
            close_series = data.get((ticker, "Close"))
            if close_series is None:
                continue
            close_series = close_series.dropna()
            if len(close_series) < 2:
                continue
            latest = close_series.iloc[-1]
            previous = close_series.iloc[-2]
            change_pct = (latest - previous) / previous * 100
            results.append(
                {
                    "ticker": ticker,
                    "price": latest,
                    "change": change_pct,
                }
            )
    else:
        close_series = data["Close"].dropna()
        if len(close_series) >= 2:
            latest = close_series.iloc[-1]
            previous = close_series.iloc[-2]
            change_pct = (latest - previous) / previous * 100
            results.append(
                {
                    "ticker": tickers[0],
                    "price": latest,
                    "change": change_pct,
                }
            )

    return pd.DataFrame(results)


def fetch_index_cards() -> Dict[str, Dict[str, float]]:
    tickers = list(INDEX_TICKERS.values())
    data = fetch_latest_prices(tickers)
    index_data: Dict[str, Dict[str, float]] = {}
    for name, symbol in INDEX_TICKERS.items():
        row = data.loc[data["ticker"] == symbol]
        if row.empty:
            continue
        index_data[name] = {
            "price": float(row.iloc[0]["price"]),
            "change": float(row.iloc[0]["change"]),
        }
    return index_data


def build_treemap(data: pd.DataFrame) -> px.treemap:
    fig = px.treemap(
        data,
        path=["ticker"],
        values="price",
        color="change",
        color_continuous_scale=["#d62728", "#ffffff", "#2ca02c"],
        color_continuous_midpoint=0,
        hover_data={"price": ":.2f", "change": ":.2f"},
    )
    fig.update_traces(texttemplate="%{label}<br>%{customdata[1]:+.2f}%")
    fig.update_layout(margin=dict(t=10, l=10, r=10, b=10))
    return fig


def parse_stock_input(raw_value: str) -> List[str]:
    tickers = [ticker.strip().upper() for ticker in raw_value.split(",")]
    return [ticker for ticker in tickers if ticker]


def main() -> None:
    st.set_page_config(page_title="Market Dashboard", layout="wide")
    st.title("Market Snapshot")

    with st.sidebar:
        st.header("Settings")
        raw_tickers = st.text_area(
            "Top stocks (comma-separated)",
            value=", ".join(DEFAULT_STOCKS),
            height=120,
        )
        refresh_seconds = st.number_input(
            "Auto-refresh interval (seconds)",
            min_value=0,
            value=0,
            step=30,
            help="Set to 0 to disable auto-refresh.",
        )

    if refresh_seconds > 0:
        st.caption(f"Auto-refreshing every {int(refresh_seconds)} seconds.")

    if st.button("Refresh data"):
        st.cache_data.clear()
        st.experimental_rerun()

    if refresh_seconds > 0:
        time.sleep(refresh_seconds)
        st.cache_data.clear()
        st.experimental_rerun()

    index_data = fetch_index_cards()

    columns = st.columns(3)
    for column, (label, values) in zip(columns, index_data.items()):
        column.metric(
            label,
            f"{values['price']:.2f}",
            f"{values['change']:+.2f}%",
        )

    tickers = parse_stock_input(raw_tickers)
    if not tickers:
        st.warning("Please provide at least one ticker.")
        return

    stock_data = fetch_latest_prices(tickers)
    if stock_data.empty:
        st.warning("No data returned for the selected tickers.")
        return

    st.subheader("Top Stocks Performance")
    treemap = build_treemap(stock_data)
    st.plotly_chart(treemap, use_container_width=True)


if __name__ == "__main__":
    main()
