from typing import Dict


def is_high_probability(row: Dict) -> bool:
    entry = float(row.get("entry_price", 0) or 0)
    stop = float(row.get("stop_loss", 0) or 0)

    if entry <= 0 or stop <= 0:
        return False

    risk = abs(entry - stop)

    if risk < 0.2:
        return False

    if risk > entry * 0.05:
        return False

    return True

def evaluate_nasdaq_penny_bullish(df):
    if len(df) < 20:
        return None

    df["ema9"] = df["Close"].ewm(span=9).mean()
    df["ema20"] = df["Close"].ewm(span=20).mean()
    df["avg_vol"] = df["Volume"].rolling(20).mean()

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    ema_cross = prev["ema9"] <= prev["ema20"] and latest["ema9"] > latest["ema20"]
    volume_spike = latest["Volume"] > 2 * latest["avg_vol"]
    breakout = latest["Close"] > df["High"].rolling(10).max().iloc[-1]

    if ema_cross and volume_spike and breakout:
        return "LONG", latest["Close"]

    return None


def evaluate_nasdaq_penny_bearish(df):
    if len(df) < 20:
        return None

    df["ema9"] = df["Close"].ewm(span=9).mean()
    df["ema20"] = df["Close"].ewm(span=20).mean()
    df["avg_vol"] = df["Volume"].rolling(20).mean()

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    ema_cross = prev["ema9"] >= prev["ema20"] and latest["ema9"] < latest["ema20"]
    volume_spike = latest["Volume"] > 2 * latest["avg_vol"]
    breakdown = latest["Close"] < df["Low"].rolling(10).min().iloc[-1]

    if ema_cross and volume_spike and breakdown:
        return "SHORT", latest["Close"]

    return None
