import argparse
import os
import pandas as pd
from dotenv import load_dotenv
from config.settings import Settings
from scanner.signal_engine import run_stage_for_market
from utils.logging_utils import get_logger
from datetime import datetime
from services.premium_ranker import PremiumRanker
from services.trend_service import TrendService
from services.trade_calculator import TradeCalculator
from services.confidence_engine import ConfidenceEngine
from utils.telegram_utils import send_telegram_message
from utils.market_session import is_market_open

logger = get_logger("main")

# Load ENV
load_dotenv(dotenv_path="/opt/algo-trading-scanner-v2/.env")


# ==============================
# ARGUMENT PARSER
# ==============================
def parse_args():
    parser = argparse.ArgumentParser(description="Algo Trading Scanner V2")
    parser.add_argument("--market", required=True, choices=["NSE", "NASDAQ"])
    parser.add_argument("--stage", required=True, choices=["prep", "live", "range15"])
    return parser.parse_args()


# ==============================
# LOAD SYMBOLS
# ==============================
def load_symbols(project_root, market):
    file_path = os.path.join(
        project_root,
        "data",
        "watchlists",
        f"{market.lower()}_symbols.csv"
    )

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Symbols file not found: {file_path}")

    df = pd.read_csv(file_path, header=None)

    symbols = (
        df[0]
        .astype(str)
        .str.strip()
        .str.replace("$", "", regex=False)
    )

    symbols = symbols[
        (symbols != "") &
        (symbols.str.lower() != "symbol") &
        (~symbols.str.contains("^nan$", case=False))
    ]

    symbols = symbols.tolist()

    if market == "NSE":
        symbols = [s if s.endswith(".NS") else f"{s}.NS" for s in symbols]

    return symbols


# ==============================
# BUILD TELEGRAM MESSAGE
# ==============================
def build_message(market, trend_info, top_bullish, top_bearish, calc, conf_engine):
    msg = f"📊 {market} Market Trend: {trend_info['trend']} ({trend_info.get('confidence','N/A')})\n\n"

    msg += "🟢 Top 5 Bullish\n"
    for _, row in top_bullish.iterrows():
        trade = calc.calculate(row["price"], "bullish")
        conf = conf_engine.calculate(row["score"])

        msg += (
            f"{row['symbol']} | Entry:{trade['entry']} "
            f"SL:{trade['sl']} Target:{trade['target']} {conf}\n"
        )

    msg += "\n🔴 Top 5 Bearish\n"
    for _, row in top_bearish.iterrows():
        trade = calc.calculate(row["price"], "bearish")
        conf = conf_engine.calculate(row["score"])

        msg += (
            f"{row['symbol']} | Entry:{trade['entry']} "
            f"SL:{trade['sl']} Target:{trade['target']} {conf}\n"
        )

    return msg


# ==============================
# MAIN
# ==============================
def main():
    try:
        args = parse_args()
        settings = Settings.load()
        project_root = settings.project_root

        logger.info(f"Project root: {project_root}")

        # =========================
        # MARKET CHECK
        # =========================
        now = datetime.now()

        if not is_market_open():
            print("Market closed - skipping scan")
            return

        if now.hour == 9 and now.minute < 25:
            print("Waiting for stable market data...")
            return

        # =========================
        # LOAD SYMBOLS
        # =========================
        symbols = load_symbols(project_root, args.market)
        logger.info(f"Loaded {len(symbols)} symbols for {args.market}")

        # =========================
        # RUN SCANNER
        # =========================
        result_df = run_stage_for_market(
            symbols=symbols,
            market=args.market,
            stage=args.stage
        )

        # =========================
        # NO SIGNALS (FAIL-SAFE ALERT)
        # =========================
        if result_df is None or result_df.empty:
            logger.warning("No signals generated.")

            msg = f"""
                📊 {args.market} Market Update

                ⚠️ No strong signals found.

                ⏱ Time: {datetime.now()}
            """

            send_telegram_message(msg)
            print("Fallback alert sent")
            return

        logger.info(f"Extracted signals: {len(result_df)}")
        print(f"Extracted signals: {len(result_df)}")

        # =========================
        # SERVICES
        # =========================
        ranker = PremiumRanker()
        trend_service = TrendService()
        calc = TradeCalculator()
        conf_engine = ConfidenceEngine()

        # =========================
        # TREND
        # =========================
        signals = result_df.to_dict("records")
        trend_info = trend_service.get_current_trend(args.market)

        # =========================
        # RANKING
        # =========================
        top_bullish, top_bearish = ranker.rank(result_df)

        print("\n🟢 TOP 5 BULLISH")
        print(top_bullish)

        print("\n🔴 TOP 5 BEARISH")
        print(top_bearish)

        # =========================
        # TELEGRAM
        # =========================
        msg = build_message(
            args.market,
            trend_info,
            top_bullish,
            top_bearish,
            calc,
            conf_engine
        )

        print("Sending Telegram message...")
        print(msg)

        success = send_telegram_message(msg)
        print("Bot Started....")
        print("Running scan at:", datetime.now())

        if success:
            logger.info("Telegram alert sent successfully")
        else:
            logger.error("Telegram failed")

    except Exception as e:
        logger.error(f"CRITICAL ERROR: {e}")

        try:
            send_telegram_message(f"🚨 SYSTEM ERROR:\n{str(e)}")
        except:
            pass


# ==============================
# ENTRY POINT
# ==============================
if __name__ == "__main__":
    main()
