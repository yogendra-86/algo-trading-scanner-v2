from typing import Dict


STRATEGY_PRIORITY = {
    "VWAP": 5,
    "EMA": 4,
    "MACD": 4,
    "RSI": 3,
    "CPR": 2,
    "FIRST15MIN": 5,
    "RANGE15": 5,
}


def compute_score(row: Dict) -> float:
    score = 0.0
    strategy = str(row.get("strategy_name", "")).upper()

    for key, value in STRATEGY_PRIORITY.items():
        if key in strategy:
            score += value

    if str(row.get("rr_ratio", "")) == "1:2":
        score += 2

    entry = float(row.get("entry_price", 0) or 0)
    target = float(row.get("target_price", 0) or 0)
    stop = float(row.get("stop_loss", 0) or 0)

    if entry > 0 and target > 0 and stop > 0:
        score += 1

    return round(score, 2)
