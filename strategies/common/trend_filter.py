def get_trend(df):
    latest = df.iloc[-1]

    ema5 = latest["ema_5"]
    ema20 = latest["ema_20"]
    ema50 = latest["ema_50"]
    rsi = latest["rsi"]

    if ema5 > ema20 > ema50 and rsi > 50:
        return "bullish"
    elif ema5 < ema20 < ema50 and rsi < 50:
        return "bearish"
    else:
        return "neutral"
