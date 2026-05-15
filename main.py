import argparse
import logging
from datetime import datetime
import os

import pandas as pd
import pytz
from dotenv import load_dotenv

from scanner.signal_engine import SignalEngine
from services.premium_ranker import PremiumRanker
from services.sl_target_service import SLTargetService
from services.confidence_engine import ConfidenceEngine
from services.trend_service import TrendService
from utils.market_session import is_market_open
from utils.telegram_utils import send_telegram_message

# ==========================================
# LOAD ENV
# ==========================================
load_dotenv(dotenv_path=".env")

# ==========================================
# LOGGING
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ==========================================
# ARGUMENTS
# ==========================================
def parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--market",
        required=True,
        choices=["NSE", "NASDAQ"]
    )

    parser.add_argument(
        "--stage",
        default="live"
    )

    parser.add_argument(
        "--force",
        action="store_true"
    )

    # ======================================
    # TXT STRATEGY
    # ======================================
    parser.add_argument(
        "--txt-strategy",
        default=None,
        help="Run specific TXT strategy only"
    )

    return parser.parse_args()


# ==========================================
# SAVE ALERTED TRADES
# ==========================================
def save_alerted_trades(
    market,
    bullish_rank,
    bearish_rank
):

    ist = pytz.timezone("Asia/Kolkata")

    today = datetime.now(ist).strftime("%Y-%m-%d")

    output_dir = f"output/{market}/{today}"

    os.makedirs(output_dir, exist_ok=True)

    alerted_df = pd.concat([
        bullish_rank,
        bearish_rank
    ])

    file_path = (
        f"{output_dir}/"
        f"{market}_ALERTED_TRADES.csv"
    )

    alerted_df.to_csv(
        file_path,
        index=False
    )

    logger.info(
        f"Alerted trades saved: {file_path}"
    )


# ==========================================
# BUILD TELEGRAM MESSAGE
# ==========================================
def build_message(
    market,
    bullish_rank,
    bearish_rank,
    trend_info,
    sl_service,
    confidence_engine,
    strategy_mode
):

    msg = (
        f"📊 {market} Market Trend: "
        f"{trend_info}\n"
        f"🧠 Strategy Mode: "
        f"{strategy_mode}\n\n"
    )

    # ======================================
    # TXT STRATEGY MODE
    # ======================================
    if bullish_rank.empty and bearish_rank.empty:
        return "No signals found"

    # ======================================
    # BULLISH
    # ======================================
    if not bullish_rank.empty:

        msg += "🟢 Top Bullish\n"

        for _, row in bullish_rank.iterrows():

            sl, target = sl_service.calculate(
                row["price"],
                "bullish"
            )

            confidence = confidence_engine.calculate(
                row["score"]
            )

            msg += (
                f"{row['symbol']} | "
                f"Entry:{row['price']:.2f} "
                f"SL:{sl:.2f} "
                f"Target:{target:.2f} "
                f"{confidence}\n"
            )

        msg += "\n"

    # ======================================
    # BEARISH
    # ======================================
    if not bearish_rank.empty:

        msg += "🔴 Top Bearish\n"

        for _, row in bearish_rank.iterrows():

            sl, target = sl_service.calculate(
                row["price"],
                "bearish"
            )

            confidence = confidence_engine.calculate(
                row["score"]
            )

            msg += (
                f"{row['symbol']} | "
                f"Entry:{row['price']:.2f} "
                f"SL:{sl:.2f} "
                f"Target:{target:.2f} "
                f"{confidence}\n"
            )

    return msg


# ==========================================
# MAIN
# ==========================================
def main():

    args = parse_args()

    logger.info(
        f"Running for market: {args.market}"
    )

    # ======================================
    # MARKET HOURS CHECK
    # ======================================
    if (
        not is_market_open(args.market)
        and args.stage != "close"
        and not args.force
    ):
        logger.info(
            "Market closed - skipping scan"
        )
        return

    # ======================================
    # SIGNAL ENGINE
    # ======================================
    signal_engine = SignalEngine()

    result_df = signal_engine.run(
        market=args.market,
        stage=args.stage,
        txt_strategy=args.txt_strategy
    )

    if result_df is None or result_df.empty:

        logger.warning("No signals found")
        return

    logger.info(
        f"Extracted signals: {len(result_df)}"
    )

    # ======================================
    # RANK SIGNALS
    # ======================================
    ranker = PremiumRanker()

    bullish_rank, bearish_rank = ranker.rank(
        result_df
    )

    # ======================================
    # SAVE ALERTED TRADES
    # ======================================
    save_alerted_trades(
        args.market,
        bullish_rank,
        bearish_rank
    )

    # ======================================
    # TREND
    # ======================================
    trend_service = TrendService()

    trend_info = trend_service.get_trend(
        result_df
    )

    # ======================================
    # SERVICES
    # ======================================
    sl_service = SLTargetService()

    confidence_engine = ConfidenceEngine()

    # ======================================
    # STRATEGY MODE
    # ======================================
    if args.txt_strategy:

        strategy_mode = (
            args.txt_strategy
            .replace(".txt", "")
        )

    else:

        strategy_mode = "Inbuild"

    # ======================================
    # MESSAGE
    # ======================================
    msg = build_message(
        args.market,
        bullish_rank,
        bearish_rank,
        trend_info,
        sl_service,
        confidence_engine,
        strategy_mode
    )

    # ======================================
    # TELEGRAM
    # ======================================
    success = send_telegram_message(msg)

    if success:

        logger.info(
            "Telegram alert sent successfully"
        )

    else:

        logger.error(
            "Telegram alert failed"
        )


# ==========================================
# ENTRY
# ==========================================
if __name__ == "__main__":
    main()
