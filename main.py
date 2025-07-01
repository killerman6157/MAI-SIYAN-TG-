from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from handlers import start_handler, cancel_handler, balance_handler, withdraw_handler, language_handler

import os
from database import init_db

BOT_TOKEN = os.getenv("BOT_TOKEN") or "PASTE_YOUR_BOT_TOKEN_HERE"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

init_db()

# Register handlers
start_handler.register(dp)
cancel_handler.register(dp)
balance_handler.register(dp)
withdraw_handler.register(dp)
language_handler.register(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
