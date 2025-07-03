"""
Scheduler for time-based operations
"""

import logging
from datetime import datetime, time
import pytz

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import Config
from database import Database

logger = logging.getLogger(__name__)

class BotScheduler:
    def __init__(self, config: Config):
        self.config = config
        self.scheduler = AsyncIOScheduler()
        self.database = Database(config.DATABASE_NAME)
        
    async def start(self):
        """Start the scheduler"""
        # Schedule account opening at 8:00 AM WAT
        self.scheduler.add_job(
            self.open_accounts,
            CronTrigger(
                hour=self.config.OPEN_HOUR,
                minute=0,
                timezone=pytz.timezone(self.config.TIMEZONE)
            ),
            id='open_accounts'
        )
        
        # Schedule account closing at 10:00 PM WAT
        self.scheduler.add_job(
            self.close_accounts,
            CronTrigger(
                hour=self.config.CLOSE_HOUR,
                minute=0,
                timezone=pytz.timezone(self.config.TIMEZONE)
            ),
            id='close_accounts'
        )
        
        self.scheduler.start()
        logger.info("Scheduler started")
        
    async def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
        
    async def open_accounts(self):
        """Open accounts for receiving (8:00 AM WAT)"""
        try:
            await self.database.set_accounts_open_status(True)
            logger.info("Accounts opened for receiving")
        except Exception as e:
            logger.error(f"Error opening accounts: {e}")
            
    async def close_accounts(self):
        """Close accounts for receiving (10:00 PM WAT)"""
        try:
            await self.database.set_accounts_open_status(False)
            logger.info("Accounts closed for receiving")
        except Exception as e:
            logger.error(f"Error closing accounts: {e}")
