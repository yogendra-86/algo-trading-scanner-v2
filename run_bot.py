from dotenv import load_dotenv
load_dotenv()

from bot.telegram_bot import TelegramBot

if __name__ == "__main__":
    bot = TelegramBot()
    bot.run_forever()
