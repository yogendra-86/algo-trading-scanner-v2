import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo


IST = ZoneInfo("Asia/Kolkata")
ET = ZoneInfo("America/New_York")


class SnapshotService:
    def __init__(self, state_dir: str = "/opt/algo-trading-scanner-v2/state"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def save_opening_snapshot(self, market: str, payload: Dict[str, Any]) -> Path:
        path = self._snapshot_path(market)
        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        return path

    def load_opening_snapshot(self, market: str) -> Optional[Dict[str, Any]]:
        path = self._snapshot_path(market)
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _snapshot_path(self, market: str) -> Path:
        market = market.upper()
        date_key = self._date_key_for_market(market)
        return self.state_dir / f"{market.lower()}_{date_key}_opening_snapshot.json"

    @staticmethod
    def _date_key_for_market(market: str) -> str:
        if market.upper() == "NSE":
            return datetime.now(IST).strftime("%Y-%m-%d")
        return datetime.now(ET).strftime("%Y-%m-%d")
