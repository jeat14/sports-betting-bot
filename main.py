#!/usr/bin/env python3
"""
Enhanced Sports Betting Predictions Bot
Clean version with minimal dependencies for successful Heroku deployment
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from bot_handlers import BotHandlers

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the bot"""
    try:
        # Get bot token from environment
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN')
        
        if not bot_token:
            logger.error("No bot token found in environment variables")
            return
        
        logger.info("Starting Enhanced Sports Betting Predictions Bot...")
        logger.info("Environment token check: Bot token configured")
        
        # Create application
        application = Application.builder().token(bot_token).build()
        
        # Initialize bot handlers
        handlers = BotHandlers()
        logger.info("Bot handlers initialized successfully")
        
        # Add command handlers
        application.add_handler(CommandHandler("start", handlers.start_command))
        application.add_handler(CommandHandler("help", handlers.help_command))
        application.add_handler(CommandHandler("predictions", handlers.predictions_command))
        application.add_handler(CommandHandler("arbitrage", handlers.arbitrage_command))
        application.add_handler(CommandHandler("bankroll", handlers.bankroll_command))
        application.add_handler(CommandHandler("steam", handlers.steam_command))
        application.add_handler(CommandHandler("picks", handlers.picks_command))
        application.add_handler(CommandHandler("odds", handlers.odds_command))
        application.add_handler(CommandHandler("insider", handlers.insider_command))
        application.add_handler(CommandHandler("edges", handlers.edges_command))
        application.add_handler(CommandHandler("fifa", handlers.fifa_command))
        application.add_handler(CommandHandler("risk", handlers.risk_command))
        application.add_handler(CommandHandler("patterns", handlers.patterns_command))
        application.add_handler(CommandHandler("scan", handlers.scan_command))
        application.add_handler(CommandHandler("scores", handlers.scores_command))
        
        # Add error handler
        application.add_error_handler(handlers.error_handler)
        
        logger.info("Bot is starting...")
        
        # Run the bot
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise

if __name__ == '__main__':
    main()
