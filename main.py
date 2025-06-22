#!/usr/bin/env python3
"""
Enhanced Sports Betting Predictions Bot
Professional-grade sports betting intelligence with AI predictions and arbitrage detection
"""

import os
import sys
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from bot_handlers import BotHandlers

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Start the bot"""
    try:
        # Get bot token from environment (try both possible names)
        bot_token = os.getenv('TELEGRAM_TOKEN') or os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            raise ValueError("No TELEGRAM_TOKEN or TELEGRAM_BOT_TOKEN provided in environment")
        
        logger.info("Starting Enhanced Sports Betting Predictions Bot...")
        logger.info(f"Environment token check: Bot token configured from {'TELEGRAM_TOKEN' if os.getenv('TELEGRAM_TOKEN') else 'TELEGRAM_BOT_TOKEN'}")
        
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
        application.add_handler(CommandHandler("games", handlers.games_command))
        application.add_handler(CommandHandler("today", handlers.today_command))
        application.add_handler(CommandHandler("scores", handlers.scores_command))
        application.add_handler(CommandHandler("advanced", handlers.advanced_predictions_command))
        application.add_handler(CommandHandler("arbitrage", handlers.arbitrage_command))
        application.add_handler(CommandHandler("bankroll", handlers.bankroll_command))
        application.add_handler(CommandHandler("strategies", handlers.strategies_command))
        application.add_handler(CommandHandler("allsports", handlers.all_sports_command))
        application.add_handler(CommandHandler("trackbet", handlers.track_bet_command))
        application.add_handler(CommandHandler("mystats", handlers.my_stats_command))
        application.add_handler(CommandHandler("pending", handlers.pending_bets_command))
        application.add_handler(CommandHandler("horses", handlers.horse_racing_command))
        application.add_handler(CommandHandler("steam", handlers.steam_moves_command))
        application.add_handler(CommandHandler("edges", handlers.mathematical_edges_command))
        application.add_handler(CommandHandler("insider", handlers.insider_intelligence_command))
        application.add_handler(CommandHandler("scan", handlers.multi_sport_scan_command))
        application.add_handler(CommandHandler("picks", handlers.picks_command))
        application.add_handler(CommandHandler("fifa", handlers.fifa_world_cup_command))
        application.add_handler(CommandHandler("risk", handlers.risk_assessment_command))
        application.add_handler(CommandHandler("patterns", handlers.patterns_command))
        
        # Add callback query handler for buttons
        application.add_handler(CallbackQueryHandler(handlers.button_callback))
        
        # Add error handler
        application.add_error_handler(handlers.error_handler)
        
        logger.info("Bot handlers initialized successfully")
        logger.info("Bot is starting...")
        
        # Run the bot
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
