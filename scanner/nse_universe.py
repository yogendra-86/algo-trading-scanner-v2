from pathlib import Path
from typing import List

import pandas as pd


DEFAULT_NSE_SYMBOLS = [
    "RELIANCE",
    "TCS",
    "INFY",
    "HDFCBANK",
    "ICICIBANK",
    "SBIN",
    "LT",
]


def load_nse_symbols(project_root: Path, watchlist_file: str) -> List[str]:
    path = project_root / watchlist_file

    if not path.exists():
        return DEFAULT_NSE_SYMBOLS

    df = pd.read_csv(path)
    print(df.columns)
    if "symbol" not in df.columns:
        return DEFAULT_NSE_SYMBOLS

    symbols = df["symbol"].dropna().astype(str).str.strip().tolist()
    return symbols or DEFAULT_NSE_SYMBOLS
