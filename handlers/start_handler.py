from aiogram import types
from database import get_user
from messages import MESSAGES

def register(dp):
    @dp.message_handler(commands=['start'])
    async def start(msg: types.Message):
        user = get_user(msg.from_user.id)
        lang = user[4]
        await msg.answer(MESSAGES[lang]['start'])
