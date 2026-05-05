def pullback_sell(df, market="NSE"):
    score = 0

    close = df["Close"].iloc[-1]
    sma20 = df["Close"].rolling(20).mean().iloc[-1]

    rejection_strength = 0.998 if market == "NSE" else 0.996

    if abs(close - sma20) / sma20 < 0.02:
        score += 1

    if close < df["Close"].iloc[-2] * rejection_strength:
        score += 2

    if df["High"].iloc[-1] < df["High"].iloc[-2]:
        score += 1

    return score
