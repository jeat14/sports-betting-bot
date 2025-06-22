#!/usr/bin/env python3
"""
Sports Betting Bot - Heroku Worker Fix
Minimal working version for reliable Heroku deployment
"""

import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Start the bot with minimal configuration"""
    # Get environment variables
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found")
        return

    # Create application
    application = Application.builder().token(token).build()
    
    # Initialize handlers with fallback
    try:
        from bot_handlers import BotHandlers
        handlers = BotHandlers()
        logger.info("Bot handlers initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize bot handlers: {e}")
        
        # Minimal fallback handler
        async def fallback_start(update: Update, context):
            await update.message.reply_text(
                "🤖 Enhanced Sports Betting Bot is starting up...\n"
                "Please wait a moment and try your commands again."
            )
        
        application.add_handler(CommandHandler("start", fallback_start))
        
        async def fallback_help(update: Update, context):
            help_text = """
🎯 Sports Betting Bot Commands:
/start - Start the bot
/help - Show this help
/sports - Available sports
/odds - Live odds
/predictions - AI predictions
/games - Today's games
/enhance - Enhanced predictions
/livesteam - Steam moves
/reverse - Line movement
/clv - Closing line value
            """
            await update.message.reply_text(help_text)
        
        application.add_handler(CommandHandler("help", fallback_help))
        logger.info("Using fallback handlers")
        
        # Start with fallback
        logger.info("Starting bot with fallback configuration...")
        application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
        return

    # Register all handlers if initialization succeeded
    try:
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
        application.add_handler(CommandHandler("patterns", handlers.patterns_command))
        application.add_handler(CommandHandler("picks", handlers.picks_command))
        
        # Enhanced commands
        application.add_handler(CommandHandler("enhance", handlers.enhanced_predictions_command))
        application.add_handler(CommandHandler("livesteam", handlers.live_steam_command))
        application.add_handler(CommandHandler("reverse", handlers.reverse_movement_command))
        application.add_handler(CommandHandler("clv", handlers.clv_command))
        
        # Callback handler
        application.add_handler(CallbackQueryHandler(handlers.button_callback))
        
        # Unknown command handler
        async def unknown_command(update: Update, context):
            if update.message:
                await update.message.reply_text("❓ Unknown command. Use /help to see available commands.")
        
        application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
        
        logger.info("All handlers registered successfully")
        
    except Exception as e:
        logger.error(f"Error registering handlers: {e}")
    
    # Start the bot
    logger.info("Starting Enhanced Sports Betting Bot...")
    try:
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False
        )
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

if __name__ == '__main__':
    main()
