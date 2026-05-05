import pandas as pd
import yfinance as yf
from datetime import datetime
import argparse
from utils.telegram_utils import send_telegram_message


# ==============================
# ARGUMENT PARSER
# ==============================
def parse_args():
    parser = argparse.ArgumentParser(description="Pre-close P&L Summary")
    parser.add_argument("--market", default="NSE", choices=["NSE", "NASDAQ"])
    return parser.parse_args()


# ==============================
# FETCH LTP
# ==============================
def fetch_ltp(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="5m", progress=False)

        if df is None or df.empty:
            return None

        return float(df["Close"].iloc[-1])

    except Exception as e:
        print(f"Error fetching LTP for {symbol}: {e}")
        return None


# ==============================
# CALCULATE P&L
# ==============================
def calculate_pnl(entry, ltp, direction):
    if ltp is None:
        return 0

    if direction == "bullish":
        return ltp - entry
    else:
        return entry - ltp


# ==============================
# MAIN FUNCTION
# ==============================
def main():
    args = parse_args()

    today = datetime.now().strftime("%Y-%m-%d")
    file_path = f"output/{args.market}/{today}/{args.market}_live_FINAL.csv"

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"❌ No data found: {e}")
        send_telegram_message(f"⚠️ {args.market} No data available for pre-close analysis.")
        return

    if df.empty:
        send_telegram_message(f"⚠️ {args.market} No trades generated today.")
        return

    msg = f"📊 {args.market} Pre-Close Summary\n\n"

    total_profit = 0
    total_trades = 0
    win_count = 0

    # ==============================
    # LOOP THROUGH TRADES
    # ==============================
    for _, row in df.iterrows():
        symbol = row["symbol"]
        entry = float(row["price"])
        direction = row["direction"]

        ltp = fetch_ltp(symbol)

        if ltp is None:
            continue

        pnl = calculate_pnl(entry, ltp, direction)
        total_profit += pnl
        total_trades += 1

        if pnl > 0:
            win_count += 1

        status = "🟢 Profit" if pnl > 0 else "🔴 Loss"

        msg += (
            f"{symbol} | Entry:{round(entry, 2)} "
            f"LTP:{round(ltp, 2)} "
            f"P&L:{round(pnl, 2)} {status}\n"
        )

    # ==============================
    # SUMMARY SECTION
    # ==============================
    win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0

    msg += "\n-------------------------\n"
    msg += f"💰 Total P&L: {round(total_profit, 2)}\n"
    msg += f"📈 Trades: {total_trades}\n"
    msg += f"✅ Win Rate: {round(win_rate, 2)}%\n"
    msg += f"⏱ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    # ==============================
    # SEND TELEGRAM
    # ==============================
    send_telegram_message(msg)
    print("✅ Pre-close alert sent successfully")


# ==============================
# ENTRY POINT
# ==============================
if __name__ == "__main__":
    main()
