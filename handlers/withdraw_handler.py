from aiogram import types
from messages import MESSAGES
from database import get_user

def register(dp):
    @dp.message_handler(commands=['withdraw'])
    async def withdraw(msg: types.Message):
        lang = get_user(msg.from_user.id)[4]
        await msg.answer(MESSAGES[lang]['withdraw_prompt'])
        # Add step handling here if needed
