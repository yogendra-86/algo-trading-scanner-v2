import pandas as pd


class CSVSignalExtractor:

    def extract(self, csv_paths):
        signals = []

        for path in csv_paths:
            try:
                df = pd.read_csv(path)
                df.columns = [c.lower() for c in df.columns]

                for _, row in df.iterrows():
                    symbol = row.get("symbol") or row.get("stock")
                    price = row.get("close") or row.get("ltp")

                    if not symbol or not price:
                        continue

                    price = float(price)

                    signals.append({
                        "symbol": symbol,
                        "entry": price,
                        "sl": round(price * 0.99, 2),
                        "target": round(price * 1.02, 2),
                        "direction": "bearish" if "bearish" in path.lower() else "bullish",
                        "strategy": path.split("/")[-1]
                    })

            except Exception as e:
                print(e)

        return signals
