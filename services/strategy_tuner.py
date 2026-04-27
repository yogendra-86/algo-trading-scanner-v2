from typing import Dict, Any


class StrategyTuner:
    """
    Applies relaxed + consistent rules across all strategies
    to increase signal frequency without breaking logic.
    """

    def tune(self, signal: Dict[str, Any]) -> Dict[str, Any] | None:
        entry = self._num(signal.get("entry"))
        sl = self._num(signal.get("sl"))
        target = self._num(signal.get("target"))

        if not entry or not sl or not target:
            return None

        rr = abs(target - entry) / max(abs(entry - sl), 1e-6)

        # ❌ reject extremely bad RR
        if rr < 0.8:
            return None

        # 🔥 auto-adjust target if RR < 1
        if rr < 1.0:
            if target > entry:
                target = entry + (entry - sl)
            else:
                target = entry - (sl - entry)

        signal["entry"] = round(entry, 2)
        signal["sl"] = round(sl, 2)
        signal["target"] = round(target, 2)
        signal["rr"] = round(abs(target - entry) / abs(entry - sl), 2)

        return signal

    @staticmethod
    def _num(x):
        try:
            return float(x)
        except Exception:
            return None
