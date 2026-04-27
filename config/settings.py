import os
from dataclasses import dataclass
from dotenv import load_dotenv


# =========================
# MODULE-LEVEL CONFIG
# =========================

TELEGRAM_ENABLED = os.getenv("TELEGRAM_ENABLED", "false").strip().lower() == "true"

MARKET_CONFIG = {
    "NSE": {
        "min_price": 50,
        "max_price": 2000,
        "min_volume": 30000,
    },
    "NASDAQ": {
        "min_price": 5,
        "max_price": 100,
        "min_volume": 200000,
    },
}


@dataclass
class Settings:
    project_root: str

    email_enabled: bool
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_pass: str
    email_to: str

    telegram_enabled: bool
    telegram_bot_token: str
    telegram_chat_id: str

    @classmethod
    def load(cls) -> "Settings":
        load_dotenv()

        return cls(
            project_root=os.getenv("PROJECT_ROOT", "/opt/algo-trading-scanner-v2"),

            email_enabled=os.getenv("EMAIL_ENABLED", "false").strip().lower() == "true",
            smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            smtp_user=os.getenv("SMTP_USER", "").strip(),
            smtp_pass=os.getenv("SMTP_PASS", "").strip(),
            email_to=os.getenv("EMAIL_TO", "yogendra.gaonkar@gmail.com").strip(),

            telegram_enabled=os.getenv("TELEGRAM_ENABLED", "false").strip().lower() == "true",
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", "").strip(),
        )
