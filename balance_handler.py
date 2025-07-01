from aiogram import types
from messages import MESSAGES
from database import get_user
from datetime import datetime

def register(dp):
    @dp.message_handler(commands=['account_balance'])
    async def account_balance(msg: types.Message):
        user = get_user(msg.from_user.id)
        lang = user[4]
        text = MESSAGES[lang]['balance'].format(
            user_id=user[0],
            verified=user[1],
            unverified=user[2],
            balance=user[3],
            date=datetime.now().strftime("%Y-%m-%d")
        )
        await msg.answer(text)
