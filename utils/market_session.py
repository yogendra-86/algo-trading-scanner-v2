from datetime import datetime, time
import pytz


def is_market_open():
    # Convert UTC → IST
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    # Weekend check
    if now.weekday() >= 5:
        return False

    current_time = now.time()

    # NSE timings (IST)
    market_start = time(9, 15)
    market_end = time(15, 30)

    if market_start <= current_time <= market_end:
        return True

    return False
