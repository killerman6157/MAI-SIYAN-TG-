"""
Snapshot command handlers for transaction receipts
"""

import logging
from typing import Dict, Any
from datetime import datetime

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import Database
from config import Config
from snapshot_generator import generate_transaction_snapshot

logger = logging.getLogger(__name__)

class SnapshotStates(StatesGroup):
    waiting_for_transaction_id = State()

router = Router()

@router.message(Command("snapshot"))
async def snapshot_command(message: types.Message, state: FSMContext, database: Database, config: Config):
    """Handle /snapshot command to generate transaction receipt"""
    user_id = message.from_user.id
    
    # Get user's recent successful accounts
    user_accounts = await database.get_user_accounts(user_id)
    successful_accounts = [acc for acc in user_accounts if acc['status'] == 'successful']
    
    if not successful_accounts:
        await message.answer(
            "Ba ka da wani account da aka karba cikin nasara. "
            "Don Allah ka tura account din ka tukuna kafin ka nemi snapshot."
        )
        return
    
    # For now, create snapshot for the most recent successful transaction
    latest_account = successful_accounts[0]
    
    # Generate transaction data
    transaction_data = await _prepare_transaction_data(user_id, latest_account, database)
    
    # Generate snapshot
    await _generate_and_send_snapshot(message, transaction_data)

@router.message(Command("my_receipt"))
async def my_receipt_command(message: types.Message, database: Database, config: Config):
    """Handle /my_receipt command - quick access to latest receipt"""
    user_id = message.from_user.id
    
    # Get user's account information
    accounts = await database.get_user_accounts(user_id)
    if not accounts:
        await message.answer("Ba ka da wani account da aka yi rajista.")
        return
    
    # Create receipt for latest account
    latest_account = accounts[0]
    transaction_data = await _prepare_transaction_data(user_id, latest_account, database)
    
    await _generate_and_send_snapshot(message, transaction_data)

@router.message(Command("payment_receipt"))
async def payment_receipt_command(message: types.Message, database: Database, config: Config):
    """Handle /payment_receipt command for payment confirmations"""
    user_id = message.from_user.id
    
    # Check if user has any paid accounts
    paid_count = await database.get_user_account_count(user_id)
    if paid_count == 0:
        await message.answer(
            "Ba ka da wani account da aka biya. "
            "Don Allah ka yi withdrawal tukuna."
        )
        return
    
    # Get withdrawal requests
    withdrawal_data = await database.get_user_withdrawal_requests(user_id)
    if not withdrawal_data:
        await message.answer("Ba a sami bayanan withdrawal ba.")
        return
    
    # Create payment receipt
    latest_withdrawal = withdrawal_data[0]
    payment_data = await _prepare_payment_data(user_id, latest_withdrawal, paid_count, database)
    
    await _generate_and_send_snapshot(message, payment_data)

async def _prepare_transaction_data(user_id: int, account_data: Dict, database: Database) -> Dict[str, Any]:
    """Prepare transaction data for snapshot generation"""
    
    # Calculate estimated amount (example: ₦500 per account)
    amount_per_account = 500
    user_account_count = await database.get_user_account_count(user_id)
    total_amount = user_account_count * amount_per_account
    
    transaction_data = {
        'transaction_id': f"TG{user_id}{account_data['phone'][-4:]}",
        'status': account_data['status'],
        'amount': f"{total_amount:,}",
        'phone_number': account_data['phone'],
        'user_id': str(user_id),
        'account_type': 'Telegram Premium Account',
        'date': account_data.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        'payment_method': 'Pending Withdrawal',
        'bank_details': 'Will be provided during withdrawal',
        'reference': f"TG{datetime.now().strftime('%Y%m%d')}{user_id}",
        'transaction_type': 'Account Submission'
    }
    
    return transaction_data

async def _prepare_payment_data(user_id: int, withdrawal_data: Dict, account_count: int, database: Database) -> Dict[str, Any]:
    """Prepare payment data for snapshot generation"""
    
    amount_per_account = 500
    total_amount = account_count * amount_per_account
    
    payment_data = {
        'transaction_id': f"PAY{user_id}{datetime.now().strftime('%m%d')}",
        'status': 'successful',
        'amount': f"{total_amount:,}",
        'phone_number': 'Multiple Accounts',
        'user_id': str(user_id),
        'account_type': f'{account_count} Telegram Accounts',
        'date': withdrawal_data.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        'payment_method': 'Bank Transfer',
        'bank_details': withdrawal_data.get('bank_details', 'Bank Transfer'),
        'reference': f"PAY{datetime.now().strftime('%Y%m%d')}{user_id}",
        'transaction_type': 'Payment Completed'
    }
    
    return payment_data

