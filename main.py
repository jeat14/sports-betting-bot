"""
Production Heroku Main File - Simplified for Stability
"""

import os
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Start the bot for Heroku deployment"""
    try:
        # Get bot token
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            logger.error("TELEGRAM_BOT_TOKEN not found")
            return
        
        logger.info("Starting Enhanced Betting Bot on Heroku...")
        
        # Create application
        application = Application.builder().token(bot_token).build()
        
        # Import handlers here to avoid circular imports
        from bot_handlers import BotHandlers
        handlers = BotHandlers()
        
        # Register core commands
        application.add_handler(CommandHandler("start", handlers.start_command))
        application.add_handler(CommandHandler("help", handlers.help_command))
        application.add_handler(CommandHandler("predictions", handlers.predictions_command))
        application.add_handler(CommandHandler("advanced", handlers.advanced_predictions_command))
        application.add_handler(CommandHandler("enhance", handlers.enhanced_predictions_command))
        application.add_handler(CommandHandler("scores", handlers.scores_command))
        application.add_handler(CommandHandler("odds", handlers.odds_command))
        application.add_handler(CommandHandler("games", handlers.games_command))
        application.add_handler(CommandHandler("today", handlers.today_command))
        application.add_handler(CommandHandler("arbitrage", handlers.arbitrage_command))
        application.add_handler(CommandHandler("bankroll", handlers.bankroll_command))
        application.add_handler(CommandHandler("strategies", handlers.strategies_command))
        application.add_handler(CommandHandler("trackbet", handlers.track_bet_command))
        application.add_handler(CommandHandler("mystats", handlers.my_stats_command))
        application.add_handler(CommandHandler("pending", handlers.pending_bets_command))
        application.add_handler(CommandHandler("sports", handlers.sports_command))
        application.add_handler(CommandHandler("allsports", handlers.all_sports_command))
        application.add_handler(CommandHandler("horses", handlers.horse_racing_command))
        
        # Enhanced intelligence commands
        application.add_handler(CommandHandler("livesteam", handlers.live_steam_command))
        application.add_handler(CommandHandler("reverse", handlers.reverse_movement_command))
        application.add_handler(CommandHandler("clv", handlers.clv_command))
        application.add_handler(CommandHandler("insider", handlers.insider_command))
        application.add_handler(CommandHandler("edges", handlers.mathematical_edges_command))
        application.add_handler(CommandHandler("steam", handlers.steam_moves_command))
        application.add_handler(CommandHandler("scan", handlers.multi_sport_scan_command))
        
        # Additional features
        application.add_handler(CommandHandler("fifa", handlers.fifa_world_cup_command))
        application.add_handler(CommandHandler("risk", handlers.risk_assessment_command))
        
        # Callback handler
        application.add_handler(CallbackQueryHandler(handlers.button_callback))
        
        # Remove error handler to prevent compatibility issues
        # application.add_error_handler(error_handler)
        
        # Get port from environment
        port = int(os.environ.get('PORT', 8443))
        
        # Start with webhook for Heroku
        app_name = os.environ.get('HEROKU_APP_NAME')
        if app_name:
            webhook_url = f"https://{app_name}.herokuapp.com/{bot_token}"
            application.run_webhook(
                listen="0.0.0.0",
                port=port,
                url_path=bot_token,
                webhook_url=webhook_url
            )
        else:
            # Fallback to polling if app name not set
            logger.info("HEROKU_APP_NAME not set, using polling mode")
            application.run_polling()
        
    except Exception as e:
        logger.error(f"Bot startup error: {e}")

if __name__ == '__main__':
    main()
