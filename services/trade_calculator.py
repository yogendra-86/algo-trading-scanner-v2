class TradeCalculator:

    def calculate(self, price, direction):
        price = float(price)

        if direction == "bullish":
            sl = round(price * 0.99, 2)
            target = round(price * 1.01, 2)

        else:
            sl = round(price * 1.01, 2)
            target = round(price * 0.99, 2)

        return {
            "entry": price,
            "sl": sl,
            "target": target
        }
