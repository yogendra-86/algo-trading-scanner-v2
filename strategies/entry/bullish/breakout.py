def breakout_entry(df):
    latest = df.iloc[-1]
    volume = latest["Volume"]
    vol_sma = latest["volume_sma"]

    high_20 = df["High"].rolling(20).max().iloc[-2]

    return (
        latest["Close"] > high_20 * 1.002 and
        volume > 1.3 * vol_sma
    )