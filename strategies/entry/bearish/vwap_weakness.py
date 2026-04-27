def vwap_weakness(df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    return (
        latest["Close"] < latest["vwap"] and
        prev["Close"] > prev["vwap"]
    )
