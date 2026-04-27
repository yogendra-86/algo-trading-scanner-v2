import pandas as pd


def add_indicators(df):
    # EMA
    df["ema_5"] = df["Close"].ewm(span=5).mean()
    df["ema_20"] = df["Close"].ewm(span=20).mean()
    df["ema_50"] = df["Close"].ewm(span=50).mean()

    # RSI
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))

    # VWAP
    df["vwap"] = (df["Close"] * df["Volume"]).cumsum() / df["Volume"].cumsum()

    # Volume SMA
    df["volume_sma"] = df["Volume"].rolling(20).mean()

    df.dropna(inplace=True)

    return df