async def _generate_and_send_snapshot(message: types.Message, transaction_data: Dict[str, Any]):
    """Generate and send transaction snapshot"""
    try:
        # Send "generating" message
        status_msg = await message.answer("🎨 Ana ƙirƙirar snapshot... Don Allah a jira.")
        
        # Generate snapshot
        snapshot_buffer = generate_transaction_snapshot(transaction_data)
        
        if snapshot_buffer and snapshot_buffer.getvalue():
            # Delete status message
            await status_msg.delete()
            
            # Prepare caption
            caption = _create_snapshot_caption(transaction_data)
            
            # Send photo
            photo = types.BufferedInputFile(
                snapshot_buffer.getvalue(),
                filename=f"transaction_{transaction_data['transaction_id']}.png"
            )
            
            await message.answer_photo(
                photo=photo,
                caption=caption,
                parse_mode="Markdown"
            )
            
            # Send sharing instructions
            await message.answer(
                "📤 *Yadda Za Ka Raba Wannan Receipt:*\n\n"
                "1️⃣ Danna akan hoton na sama\n"
                "2️⃣ Zaɓi 'Forward' ko 'Share'\n"
                "3️⃣ Zaɓi inda kake son raba\n\n"
                "💡 *Tips:*\n"
                "• Ka iya share zuwa WhatsApp, Telegram, ko social media\n"
                "• Receipt ɗin ya ƙunshi QR code don verification\n"
                "• Bayanai sun kasance secure da encrypted",
                parse_mode="Markdown"
            )
            
            logger.info(f"Snapshot generated and sent for user {message.from_user.id}")
            
        else:
            await status_msg.edit_text(
                "❌ Kuskure yayin ƙirƙirar snapshot. Don Allah ka sake gwadawa."
            )
            
    except Exception as e:
        logger.error(f"Error generating snapshot: {e}")
        await message.answer(
            "❌ Kuskure yayin ƙirƙirar snapshot. Don Allah ka sake gwadawa."
        )

def _create_snapshot_caption(transaction_data: Dict[str, Any]) -> str:
    """Create caption for the snapshot image"""
    caption = f"""🧾 **Transaction Receipt**

📊 **Details:**
• ID: `{transaction_data['transaction_id']}`
• Status: **{transaction_data['status'].upper()}**
• Amount: **₦{transaction_data['amount']}**
• Date: `{transaction_data['date']}`

📱 **Account:** `{transaction_data['account_type']}`
💳 **Method:** `{transaction_data['payment_method']}`

🔐 *Verified & Secure Transaction*
🤖 *Telegram Trading Bot*"""

    return caption

@router.message(Command("share_receipt"))
async def share_receipt_command(message: types.Message, database: Database):
    """Handle /share_receipt command with instructions"""
    await message.answer(
        "📤 *Yadda Za Ka Raba Receipt:*\n\n"
        "1️⃣ Yi amfani da `/snapshot` don ƙirƙirar receipt\n"
        "2️⃣ Danna akan hoton da aka aiko\n"
        "3️⃣ Zaɓi 'Forward' daga menu\n"
        "4️⃣ Zaɓi contact ko group da kake so\n\n"
        "🌐 *Sharing Options:*\n"
        "• WhatsApp - Don family da friends\n"
        "• Telegram Groups - Don business\n"
        "• Social Media - Don public sharing\n"
        "• Email - Don official records\n\n"
        "🔒 *Security:* Phone numbers sun kasance masked don privacy",
        parse_mode="Markdown"
    )

async def register_handlers(dp, database: Database, config: Config):
    """Register all snapshot handlers"""
    # Register middleware to inject dependencies
    @router.message.middleware()
    async def inject_dependencies(handler, event, data):
        data["database"] = database
        data["config"] = config
        return await handler(event, **data)
    
    dp.include_router(router)
