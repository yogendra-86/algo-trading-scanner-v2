from typing import Optional

from services.eod_service import EODService
from services.market_hours import MarketHoursService
from services.top5_service import Top5Service
from services.trend_service import TrendService
from services.alert_formatter import AlertFormatter
from bot.session_store import SessionStore


class CommandRouter:
    def __init__(self, session_store: SessionStore):
        self.session_store = session_store
        self.market_hours = MarketHoursService()
        self.top5_service = Top5Service()
        self.trend_service = TrendService()
        self.eod_service = EODService()
        self.formatter = AlertFormatter()

    def handle_text(self, chat_id: int, text: str) -> str:
        raw = (text or "").strip()
        normalized = raw.lower()

        # Check if user is in middle of conversation
        pending = self.session_store.get(chat_id)
        if pending:
            response = self._handle_pending(chat_id, raw, pending)
            if response:
                return response

        # Commands
        if normalized in {"/start", "start"}:
            return (
                "Algo Trading Bot Ready\n\n"
                "Commands:\n"
                "/send currenttrend\n"
                "top5 bullish\n"
                "top5 bearish"
            )

        if normalized == "/send currenttrend":
            self.session_store.set(chat_id, {"action": "currenttrend_market"})
            return "Please enter market: NSE or NASDAQ"

        if normalized == "top5 bullish":
            self.session_store.set(chat_id, {"action": "top5_bullish_market"})
            return "Please enter market: NSE or NASDAQ"

        if normalized == "top5 bearish":
            self.session_store.set(chat_id, {"action": "top5_bearish_market"})
            return "Please enter market: NSE or NASDAQ"

        return "Invalid command. Use /send currenttrend or top5 bullish/bearish"

    def _handle_pending(self, chat_id: int, text: str, pending: dict) -> Optional[str]:
        market = text.strip().upper()

        if market not in ["NSE", "NASDAQ"]:
            return "Invalid market. Enter NSE or NASDAQ"

        action = pending.get("action")
        self.session_store.clear(chat_id)

        if action == "currenttrend_market":
            return self._current_trend(market)

        if action == "top5_bullish_market":
            return self._top5(market, "bullish")

        if action == "top5_bearish_market":
            return self._top5(market, "bearish")

        return None

    def _current_trend(self, market: str) -> str:
        session = self.market_hours.get_session(market)

        if session.is_open:
            data = self.trend_service.get_current_trend(market)
            return self.formatter.format_current_trend(
                market, data["trend"], session.session_label, data["as_of"]
            )

        eod = self.eod_service.get_market_closed_summary(market)
        return self.formatter.format_market_closed_eod(
            market,
            eod["trend"],
            eod["bullish_top5"],
            eod["bearish_top5"],
            eod["as_of"],
        )

    def _top5(self, market: str, direction: str) -> str:
        session = self.market_hours.get_session(market)

        if session.is_open:
            data = self.top5_service.get_top5(market, direction)
            return self.formatter.format_top5_alert(
                market, direction, data["picks"], data["as_of"]
            )

        eod = self.eod_service.get_market_closed_summary(market)
        return self.formatter.format_market_closed_eod(
            market,
            eod["trend"],
            eod["bullish_top5"],
            eod["bearish_top5"],
            eod["as_of"],
        )
