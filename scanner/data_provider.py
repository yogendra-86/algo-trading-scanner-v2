from typing import Dict, List

import pandas as pd
import yfinance as yf


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]

    df = df.rename(columns=str.lower)
    return df


def to_market_ticker(symbol: str, market: str) -> str:
    if market == "NSE" and not symbol.endswith(".NS"):
        return f"{symbol}.NS"
    return symbol


def fetch_intraday_data(
    symbol: str,
    market: str,
    period: str = "5d",
    interval: str = "5m",
) -> pd.DataFrame:
    ticker = to_market_ticker(symbol, market)

    try:
        df = yf.download(
            ticker,
            period=period,
            interval=interval,
            auto_adjust=False,
            progress=False,
            threads=False,
        )
    except Exception:
        return pd.DataFrame()

    if df is None or df.empty:
        return pd.DataFrame()

    df = normalize_columns(df)

    required_cols = {"open", "high", "low", "close", "volume"}
    if not required_cols.issubset(set(df.columns)):
        return pd.DataFrame()

    df = df.dropna(subset=["open", "high", "low", "close"])
    print("Fetched data:")   #
    print(df.tail(3))   #
    return df


def fetch_batch_intraday_data(symbols: List[str], market: str) -> Dict[str, pd.DataFrame]:
    return {symbol: fetch_intraday_data(symbol, market) for symbol in symbols}
