import sqlite3
from datetime import datetime

import yfinance as yf

from services.paper_trade_service import (
    PaperTradeService
)

from utils.telegram_utils import (
    send_telegram_message
)

DB_PATH = "data/trade_registry.db"


def already_alerted(
    trade_uid,
    alert_type
):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT 1
    FROM trade_alerts
    WHERE trade_uid=?
    AND alert_type=?
    """, (
        trade_uid,
        alert_type
    ))

    row = cursor.fetchone()

    conn.close()

    return row is not None


def save_alert(
    trade_uid,
    alert_type
):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE
    INTO trade_alerts
    VALUES (?, ?, ?)
    """, (
        trade_uid,
        alert_type,
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()


service = PaperTradeService()

trades = service.get_open_trades()

for trade in trades:

    trade_uid = trade[0]
    symbol = trade[1]
    direction = trade[2]

    stop_loss = trade[5]
    target = trade[6]

    if stop_loss is None:
        continue

    if target is None:
        continue

    try:

        ticker = yf.Ticker(symbol)

        ltp = (
            ticker.history(period="1d")
            ["Close"]
            .iloc[-1]
        )

        if direction == "bullish":

            if (
                ltp >= target
                and not already_alerted(
                    trade_uid,
                    "TARGET"
                )
            ):

                send_telegram_message(
                    f"🎯 TARGET HIT\n\n"
                    f"Trade: {trade_uid}\n"
                    f"Symbol: {symbol}\n"
                    f"Target: {target}\n"
                    f"LTP: {ltp:.2f}"
                )

                save_alert(
                    trade_uid,
                    "TARGET"
                )

            if (
                ltp <= stop_loss
                and not already_alerted(
                    trade_uid,
                    "SL"
                )
            ):

                send_telegram_message(
                    f"🛑 STOP LOSS HIT\n\n"
                    f"Trade: {trade_uid}\n"
                    f"Symbol: {symbol}\n"
                    f"SL: {stop_loss}\n"
                    f"LTP: {ltp:.2f}"
                )

                save_alert(
                    trade_uid,
                    "SL"
                )

        else:

            if (
                ltp <= target
                and not already_alerted(
                    trade_uid,
                    "TARGET"
                )
            ):

                send_telegram_message(
                    f"🎯 TARGET HIT\n\n"
                    f"Trade: {trade_uid}\n"
                    f"Symbol: {symbol}\n"
                    f"Target: {target}\n"
                    f"LTP: {ltp:.2f}"
                )

                save_alert(
                    trade_uid,
                    "TARGET"
                )

            if (
                ltp >= stop_loss
                and not already_alerted(
                    trade_uid,
                    "SL"
                )
            ):

                send_telegram_message(
                    f"🛑 STOP LOSS HIT\n\n"
                    f"Trade: {trade_uid}\n"
                    f"Symbol: {symbol}\n"
                    f"SL: {stop_loss}\n"
                    f"LTP: {ltp:.2f}"
                )

                save_alert(
                    trade_uid,
                    "SL"
                )

    except Exception as e:

        print(
            symbol,
            e
        )
