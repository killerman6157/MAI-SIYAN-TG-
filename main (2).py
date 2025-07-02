#!/usr/bin/env python3
"""
Telegram Account Trading Bot
A bot for automated account trading with OTP forwarding and payment management
"""

import asyncio
import logging
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import Config
from database import Database
from handlers import start, admin, withdraw
from scheduler import BotScheduler
from telethon_client import TelethonManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TelegramTradingBot:
    def __init__(self):
        self.config = Config()
        self.bot = Bot(token=self.config.BOT_TOKEN)
        self.dp = Dispatcher(storage=MemoryStorage())
        self.database = Database(self.config.DATABASE_NAME)
        self.telethon_manager = TelethonManager(self.config)
        self.scheduler = BotScheduler(self.config)
        
    async def setup_bot_commands(self):
        """Setup bot commands menu"""
        commands = [
            BotCommand(command="start", description="Fara aiki da bot"),
            BotCommand(command="myaccounts", description="Duba lambobin da ka tura"),
            BotCommand(command="withdraw", description="Nemi cire kuɗi"),
            BotCommand(command="cancel", description="Soke aiki"),
        ]
        await self.bot.set_my_commands(commands)
        
    async def setup_handlers(self):
        """Setup message handlers"""
        # Import and register handlers
        await start.register_handlers(self.dp, self.database, self.telethon_manager, self.config)
        await admin.register_handlers(self.dp, self.database, self.config)
        await withdraw.register_handlers(self.dp, self.database, self.config)
        
    async def startup(self):
        """Bot startup sequence"""
        logger.info("Bot yana farawa...")
        
        # Initialize database
        await self.database.init_db()
        
        # Setup bot commands
        await self.setup_bot_commands()
        
        # Setup handlers
        await self.setup_handlers()
        
        # Start Telethon manager
        await self.telethon_manager.start()
        
        # Start scheduler
        await self.scheduler.start()
        
        logger.info("Bot ya fara aiki cikin nasara!")
        
    async def shutdown(self):
        """Bot shutdown sequence"""
        logger.info("Bot yana rufewa...")
        
        # Stop scheduler
        await self.scheduler.stop()
        
        # Stop Telethon manager
        await self.telethon_manager.stop()
        
        # Close database
        await self.database.close()
        
        logger.info("Bot ya rufe cikin nasara!")

async def main():
    """Main function"""
    bot_instance = TelegramTradingBot()
    
    try:
        await bot_instance.startup()
        await bot_instance.dp.start_polling(bot_instance.bot)
    except KeyboardInterrupt:
        logger.info("An tsaida bot ta hanyar keyboard interrupt")
    except Exception as e:
        logger.error(f"Kuskure a farawa: {e}")
    finally:
        await bot_instance.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot ya tsaida.")
