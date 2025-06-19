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
     self.advanced_engine = AdvancedPredictionEngine()
self.betting_tracker = BettingTracker()   self.odds_service = OddsService()
        self.prediction_engine = PredictionEngine(self.odds_service)
        self.score_predictor = ScorePredictor()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🎯 **Sports Betting Bot**

Get betting predictions with live odds analysis.

**Quick Commands:**
/today - See today's games
/predictions - Get betting tips
/scores - Exact score predictions
/odds - View current odds

Choose a sport below:
"""
        
        # Create simple keyboard for main sports
        keyboard = [
            [InlineKeyboardButton("🏆 FIFA World Cup", callback_data="pred_soccer_fifa_club_world_cup")],
            [InlineKeyboardButton("⚾ Baseball", callback_data="pred_baseball_mlb"),
             InlineKeyboardButton("🏀 Basketball", callback_data="pred_basketball_nba")],
            [InlineKeyboardButton("📋 All Sports", callback_data="sports_list")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def sports_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /sports command"""
        message = "🏆 **Available Sports:**\n\n"
        
        for sport_key, sport_name in SPORTS.items():
            message += f"• {sport_name} (`{sport_key}`)\n"
        
        message += "\n💡 Use `/odds [sport_key]` or `/predictions [sport_key]` to get data for a specific sport."
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def odds_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /odds command"""
        # If no sport specified, show FIFA Club World Cup by default
        sport_key = 'soccer_fifa_club_world_cup'
        if context.args and context.args[0] in SPORTS:
            sport_key = context.args[0]
        
        await update.message.reply_text("🔄 Fetching live odds data...")
        
        try:
            games = self.odds_service.get_upcoming_games(sport_key, 5)
            
            if not games:
                await update.message.reply_text(
                    f"❌ No upcoming games found for {SPORTS[sport_key]} or API error occurred."
                )
                return
            
            message = f"📊 **Live Odds - {SPORTS[sport_key]}**\n\n"
            
            for i, game in enumerate(games, 1):
                message += f"**Game {i}:**\n"
                message += format_game_summary(game) + "\n"
                
                # Show odds from first bookmaker
                if game.get('bookmakers'):
                    bookmaker = game['bookmakers'][0]
                    h2h_market = next((m for m in bookmaker['markets'] if m['key'] == 'h2h'), None)
                    
                    if h2h_market:
                        message += "💰 **Odds**:\n"
                        for outcome in h2h_market['outcomes']:
                            message += f"  {outcome['name']}: {format_odds_display(float(outcome['price']))}\n"
                
                message += "\n"
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error in odds command: {e}")
            await update.message.reply_text(
                "❌ Error fetching odds data. Please try again later."
            )
    
    async def predictions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /predictions command"""
        # If no sport specified, show FIFA Club World Cup by default
        sport_key = 'soccer_fifa_club_world_cup'
        if context.args and context.args[0] in SPORTS:
            sport_key = context.args[0]
        
        await update.message.reply_text("🤖 Analyzing odds and generating predictions...")
        
        try:
            predictions = self.prediction_engine.generate_predictions(sport_key)
            
            if not predictions:
                await update.message.reply_text(
                    f"❌ No betting opportunities found for {SPORTS[sport_key]} at the moment.\n"
                    "This could mean:\n"
                    "• No games scheduled soon\n"
                    "• Odds are not favorable for betting\n"
                    "• API data temporarily unavailable"
                )
                return
            
            # Send up to 3 predictions to avoid message length limits
            for i, prediction in enumerate(predictions[:3], 1):
                message = f"**Prediction {i}/{min(len(predictions), 3)}**\n\n"
                message += format_prediction_message(prediction)
                
                await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
            if len(predictions) > 3:
                await update.message.reply_text(
                    f"📊 Found {len(predictions)} total predictions. Showing top 3.\n"
                    "Use the command again for updated analysis."
                )
        
        except Exception as e:
            logger.error(f"Error in predictions command: {e}")
            await update.message.reply_text(
                "❌ Error generating predictions. Please try again later."
            )
    
    async def games_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /games command"""
        if not context.args:
            await update.message.reply_text(
                "Please specify a sport. Use /sports to see available options.\n"
                "Example: `/games americanfootball_nfl`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        sport_key = context.args[0]
        if sport_key not in SPORTS:
            await update.message.reply_text(
                f"Invalid sport key: `{sport_key}`\n"
                "Use /sports to see available options.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        await update.message.reply_text("📅 Fetching upcoming games...")
        
        try:
            games = self.odds_service.get_upcoming_games(sport_key, 8)
            
            if not games:
                await update.message.reply_text(
                    f"❌ No upcoming games found for {SPORTS[sport_key]}."
                )
                return
            
            message = f"📅 **Upcoming Games - {SPORTS[sport_key]}**\n\n"
            
            for i, game in enumerate(games, 1):
                message += f"**{i}.** {format_game_summary(game)}\n\n"
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error in games command: {e}")
            await update.message.reply_text(
                "❌ Error fetching games data. Please try again later."
            )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard button presses"""
        query = update.callback_query
        await query.answer()
        
        chat_id = query.message.chat_id
        
        if query.data.startswith("pred_"):
            sport_key = query.data.replace("pred_", "")
            await query.message.reply_text("🤖 Analyzing odds and generating predictions...")
            
            try:
                predictions = self.prediction_engine.generate_predictions(sport_key)
                
                if not predictions:
                    await query.message.reply_text(
                        f"❌ No betting opportunities found for {SPORTS.get(sport_key, sport_key)} at the moment.\n"
                        "This could mean:\n"
                        "• No games scheduled soon\n"
                        "• Odds are not favorable for betting\n"
                        "• API data temporarily unavailable"
                    )
                    return
                
                # Send up to 3 predictions
                for i, prediction in enumerate(predictions[:3], 1):
                    message = f"**Prediction {i}/{min(len(predictions), 3)}**\n\n"
                    message += format_prediction_message(prediction)
                    await query.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
                
                if len(predictions) > 3:
                    await query.message.reply_text(
                        f"📊 Found {len(predictions)} total predictions. Showing top 3."
                    )
            except Exception as e:
                logger.error(f"Error in button predictions: {e}")
                await query.message.reply_text("❌ Error generating predictions. Please try again later.")
        
        elif query.data == "sports_list":
            message = "🏆 **Available Sports:**\n\n"
            for sport_key, sport_name in SPORTS.items():
                message += f"• {sport_name} (`{sport_key}`)\n"
            message += "\n💡 Use `/odds [sport_key]` or `/predictions [sport_key]` to get data for a specific sport."
            await query.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def today_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /today command - show games happening today across all sports"""
        await update.message.reply_text("🔄 Scanning all sports for today's games...")
        
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        today_end = now + timedelta(hours=24)
        
        all_today_games = []
        
        # Check each sport for games today
        for sport_key, sport_name in SPORTS.items():
            try:
                games = self.odds_service.get_upcoming_games(sport_key, 10)
                for game in games:
                    try:
                        game_time = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00'))
                        hours_until = (game_time - now).total_seconds() / 3600
                        
                        if -2 <= hours_until <= 24:  # Games from 2 hours ago to 24 hours ahead
                            all_today_games.append({
                                'sport': sport_name,
                                'game': game,
                                'hours_until': hours_until
                            })
                    except:
                        continue
            except:
                continue
        
        if not all_today_games:
            await update.message.reply_text(
                "❌ No games found for today across all sports.\n"
                "This could mean it's an off-day or the API has limited data."
            )
            return
        
        # Sort by time
        all_today_games.sort(key=lambda x: x['hours_until'])
        
        message = f"📅 **Games Today/Tomorrow** ({len(all_today_games)} found)\n\n"
        
        for item in all_today_games[:15]:  # Limit to 15 games
            game = item['game']
            hours = item['hours_until']
            
            if hours < 0:
                time_str = "🔴 Live"
            elif hours < 1:
                time_str = f"⏰ {int(hours * 60)}min"
            else:
                time_str = f"🕐 {hours:.1f}h"
            
            message += f"**{item['sport']}**\n"
            message += f"{game['away_team']} @ {game['home_team']}\n"
            message += f"{time_str}\n\n"
        
        if len(all_today_games) > 15:
            message += f"... and {len(all_today_games) - 15} more games"
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

    async def scores_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /scores command - exact score predictions"""
        try:
            await update.message.reply_text("🎯 Analyzing matches for exact score predictions...")
            
            # Get score predictions for FIFA Club World Cup
            score_summary = self.score_predictor.get_score_predictions_summary('soccer_fifa_club_world_cup')
            
            if score_summary:
                await update.message.reply_text(score_summary, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(
                    "No exact score predictions available right now. Try again later for upcoming matches!"
                )
                
        except Exception as e:
            logger.error(f"Error in scores command: {e}")
            await update.message.reply_text(
                "Sorry, couldn't generate score predictions at the moment. Please try again later."
            )
async def advanced_predictions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /advanced command - enhanced predictions"""
    try:
        await update.message.reply_text("🔬 Running advanced analysis...")
        
        predictions = self.advanced_engine.generate_enhanced_predictions('soccer_fifa_club_world_cup')
        if predictions:
            message = "🎯 **ADVANCED PREDICTIONS**\n\n"
            for i, pred in enumerate(predictions[:3], 1):
                message += f"{i}. **{pred['home_team']} vs {pred['away_team']}**\n"
                message += f"   🎲 Bet: {pred['recommended_team']} @ {pred['best_odds']:.2f}\n"
                message += f"   📊 Confidence: {pred['confidence']:.0f}%\n"
                message += f"   💰 Expected Value: {pred['expected_value']:.3f}\n\n"
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("No high-value opportunities found.")
    except Exception as e:
        await update.message.reply_text("Error generating advanced predictions.")

async def track_bet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /trackbet command"""
    try:
        if not context.args or len(context.args) < 4:
            await update.message.reply_text(
                "Usage: `/trackbet [sport] [team] [odds] [stake]`\n"
                "Example: `/trackbet soccer ManCity 1.50 10`"
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
            f"🎰 Potential: £{(odds * stake):.2f}"
        )
    except:
        await update.message.reply_text("❌ Invalid format. Use: /trackbet sport team odds stake")

async def my_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mystats command"""
    try:
        summary = self.betting_tracker.generate_performance_summary()
        await update.message.reply_text(summary, parse_mode=ParseMode.MARKDOWN)
    except:
        await update.message.reply_text("Error retrieving statistics.")
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
**Sports Betting Bot Help**

**Simple Commands:**
/today - See all games today
/predictions - FIFA World Cup predictions
/scores - Exact score predictions
/odds - Current FIFA World Cup odds

**How it works:**
Analyzes live odds from multiple bookmakers to find the best betting opportunities with confidence ratings.

**Available Sports:**
FIFA Club World Cup, MLB, NBA, NFL, NHL, Premier League

Use /start to see sport buttons or /sports for the full list.
"""
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.message:
            await update.message.reply_text(
                "❌ An unexpected error occurred. Please try again later.\n"
                "If the problem persists, use /help for guidance."
            )
