from typing import Dict

from services.premium_ranker import PremiumRanker
from services.scanner_gateway import ScannerGateway


class Top5Service:
    """
    Top5 Service (Production Ready)

    - Uses cached/latest scan → FAST response
    - Applies PremiumRanker
    - Ensures balanced output (5 bullish + 5 bearish)
    """

    def __init__(self):
        self.gateway = ScannerGateway()

    def get_top5(self, market: str, direction: str) -> Dict:
        market = market.upper().strip()
        direction = direction.lower().strip()

        if direction not in ["bullish", "bearish"]:
            raise ValueError("direction must be 'bullish' or 'bearish'")

        # ================================
        # STEP 1: FETCH LATEST SCAN (FAST)
        # ================================
        payload = self.gateway.get_latest_available_scan(
            market=market,
            stage="range15"
        )

        signals = payload.get("signals", [])
        as_of = payload.get("as_of")

        print(f"[DEBUG] {market} signals fetched: {len(signals)}")

        # ================================
        # STEP 2: HANDLE NO SIGNAL CASE
        # ================================
        if not signals:
            return {
                "market": market,
                "direction": direction,
                "picks": [],
                "as_of": as_of,
                "message": "⚠️ No signals found in latest scan"
            }

        # ================================
        # STEP 3: SELECT PRICE BAND
        # ================================
        if market == "NASDAQ":
            min_price, max_price = 5, 50
        else:
            min_price, max_price = 50, 2000

        ranker = PremiumRanker(
            min_price=min_price,
            max_price=max_price,
            min_rr=1.0,
            top_n=5
        )

        # ================================
        # STEP 4: BALANCED RANKING
        # ================================
        bullish_top5, bearish_top5 = ranker.get_balanced_top5(signals)

        # ================================
        # STEP 5: PICK BASED ON USER REQUEST
        # ================================
        picks = bullish_top5 if direction == "bullish" else bearish_top5

        # ================================
        # STEP 6: FINAL RESPONSE
        # ================================
        if not picks:
            return {
                "market": market,
                "direction": direction,
                "picks": [],
                "as_of": as_of,
                "message": "⚠️ No stocks matched criteria after filtering"
            }

        return {
            "market": market,
            "direction": direction,
            "picks": picks,
            "as_of": as_of,
            "count": len(picks)
        }
