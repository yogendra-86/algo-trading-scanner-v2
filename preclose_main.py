import argparse
import logging
import os
from datetime import datetime, timedelta, time

import pandas as pd
import pytz
import yfinance as yf

from dotenv import load_dotenv

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
        "--force",
        action="store_true",
        help="Force run regardless of schedule"
    )

    return parser.parse_args()


# ==========================================
# GET TRADING DATE
# ==========================================
def get_trading_date(market):

    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    # ======================================
    # NASDAQ crosses midnight IST
    # ======================================
    if market == "NASDAQ":

        # After midnight but before 2 AM
        if now.time() <= time(2, 0):

            trading_date = (
                now - timedelta(days=1)
            ).strftime("%Y-%m-%d")

        else:

            trading_date = now.strftime("%Y-%m-%d")

    else:

        trading_date = now.strftime("%Y-%m-%d")

    return trading_date


# ==========================================
# LOAD SIGNAL FILE
# ==========================================
def load_signal_file(market):

    trading_date = get_trading_date(market)

    file_path = (
        f"output/{market}/{trading_date}/"
        f"{market}_ALERTED_TRADES.csv"
    )

    logger.info(f"Loading signal file: {file_path}")

    if not os.path.exists(file_path):

        logger.error("Signal file not found")
        return None

    try:

        df = pd.read_csv(file_path)

        if df.empty:
            logger.warning("Signal file empty")
            return None

        return df

    except Exception as e:

        logger.error(f"Error reading signal file: {e}")
        return None


# ==========================================
# FETCH LATEST PRICE
# ==========================================
def fetch_latest_price(symbol):

    try:
        ticker = yf.Ticker(symbol)

        # ======================================
        # TRY FAST INFO
        # ======================================
        fast_info = ticker.fast_info

        latest_price = fast_info.get("lastPrice")

        if latest_price is not None:
            return float(latest_price)

        # ======================================
        # FALLBACK
        # ======================================
        df = ticker.history(period="1d")

        if df is None or df.empty:
            return None

        return float(df["Close"].iloc[-1])

    except Exception as e:

        logger.error(
            f"{symbol} latest price error: {e}"
        )

        return None



# ==========================================
# CALCULATE TRADE RESULT
# ==========================================
def calculate_trade_result(row):

    symbol = row["symbol"]
    direction = row["direction"]
    entry = float(row["price"])

    latest_price = fetch_latest_price(symbol)

    if latest_price is None:
        return None

    # ======================================
    # BULLISH
    # ======================================
    if direction == "bullish":

        pnl = latest_price - entry

    # ======================================
    # BEARISH
    # ======================================
    else:

        pnl = entry - latest_price

    pnl_pct = (pnl / entry) * 100

    status = "PROFIT" if pnl > 0 else "LOSS"

    return {
        "symbol": symbol,
        "direction": direction,
        "entry": round(entry, 2),
        "latest": round(latest_price, 2),
        "pnl": round(pnl, 2),
        "pnl_pct": round(pnl_pct, 2),
        "status": status
    }


# ==========================================
# BUILD SUMMARY
# ==========================================
def build_summary(results, market):

    total = len(results)

    wins = len([
        r for r in results
        if r["status"] == "PROFIT"
    ])

    losses = total - wins

    win_rate = (
        (wins / total) * 100
        if total > 0 else 0
    )

    total_pnl = sum([
        r["pnl"]
        for r in results
    ])

    msg = (
        f"📉 {market} Market Close Summary\n\n"
        f"Trades: {total}\n"
        f"Wins: {wins}\n"
        f"Losses: {losses}\n"
        f"Win Rate: {win_rate:.2f}%\n"
        f"Total P&L: {total_pnl:.2f}\n\n"
    )

    # ======================================
    # TOP RESULTS
    # ======================================
    sorted_results = sorted(
        results,
        key=lambda x: x["pnl"],
        reverse=True
    )

    msg += "🏆 Top Trades\n"

    for r in sorted_results:

        emoji = "🟢" if r["pnl"] > 0 else "🔴"

        msg += (
            f"{emoji} {r['symbol']} | "
            f"{r['direction']} | "
            f"Entry:{r['entry']:.2f} | "
            f"Close:{r['latest']:.2f} | "
            f"P&L:{r['pnl']:.2f} "
            f"({r['pnl_pct']:.2f}%)\n"
        )

    return msg


# ==========================================
# MAIN
# ==========================================
def main():

    args = parse_args()

    logger.info(
        f"Running preclose summary for {args.market}"
    )

    # ======================================
    # LOAD SIGNALS
    # ======================================
    signal_df = load_signal_file(args.market)

    if signal_df is None or signal_df.empty:

        logger.warning("No signals available")
        return

    logger.info(
        f"Loaded {len(signal_df)} signals"
    )

    # ======================================
    # CALCULATE RESULTS
    # ======================================
    results = []

    for _, row in signal_df.iterrows():

        result = calculate_trade_result(row)

        if result:
            results.append(result)

    if not results:

        logger.warning("No valid trade results")
        return

    logger.info(
        f"Calculated {len(results)} trade results"
    )

    # ======================================
    # BUILD SUMMARY
    # ======================================
    msg = build_summary(
        results,
        args.market
    )

    # ======================================
    # SEND TELEGRAM
    # ======================================
    success = send_telegram_message(msg)

    if success:

        logger.info(
            "Preclose Telegram alert sent successfully"
        )

    else:

        logger.error(
            "Preclose Telegram alert failed"
        )


# ==========================================
# ENTRY
# ==========================================
if __name__ == "__main__":
    main()
