import re
from typing import Dict


def _extract_value(line: str, prefix: str) -> str:
    return line.split(prefix, 1)[1].strip()


def parse_strategy_text(raw_text: str) -> Dict:
    """
    Partial parser for strategy TXT files.

    Supports:
    - STRATEGY_NAME:
    - MARKET:
    - STAGE:
    - SIDE:
    - FILTERS:
      - Price between X and Y
      - Volume > N
    - LOGIC:
      keyword-based flags
    """
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

    result = {
        "strategy_name": "",
        "market": "",
        "stage": "",
        "side": "",
        "filters": {},
        "logic_flags": {},
        "entry_text": "",
        "exit_text": "",
    }

    section = None

    for line in lines:
        upper = line.upper()

        if upper.startswith("STRATEGY_NAME:"):
            result["strategy_name"] = _extract_value(line, ":")
            continue

        if upper.startswith("MARKET:"):
            result["market"] = _extract_value(line, ":").upper()
            continue

        if upper.startswith("STAGE:"):
            result["stage"] = _extract_value(line, ":").lower()
            continue

        if upper.startswith("SIDE:"):
            result["side"] = _extract_value(line, ":").upper()
            continue

        if upper == "LOGIC:":
            section = "logic"
            continue

        if upper == "FILTERS:":
            section = "filters"
            continue

        if upper == "ENTRY:":
            section = "entry"
            continue

        if upper == "EXIT:":
            section = "exit"
            continue

        if section == "logic":
            low = line.lower()

            keyword_map = {
                "price crosses above vwap": "vwap_breakout",
                "price crosses below vwap": "vwap_breakdown",
                "volume surge": "volume_surge",
                "volume expansion": "volume_surge",
                "rsi strength": "rsi_strength",
                "rsi weakness": "rsi_weakness",
                "break above first 15 minute high": "orb_breakout",
                "break below first 15 minute low": "orb_breakdown",
                "pullback happens near ema20": "pullback_near_ema20",
                "pullback volume contracts": "volume_decline",
                "fresh breakout candle shows volume spike": "breakout_volume_spike",
                "fresh breakdown candle shows volume spike": "breakout_volume_spike",
                "ema9 crosses above ema20": "ema_bullish_crossover",
                "ema9 crosses below ema20": "ema_bearish_crossover",
                "volume rising across recent candles": "volume_increasing",
                "bullish engulfing candle appears": "bullish_engulfing",
                "bearish engulfing candle appears": "bearish_engulfing",
                "rsi oversold and starts rising": "rsi_rising_from_oversold",
                "rsi overbought and starts falling": "rsi_falling_from_overbought",
                "price pushes above recent resistance": "fake_breakout_short",
                "rejection candle has long upper wick": "long_upper_wick",
            }

            for phrase, flag in keyword_map.items():
                if phrase in low:
                    result["logic_flags"][flag] = True

        elif section == "filters":
            low = line.lower()

            price_match = re.search(r"price between\s+([0-9.]+)\s+and\s+([0-9.]+)", low)
            if price_match:
                result["filters"]["min_price"] = float(price_match.group(1))
                result["filters"]["max_price"] = float(price_match.group(2))

            vol_match = re.search(r"volume\s*>\s*([0-9_]+)", low)
            if vol_match:
                result["filters"]["min_volume"] = int(vol_match.group(1).replace("_", ""))

        elif section == "entry":
            result["entry_text"] += (line + " ")

        elif section == "exit":
            result["exit_text"] += (line + " ")

    return result


def infer_strategy_type(strategy_name: str) -> str:
    lower_name = strategy_name.lower()

    if "vwap" in lower_name:
        return "VWAP"
    if "cpr" in lower_name:
        return "CPR"
    if "ema" in lower_name or "macd" in lower_name:
        return "EMA_MACD"
    if "first15min" in lower_name or "orb" in lower_name or "range_break" in lower_name:
        return "RANGE15"
    if "rsi" in lower_name:
        return "RSI_DIVERGENCE"
    if "bullflag" in lower_name:
        return "BULLFLAG"
    if "bearflag" in lower_name:
        return "BEARFLAG"
    if "fakebreakout" in lower_name:
        return "FAKE_BREAKOUT"
    return "GENERIC"


def enabled_stages(strategy_name: str, stage_from_file: str | None = None) -> list[str]:
    if stage_from_file in {"prep", "live", "range15"}:
        return [stage_from_file]

    lower_name = strategy_name.lower()

    if "first15min" in lower_name or "orb" in lower_name:
        return ["range15"]

    return ["prep", "live"]


def parse_strategy(strategy: Dict) -> Dict:
    return {
        **strategy,
        "type": infer_strategy_type(strategy["name"]),
        "enabled_stages": enabled_stages(strategy["name"], strategy.get("stage")),
    }
