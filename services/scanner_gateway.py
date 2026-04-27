import csv
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class ScannerGateway:
    """
    Scanner Gateway:
    - Reads latest generated CSV outputs (FAST)
    - Avoids re-running scanner unnecessarily
    - Parses strategy-wise CSV files
    """

    def __init__(self, project_root: str = "/opt/algo-trading-scanner-v2"):
        self.project_root = Path(project_root)
        self.output_dir = self.project_root / "output"
        self.main_py = self.project_root / "main.py"

    # ================================
    # PUBLIC METHODS
    # ================================
    def get_latest_available_scan(self, market: str, stage: str = "range15") -> Dict:
        payload = self._collect_latest_scan_payload(market, stage)
        payload["as_of"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return payload

    def run_live_scan(self, market: str, stage: str = "range15") -> Dict:
        """
        Use only when fresh scan is required
        (NOT recommended for bot → slow)
        """
        self._run_main(market, stage)
        return self.get_latest_available_scan(market, stage)

    # ================================
    # INTERNAL METHODS
    # ================================
    def _run_main(self, market: str, stage: str):
        cmd = [
            sys.executable,
            str(self.main_py),
            "--market",
            market,
            "--stage",
            stage,
        ]

        try:
            subprocess.run(
                cmd,
                cwd=str(self.project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=int(os.getenv("BOT_SCAN_TIMEOUT", "900")),
            )
        except Exception as e:
            print(f"[ERROR] Scanner execution failed: {e}")

    def _collect_latest_scan_payload(self, market: str, stage: str) -> Dict:
        files = self._find_latest_csv_files(market, stage)

        signals: List[Dict[str, Any]] = []

        for file_path in files:
            parsed = self._parse_csv(file_path)
            signals.extend(parsed)

        return {
            "market": market.upper(),
            "stage": stage,
            "signals": signals,
            "files_used": [str(f) for f in files],
        }

    def _find_latest_csv_files(self, market: str, stage: str) -> List[Path]:
        market_dir = self.output_dir / market.upper()

        if not market_dir.exists():
            return []

        # Find latest date folder
        date_dirs = [d for d in market_dir.iterdir() if d.is_dir()]
        if not date_dirs:
            return []

        latest_dir = max(date_dirs, key=lambda d: d.stat().st_mtime)

        stage_dir = latest_dir / stage
        if not stage_dir.exists():
            return []

        csv_files = []

        for file in stage_dir.glob("*.csv"):
            name = file.name.lower()

            # Skip final summary (we want raw signals)
            if "final" in name:
                continue

            csv_files.append(file)

        return csv_files

    def _parse_csv(self, file_path: Path) -> List[Dict]:
        results = []

        direction = self._infer_direction(file_path.name)
        strategy_name = file_path.stem

        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    parsed = self._normalize_row(row, strategy_name, direction)
                    if parsed:
                        results.append(parsed)

        except Exception as e:
            print(f"[ERROR] Failed parsing {file_path}: {e}")

        return results

    # ================================
    # HELPERS
    # ================================
    def _normalize_row(self, row: Dict, strategy: str, direction: str) -> Dict | None:
        symbol = self._get_value(row, ["symbol", "Symbol", "ticker"])
        entry = self._get_value(row, ["entry", "Entry", "price", "LTP"])
        sl = self._get_value(row, ["sl", "SL", "stop_loss"])
        target = self._get_value(row, ["target", "Target"])
        score = self._get_value(row, ["score", "Score"])

        if not symbol:
            return None

        return {
            "symbol": str(symbol).upper(),
            "strategy": strategy,
            "direction": direction,
            "entry": self._to_float(entry),
            "sl": self._to_float(sl),
            "target": self._to_float(target),
            "score": self._to_float(score),
        }

    def _infer_direction(self, filename: str) -> str:
        name = filename.lower()

        if any(x in name for x in ["breakdown", "bearish", "short", "resistance"]):
            return "bearish"

        if any(x in name for x in ["breakout", "bounce", "support", "long"]):
            return "bullish"

        return "bullish"  # default fallback

    def _get_value(self, row: Dict, keys: List[str]):
        for key in keys:
            if key in row and row[key]:
                return row[key]
        return None

    def _to_float(self, val):
        try:
            return float(str(val).replace(",", ""))
        except:
            return None
