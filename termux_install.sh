#!/bin/bash

# Telegram Trading Bot - Termux-specific installation script
# This script is designed for proper Termux environment

echo "🤖 Installing Telegram Trading Bot for Termux..."
echo "==============================================="

# Check if we're in Termux
if [ -z "$PREFIX" ]; then
    echo "❌ This script is designed for Termux environment only!"
    echo "If you're using Termux, please ensure it's properly set up."
    echo "For other Linux distributions, use regular installation commands."
    exit 1
fi

# Update package list
echo "📦 Updating package list..."
pkg update -y

# Install essential packages
echo "🛠️ Installing essential packages..."
pkg install python -y
pkg install python-pip -y
pkg install git -y
pkg install openssl -y
pkg install libffi -y
pkg install libjpeg-turbo -y
pkg install zlib -y

# Upgrade pip
echo "⬆️ Upgrading pip..."
python -m pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python packages..."
python -m pip install aiogram==3.4.1
python -m pip install telethon==1.36.0
python -m pip install aiosqlite==0.19.0
python -m pip install python-dotenv==1.0.0
python -m pip install apscheduler==3.10.4
python -m pip install pytz==2023.3
python -m pip install cryptg

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p sessions
mkdir -p logs

# Set proper permissions
echo "🔐 Setting permissions..."
chmod +x main.py
chmod +x termux_install.sh

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️ Creating .env file..."
    cp .env.example .env
    echo ""
    echo "📝 IMPORTANT: Edit .env file with your configuration!"
fi

echo ""
echo "✅ Termux installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your bot credentials:"
echo "   nano .env"
echo ""
echo "2. Get your bot token from @BotFather on Telegram"
echo "3. Get API_ID and API_HASH from https://my.telegram.org"
echo "4. Set your Telegram user ID as ADMIN_ID"
echo ""
echo "5. Run the bot:"
echo "   python main.py"
echo ""
echo "🔧 Required configuration in .env:"
echo "- BOT_TOKEN=your_bot_token_from_botfather"
echo "- ADMIN_ID=your_telegram_user_id"
echo "- API_ID=your_api_id_from_my_telegram_org"
echo "- API_HASH=your_api_hash_from_my_telegram_org"
echo "- CHANNEL_ID=your_channel_id_for_notifications (optional)"
echo ""
echo "🚀 Happy trading!"