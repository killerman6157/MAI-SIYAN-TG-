from aiogram import types
from messages import MESSAGES
from database import get_user

def register(dp):
    @dp.message_handler(commands=['cancel'])
    async def cancel(msg: types.Message):
        lang = get_user(msg.from_user.id)[4]
        await msg.answer(MESSAGES[lang]['cancel'])
