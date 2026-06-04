from services.alert_service import AlertService
from datetime import datetime


class PaperTradeService:

    def __init__(self):

        self.alert_service = AlertService()

        self.conn = self.alert_service.conn

    def generate_trade_uid(self):

        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT COUNT(*)
        FROM paper_trades
        """)

        count = cursor.fetchone()[0] + 1

        return f"PT-{count:06d}"

    def create_trade(
        self,
        alert_uid,
        signal_uid,
        quantity
    ):

        cursor = self.conn.cursor()

        full_signal_uid = (
            f"{alert_uid}-{signal_uid}"
        )

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

            return None

        symbol = row[0]
        direction = row[1]
        entry_price = row[2]

        trade_uid = (
            self.generate_trade_uid()
        )

        cursor.execute("""
        INSERT INTO paper_trades
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            trade_uid,

            alert_uid,

            full_signal_uid,

            symbol,

            direction,

            quantity,

            entry_price,

            "OPEN",

            datetime.utcnow().isoformat()

        ))

        self.conn.commit()

        return {

            "trade_uid":
                trade_uid,

            "symbol":
                symbol,

            "direction":
                direction,

            "entry_price":
                entry_price,

            "quantity":
                quantity
        }

    def create_trade_from_signal(
        self,
        alert_uid,
        signal_uid,
        quantity
    ):

        return self.create_trade(
            alert_uid,
            signal_uid,
            quantity
        )
