from aiogram import types
from database import get_user
from messages import MESSAGES

def register(dp):
    @dp.message_handler(commands=['language'])
    async def change_lang(msg: types.Message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🇬🇧 English", "🇳🇬 Hausa")
        lang = get_user(msg.from_user.id)[4]
        await msg.answer(MESSAGES[lang]['language'], reply_markup=markup)

    @dp.message_handler(lambda m: m.text in ["🇬🇧 English", "🇳🇬 Hausa"])
    async def set_lang(msg: types.Message):
        conn = sqlite3.connect("accounts.db")
        cursor = conn.cursor()
        lang = 'en' if "English" in msg.text else 'ha'
        cursor.execute("UPDATE users SET language=? WHERE user_id=?", (lang, msg.from_user.id))
        conn.commit()
        conn.close()
        await msg.answer("Language updated successfully.")
