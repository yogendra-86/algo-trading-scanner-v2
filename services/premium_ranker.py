import pandas as pd


class PremiumRanker:

    def rank(self, df):
        if df is None or df.empty:
            return pd.DataFrame(), pd.DataFrame()

        # ✅ USE ACTUAL SCORE (DO NOT OVERRIDE)
        if "score" not in df.columns:
            print("❌ Score column missing in dataframe")
            return pd.DataFrame(), pd.DataFrame()

        # ✅ Aggregate per symbol + direction
        agg_df = (
            df.groupby(["symbol", "direction"], as_index=False)
            .agg({
                "score": "max",   # take best strategy score
                "price": "last"
            })
        )

        # ✅ Split using direction (correct field)
        bullish = agg_df[agg_df["direction"] == "bullish"]
        bearish = agg_df[agg_df["direction"] == "bearish"]

        # ✅ Rank
        bullish_rank = (
            bullish.sort_values(by="score", ascending=False)
            .head(5)
            .reset_index(drop=True)
        )

        bearish_rank = (
            bearish.sort_values(by="score", ascending=False)
            .head(5)
            .reset_index(drop=True)
        )

        return bullish_rank, bearish_rank
