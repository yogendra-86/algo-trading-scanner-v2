def pullback_entry(df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    return (
        latest["Close"] > latest["ema_20"] and
        prev["Close"] < prev["ema_20"] and
        latest["rsi"] > 50
    )
