"""
Start command and account submission handlers
"""

import re
import logging
from typing import Dict, Any

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import Database
from telethon_client import TelethonManager
from config import Config
from utils import is_valid_phone_number, format_phone_number

logger = logging.getLogger(__name__)

class AccountSubmissionStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_otp = State()

router = Router()

@router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext, database: Database, config: Config):
    """Handle /start command"""
    user_id = message.from_user.id
    
    # Check if accounts are open
    accounts_open = await database.get_accounts_open_status()
    if not accounts_open:
        await message.answer(
            "An rufe karbar Telegram accounts na yau. An rufe karbar accounts da karfe 10:00 na dare (WAT). "
            "Za a sake buɗewa gobe karfe 8:00 na safe. Don Allah a gwada gobe."
        )
        return
    
    # Clear any existing state
    await state.clear()
    
    # Welcome message in Hausa
    welcome_text = (
        "Barka da zuwa cibiyar karbar Telegram accounts! Don farawa, turo lambar wayar "
        "account din da kake son sayarwa (misali: +2348167757987).\n\n"
        "Tabbatar ka cire Two-Factor Authentication (2FA) kafin ka tura."
    )
    
    await message.answer(welcome_text)
    await state.set_state(AccountSubmissionStates.waiting_for_phone)

@router.message(AccountSubmissionStates.waiting_for_phone)
async def process_phone_number(message: types.Message, state: FSMContext, database: Database, 
                              telethon_manager: TelethonManager, config: Config):
    """Process phone number submission"""
    phone_text = message.text.strip()
    
    # Validate phone number format
    if not is_valid_phone_number(phone_text):
        await message.answer(
            "Lambar wayar ba daidai ba ce. Don Allah ka tura lambar waya mai kyau kamar: +2348167757987"
        )
        return
    
    phone_number = format_phone_number(phone_text)
    
    # Check if phone number already exists
    if await database.check_phone_exists(phone_number):
        await message.answer(
            f"⚠️ Kuskure! An riga an yi rajistar wannan lambar!\n"
            f"{phone_number}\n"
            f"Ba za ka iya sake tura wannan lambar ba sai nan da mako ɗaya."
        )
        await state.clear()
        return
    
    # Save phone number to state
    await state.update_data(phone_number=phone_number)
    
    try:
        # Request OTP via Telethon
        success = await telethon_manager.request_otp(phone_number)
        
        if success:
            await message.answer(
                f"🇳🇬 Ana sarrafawa... Don Allah a jira.\n"
                f"An tura lambar sirri (OTP) zuwa lambar: {phone_number}. "
                f"Don Allah ka tura lambar sirrin a nan."
            )
            await state.set_state(AccountSubmissionStates.waiting_for_otp)
        else:
            await message.answer(
                "Kuskure yayin neman OTP. Don Allah ka tabbatar lambar wayar daidai ce kuma ka sake gwadawa."
            )
            await state.clear()
            
    except Exception as e:
        logger.error(f"Error requesting OTP for {phone_number}: {e}")
        await message.answer(
            "Kuskure yayin neman OTP. Don Allah ka sake gwadawa."
        )
        await state.clear()

@router.message(AccountSubmissionStates.waiting_for_otp)
async def process_otp(message: types.Message, state: FSMContext, database: Database, 
                     telethon_manager: TelethonManager, config: Config):
    """Process OTP submission"""
    otp_text = message.text.strip()
    
    # Validate OTP format (should be 5 digits)
    if not re.match(r'^\d{5}$', otp_text):
        await message.answer(
            "Lambar sirri ba daidai ba ce. Don Allah ka tura lambar sirri mai lambobi 5 kawai."
        )
        return
    
    # Get phone number from state
    data = await state.get_data()
    phone_number = data.get('phone_number')
    
    if not phone_number:
        await message.answer(
            "Kuskure yayin karbar lambar waya. Don Allah ka sake farawa da /start"
        )
        await state.clear()
        return
    
    try:
        # Verify OTP and login
        login_result = await telethon_manager.verify_otp_and_login(phone_number, otp_text)
        
        if login_result['success']:
            # Check if 2FA is required
            if login_result.get('requires_2fa'):
                await message.answer(
                    "⚠️ Lambar tana da 2FA/password. Ka cire 2FA kafin ka sake tura."
                )
                await state.clear()
                return
            
            # Add account to database
            user_id = message.from_user.id
            username = message.from_user.username or ""
            
            if await database.add_user_account(user_id, username, phone_number):
                # Set 2FA password
                await telethon_manager.set_2fa_password(phone_number, config.ACCOUNT_PASSWORD)
                
                # Update account status
                await database.update_account_status(phone_number, 'successful')
                
                # Success message
                await message.answer(
                    "An shiga account din ku cikin nasara ku cire shi daga na'urar ku. "
                    "Za a biya ku bisa ga adadin account din da kuka kawo. "
                    "Ana biyan kuɗi daga karfe 8:00 na dare (WAT) zuwa gaba. "
                    "Don Allah ka shirya tura bukatar biya."
                )
                
                logger.info(f"Account {phone_number} successfully processed for user {user_id}")
                
            else:
                await message.answer(
                    "Kuskure yayin ajiye account. Don Allah ka sake gwadawa."
                )
                
        else:
            await message.answer(
                f"Kuskure yayin shiga account: {login_result.get('error', 'Ba a san dalilin kuskure ba')}"
            )
            
    except Exception as e:
        logger.error(f"Error processing OTP for {phone_number}: {e}")
        await message.answer(
            "Kuskure yayin shiga account. Don Allah ka tabbatar lambar sirri daidai ce."
        )
        
    finally:
        await state.clear()

@router.message(Command("cancel"))
async def cancel_command(message: types.Message, state: FSMContext):
    """Handle /cancel command"""
    await state.clear()
    await message.answer("An soke aikin cikin nasara.")

@router.message(Command("myaccounts"))
async def my_accounts_command(message: types.Message, database: Database):
    """Handle /myaccounts command"""
    user_id = message.from_user.id
    accounts = await database.get_user_accounts(user_id)
    
    if not accounts:
        await message.answer("Ba ka da wata lamba da ka tura tukuna.")
        return
    
    response = "📋 Lambar da ka tura:\n\n"
    for account in accounts:
        response += f"📞 `{account['phone']}` — `{account['status']}`\n"
    
    await message.answer(response, parse_mode="Markdown")

async def register_handlers(dp, database: Database, telethon_manager: TelethonManager, config: Config):
    """Register all handlers"""
    # Register middleware to inject dependencies
    @router.message.middleware()
    async def inject_dependencies(handler, event, data):
        data["database"] = database
        data["telethon_manager"] = telethon_manager
        data["config"] = config
        return await handler(event, **data)
    
    dp.include_router(router)
