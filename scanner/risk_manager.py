from typing import Literal


TradeSide = Literal["LONG", "SHORT"]


def compute_target_and_stop(
    side: TradeSide,
    entry_price: float,
    stop_loss: float,
) -> dict:
    if side == "LONG":
        risk = entry_price - stop_loss
        if risk <= 0:
            return {}
        target_price = entry_price + (2 * risk)
    else:
        risk = stop_loss - entry_price
        if risk <= 0:
            return {}
        target_price = entry_price - (2 * risk)

    return {
        "entry_price": round(entry_price, 2),
        "stop_loss": round(stop_loss, 2),
        "target_price": round(target_price, 2),
        "rr_ratio": "1:2",
    }