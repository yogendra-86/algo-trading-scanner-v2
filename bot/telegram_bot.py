import time
import os
import requests
import pandas as pd

from services.premium_ranker import PremiumRanker
from services.trend_service import TrendService
from services.trade_calculator import TradeCalculator
from services.confidence_engine import ConfidenceEngine

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


class TelegramBot:
    def __init__(self, project_root):
        self.offset = None
        self.project_root = project_root

        self.ranker = PremiumRanker()
        self.trend_service = TrendService()
        self.trade_calc = TradeCalculator()
        self.conf_engine = ConfidenceEngine()

    # ==============================
    # TELEGRAM API
    # ==============================
    def get_updates(self):
        url = f"{BASE_URL}/getUpdates"
        params = {"timeout": 100, "offset": self.offset}

        try:
            res = requests.get(url, params=params, timeout=120).json()
            return res.get("result", [])
        except Exception:
            return []

    def send_message(self, text):
        url = f"{BASE_URL}/sendMessage"

        try:
            requests.post(url, data={
                "chat_id": CHAT_ID,
                "text": text
            }, timeout=10)
        except Exception:
            pass

    # ==============================
    # LOAD LATEST SIGNAL FILE
    # ==============================
    def load_latest_signals(self, market="NSE"):
        base_path = f"{self.project_root}/output/{market}"

        if not os.path.exists(base_path):
            return pd.DataFrame()

        dates = sorted(os.listdir(base_path), reverse=True)

        for d in dates:
            file_path = f"{base_path}/{d}/{market}_range15_FINAL.csv"
            if os.path.exists(file_path):
                try:
                    df = pd.read_csv(file_path)
                    return df
                except Exception:
                    continue

        return pd.DataFrame()

    # ==============================
    # FORMAT TOP5 MESSAGE
    # ==============================
    def build_top5_message(self, df, market):
        if df is None or df.empty:
            return "⚠️ No signals available."

        # Convert to signals
        signals = df.to_dict("records")

        # Trend
        trend_info = self.trend_service.get_trend(signals)

        # Ranking
        top_bullish, top_bearish = self.ranker.rank(df)

        msg = f"📊 {market} Market Trend: {trend_info['trend']} ({trend_info['confidence']})\n\n"

        # =======================
        # BULLISH
        # =======================
        msg += "🟢 Top 5 Bullish\n"
        for _, row in top_bullish.iterrows():
            trade = self.trade_calc.calculate(row["price"], "bullish")
            conf = self.conf_engine.calculate(row["score"])

            msg += (
                f"{row['symbol']} | Entry:{trade['entry']} "
                f"SL:{trade['sl']} Target:{trade['target']} {conf}\n"
            )

        # =======================
        # BEARISH
        # =======================
        msg += "\n🔴 Top 5 Bearish\n"
        for _, row in top_bearish.iterrows():
            trade = self.trade_calc.calculate(row["price"], "bearish")
            conf = self.conf_engine.calculate(row["score"])

            msg += (
                f"{row['symbol']} | Entry:{trade['entry']} "
                f"SL:{trade['sl']} Target:{trade['target']} {conf}\n"
            )

        return msg

    # ==============================
    # TREND MESSAGE
    # ==============================
    def build_trend_message(self, df, market):
        if df is None or df.empty:
            return "⚠️ No data available."

        signals = df.to_dict("records")
        trend_info = self.trend_service.get_trend(signals)

        return (
            f"📈 {market} Trend: {trend_info['trend']}\n"
            f"Confidence: {trend_info['confidence']}\n"
            f"Bullish: {trend_info['bullish_count']} | "
            f"Bearish: {trend_info['bearish_count']}"
        )

    # ==============================
    # COMMAND HANDLER
    # ==============================
    def handle_command(self, text):

        text = text.lower().strip()

        # DEFAULT MARKET
        market = "NSE"

        if "nasdaq" in text:
            market = "NASDAQ"

        df = self.load_latest_signals(market)

        # =======================
        # COMMANDS
        # =======================
        if text in ["/top5", "top5 bullish", "top5 bearish"]:
            return self.build_top5_message(df, market)

        elif text in ["/trend", "/send currenttrend"]:
            return self.build_trend_message(df, market)

        else:
            return (
                "🤖 Commands:\n"
                "/top5 → Top signals\n"
                "/trend → Market trend\n"
                "top5 bullish\n"
                "top5 bearish\n"
            )

    # ==============================
    # RUN LOOP
    # ==============================
    def run(self):
        print("🚀 Telegram Bot Started...")

        while True:
            updates = self.get_updates()

            for update in updates:
                self.offset = update["update_id"] + 1

                try:
                    message = update.get("message", {})
                    text = message.get("text", "")

                    if not text:
                        continue

                    response = self.handle_command(text)
                    self.send_message(response)
                    print("Sending Telegram alert:", message) #
                except Exception:
                    continue

            time.sleep(2)
