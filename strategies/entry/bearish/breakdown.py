def breakdown_entry(df):
    latest = df.iloc[-1]
    volume = latest["Volume"]
    vol_sma = latest["volume_sma"]

    low_20 = df["Low"].rolling(20).min().iloc[-2]

    return (
        latest["Close"] < low_20 * 0.998 and
        volume > 1.3 * vol_sma
    )
