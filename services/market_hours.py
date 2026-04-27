from dataclasses import dataclass
from datetime import datetime, time
from zoneinfo import ZoneInfo


IST = ZoneInfo("Asia/Kolkata")
ET = ZoneInfo("America/New_York")


@dataclass
class MarketSession:
    market: str
    is_open: bool
    now_local: datetime
    session_label: str
    now_display: str


class MarketHoursService:
    def get_session(self, market: str) -> MarketSession:
        market = market.upper()

        if market == "NSE":
            now_local = datetime.now(IST)
            is_open = self._is_weekday(now_local) and time(9, 15) <= now_local.time() <= time(15, 30)
            return MarketSession(
                market="NSE",
                is_open=is_open,
                now_local=now_local,
                session_label="NSE Market Hours",
                now_display=now_local.strftime("%Y-%m-%d %H:%M:%S IST"),
            )

        if market == "NASDAQ":
            now_local = datetime.now(ET)
            is_open = self._is_weekday(now_local) and time(9, 30) <= now_local.time() <= time(16, 0)
            return MarketSession(
                market="NASDAQ",
                is_open=is_open,
                now_local=now_local,
                session_label="NASDAQ Market Hours",
                now_display=now_local.strftime("%Y-%m-%d %H:%M:%S ET"),
            )

        raise ValueError(f"Unsupported market: {market}")

    @staticmethod
    def _is_weekday(dt: datetime) -> bool:
        return dt.weekday() < 5
