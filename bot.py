import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from app.config import BOT_TOKEN
from app.database import init_db, close_db
from app.handlers import base, order

async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    # Initialize the database
    await init_db()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Register routers
    dp.include_router(base.router)
    dp.include_router(order.router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(main())
