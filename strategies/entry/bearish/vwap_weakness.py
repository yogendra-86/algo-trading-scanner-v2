def vwap_weakness(df, market="NSE"):
    score = 0

    close = df["Close"].iloc[-1]
    vwap = df["vwap"].iloc[-1]
    volume = df["Volume"].iloc[-1]
    avg_volume = df["Volume"].rolling(20).mean().iloc[-1]

    price_buffer = 0.998 if market == "NSE" else 0.996
    vol_multiplier = 1.3 if market == "NSE" else 1.8

    if close < vwap * price_buffer:
        score += 2

    if close < df["Close"].rolling(5).mean().iloc[-1]:
        score += 1

    if volume > avg_volume * vol_multiplier:
        score += 1

    return score
