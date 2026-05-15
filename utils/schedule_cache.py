import json
import os
from datetime import datetime

CACHE_FILE = "schedule_cache.json"


def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    with open(CACHE_FILE, "r") as f:
        return json.load(f)


def save_cache(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f)


def already_triggered(market, trigger):
    data = load_cache()
    today = datetime.now().strftime("%Y-%m-%d")
    key = f"{market}_{trigger}_{today}"

    return key in data


def mark_triggered(market, trigger):
    data = load_cache()
    today = datetime.now().strftime("%Y-%m-%d")
    key = f"{market}_{trigger}_{today}"

    data[key] = True
    save_cache(data)
