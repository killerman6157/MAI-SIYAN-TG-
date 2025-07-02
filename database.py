"""
Database management for Telegram Trading Bot
"""

import aiosqlite
import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_name: str):
        self.db_name = db_name
        
    async def init_db(self):
        """Initialize database tables"""
        async with aiosqlite.connect(self.db_name) as db:
            # User accounts table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    phone_number TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    session_file TEXT,
                    buyer_user_id INTEGER,
                    payment_status TEXT DEFAULT 'unpaid',
                    UNIQUE(phone_number)
                )
            ''')
            
            # User states table for conversation tracking
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_states (
                    user_id INTEGER PRIMARY KEY,
                    state TEXT NOT NULL,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Withdrawal requests table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS withdrawal_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    account_count INTEGER NOT NULL,
                    bank_details TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP
                )
            ''')
            
            # Account sessions table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS account_sessions (
                    phone_number TEXT PRIMARY KEY,
                    session_data TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Bot settings table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS bot_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Initialize bot settings
            await db.execute('''
                INSERT OR IGNORE INTO bot_settings (key, value) 
                VALUES ('accounts_open', 'true')
            ''')
            
            await db.commit()
            logger.info("Database initialized successfully")
            
    async def add_user_account(self, user_id: int, username: str, phone_number: str) -> bool:
        """Add a new user account"""
        try:
            async with aiosqlite.connect(self.db_name) as db:
                await db.execute('''
                    INSERT INTO user_accounts (user_id, username, phone_number, status)
                    VALUES (?, ?, ?, 'pending')
                ''', (user_id, username, phone_number))
                await db.commit()
                return True
        except aiosqlite.IntegrityError:
            return False  # Phone number already exists
        except Exception as e:
            logger.error(f"Error adding user account: {e}")
            return False
            
    async def check_phone_exists(self, phone_number: str) -> bool:
        """Check if phone number already exists"""
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('''
                SELECT COUNT(*) FROM user_accounts WHERE phone_number = ?
            ''', (phone_number,))
            count = await cursor.fetchone()
            return count[0] > 0
            
    async def update_account_status(self, phone_number: str, status: str):
        """Update account status"""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                UPDATE user_accounts 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE phone_number = ?
            ''', (status, phone_number))
            await db.commit()
            
    async def get_user_accounts(self, user_id: int) -> List[Dict]:
        """Get all accounts for a user"""
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('''
                SELECT phone_number, status, created_at 
                FROM user_accounts 
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))
            rows = await cursor.fetchall()
            return [{"phone": row[0], "status": row[1], "created_at": row[2]} for row in rows]
            
    async def get_user_account_count(self, user_id: int) -> int:
        """Get count of successful accounts for a user"""
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('''
                SELECT COUNT(*) FROM user_accounts 
                WHERE user_id = ? AND status = 'successful'
            ''', (user_id,))
            count = await cursor.fetchone()
            return count[0] if count else 0
            
    async def get_user_phone_numbers(self, user_id: int) -> List[str]:
        """Get all phone numbers for a user"""
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('''
                SELECT phone_number FROM user_accounts 
                WHERE user_id = ? AND status = 'successful'
            ''', (user_id,))
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
            
    async def set_user_state(self, user_id: int, state: str, data: str = None):
        """Set user conversation state"""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                INSERT OR REPLACE INTO user_states (user_id, state, data)
                VALUES (?, ?, ?)
            ''', (user_id, state, data))
            await db.commit()
            
    async def get_user_state(self, user_id: int) -> Optional[Dict]:
        """Get user conversation state"""
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('''
                SELECT state, data FROM user_states WHERE user_id = ?
            ''', (user_id,))
            row = await cursor.fetchone()
            return {"state": row[0], "data": row[1]} if row else None
            
    async def clear_user_state(self, user_id: int):
        """Clear user conversation state"""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('DELETE FROM user_states WHERE user_id = ?', (user_id,))
            await db.commit()
            
    async def add_withdrawal_request(self, user_id: int, username: str, account_count: int, bank_details: str):
        """Add withdrawal request"""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                INSERT INTO withdrawal_requests (user_id, username, account_count, bank_details)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, account_count, bank_details))
            await db.commit()
            
    async def get_accounts_open_status(self) -> bool:
        """Check if accounts are open for receiving"""
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('''
                SELECT value FROM bot_settings WHERE key = 'accounts_open'
            ''', )
            row = await cursor.fetchone()
            return row[0] == 'true' if row else True
            
    async def set_accounts_open_status(self, is_open: bool):
        """Set accounts open status"""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                INSERT OR REPLACE INTO bot_settings (key, value, updated_at)
                VALUES ('accounts_open', ?, CURRENT_TIMESTAMP)
            ''', ('true' if is_open else 'false',))
            await db.commit()
            
    async def get_stats(self) -> Dict:
        """Get bot statistics"""
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('''
                SELECT status, COUNT(*) FROM user_accounts GROUP BY status
            ''')
            stats = await cursor.fetchall()
            return {status: count for status, count in stats}
            
    async def mark_account_paid(self, user_id: int, account_count: int):
        """Mark accounts as paid"""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                UPDATE user_accounts 
                SET payment_status = 'paid', updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND status = 'successful' AND payment_status = 'unpaid'
                LIMIT ?
            ''', (user_id, account_count))
            await db.commit()
            
    async def set_buyer_mapping(self, phone_number: str, buyer_user_id: int):
        """Set buyer mapping for an account"""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                UPDATE user_accounts 
                SET buyer_user_id = ?, updated_at = CURRENT_TIMESTAMP
                WHERE phone_number = ?
            ''', (buyer_user_id, phone_number))
            await db.commit()
            
    async def get_buyer_by_phone(self, phone_number: str) -> Optional[int]:
        """Get buyer user ID by phone number"""
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('''
                SELECT buyer_user_id FROM user_accounts WHERE phone_number = ?
            ''', (phone_number,))
            row = await cursor.fetchone()
            return row[0] if row and row[0] else None
            
    async def save_session_data(self, phone_number: str, session_data: str):
        """Save session data for a phone number"""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                INSERT OR REPLACE INTO account_sessions (phone_number, session_data)
                VALUES (?, ?)
            ''', (phone_number, session_data))
            await db.commit()
            
    async def get_session_data(self, phone_number: str) -> Optional[str]:
        """Get session data for a phone number"""
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('''
                SELECT session_data FROM account_sessions WHERE phone_number = ? AND is_active = TRUE
            ''', (phone_number,))
            row = await cursor.fetchone()
            return row[0] if row else None
            
    async def close(self):
        """Close database connections"""
        # aiosqlite doesn't maintain persistent connections
        pass
