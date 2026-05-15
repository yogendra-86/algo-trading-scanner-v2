import pandas as pd


class TrendService:

    def get_trend(self, signals):

        # ======================================
        # EMPTY CHECK
        # ======================================
        if signals is None:
            return "neutral"

        if isinstance(signals, pd.DataFrame):

            if signals.empty:
                return "neutral"

            bullish = len(
                signals[
                    signals["direction"] == "bullish"
                ]
            )

            bearish = len(
                signals[
                    signals["direction"] == "bearish"
                ]
            )

        else:

            bullish = len([
                s for s in signals
                if s.get("direction") == "bullish"
            ])

            bearish = len([
                s for s in signals
                if s.get("direction") == "bearish"
            ])

        # ======================================
        # TREND LOGIC
        # ======================================
        if bullish > bearish:
            return "bullish"

        elif bearish > bullish:
            return "bearish"

        return "neutral"
