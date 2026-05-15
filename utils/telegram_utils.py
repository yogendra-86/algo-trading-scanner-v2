import requests
import os

from dotenv import load_dotenv

# Load .env file
load_dotenv(dotenv_path=".env")


def send_telegram_message(message):

    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram config missing ❌")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    try:

        response = requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "text": message
            },
            timeout=15
        )

        # Debug response
        print("Telegram status:", response.status_code)
        print("Telegram response:", response.text)

        if response.status_code == 200:
            return True

        return False

    except Exception as e:
        print("Telegram error:", e)
        return False
