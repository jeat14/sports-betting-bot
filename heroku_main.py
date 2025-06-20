#!/usr/bin/env python3
"""
Sports Betting Predictions Telegram Bot - Heroku Production Version

Professional institutional-grade betting bot with:
- Advanced predictions using Kelly Criterion
- Live arbitrage detection across 28+ bookmakers
- Real Market Rasen horse racing analysis
- Multi-sport scanning capabilities
- Mathematical edge calculations
- Professional betting strategies
"""

import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from bot_handlers import BotHandlers

# Configure logging for production
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update: object, context) -> None:
    """Production error handler with proper logging"""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    
    if update and hasattr(update, 'effective_message') and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ Processing error. Please try again or use /help for available commands."
            )
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")

def main():
    """Start the institutional-grade sports betting bot"""
    # Validate environment variables
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
    
    odds_api_key = os.getenv('ODDS_API_KEY')
    if not odds_api_key:
        raise ValueError("ODDS_API_KEY environment variable is required")
    
    logger.info("Starting Sports Betting Bot with professional features...")
    
    # Create application with production settings
    application = Application.builder().token(token).build()
    
    # Initialize handlers
    handlers = BotHandlers()
    
    # Register all professional betting commands
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
    application.add_handler(CommandHandler("allsports", handlers.all_sports_command))
    
    # Professional betting analysis commands
    application.add_handler(CommandHandler("horses", handlers.horses_command))  # Real Market Rasen analysis
    application.add_handler(CommandHandler("arbitrage", handlers.arbitrage_command))  # Live arbitrage detection
    application.add_handler(CommandHandler("pro", handlers.professional_strategies_command))  # Professional strategies
    application.add_handler(CommandHandler("bankroll", handlers.bankroll_command))  # Kelly Criterion management
    application.add_handler(CommandHandler("live", handlers.live_monitor_command))  # Live odds monitoring
    application.add_handler(CommandHandler("scan", handlers.scan_all_command))  # Multi-sport scanner
    application.add_handler(CommandHandler("fifa", handlers.fifa_command))  # FIFA Club World Cup
    application.add_handler(CommandHandler("edge", handlers.edge_command))  # Mathematical edge calculator
    application.add_handler(CommandHandler("insider", handlers.insider_command))  # Insider intelligence
    application.add_handler(CommandHandler("horsesplus", handlers.horses_enhanced_command))  # Enhanced horse analysis
    application.add_handler(CommandHandler("multisport", handlers.multisport_command))  # Institutional scanner
    application.add_handler(CommandHandler("steam", handlers.steam_command))  # Steam move detection
    application.add_handler(CommandHandler("strategies", handlers.strategies_command))  # Advanced strategies
    
    # Interactive handlers
    application.add_handler(CallbackQueryHandler(handlers.button_callback))
    
    # Unknown command handler
    async def unknown_command(update: Update, context):
        await update.message.reply_text(
            "❓ Command not recognized. Use /help to see all professional betting commands."
        )
    
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    application.add_error_handler(error_handler)
    
    logger.info("Bot initialized with 15+ professional betting commands")
    logger.info("Features: Kelly Criterion, Live Arbitrage, Market Rasen Racing, Multi-Sport Analysis")
    
    # Start polling
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )

if __name__ == '__main__':
    main()
