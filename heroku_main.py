"""
Heroku Production Main File - Enhanced Sports Betting Bot
All latest improvements included for production deployment
"""

import os
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
    """Start the bot for Heroku deployment"""
    try:
        # Get bot token from environment variable
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
            return
        
        logger.info("Starting Enhanced Sports Betting Bot for Heroku...")
        
        # Create application
        application = Application.builder().token(bot_token).build()
        
        # Initialize handlers
        handlers = BotHandlers()
        
        # Register all command handlers
        application.add_handler(CommandHandler("start", handlers.start_command))
        application.add_handler(CommandHandler("help", handlers.help_command))
        
        # Core prediction commands
        application.add_handler(CommandHandler("predictions", handlers.predictions_command))
        application.add_handler(CommandHandler("advanced", handlers.advanced_predictions_command))
        application.add_handler(CommandHandler("enhance", handlers.enhanced_predictions_command))
        application.add_handler(CommandHandler("scores", handlers.scores_command))
        
        # Professional intelligence tools
        application.add_handler(CommandHandler("livesteam", handlers.live_steam_command))
        application.add_handler(CommandHandler("reverse", handlers.reverse_movement_command))
        application.add_handler(CommandHandler("clv", handlers.clv_command))
        application.add_handler(CommandHandler("insider", handlers.insider_command))
        application.add_handler(CommandHandler("edges", handlers.mathematical_edges_command))
        application.add_handler(CommandHandler("steam", handlers.steam_moves_command))
        
        # Analysis and monitoring
        application.add_handler(CommandHandler("odds", handlers.odds_command))
        application.add_handler(CommandHandler("games", handlers.games_command))
        application.add_handler(CommandHandler("today", handlers.today_command))
        application.add_handler(CommandHandler("arbitrage", handlers.arbitrage_command))
        application.add_handler(CommandHandler("scan", handlers.multi_sport_scan_command))
        
        # Sports coverage
        application.add_handler(CommandHandler("sports", handlers.sports_command))
        application.add_handler(CommandHandler("allsports", handlers.all_sports_command))
        application.add_handler(CommandHandler("horses", handlers.horse_racing_command))
        
        # Risk management
        application.add_handler(CommandHandler("bankroll", handlers.bankroll_command))
        application.add_handler(CommandHandler("strategies", handlers.strategies_command))
        application.add_handler(CommandHandler("trackbet", handlers.track_bet_command))
        application.add_handler(CommandHandler("mystats", handlers.my_stats_command))
        application.add_handler(CommandHandler("pending", handlers.pending_bets_command))
        
        # Additional features
        application.add_handler(CommandHandler("fifa", handlers.fifa_world_cup_command))
        application.add_handler(CommandHandler("risk", handlers.risk_assessment_command))
        application.add_handler(CommandHandler("patterns", handlers.patterns_command))
        
        # Callback query handler for inline keyboards
        application.add_handler(CallbackQueryHandler(handlers.button_callback))
        
        # Error handler
        application.add_error_handler(handlers.error_handler)
        
        # Get port from environment variable (Heroku sets this)
        port = int(os.environ.get('PORT', 8443))
        
        # Start the bot with webhook for Heroku
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=bot_token,
            webhook_url=f"https://{os.environ.get('HEROKU_APP_NAME')}.herokuapp.com/{bot_token}"
        )
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

if __name__ == '__main__':
    main()
