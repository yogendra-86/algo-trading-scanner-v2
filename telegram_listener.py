import sqlite3
from datetime import datetime
import time

from services.telegram_command_service import (
    TelegramCommandService
)

from utils.telegram_utils import (
    get_updates,
    send_telegram_message_to_chat
)

DB_PATH = (
    "data/trade_registry.db"
)


def already_processed(
    update_id
):

    conn = sqlite3.connect(
        DB_PATH
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT 1
    FROM processed_updates
    WHERE update_id = ?
    """, (

        update_id,

    ))

    row = cursor.fetchone()

    conn.close()

    return row is not None


def mark_processed(
    update_id
):

    conn = sqlite3.connect(
        DB_PATH
    )

    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE
    INTO processed_updates
    VALUES (?, ?)
    """, (

        update_id,

        datetime.utcnow()
        .isoformat()

    ))

    conn.commit()

    conn.close()


service = (
    TelegramCommandService()
)

print(
    "Telegram listener started..."
)

while True:

    try:

        updates = (
            get_updates()
        )

        results = (
            updates.get(
                "result",
                []
            )
        )

        for update in results:

            update_id = (
                update["update_id"]
            )

            if already_processed(
                update_id
            ):
                continue

            message = update.get(
                "message",
                {}
            )

            chat = message.get(
                "chat",
                {}
            )

            chat_id = (
                chat.get("id")
            )

            text = (
                message.get(
                    "text",
                    ""
                ).strip()
            )

            if text.startswith(
                "/papertrade"
            ):

                parts = (
                    text.split()
                )

                if len(parts) != 3:

                    send_telegram_message_to_chat(

                        chat_id,

                        (
                            "Usage:\n"
                            "/papertrade "
                            "ALERT_UID "
                            "SIGNAL_UID"
                        )
                    )

                else:

                    success, msg = (
                        service
                        .handle_papertrade_command(

                            chat_id,

                            parts[1],

                            parts[2]
                        )
                    )

                    send_telegram_message_to_chat(

                        chat_id,

                        msg
                    )

            elif text.isdigit():

                success, msg = (
                    service.complete_quantity(

                        chat_id,

                        int(text)
                    )
                )

                send_telegram_message_to_chat(

                    chat_id,

                    msg
                )

            mark_processed(
                update_id
            )

    except Exception as e:

        print(
            "Listener Error:",
            e
        )

    time.sleep(5)
