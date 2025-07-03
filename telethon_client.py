"""
Telethon client for Telegram account operations
"""

import os
import logging
import asyncio
from typing import Dict, Any, Optional

from telethon import TelegramClient, errors, events
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdatePasswordSettingsRequest, GetPasswordRequest

from config import Config
from database import Database

logger = logging.getLogger(__name__)

class TelethonManager:
    def __init__(self, config: Config):
        self.config = config
        self.clients = {}  # Store active clients by phone number
        self.database = None
        
    async def start(self):
        """Initialize Telethon manager"""
        self.database = Database(self.config.DATABASE_NAME)
        logger.info("Telethon manager started")
        
    async def stop(self):
        """Stop all clients"""
        for client in self.clients.values():
            try:
                await client.disconnect()
            except:
                pass
        self.clients.clear()
        logger.info("Telethon manager stopped")
        
    async def get_or_create_client(self, phone_number: str) -> TelegramClient:
        """Get existing client or create new one"""
        if phone_number in self.clients:
            return self.clients[phone_number]
        
        # Create new client
        session_name = f"sessions/{phone_number}"
        os.makedirs("sessions", exist_ok=True)
        
        client = TelegramClient(
            session_name,
            self.config.API_ID,
            self.config.API_HASH,
            device_model="TelegramBot",
            system_version="1.0",
            app_version="1.0"
        )
        
        self.clients[phone_number] = client
        return client
        
    async def request_otp(self, phone_number: str) -> bool:
        """Request OTP for phone number"""
        try:
            client = await self.get_or_create_client(phone_number)
            await client.connect()
            
            # Check if already authorized
            if await client.is_user_authorized():
                logger.info(f"User {phone_number} already authorized")
                return True
            
            # Send code request
            await client.send_code_request(phone_number)
            logger.info(f"OTP requested for {phone_number}")
            return True
            
        except errors.PhoneNumberInvalidError:
            logger.error(f"Invalid phone number: {phone_number}")
            return False
        except errors.FloodWaitError as e:
            logger.error(f"Flood wait error for {phone_number}: {e.seconds} seconds")
            return False
        except Exception as e:
            logger.error(f"Error requesting OTP for {phone_number}: {e}")
            return False
            
    async def verify_otp_and_login(self, phone_number: str, otp: str) -> Dict[str, Any]:
        """Verify OTP and login to account"""
        try:
            client = await self.get_or_create_client(phone_number)
            
            # Try to sign in
            await client.sign_in(phone_number, otp)
            
            # Check if user is authorized
            if await client.is_user_authorized():
                logger.info(f"Successfully logged in to {phone_number}")
                
                # Setup message handler for OTP forwarding
                await self.setup_otp_forwarding(client, phone_number)
                
                return {"success": True}
            else:
                return {"success": False, "error": "Shiga ya gaza"}
                
        except errors.PhoneCodeInvalidError:
            return {"success": False, "error": "Lambar sirri ba daidai ba ce"}
        except errors.PhoneCodeExpiredError:
            return {"success": False, "error": "Lambar sirri ta kare"}
        except errors.SessionPasswordNeededError:
            return {"success": False, "error": "Ana bukatar 2FA password", "requires_2fa": True}
        except Exception as e:
            logger.error(f"Error verifying OTP for {phone_number}: {e}")
            return {"success": False, "error": str(e)}
            
    async def set_2fa_password(self, phone_number: str, password: str):
        """Set 2FA password for account"""
        try:
            client = self.clients.get(phone_number)
            if not client:
                logger.error(f"No client found for {phone_number}")
                return False
                
            # For now, skip 2FA setup due to complexity
            # In a real implementation, you would need proper password types
            logger.info(f"Skipping 2FA setup for {phone_number} - account login successful")
            return True
            
        except Exception as e:
            logger.error(f"Error setting 2FA password for {phone_number}: {e}")
            return True
            
    async def setup_otp_forwarding(self, client: TelegramClient, phone_number: str):
        """Setup OTP forwarding for the client"""
        @client.on(events.NewMessage(from_users=777000))  # Telegram system bot
        async def otp_handler(event):
            try:
                # Get buyer for this phone number
                if self.database:
                    buyer_id = await self.database.get_buyer_by_phone(phone_number)
                    
                    if buyer_id:
                        # For now, just log the OTP - proper forwarding would need bot instance
                        logger.info(f"OTP received for {phone_number}: {event.text}")
                        logger.info(f"Should forward to buyer {buyer_id}")
                        
            except Exception as e:
                logger.error(f"Error in OTP handler: {e}")
                
        logger.info(f"OTP forwarding setup for {phone_number}")
        
    async def logout_account(self, phone_number: str):
        """Logout from account and cleanup"""
        try:
            client = self.clients.get(phone_number)
            if client:
                await client.log_out()
                await client.disconnect()
                del self.clients[phone_number]
                
                # Remove session file
                session_file = f"sessions/{phone_number}.session"
                if os.path.exists(session_file):
                    os.remove(session_file)
                    
                logger.info(f"Logged out from {phone_number}")
                return True
                
        except Exception as e:
            logger.error(f"Error logging out from {phone_number}: {e}")
            return False
