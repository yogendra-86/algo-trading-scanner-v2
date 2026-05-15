class SLTargetService:

    def calculate(self, entry_price, direction):

        risk_pct = 0.01  # 1%

        if direction == "bullish":

            sl = entry_price * (1 - risk_pct)
            target = entry_price * (1 + risk_pct)

        else:

            sl = entry_price * (1 + risk_pct)
            target = entry_price * (1 - risk_pct)

        return round(sl, 2), round(target, 2)
