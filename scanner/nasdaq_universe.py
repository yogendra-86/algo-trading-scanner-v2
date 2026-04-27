from pathlib import Path
from typing import List

import pandas as pd


DEFAULT_NASDAQ_SYMBOLS = [
    "AAPL",
    "MSFT",
    "NVDA",
    "AMZN",
    "META",
    "TSLA",
    "GOOGL",
]


def load_nasdaq_symbols(project_root: Path, watchlist_file: str) -> List[str]:
    path = project_root / watchlist_file

    if not path.exists():
        return DEFAULT_NASDAQ_SYMBOLS

    df = pd.read_csv(path)
    if "symbol" not in df.columns:
        return DEFAULT_NASDAQ_SYMBOLS

    symbols = df["symbol"].dropna().astype(str).str.strip().tolist()
    return symbols or DEFAULT_NASDAQ_SYMBOLS