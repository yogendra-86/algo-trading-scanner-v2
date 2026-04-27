def vwap_strength(df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    return (
        latest["Close"] > latest["vwap"] and
        prev["Close"] < latest["vwap"]
    )
