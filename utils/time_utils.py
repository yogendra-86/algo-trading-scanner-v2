from datetime import datetime

import pytz


def now_in_timezone(timezone_name: str) -> datetime:
    tz = pytz.timezone(timezone_name)
    return datetime.now(tz)