#!/usr/bin/env python3
"""
Simple wrapper script to run the Telegram Trading Bot in Termux
This script provides better error handling and logging for Termux environment
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

def setup_logging():
    """Setup logging for Termux environment"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler()
        ]
    )

def check_environment():
    """Check if all required files and configurations exist"""
    required_files = ['.env', 'main.py', 'config.py', 'database.py']
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    # Check .env configuration
    if not check_env_config():
        return False
        
    return True

def check_env_config():
    """Check if .env file has required configuration"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = ['BOT_TOKEN', 'ADMIN_ID', 'API_ID', 'API_HASH']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print("❌ Missing environment variables in .env file:")
            for var in missing_vars:
                print(f"   - {var}")
            print("\n📝 Please edit .env file with: nano .env")
            return False
            
        return True
        
    except ImportError:
        print("❌ python-dotenv not installed. Run: pip install python-dotenv")
        return False
    except Exception as e:
        print(f"❌ Error checking .env file: {e}")
        return False

async def run_bot():
    """Run the main bot"""
    try:
        print("🤖 Starting Telegram Trading Bot...")
        print("⏰ Press Ctrl+C to stop the bot")
        print("-" * 40)
        
        # Import and run main bot
        from main import main as bot_main
        await bot_main()
        
    except KeyboardInterrupt:
        print("\n⏹️ Bot stopped by user")
    except Exception as e:
        print(f"❌ Error running bot: {e}")
        print("📋 Check bot.log file for detailed error information")
        logging.error(f"Bot error: {e}", exc_info=True)

def main():
    """Main function"""
    print("🚀 Telegram Trading Bot - Termux Edition")
    print("=" * 40)
    
    # Setup logging
    setup_logging()
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed!")
        print("📋 Please fix the issues above and try again")
        sys.exit(1)
    
    print("✅ Environment check passed!")
    print("🔄 Starting bot...")
    
    # Run bot
    try:
        asyncio.run(run_bot())
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()