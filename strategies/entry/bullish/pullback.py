def pullback_entry(df, market="NSE"):
    score = 0

    close = df["Close"].iloc[-1]
    sma20 = df["Close"].rolling(20).mean().iloc[-1]

    bounce_strength = 1.002 if market == "NSE" else 1.004

    if abs(close - sma20) / sma20 < 0.02:
        score += 1

    if close > df["Close"].iloc[-2] * bounce_strength:
        score += 2

    if df["Low"].iloc[-1] > df["Low"].iloc[-2]:
        score += 1

    return score
