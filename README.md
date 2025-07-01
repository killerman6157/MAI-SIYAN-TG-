# Telegram Account Receiver Bot

This is a simple Telegram bot built with [Aiogram 2.25.2] and SQLite to automate receiving Telegram accounts from sellers.

---

## 🧠 Features

- Receive Telegram numbers from sellers
- Wait for OTP and login (future)
- Cancel transaction
- Track verified and unverified accounts per user
- Withdraw balance via Naira or USDT (BEP20)
- Language switch: Hausa 🇳🇬 / English 🇬🇧

---

## ⚙️ Requirements

- Python 3.8+
- Aiogram 2.25.2
- SQLite (built-in)
- Optional: Termux or Pydroid 3 (Android)

---

## 📦 Installation

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
pip install -r requirements.txt
```

---

## 🔐 .env File

```env
BOT_TOKEN=1234567890:ABCDEF_your_real_token
```

---

## 🚀 Running the Bot

```bash
python main.py
```

---

## 📂 Project Structure

```
TelegramAccountBot/
├── main.py
├── database.py
├── session_handler.py
├── messages.py
├── requirements.txt
├── .env
└── handlers/
```

---

## 🌍 Language Support

| Command            | Description               |
|--------------------|---------------------------|
| /start             | Start interaction         |
| /cancel            | Cancel current operation  |
| /account_balance   | Check your stats & balance|
| /withdraw          | Choose withdrawal method  |
| /language          | Switch between English/Hausa |

# 🤖 Future Plans

Full Pyrogram/Telethon integration for OTP login

Admin panel for managing sellers

Auto alert when price drops



---

# 👤 Developer

Made with ❤️ by Bashir Rabiu


---

# ⚠️ Disclaimer

This bot is for educational and automation purposes within your private teams only. Be responsible when handling user data and Telegram accounts. We do not support misuse or violations of Telegram policies.
