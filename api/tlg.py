import asyncio
from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("TELEGRAM_API_TOKEN")
user_id = os.getenv("TELEGRAM_USER_ID")


async def async_send_tlg(message):
    bot = Bot(api_key)
    await bot.send_message(user_id, message, parse_mode=ParseMode.HTML)


def sync_send_tlg(message):
    asyncio.run(async_send_tlg(message))
