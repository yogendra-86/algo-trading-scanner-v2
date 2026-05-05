def breakdown_entry(df, market="NSE"):
    score = 0

    close = df["Close"].iloc[-1]
    prev_low = df["Low"].iloc[-2]
    volume = df["Volume"].iloc[-1]
    avg_volume = df["Volume"].rolling(20).mean().iloc[-1]

    breakdown_pct = 0.997 if market == "NSE" else 0.994
    vol_multiplier = 1.5 if market == "NSE" else 2.0

    if close < prev_low * breakdown_pct:
        score += 2

    if volume > avg_volume * vol_multiplier:
        score += 1

    if close < df["Close"].rolling(5).mean().iloc[-1]:
        score += 1

    return score
