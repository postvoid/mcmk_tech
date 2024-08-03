import asyncio
import logging
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from handlers import user, admin, messages
import os
from scheduler import schedule_jobs

load_dotenv()

token = os.getenv("TELEGRAM_API_TOKEN")
bot = Bot(token=token)
dp = Dispatcher()


async def main():
    dp.include_routers(messages.router, admin.router, user.router)
    await schedule_jobs(bot)
    await asyncio.gather(dp.start_polling(bot))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
