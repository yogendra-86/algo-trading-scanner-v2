import sqlite3
from datetime import datetime
import pytz


class AlertService:

    DB_PATH = "data/trade_registry.db"

    def __init__(self):

        self.conn = sqlite3.connect(
            self.DB_PATH
        )

        self.create_tables()

    def create_tables(self):

        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (

            alert_uid TEXT PRIMARY KEY,

            market TEXT,

            strategy_mode TEXT,

            created_at TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS signals (

            signal_uid TEXT PRIMARY KEY,

            alert_uid TEXT,

            symbol TEXT,

            strategy TEXT,

            direction TEXT,

            entry_price REAL,

            score INTEGER,

            status TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS paper_trades (

            paper_trade_uid TEXT PRIMARY KEY,

            alert_uid TEXT,

            signal_uid TEXT,

            symbol TEXT,

            direction TEXT,

            quantity INTEGER,

            entry_price REAL,

            status TEXT,

            created_at TEXT
        )
        """)

        self.conn.commit()

    def generate_alert_uid(self):

        ist = pytz.timezone(
            "Asia/Kolkata"
        )

        today = datetime.now(
            ist
        ).strftime("%Y%m%d")

        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT COUNT(*)
        FROM alerts
        WHERE alert_uid LIKE ?
        """, (f"ALT-{today}-%",))

        count = cursor.fetchone()[0] + 1

        return (
            f"ALT-{today}-"
            f"{count:03d}"
        )

    def save_alert(
        self,
        alert_uid,
        market,
        strategy_mode
    ):

        cursor = self.conn.cursor()

        cursor.execute("""
        INSERT INTO alerts
        VALUES (?, ?, ?, ?)
        """, (

            alert_uid,
            market,
            strategy_mode,
            datetime.utcnow().isoformat()

        ))

        self.conn.commit()

    def save_signal(
        self,
        signal_uid,
        alert_uid,
        row,
        strategy_mode
    ):

        cursor = self.conn.cursor()

        cursor.execute("""
        INSERT INTO signals
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            signal_uid,

            alert_uid,

            row["symbol"],

            strategy_mode,

            row["direction"],

            float(row.get("price", 0)),

            int(row.get("score", 0)),

            "NEW"

        ))

        self.conn.commit()
