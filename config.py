"""
Configuration management for Telegram Trading Bot
"""

import os
from typing import Optional

class Config:
    def __init__(self):
        # Bot Configuration
        self.BOT_TOKEN = os.getenv('BOT_TOKEN', '')
        self.ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))
        self.CHANNEL_ID = int(os.getenv('CHANNEL_ID', '0'))
        
        # Telegram API Configuration
        self.API_ID = int(os.getenv('API_ID', '0'))
        self.API_HASH = os.getenv('API_HASH', '')
        
        # Database Configuration
        self.DATABASE_NAME = os.getenv('DATABASE_NAME', 'telegram_accounts.db')
        
        # Bot Settings
        self.ACCOUNT_PASSWORD = os.getenv('ACCOUNT_PASSWORD', 'Bashir@111#')
        self.TIMEZONE = os.getenv('TIMEZONE', 'Africa/Lagos')
        
        # Operating hours (24-hour format)
        self.OPEN_HOUR = 8   # 8:00 AM
        self.CLOSE_HOUR = 22  # 10:00 PM
        
        # Validate configuration
        self._validate_config()
        
    def _validate_config(self):
        """Validate required configuration"""
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN environment variable is required")
        if not self.ADMIN_ID:
            raise ValueError("ADMIN_ID environment variable is required")
        if not self.API_ID:
            raise ValueError("API_ID environment variable is required")
        if not self.API_HASH:
            raise ValueError("API_HASH environment variable is required")
            
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id == self.ADMIN_ID
