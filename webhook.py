import logging
import sys
import os  # Исправленный импорт
from aiohttp import web
from dotenv import load_dotenv  # Добавьте эту строку
from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
load_dotenv()  
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

WEB_SERVER_HOST = "::"
WEB_SERVER_PORT = 8350

WEBHOOK_PATH = "/home/takstask/www/bot/"
WEBHOOK_SECRET = os.getenv("")
BASE_WEBHOOK_URL = "https://takstask.alwaysdata.net"

if not TOKEN:
    raise ValueError("Токен не найден! Укажите TELEGRAM_BOT_TOKEN в переменных окружения.")

router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")

@router.message()
async def echo_handler(message: Message) -> None:
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Nice try!")

async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(
        f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", 
        secret_token=WEBHOOK_SECRET if WEBHOOK_SECRET else None
    )

def main() -> None:
    dp = Dispatcher()
    dp.include_router(router)
    dp.startup.register(on_startup)

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()