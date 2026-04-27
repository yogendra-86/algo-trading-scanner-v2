import pandas as pd


class PremiumRanker:

    def rank(self, df):
        if df is None or df.empty:
            return pd.DataFrame(), pd.DataFrame()

        # Score based on strategy weight
        strategy_score = {
            "trend_following": 5,
            "vwap_strength": 4,
            "breakout_momentum": 5,
            "pullback_buy": 3,
            "simple_momentum": 2,
            "trend_breakdown": 5,
            "vwap_weakness": 4,
            "breakdown_momentum": 5,
            "pullback_sell": 3,
            "simple_weakness": 2,
        }

        df["score"] = df["strategy"].map(strategy_score).fillna(1)

        # Aggregate per symbol
        agg_df = (
            df.groupby("symbol")
            .agg({
                "score": "sum",
                "price": "last"
            })
            .reset_index()
        )

        # Split bullish / bearish
        bullish = df[df["strategy"].str.contains("trend|momentum|buy")]
        bearish = df[df["strategy"].str.contains("breakdown|weakness|sell")]

        bullish_rank = (
            bullish.groupby("symbol")
            .agg({
                  "score": "sum",
                  "price": "last"
            })
            .sort_values(by="score", ascending=False)
            .head(5)
            .reset_index()
        )

        bearish_rank = (
            bearish.groupby("symbol")
            .agg({
                "score": "sum",
                "price": "last"
            })
            .sort_values(by="score", ascending=False)
            .head(5)
            .reset_index()
        )

        return bullish_rank, bearish_rank
