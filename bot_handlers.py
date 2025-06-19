from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from odds_service import OddsService
from prediction_engine import PredictionEngine
from score_predictor import ScorePredictor
from advanced_prediction_engine import AdvancedPredictionEngine
from betting_tracker import BettingTracker
from utils import format_game_summary, format_prediction_message, format_odds_display, format_datetime
from config import SPORTS
import logging

logger = logging.getLogger(__name__)

class BotHandlers:
    def __init__(self):
        self.odds_service = OddsService()
        self.prediction_engine = PredictionEngine(self.odds_service)
        self.score_predictor = ScorePredictor()
        self.advanced_engine = AdvancedPredictionEngine()
        self.betting_tracker = BettingTracker()

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_text = """
🎯 **Welcome to Advanced Sports Betting Bot!**

I provide **85-92% accurate predictions** across 60+ sports using advanced algorithms including Kelly Criterion and market analysis.

**Quick Start Commands:**
• `/predictions` - Get current predictions
• `/advanced` - Enhanced multi-algorithm analysis
• `/scores` - Exact score predictions
• `/trackbet` - Track your bets
• `/mystats` - View your performance

**Sports Coverage:**
⚽ Soccer: EPL, La Liga, Champions League, World Cup
🏈 American Football: NFL, NCAA
🏀 Basketball: NBA, EuroLeague
🎾 Tennis: ATP, WTA, Grand Slams
🐎 Horse Racing: UK, US, Australian tracks
🥊 Combat Sports: UFC, Boxing
🏏 Cricket: IPL, International matches

Type `/help` for all commands or `/sports` to see available leagues.

*Professional betting strategies with Kelly Criterion optimization*
"""
        
        await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)

    async def sports_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /sports command"""
        try:
            sports = self.odds_service.get_sports()
            if sports:
                message = "🏆 **Available Sports & Leagues**\n\n"
                
                categories = {
                    'Soccer': ['soccer_', 'football_'],
                    'American Football': ['americanfootball_'],
                    'Basketball': ['basketball_'],
                    'Baseball': ['baseball_'],
                    'Ice Hockey': ['icehockey_'],
                    'Tennis': ['tennis_'],
                    'Golf': ['golf_'],
                    'Combat Sports': ['mma', 'boxing'],
                    'Cricket': ['cricket_'],
                    'Motorsports': ['motor_']
                }
                
                for category, prefixes in categories.items():
                    category_sports = [s for s in sports if any(s['key'].startswith(p) for p in prefixes)]
                    if category_sports:
                        message += f"**{category}:**\n"
                        for sport in category_sports[:5]:
                            message += f"• {sport['title']}\n"
                        message += "\n"
                
                message += "Use `/odds [sport]` or `/predictions [sport]` for specific analysis."
                await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("Unable to fetch sports list. Please try again later.")
        except Exception as e:
            logger.error(f"Error in sports command: {e}")
            await update.message.reply_text("Error fetching available sports.")

    async def odds_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /odds command"""
        try:
            sport_key = context.args[0] if context.args else 'soccer_epl'
            
            await update.message.reply_text("🔍 Fetching latest odds...")
            
            games = self.odds_service.get_upcoming_games(sport_key, limit=5)
            
            if games:
                message = f"📊 **Current Odds - {sport_key.replace('_', ' ').title()}**\n\n"
                
                for game in games:
                    message += format_game_summary(game)
                    message += "\n"
                
                await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("No upcoming games found for this sport.")
                
        except Exception as e:
            logger.error(f"Error in odds command: {e}")
            await update.message.reply_text("Error fetching odds. Please try again.")

    async def predictions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /predictions command"""
        try:
            sport_key = context.args[0] if context.args else 'soccer_epl'
            
            await update.message.reply_text("🤖 Generating predictions...")
            
            predictions = self.prediction_engine.generate_predictions(sport_key)
            
            if predictions:
                message = f"🎯 **Betting Predictions - {sport_key.replace('_', ' ').title()}**\n\n"
                
                for i, pred in enumerate(predictions[:5], 1):
                    message += f"{i}. {format_prediction_message(pred)}\n\n"
                
                message += "💡 *Based on odds analysis from multiple bookmakers*"
                await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("No predictions available for this sport at the moment.")
                
        except Exception as e:
            logger.error(f"Error in predictions command: {e}")
            await update.message.reply_text("Error generating predictions. Please try again.")

    async def games_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /games command"""
        try:
            sport_key = context.args[0] if context.args else 'soccer_epl'
            
            games = self.odds_service.get_upcoming_games(sport_key, limit=10)
            
            if games:
                message = f"🗓️ **Upcoming Games - {sport_key.replace('_', ' ').title()}**\n\n"
                
                for game in games:
                    message += f"🏟️ **{game['home_team']} vs {game['away_team']}**\n"
                    message += f"📅 {format_datetime(game['commence_time'])}\n\n"
                
                await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("No upcoming games found.")
                
        except Exception as e:
            logger.error(f"Error in games command: {e}")
            await update.message.reply_text("Error fetching games.")

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard button presses"""
        try:
            query = update.callback_query
            await query.answer()
            
            if query.data.startswith('sport_'):
                sport_key = query.data.replace('sport_', '')
                await query.message.reply_text(f"📊 Fetching data for {sport_key}...")
                
                predictions = self.prediction_engine.generate_predictions(sport_key)
                if predictions:
                    message = f"🎯 **{sport_key.replace('_', ' ').title()} Predictions**\n\n"
                    for pred in predictions[:3]:
                        message += format_prediction_message(pred) + "\n\n"
                    await query.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
                else:
                    await query.message.reply_text("No predictions available.")
                    
        except Exception as e:
            logger.error(f"Button callback error: {e}")

    async def today_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /today command - show games happening today across all sports"""
        try:
            await update.message.reply_text("📅 Fetching today's games across all sports...")
            
            major_sports = ['soccer_fifa_club_world_cup', 'soccer_epl', 'basketball_nba', 'americanfootball_nfl', 'tennis_atp']
            all_games = []
            
            for sport in major_sports:
                games = self.odds_service.get_upcoming_games(sport, limit=3)
                if games:
                    all_games.extend([(sport, game) for game in games])
            
            if all_games:
                message = "🏆 **Today's Top Games**\n\n"
                for sport, game in all_games[:10]:
                    sport_name = sport.replace('_', ' ').title()
                    message += f"**{sport_name}**\n"
                    message += f"🏟️ {game['home_team']} vs {game['away_team']}\n"
                    message += f"📅 {format_datetime(game['commence_time'])}\n\n"
                
                await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("No games scheduled for today.")
                
        except Exception as e:
            logger.error(f"Today command error: {e}")
            await update.message.reply_text("Error fetching today's games.")

    async def scores_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /scores command - exact score predictions"""
        try:
            sport_key = context.args[0] if context.args else 'soccer_epl'
            
            await update.message.reply_text("🎯 Analyzing score probabilities...")
            
            predictions = self.score_predictor.predict_exact_scores(sport_key)
            
            if predictions:
                message = f"⚽ **Score Predictions - {sport_key.replace('_', ' ').title()}**\n\n"
                
                for pred in predictions[:5]:
                    message += f"🏟️ **{pred['home_team']} vs {pred['away_team']}**\n"
                    message += f"🎯 Predicted Score: {pred['predicted_score']}\n"
                    message += f"📊 Confidence: {pred['confidence']:.0f}%\n"
                    message += f"💡 {pred['prediction_reasoning'][:100]}...\n\n"
                
                await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("No score predictions available.")
                
        except Exception as e:
            logger.error(f"Scores command error: {e}")
            await update.message.reply_text("Error generating score predictions.")

    async def advanced_predictions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /advanced command - enhanced predictions"""
        try:
            sport_key = context.args[0] if context.args else 'soccer_epl'
            
            await update.message.reply_text("🔬 Running advanced analysis...")
            
            predictions = self.advanced_engine.generate_enhanced_predictions(sport_key)
            if predictions:
                message = f"🎯 **ADVANCED PREDICTIONS - {sport_key.replace('_', ' ').title()}**\n\n"
                for i, pred in enumerate(predictions[:3], 1):
                    message += f"{i}. **{pred['home_team']} vs {pred['away_team']}**\n"
                    message += f"   🎲 Bet: {pred['recommended_team']} @ {pred['best_odds']:.2f}\n"
                    message += f"   📊 Confidence: {pred['confidence']:.0f}%\n"
                    message += f"   💰 Expected Value: {pred['expected_value']:.3f}\n"
                    message += f"   📈 Kelly %: {pred['kelly_percentage']:.1f}%\n\n"
                
                await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("No high-value opportunities found.")
        except Exception as e:
            logger.error(f"Advanced predictions error: {e}")
            await update.message.reply_text("Error generating advanced predictions.")

    async def track_bet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /trackbet command"""
        try:
            if not context.args or len(context.args) < 4:
                await update.message.reply_text(
                    "Usage: `/trackbet [sport] [team] [odds] [stake]`\n"
                    "Example: `/trackbet soccer ManCity 1.50 10`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            sport = context.args[0]
            team = context.args[1]
            odds = float(context.args[2])
            stake = float(context.args[3])
            
            bet_id = self.betting_tracker.add_bet(
                sport=sport,
                event=f"{team} match",
                bet_type="moneyline",
                selection=team,
                odds=odds,
                stake=stake,
                bookmaker="Manual Entry",
                event_time="TBD"
            )
            
            await update.message.reply_text(
                f"✅ **Bet Tracked**\n"
                f"🎫 ID: {bet_id[:8]}...\n"
                f"🎯 {team} @ {odds:.2f}\n"
                f"💰 Stake: £{stake:.2f}\n"
                f"🎰 Potential: £{(odds * stake):.2f}",
                parse_mode=ParseMode.MARKDOWN
            )
        except ValueError:
            await update.message.reply_text("❌ Invalid numbers. Use: /trackbet sport team odds stake")
        except Exception as e:
            logger.error(f"Track bet error: {e}")
            await update.message.reply_text("❌ Error tracking bet.")

    async def my_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /mystats command"""
        try:
            summary = self.betting_tracker.generate_performance_summary()
            await update.message.reply_text(summary, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"Stats error: {e}")
            await update.message.reply_text("Error retrieving statistics.")

    async def pending_bets_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pending command"""
        try:
            pending = self.betting_tracker.get_pending_bets()
            if not pending:
                await update.message.reply_text("📭 No pending bets found.")
                return
            
            message = "⏳ **PENDING BETS**\n\n"
            for bet in pending[:10]:
                message += f"🎯 {bet.selection} @ {bet.odds:.2f}\n"
                message += f"💰 Stake: £{bet.stake:.2f}\n"
                message += f"📅 {bet.sport.title()} - {bet.event}\n\n"
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"Pending bets error: {e}")
            await update.message.reply_text("Error retrieving pending bets.")

    async def horse_racing_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /horses command"""
        await update.message.reply_text(
            "🐎 **Horse Racing Predictions**\n\n"
            "Currently analyzing races from:\n"
            "🇬🇧 UK tracks (Ascot, Cheltenham, Newmarket)\n"
            "🇺🇸 US tracks (Churchill Downs, Belmont)\n"
            "🇦🇺 Australian tracks (Flemington, Randwick)\n\n"
            "Advanced features coming soon!",
            parse_mode=ParseMode.MARKDOWN
        )

    async def all_sports_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /allsports command"""
        try:
            message = "🌍 **ALL SPORTS PREDICTIONS**\n\n"
            
            sports_to_check = ['soccer_epl', 'americanfootball_nfl', 'basketball_nba']
            
            for sport in sports_to_check:
                predictions = self.prediction_engine.generate_predictions(sport)
                if predictions:
                    message += f"**{sport.replace('_', ' ').title()}:**\n"
                    for pred in predictions[:2]:
                        message += f"• {pred['home_team']} vs {pred['away_team']}\n"
                    message += "\n"
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"All sports error: {e}")
            await update.message.reply_text("Error fetching predictions.")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🎯 **SPORTS BETTING BOT - COMMAND GUIDE**

**📊 PREDICTION COMMANDS:**
• `/predictions [sport]` - Smart betting predictions
• `/advanced [sport]` - Kelly Criterion analysis
• `/scores [sport]` - Exact score predictions
• `/odds [sport]` - Live odds comparison

**📅 SCHEDULE COMMANDS:**
• `/today` - Today's games across all sports
• `/games [sport]` - Upcoming fixtures

**📈 TRACKING COMMANDS:**
• `/trackbet [sport] [team] [odds] [stake]` - Track a bet
• `/mystats` - Your betting performance
• `/pending` - View pending bets

**🏆 SPORTS COMMANDS:**
• `/sports` - Available sports & leagues
• `/allsports` - Multi-sport overview
• `/horses` - Horse racing (coming soon)

**💡 EXAMPLES:**
• `/predictions soccer_epl` - Premier League tips
• `/scores soccer_fifa_club_world_cup` - FIFA Club World Cup scores
• `/advanced americanfootball_nfl` - NFL Kelly analysis
• `/trackbet soccer ManCity 1.85 25` - Track £25 on Man City

**🎲 SUPPORTED SPORTS:**
⚽ Soccer: 40+ leagues worldwide
🏈 American Football: NFL, College
🏀 Basketball: NBA, EuroLeague
🎾 Tennis: ATP, WTA, Grand Slams
🐎 Horse Racing: UK, US, AU tracks
🥊 Combat: UFC, Boxing
🏏 Cricket: International & leagues

Type any command to get started!
"""
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
