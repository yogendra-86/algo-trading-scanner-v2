from datetime import datetime, time, timedelta
import pytz

# ==============================
# MARKET TIMINGS (IST)
# ==============================
MARKET_SCHEDULE = {
    "NSE": {
        "open": time(9, 15),
        "close": time(15, 30)
    },
    "NASDAQ": {
        "open": time(19, 0),
        "close": time(1, 30)  # next day
    }
}


# ==============================
# CHECK MARKET OPEN
# ==============================
def is_market_open(market):
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    if now.weekday() >= 5:
        return False

    current_time = now.time()

    schedule = MARKET_SCHEDULE.get(market)
    if not schedule:
        return False

    open_time = schedule["open"]
    close_time = schedule["close"]

    if market == "NSE":
        return open_time <= current_time <= close_time

    elif market == "NASDAQ":
        return (current_time >= open_time) or (current_time <= close_time)

    return False


# ==============================
# ALERT TRIGGER SYSTEM
# ==============================
def get_trigger_type(market):
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist).time()

    # ==============================
    # NSE TRIGGERS
    # ==============================
    if market == "NSE":
        # PRE OPEN
        if time(8, 55) <= now <= time(9, 15):
            return "PRE_OPEN"

        # POST OPEN
        elif time(9, 30) <= now <= time(9, 50):
            return "POST_OPEN"

        # PRE CLOSE
        elif time(15, 0) <= now <= time(15, 20):
            return "PRE_CLOSE"

        # FINAL CLOSE
        elif time(15, 20) <= now <= time(15, 30):
            return "FINAL_CLOSE"

    # ==============================
    # NASDAQ TRIGGERS
    # ==============================
    elif market == "NASDAQ":
        # PRE OPEN
        if time(18, 40) <= now <= time(19, 0):
            return "PRE_OPEN"

        # POST OPEN
        elif time(19, 15) <= now <= time(19, 35):
            return "POST_OPEN"

        # PRE CLOSE
        elif time(1, 10) <= now <= time(1, 20):
            return "PRE_CLOSE"

        # FINAL CLOSE
        elif time(1, 20) <= now <= time(1, 30):
            return "FINAL_CLOSE"


    return None
