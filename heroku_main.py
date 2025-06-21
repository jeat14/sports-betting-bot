#!/usr/bin/env python3
"""
Sports Betting Predictions Telegram Bot - Heroku Version

This bot fetches live sports odds and provides betting predictions
based on odds analysis from multiple bookmakers.
"""

import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from bot_handlers import BotHandlers

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update: object, context) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    
    if update and hasattr(update, 'effective_message') and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ An error occurred while processing your request. Please try again."
            )
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")

def main():
    """Start the bot"""
    # Get environment variables
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
    
    odds_api_key = os.getenv('ODDS_API_KEY')
    if not odds_api_key:
        raise ValueError("ODDS_API_KEY environment variable is required")
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Initialize handlers
    handlers = BotHandlers()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", handlers.start_command))
    application.add_handler(CommandHandler("help", handlers.help_command))
    application.add_handler(CommandHandler("sports", handlers.sports_command))
    application.add_handler(CommandHandler("odds", handlers.odds_command))
    application.add_handler(CommandHandler("predictions", handlers.predictions_command))
    application.add_handler(CommandHandler("games", handlers.games_command))
    application.add_handler(CommandHandler("today", handlers.today_command))
    application.add_handler(CommandHandler("scores", handlers.scores_command))
    application.add_handler(CommandHandler("advanced", handlers.advanced_predictions_command))
    application.add_handler(CommandHandler("trackbet", handlers.track_bet_command))
    application.add_handler(CommandHandler("mystats", handlers.my_stats_command))
    application.add_handler(CommandHandler("pending", handlers.pending_bets_command))
    application.add_handler(CommandHandler("horses", handlers.horse_racing_command))
    application.add_handler(CommandHandler("allsports", handlers.all_sports_command))
    application.add_handler(CommandHandler("arbitrage", handlers.arbitrage_command))
    application.add_handler(CommandHandler("bankroll", handlers.bankroll_command))
    application.add_handler(CommandHandler("strategies", handlers.strategies_command))
    application.add_handler(CommandHandler("steam", handlers.steam_moves_command))
    application.add_handler(CommandHandler("edges", handlers.mathematical_edges_command))
    application.add_handler(CommandHandler("insider", handlers.insider_intelligence_command))
    application.add_handler(CommandHandler("fifa", handlers.fifa_world_cup_command))
    application.add_handler(CommandHandler("scan", handlers.multi_sport_scan_command))
    application.add_handler(CommandHandler("risk", handlers.risk_assessment_command))
    
    # Register callback query handler for inline keyboards
    application.add_handler(CallbackQueryHandler(handlers.button_callback))
    
    # Register message handler for unknown commands
    async def unknown_command(update: Update, context):
        await update.message.reply_text(
            "❓ Unknown command. Use /help to see available commands."
        )
    
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Starting Sports Betting Predictions Bot...")
    logger.info("Bot is starting...")
    
    # Use polling for Heroku (avoids webhook dependency issues)
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
        close_loop=False
    )

if __name__ == '__main__':
    main()
