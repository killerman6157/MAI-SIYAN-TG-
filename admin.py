"""
Admin command handlers
"""

import logging
from typing import Dict, Any

from aiogram import Router, types, F
from aiogram.filters import Command

from database import Database
from config import Config

logger = logging.getLogger(__name__)

router = Router()

@router.message(Command("user_accounts"))
async def user_accounts_command(message: types.Message, database: Database, config: Config):
    """Handle /user_accounts command (Admin only)"""
    if not config.is_admin(message.from_user.id):
        return
    
    # Extract user ID from command
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Amfani: /user_accounts [User ID]")
        return
    
    try:
        user_id = int(parts[1])
    except ValueError:
        await message.answer("User ID dole ya zama lamba.")
        return
    
    # Get user account count
    account_count = await database.get_user_account_count(user_id)
    
    await message.answer(
        f"User ID {user_id} yana da accounts guda {account_count} da aka karba, "
        f"kuma a shirye suke don biya."
    )

@router.message(Command("mark_paid"))
async def mark_paid_command(message: types.Message, database: Database, config: Config):
    """Handle /mark_paid command (Admin only)"""
    if not config.is_admin(message.from_user.id):
        return
    
    # Extract parameters from command
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("Amfani: /mark_paid [User ID] [Adadin Accounts da Aka Biya]")
        return
    
    try:
        user_id = int(parts[1])
        account_count = int(parts[2])
    except ValueError:
        await message.answer("User ID da adadin accounts dole su zama lambobi.")
        return
    
    # Mark accounts as paid
    await database.mark_account_paid(user_id, account_count)
    
    await message.answer(
        f"An yiwa User ID {user_id} alamar biya don accounts guda {account_count}. "
        f"An cire su daga jerin biyan da ake jira, an kuma sanya su a matsayin wanda aka biya."
    )

@router.message(Command("completed_today_payment"))
async def completed_today_payment_command(message: types.Message, database: Database, config: Config):
    """Handle /completed_today_payment command (Admin only)"""
    if not config.is_admin(message.from_user.id):
        return
    
    # Send notification to channel
    try:
        from aiogram import Bot
        bot = Bot.get_current()
        
        await bot.send_message(
            config.CHANNEL_ID,
            "SANARWA: An biya duk wanda ya nemi biya yau! Muna maku fatan alheri, sai gobe karfe 8:00 na safe."
        )
        
        await message.answer("An tura sanarwa zuwa channel.")
        
    except Exception as e:
        logger.error(f"Error sending channel notification: {e}")
        await message.answer("Kuskure yayin tura sanarwa zuwa channel.")

@router.message(Command("stats"))
async def stats_command(message: types.Message, database: Database, config: Config):
    """Handle /stats command (Admin only)"""
    if not config.is_admin(message.from_user.id):
        return
    
    # Get statistics
    stats = await database.get_stats()
    
    response = "📊 *Statistics:*\n"
    for status, count in stats.items():
        response += f"• {status}: {count}\n"
    
    await message.answer(response, parse_mode="Markdown")

async def register_handlers(dp, database: Database, config: Config):
    """Register all admin handlers"""
    # Register middleware to inject dependencies
    @router.message.middleware()
    async def inject_dependencies(handler, event, data):
        data["database"] = database
        data["config"] = config
        return await handler(event, **data)
    
    dp.include_router(router)
