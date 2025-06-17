#!/usr/bin/env python3
"""
Sports Betting Predictions Telegram Bot

This bot fetches live sports odds and provides betting predictions
based on odds analysis from multiple bookmakers.
"""

import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from bot_handlers import BotHandlers

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error("Exception while handling an update:", exc_info=context.error)

def main():
    """Start the bot"""
    try:
        # Get bot token from environment
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
            return
        
        logger.info("Starting Sports Betting Predictions Bot...")
        
        # Create application
        application = Application.builder().token(bot_token).build()
        
        # Initialize handlers
        handlers = BotHandlers()
        
        # Register command handlers
        application.add_handler(CommandHandler("start", handlers.start_command))
        application.add_handler(CommandHandler("help", handlers.help_command))
        application.add_handler(CommandHandler("sports", handlers.sports_command))
        application.add_handler(CommandHandler("odds", handlers.odds_command))
        application.add_handler(CommandHandler("predictions", handlers.predictions_command))
        application.add_handler(CommandHandler("scores", handlers.scores_command))
        application.add_handler(CommandHandler("games", handlers.games_command))
        application.add_handler(CommandHandler("today", handlers.today_command))
        
        # Register callback query handler for inline buttons
        application.add_handler(CallbackQueryHandler(handlers.button_callback))
        
        # Add error handler
        application.add_error_handler(error_handler)
        
        # Handle unknown commands
        async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if update.message:
                await update.message.reply_text(
                    "Unknown command. Use /help to see available commands."
                )
        
        application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
        
        # Start the bot
        logger.info("Bot is starting...")
        
        # Run the bot
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"Fatal error: {e}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        print("Bot stopped!")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"Fatal error: {e}")