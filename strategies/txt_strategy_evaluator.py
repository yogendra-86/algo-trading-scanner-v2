class TxtStrategyEvaluator:

    # ======================================
    # EVALUATE CONDITIONS
    # ======================================
    def evaluate(self, strategy, df):

        close = float(df["Close"].iloc[-1])

        sma20 = float(
            df["Close"].rolling(20).mean().iloc[-1]
        )

        vwap = float(df["vwap"].iloc[-1])

        volume = float(df["Volume"].iloc[-1])

        avg_volume = float(
            df["Volume"].rolling(20).mean().iloc[-1]
        )

        condition_map = {

            "close > sma20": close > sma20,

            "close > vwap": close > vwap,

            "volume > avg_volume": (
                volume > avg_volume
            ),
        }

        for condition in strategy["conditions"]:

            if not condition_map.get(
                condition,
                False
            ):
                return 0

        return int(
            strategy.get("SCORE", 1)
        )
