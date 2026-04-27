from typing import Dict

from services.premium_ranker import PremiumRanker
from services.scanner_gateway import ScannerGateway


class EODService:
    def __init__(self):
        self.gateway = ScannerGateway()
        self.ranker = PremiumRanker(
            min_price=50.0,
            max_price=2000.0,
            min_rr=1.0,
            top_n=5,
        )

    def get_market_closed_summary(self, market: str) -> Dict:
        payload = self.gateway.get_latest_available_scan(market=market, stage="range15")
        signals = payload.get("signals", [])

        bullish_top5 = self.ranker.rank(signals=signals, direction="bullish")
        bearish_top5 = self.ranker.rank(signals=signals, direction="bearish")

        bullish_total = sum(float(item.get("premium_score", 0)) for item in bullish_top5)
        bearish_total = sum(float(item.get("premium_score", 0)) for item in bearish_top5)

        if bullish_total > bearish_total:
            trend = "Bullish"
        elif bearish_total > bullish_total:
            trend = "Bearish"
        else:
            trend = "Neutral"

        return {
            "market": market.upper(),
            "trend": trend,
            "bullish_top5": bullish_top5,
            "bearish_top5": bearish_top5,
            "as_of": payload.get("as_of"),
            "raw": payload,
        }
