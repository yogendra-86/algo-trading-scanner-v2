import sqlite3
from datetime import datetime

from services.alert_service import AlertService
from services.paper_trade_service import PaperTradeService


class TelegramCommandService:

    def __init__(self):

        self.alert_service = AlertService()

        self.conn = self.alert_service.conn

    def handle_papertrade_command(
        self,
        chat_id,
        alert_uid,
        signal_uid
    ):

        full_signal_uid = (
            f"{alert_uid}-{signal_uid}"
        )

        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT
            symbol,
            direction,
            entry_price
        FROM signals
        WHERE signal_uid = ?
        """, (full_signal_uid,))

        row = cursor.fetchone()

        if not row:

            return (
                False,
                "Signal not found"
            )

        symbol = row[0]
        direction = row[1]
        entry_price = row[2]

        cursor.execute("""
        INSERT INTO pending_commands (

            chat_id,

            command,

            alert_uid,

            signal_uid,

            status,

            created_at

        )
        VALUES (?, ?, ?, ?, ?, ?)
        """, (

            str(chat_id),

            "papertrade",

            alert_uid,

            signal_uid,

            "WAITING_QTY",

            datetime.utcnow().isoformat()

        ))

        self.conn.commit()

        msg = (
            "Signal Found\n\n"

            f"Alert: {alert_uid}\n"

            f"Signal: {signal_uid}\n\n"

            f"Symbol: {symbol}\n"

            f"Direction: {direction}\n"

            f"Entry: {entry_price:.2f}\n\n"

            "Enter Quantity:"
        )

        return (
            True,
            msg
        )

    def get_pending_command(
        self,
        chat_id
    ):

        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT

            id,

            command,

            alert_uid,

            signal_uid

        FROM pending_commands

        WHERE chat_id = ?

        AND status = 'WAITING_QTY'

        ORDER BY id DESC

        LIMIT 1
        """, (

            str(chat_id),

        ))

        return cursor.fetchone()

    def mark_completed(
        self,
        pending_id
    ):

        cursor = self.conn.cursor()

        cursor.execute("""
        UPDATE pending_commands

        SET status = 'COMPLETED'

        WHERE id = ?
        """, (

            pending_id,

        ))

        self.conn.commit()

    def complete_quantity(
        self,
        chat_id,
        quantity
    ):

        pending = self.get_pending_command(
            chat_id
        )

        if not pending:

            return (
                False,
                "No pending command"
            )

        pending_id = pending[0]

        alert_uid = pending[2]

        signal_uid = pending[3]

        service = PaperTradeService()

        trade = (
            service.create_trade(
                alert_uid,
                signal_uid,
                int(quantity)
            )
        )

        self.mark_completed(
            pending_id
        )

        if not trade:

            return (
                False,
                "Trade creation failed"
            )

        msg = (
            "Paper Trade Created\n\n"

            f"Trade UID: "
            f"{trade['trade_uid']}\n\n"

            f"Symbol: "
            f"{trade['symbol']}\n"

            f"Qty: "
            f"{trade['quantity']}\n\n"

            "Status: OPEN"
        )

        return (
            True,
            msg
        )
