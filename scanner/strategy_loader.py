from pathlib import Path
from typing import Dict, List

from scanner.strategy_parser import parse_strategy_text


def load_strategies(strategies_root: Path) -> List[Dict]:
    strategies: List[Dict] = []

    for side in ["bullish", "bearish"]:
        side_dir = strategies_root / side
        if not side_dir.exists():
            continue

        for file_path in sorted(side_dir.glob("*.txt")):
            raw_text = file_path.read_text(encoding="utf-8").strip()
            parsed = parse_strategy_text(raw_text)

            strategy = {
                "name": file_path.stem,
                "side": parsed.get("side", side.upper()),
                "path": str(file_path),
                "raw_text": raw_text,
                "stage": parsed.get("stage", ""),
                "market": parsed.get("market", ""),
                "filters": parsed.get("filters", {}),
                "logic_flags": parsed.get("logic_flags", {}),
                "entry_text": parsed.get("entry_text", ""),
                "exit_text": parsed.get("exit_text", ""),
            }

            strategies.append(strategy)

    return strategies
