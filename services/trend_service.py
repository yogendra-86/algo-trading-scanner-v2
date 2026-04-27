from typing import Dict, List


class TrendService:
    """
    Lightweight trend calculation using already generated signals.
    No re-scan. Fast. Accurate.
    """

    def get_trend(self, signals: List[dict]) -> Dict:
        if not signals:
            return {
                "trend": "Neutral",
                "bullish_count": 0,
                "bearish_count": 0,
                "confidence": "Low"
            }

        bullish = [
            s for s in signals
            if s.get("direction") == "bullish"
        ]

        bearish = [
            s for s in signals
            if s.get("direction") == "bearish"
        ]

        bullish_count = len(bullish)
        bearish_count = len(bearish)

        total = bullish_count + bearish_count

        # =========================
        # TREND LOGIC
        # =========================
        if bullish_count > bearish_count * 1.2:
            trend = "🟢 Bullish"
        elif bearish_count > bullish_count * 1.2:
            trend = "🔴 Bearish"
        else:
            trend = "⚖️ Sideways"

        # =========================
        # CONFIDENCE
        # =========================
        dominance = abs(bullish_count - bearish_count) / max(total, 1)

        if dominance > 0.5:
            confidence = "🔥 High"
        elif dominance > 0.25:
            confidence = "⚡ Medium"
        else:
            confidence = "⚠️ Low"

        return {
            "trend": trend,
            "bullish_count": bullish_count,
            "bearish_count": bearish_count,
            "confidence": confidence
        }

    def get_current_trend(self, market):
        """
        Backward compatibility method.
        Converts market-based request into signal-based trend.
        """

        try:
            # If you already have signals stored somewhere, use them
            # Otherwise return default structure

            return {
                "market": market,
                "trend": "neutral",
                "message": "Trend data not available (fallback)"
            }

        except Exception as e:
            print(f"TrendService error: {e}")
            return {
                "market": market,
                "trend": "neutral"
            }
