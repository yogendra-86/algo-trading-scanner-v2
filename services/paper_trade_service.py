from services.alert_service import AlertService
from datetime import datetime
import yfinance as yf


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
            entry_price,
            stop_loss,
            target
        FROM signals
        WHERE signal_uid = ?
        """, (full_signal_uid,))

        row = cursor.fetchone()

        if not row:

            return None

        symbol = row[0]
        direction = row[1]
        entry_price = row[2]
        stop_loss = row[3]
        target = row[4]

        trade_uid = (
            self.generate_trade_uid()
        )

        cursor.execute("""
        INSERT INTO paper_trades (

            paper_trade_uid,
            alert_uid,
            signal_uid,
            symbol,
            direction,
            quantity,
            entry_price,
            status,
            created_at,
            stop_loss,
            target

        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            trade_uid,
            alert_uid,
            full_signal_uid,
            symbol,
            direction,
            quantity,
            entry_price,
            "OPEN",
            datetime.utcnow().isoformat(),
            stop_loss,
            target
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

    def get_open_trades(self):

        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT
            paper_trade_uid,
            symbol,
            direction,
            quantity,
            entry_price,
            stop_loss,
            target

        FROM paper_trades
        WHERE status = 'OPEN'
        """)

        return cursor.fetchall()

    def get_trade(self, trade_uid):

        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT
            paper_trade_uid,
            symbol,
            direction,
            quantity,
            entry_price,
            status
        FROM paper_trades
        WHERE paper_trade_uid = ?
        """, (
        trade_uid,

        ))

        return cursor.fetchone()

    def close_trade(self,trade_uid):

        trade = self.get_trade(trade_uid)

        if not trade:
            return None

        if trade[5] != "OPEN":
            return None

        symbol = trade[1]
        direction = trade[2]
        quantity = trade[3]
        entry_price = trade[4]
        ticker = yf.Ticker(symbol)

        current_price = (
        ticker.history(period="1d")["Close"].iloc[-1])

        if direction == "bullish":
            pnl = (current_price - entry_price) * quantity
        else:
            pnl = (entry_price - current_price) * quantity

        cursor = self.conn.cursor()

        cursor.execute("""
            UPDATE paper_trades
            SET
                status = ?,
                exit_price = ?,
                closed_at = ?,
                pnl = ?

        WHERE paper_trade_uid = ?
        """, (
            "CLOSED",

            float(current_price),
            datetime.utcnow().isoformat(),

            float(pnl),
            trade_uid

        ))

        self.conn.commit()

        return {
            "trade_uid": trade_uid,
            "symbol": symbol,
            "exit_price": float(current_price),
            "pnl": float(pnl)
        }

    def get_closed_trades(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT
            paper_trade_uid,
            symbol,
            quantity,
            entry_price,
            exit_price,
            pnl,
            closed_at

        FROM paper_trades
        WHERE status = 'CLOSED'
        ORDER BY closed_at DESC
        """)

        return cursor.fetchall()
