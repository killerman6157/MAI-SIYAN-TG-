"""
Withdrawal command handlers
"""

import logging
from typing import Dict, Any

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import Database
from config import Config

logger = logging.getLogger(__name__)

class WithdrawStates(StatesGroup):
    waiting_for_bank_details = State()

router = Router()

async def withdraw_command(message: types.Message, state: FSMContext, database: Database, config: Config):
    """Handle /withdraw command"""
    user_id = message.from_user.id
    
    # Check if accounts are open (withdrawal might be restricted during closed hours)
    accounts_open = await database.get_accounts_open_status()
    if not accounts_open:
        await message.answer(
            "An rufe biyan kuɗi na yau. Za a fara biyan kuɗi gobe da karfe 8:00 na safe (WAT). "
            "Don Allah a jira."
        )
        return
    
    # Check if user has any successful accounts
    account_count = await database.get_user_account_count(user_id)
    if account_count == 0:
        await message.answer(
            "Ba ka da wani account da aka karba cikin nasara. "
            "Don Allah ka tura account din ka tukuna kafin ka nemi cire kuɗi."
        )
        return
    
    # Clear any existing state
    await state.clear()
    
    # Ask for bank details
    await message.answer(
        "Danna hanyar cire kuɗinka.\n\n"
        "Maza turo lambar asusun bankinka da sunan mai asusun. Misali:\n"
        "9131085651 OPay Bashir Rabiu\n\n"
        "Za a fara biyan kuɗi daga karfe 8:00 na dare (WAT). "
        "Admin zai tura maka kuɗin ka akan lokaci."
    )
    
    await state.set_state(WithdrawStates.waiting_for_bank_details)

async def process_bank_details(message: types.Message, state: FSMContext, database: Database, config: Config):
    """Process bank details submission"""
    bank_details = message.text.strip()
    
    # Basic validation
    if len(bank_details) < 10:
        await message.answer(
            "Bayanin banki ba cikakke ba ne. Don Allah ka tura lambar asusun, sunan banki, "
            "da sunan mai asusun. Misali: 9131085651 OPay Bashir Rabiu"
        )
        return
    
    user_id = message.from_user.id
    username = message.from_user.username or ""
    
    # Get account count
    account_count = await database.get_user_account_count(user_id)
    phone_numbers = await database.get_user_phone_numbers(user_id)
    
    # Add withdrawal request
    await database.add_withdrawal_request(user_id, username, account_count, bank_details)
    
    # Send confirmation to user
    await message.answer(
        "An karbi bukatarku don cire kuɗi. Admin zai tura maku kuɗin ku akan lokaci."
    )
    
    # Send notification to admin
    try:
        from aiogram import Bot
        bot = Bot.get_current()
        
        admin_message = (
            "BUKATAR BIYA!\n\n"
            f"User ID: {user_id} (Username: @{username})\n"
            f"Bukatar biya don accounts guda: {account_count}\n"
            f"Lambobin Accounts da aka karba daga wannan user: {', '.join(phone_numbers)}\n"
            f"Bayanan Banki: {bank_details}\n\n"
            f"Danna /mark_paid {user_id} {account_count} don tabbatar da biyan."
        )
        
        await bot.send_message(config.ADMIN_ID, admin_message)
        
    except Exception as e:
        logger.error(f"Error sending admin notification: {e}")
    
    await state.clear()

async def register_handlers(dp, database: Database, config: Config):
    """Register all withdrawal handlers"""
    # Helper function to wrap handlers with dependencies
    def wrap_handler(handler):
        async def wrapped_handler(event, **kwargs):
            kwargs["database"] = database
            kwargs["config"] = config
            return await handler(event, **kwargs)
        return wrapped_handler
    
    # Register withdrawal handlers
    dp.message.register(wrap_handler(withdraw_command), Command("withdraw"))
    dp.message.register(wrap_handler(process_bank_details), WithdrawStates.waiting_for_bank_details)
