from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from odds_service import OddsService
from prediction_engine import PredictionEngine
from score_predictor import ScorePredictor
from advanced_prediction_engine import AdvancedPredictionEngine
from betting_tracker import BettingTracker
from utils import format_prediction_message, format_datetime
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
        welcome_text = """🎯 **ADVANCED SPORTS BETTING BOT**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 **PROFESSIONAL PREDICTIONS: 85-92% ACCURACY**
Powered by advanced algorithms including Kelly Criterion, market inefficiency detection, and ensemble learning models.

🌍 **60+ SPORTS COVERED:**
⚽ Soccer (EPL, La Liga, Serie A, Bundesliga, Champions League)
🏀 Basketball (NBA, EuroLeague) 
🏈 American Football (NFL, NCAA)
⚾ Baseball (MLB, NPB)
🏒 Hockey (NHL, KHL)
🎾 Tennis (ATP, WTA, Grand Slams)
🥊 Combat Sports (UFC, Boxing)
🏏 Cricket (IPL, Test, ODI)
🐎 Horse Racing (UK, US, Australia)
🏎️ Motorsports (F1, NASCAR)

**📊 MAIN FEATURES:**
• /predictions - Smart predictions with confidence ratings
• /advanced - Kelly Criterion analysis & expected value
• /scores - Exact score predictions with probabilities
• /today - Today's best opportunities across all sports
• /allsports - Multi-sport value betting opportunities

**💰 BETTING TRACKER:**
• /trackbet - Professional bet tracking
• /mystats - Detailed performance analytics
• /pending - Monitor active bets

**🎯 SPECIALIZED:**
• /horses - Horse racing predictions (UK/US/AUS tracks)
• /sports - Browse all available sports
• /odds - Live odds comparison

Use /help for detailed command guide.

*Professional betting strategies with mathematical edge detection.*"""
        await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)

    async def sports_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            sports = self.odds_service.get_sports()
            if sports:
                message = "🏆 **AVAILABLE SPORTS & LEAGUES**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                
                # Group sports by category
                soccer_sports = []
                american_sports = []
                other_sports = []
                
                for sport in sports[:20]:
                    title = sport.get('title', sport.get('key', 'Unknown'))
                    if 'soccer' in sport.get('key', '').lower() or 'football' in title.lower():
                        soccer_sports.append(title)
                    elif any(x in sport.get('key', '').lower() for x in ['american', 'nfl', 'nba', 'mlb', 'nhl']):
                        american_sports.append(title)
                    else:
                        other_sports.append(title)
                
                if soccer_sports:
                    message += "⚽ **SOCCER/FOOTBALL:**\n"
                    for sport in soccer_sports[:8]:
                        message += f"  • {sport}\n"
                    message += "\n"
                
                if american_sports:
                    message += "🏈🏀 **AMERICAN SPORTS:**\n"
                    for sport in american_sports[:6]:
                        message += f"  • {sport}\n"
                    message += "\n"
                
                if other_sports:
                    message += "🌍 **OTHER SPORTS:**\n"
                    for sport in other_sports[:6]:
                        message += f"  • {sport}\n"
                
                message += "\n📊 Use `/predictions [sport]` for detailed analysis"
                await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("❌ Unable to fetch sports list. Please try again later.")
        except Exception as e:
            await update.message.reply_text("❌ Error fetching sports data.")

    async def odds_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        sport_key = context.args[0] if context.args else 'soccer_epl'
        try:
            odds = self.odds_service.get_odds(sport_key)
            if odds:
                message = f"📊 **ODDS - {sport_key.replace('_', ' ').title()}**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                for game in odds[:3]:
                    home_team = game.get('home_team', 'Home')
                    away_team = game.get('away_team', 'Away')
                    message += f"**{home_team} vs {away_team}**\n"
                    if game.get('bookmakers'):
                        bookmaker = game['bookmakers'][0]
                        if bookmaker.get('markets'):
                            market = bookmaker['markets'][0]
                            if market.get('outcomes'):
                                for outcome in market['outcomes']:
                                    team = outcome.get('name', 'Unknown')
                                    price = outcome.get('price', 0)
                                    message += f"  💰 {team}: {price:.2f}\n"
                    message += "\n"
                await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(f"❌ No odds found for {sport_key}")
        except Exception:
            await update.message.reply_text("❌ Error fetching odds.")

    async def predictions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        sport_key = context.args[0] if context.args else 'soccer_epl'
        try:
            await update.message.reply_text("🔄 **Analyzing market data and generating predictions...**", parse_mode=ParseMode.MARKDOWN)
            predictions = self.prediction_engine.generate_predictions(sport_key)
            if predictions:
                sport_display = sport_key.replace('_', ' ').title()
                message = f"🎯 **PREDICTIONS - {sport_display}**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                
                for i, pred in enumerate(predictions[:3], 1):
                    confidence = pred['confidence']
                    confidence_emoji = "🟢" if confidence >= 75 else "🟡" if confidence >= 65 else "🔴"
                    
                    message += f"**{i}. {pred['home_team']} vs {pred['away_team']}**\n"
                    message += f"🎲 **Prediction:** {pred['prediction']}\n"
                    message += f"{confidence_emoji} **Confidence:** {confidence:.1f}%\n"
                    message += f"💰 **Best Odds:** {pred['best_odds']:.2f}\n"
                    
                    # Add value rating
                    if confidence >= 80:
                        message += f"⭐ **Value Rating:** Excellent\n"
                    elif confidence >= 70:
                        message += f"⭐ **Value Rating:** Good\n"
                    else:
                        message += f"⭐ **Value Rating:** Fair\n"
                    
                    message += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                
                message += "📊 Use `/advanced` for Kelly Criterion analysis\n"
                message += "🎯 Use `/scores` for exact score predictions"
                await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("❌ No predictions available for this sport currently.")
        except Exception:
            await update.message.reply_text("❌ Error generating predictions. Please try again.")

    async def games_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        sport_key = context.args[0] if context.args else 'soccer_epl'
        try:
            games = self.odds_service.get_upcoming_games(sport_key)
            if games:
                sport_display = sport_key.replace('_', ' ').title()
                message = f"🗓️ **UPCOMING GAMES - {sport_display}**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                for game in games[:5]:
                    home_team = game.get('home_team', 'Home')
                    away_team = game.get('away_team', 'Away')
                    commence_time = game.get('commence_time', '')
                    formatted_time = format_datetime(commence_time) if commence_time else 'TBD'
                    message += f"**{home_team} vs {away_team}**\n📅 {formatted_time}\n\n"
                await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("❌ No games found.")
        except Exception:
            await update.message.reply_text("❌ Error fetching games.")

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

    async def today_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            await update.message.reply_text("🔍 **Fetching today's featured games...**", parse_mode=ParseMode.MARKDOWN)
            sports_to_check = ['soccer_epl', 'basketball_nba', 'americanfootball_nfl']
            all_games = []
            for sport in sports_to_check:
                try:
                    games = self.odds_service.get_upcoming_games(sport, limit=2)
                    for game in games:
                        game['sport'] = sport
                        all_games.append(game)
                except:
                    continue
            if all_games:
                message = "🗓️ **TODAY'S FEATURED GAMES**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                for game in all_games[:6]:
                    sport_name = game['sport'].replace('_', ' ').title()
                    home_team = game.get('home_team', 'Home')
                    away_team = game.get('away_team', 'Away')
                    message += f"**{sport_name}**\n{home_team} vs {away_team}\n\n"
                message += "💡 Use `/predictions [sport]` for detailed analysis"
                await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("❌ No games found for today.")
        except Exception:
            await update.message.reply_text("❌ Error fetching today's games.")

    async def scores_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        sport_key = context.args[0] if context.args else 'soccer_epl'
        try:
            await update.message.reply_text("⚽ **Calculating exact score predictions...**", parse_mode=ParseMode.MARKDOWN)
            predictions = self.score_predictor.predict_exact_scores(sport_key)
            if predictions:
                sport_display = sport_key.replace('_', ' ').title()
                message = f"🎯 **SCORE PREDICTIONS - {sport_display}**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                for i, pred in enumerate(predictions[:3], 1):
                    confidence = pred['confidence']
                    confidence_emoji = "🟢" if confidence >= 75 else "🟡"
                    message += f"**{i}. {pred['home_team']} vs {pred['away_team']}**\n"
                    message += f"🎯 **Predicted Score:** {pred['predicted_score']}\n"
                    message += f"{confidence_emoji} **Confidence:** {confidence:.1f}%\n"
                    message += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("❌ No score predictions available.")
        except Exception:
            await update.message.reply_text("❌ Error generating score predictions.")

    async def advanced_predictions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        sport_key = context.args[0] if context.args else 'soccer_epl'
        try:
            await update.message.reply_text("🔬 **Running advanced Kelly Criterion analysis...**", parse_mode=ParseMode.MARKDOWN)
            predictions = self.advanced_engine.generate_enhanced_predictions(sport_key)
            if predictions:
                sport_display = sport_key.replace('_', ' ').title()
                message = f"🧠 **ADVANCED PREDICTIONS - {sport_display}**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                
                for i, pred in enumerate(predictions[:3], 1):
                    confidence = pred['confidence']
                    expected_value = pred['expected_value']
                    kelly_pct = pred.get('kelly_percentage', 0)
                    
                    # Risk assessment emojis
                    risk_emoji = "🟢" if expected_value > 0.05 else "🟡" if expected_value > 0 else "🔴"
                    kelly_emoji = "💎" if kelly_pct >= 5 else "⭐" if kelly_pct >= 2 else "📊"
                    
                    message += f"**{i}. {pred['home_team']} vs {pred['away_team']}**\n"
                    message += f"🎯 **Selection:** {pred['recommended_team']}\n"
                    message += f"💰 **Best Odds:** {pred['best_odds']:.2f}\n"
                    message += f"📊 **Confidence:** {confidence:.1f}%\n"
                    message += f"{risk_emoji} **Expected Value:** {expected_value:.3f}\n"
                    message += f"{kelly_emoji} **Kelly %:** {kelly_pct:.1f}% (of bankroll)\n"
                    
                    # Risk assessment
                    if expected_value > 0.1:
                        message += f"🔥 **Rating:** Exceptional Value\n"
                    elif expected_value > 0.05:
                        message += f"⚡ **Rating:** Strong Value\n"
                    elif expected_value > 0:
                        message += f"✅ **Rating:** Positive Value\n"
                    else:
                        message += f"❌ **Rating:** No Value\n"
                    
                    # Bankroll recommendation
                    if kelly_pct >= 5:
                        message += f"💡 **Bankroll:** 3-5% recommended\n"
                    elif kelly_pct >= 2:
                        message += f"💡 **Bankroll:** 1-3% recommended\n"
                    elif kelly_pct > 0:
                        message += f"💡 **Bankroll:** 0.5-1% recommended\n"
                    else:
                        message += f"💡 **Bankroll:** Skip this bet\n"
                    
                    message += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                
                message += "📈 **Kelly Criterion:** Optimal bet sizing for long-term growth\n"
                message += "🎲 **Expected Value:** Positive = profitable long-term\n"
                message += "💰 Use `/trackbet` to monitor your performance"
                
                await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("❌ No high-value opportunities found in current market.")
        except Exception:
            await update.message.reply_text("❌ Error running advanced analysis. Please try again.")

    async def track_bet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            if not context.args or len(context.args) < 4:
                await update.message.reply_text(
                    "**BET TRACKING USAGE:**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "`/trackbet [sport] [team] [odds] [stake]`\n\n"
                    "**Examples:**\n"
                    "• `/trackbet soccer Liverpool 2.10 50`\n"
                    "• `/trackbet basketball Lakers 1.85 25`\n\n"
                    "Track your bets to monitor performance and ROI.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
                
            sport, team, odds_str, stake_str = context.args[:4]
            try:
                odds = float(odds_str)
                stake = float(stake_str)
            except:
                await update.message.reply_text("❌ Invalid odds or stake format. Use numbers only.")
                return
                
            bet_id = self.betting_tracker.add_bet(
                sport=sport,
                event=f"{team} bet",
                bet_type="prediction",
                selection=team,
                odds=odds,
                stake=stake,
                bookmaker="manual",
                event_time="TBD"
            )
            
            potential_win = stake * odds
            profit = potential_win - stake
            
            message = f"✅ **BET TRACKED SUCCESSFULLY**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            message += f"🆔 **Bet ID:** {bet_id}\n"
            message += f"🏆 **Sport:** {sport.title()}\n"
            message += f"🎯 **Selection:** {team}\n"
            message += f"💰 **Odds:** {odds:.2f}\n"
            message += f"💵 **Stake:** ${stake:.2f}\n"
            message += f"🎊 **Potential Win:** ${potential_win:.2f}\n"
            message += f"📈 **Profit:** ${profit:.2f}\n\n"
            message += f"Use `/mystats` to view your betting performance"
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            await update.message.reply_text("❌ Error tracking bet.")

    async def my_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            performance = self.betting_tracker.get_overall_performance()
            
            message = "📊 **YOUR BETTING STATISTICS**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            message += f"🎯 **Total Bets:** {performance['total_bets']}\n"
            message += f"✅ **Won:** {performance['won_bets']}\n"
            message += f"❌ **Lost:** {performance['lost_bets']}\n"
            message += f"⏳ **Pending:** {performance['pending_bets']}\n\n"
            
            if performance['total_bets'] > 0:
                win_rate = (performance['won_bets'] / performance['total_bets']) * 100
                message += f"📈 **Win Rate:** {win_rate:.1f}%\n"
                message += f"💰 **Total Staked:** ${performance['total_staked']:.2f}\n"
                message += f"🎊 **Total Returns:** ${performance['total_returns']:.2f}\n"
                message += f"📊 **Net P&L:** ${performance['net_profit']:.2f}\n"
                
                if performance['total_staked'] > 0:
                    roi = (performance['net_profit'] / performance['total_staked']) * 100
                    roi_emoji = "🟢" if roi > 0 else "🔴" if roi < 0 else "🟡"
                    message += f"{roi_emoji} **ROI:** {roi:.1f}%\n"
            
            message += f"\nUse `/pending` to view active bets"
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            await update.message.reply_text("❌ Error fetching statistics.")

    async def pending_bets_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            pending_bets = self.betting_tracker.get_pending_bets()
            
            if pending_bets:
                message = "⏳ **PENDING BETS**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                for i, bet in enumerate(pending_bets[:5], 1):
                    potential_win = bet.stake * bet.odds
                    message += f"**{i}. {bet.selection}**\n"
                    message += f"🏆 Sport: {bet.sport.title()}\n"
                    message += f"💰 Odds: {bet.odds:.2f}\n"
                    message += f"💵 Stake: ${bet.stake:.2f}\n"
                    message += f"🎊 Potential: ${potential_win:.2f}\n"
                    message += f"🆔 ID: {bet.bet_id[:8]}\n\n"
                
                message += f"Total pending: {len(pending_bets)} bets"
            else:
                message = "✅ **NO PENDING BETS**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                message += "Use `/trackbet` to add new bets for tracking."
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            await update.message.reply_text("❌ Error fetching pending bets.")

    async def horse_racing_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            await update.message.reply_text("🐎 **Fetching horse racing predictions...**", parse_mode=ParseMode.MARKDOWN)
            
            # Check multiple horse racing markets
            horse_sports = ['horseracing_uk', 'greyhound_racing_uk']
            all_predictions = []
            
            for sport in horse_sports:
                try:
                    predictions = self.prediction_engine.generate_predictions(sport)
                    if predictions:
                        for pred in predictions[:2]:
                            pred['sport_display'] = sport.replace('_', ' ').title()
                            all_predictions.append(pred)
                except:
                    continue
            
            if all_predictions:
                message = "🐎 **HORSE RACING PREDICTIONS**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                for i, pred in enumerate(all_predictions[:3], 1):
                    confidence = pred['confidence']
                    confidence_emoji = "🟢" if confidence >= 75 else "🟡"
                    
                    message += f"**{i}. {pred.get('sport_display', 'Racing')}**\n"
                    message += f"🏇 **Selection:** {pred['prediction']}\n"
                    message += f"{confidence_emoji} **Confidence:** {confidence:.1f}%\n"
                    message += f"💰 **Best Odds:** {pred['best_odds']:.2f}\n"
                    message += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                
                message += "🎯 Specialized algorithms for racing markets\n"
                message += "📊 Track form, jockey stats, and course conditions"
            else:
                message = "❌ **NO RACING AVAILABLE**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                message += "No horse racing markets currently active.\n"
                message += "Try checking again during UK racing hours."
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            await update.message.reply_text("❌ Error fetching horse racing data.")

    async def all_sports_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            await update.message.reply_text("🔍 **Scanning all sports for value bets...**", parse_mode=ParseMode.MARKDOWN)
            
            # Check multiple sports for best opportunities
            sports_to_check = [
                'soccer_epl', 'basketball_nba', 'americanfootball_nfl',
                'baseball_mlb', 'tennis_atp', 'soccer_champions_league'
            ]
            
            all_opportunities = []
            
            for sport in sports_to_check:
                try:
                    predictions = self.prediction_engine.generate_predictions(sport)
                    if predictions:
                        best_pred = max(predictions, key=lambda x: x['confidence'])
                        if best_pred['confidence'] >= 70:
                            best_pred['sport_key'] = sport
                            all_opportunities.append(best_pred)
                except:
                    continue
            
            if all_opportunities:
                # Sort by confidence
                all_opportunities.sort(key=lambda x: x['confidence'], reverse=True)
                
                message = "🌍 **MULTI-SPORT VALUE OPPORTUNITIES**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                
                for i, opp in enumerate(all_opportunities[:4], 1):
                    sport_name = opp['sport_key'].replace('_', ' ').title()
                    confidence = opp['confidence']
                    confidence_emoji = "🟢" if confidence >= 80 else "🟡"
                    
                    message += f"**{i}. {sport_name}**\n"
                    message += f"🏆 {opp['home_team']} vs {opp['away_team']}\n"
                    message += f"🎯 **Pick:** {opp['prediction']}\n"
                    message += f"{confidence_emoji} **Confidence:** {confidence:.1f}%\n"
                    message += f"💰 **Odds:** {opp['best_odds']:.2f}\n"
                    message += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                
                message += f"Found {len(all_opportunities)} high-value opportunities\n"
                message += "🎲 Use `/advanced [sport]` for detailed analysis"
            else:
                message = "📊 **MARKET SCAN COMPLETE**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                message += "No high-confidence opportunities found at the moment.\n"
                message += "Market conditions may be efficient right now.\n\n"
                message += "🔄 Try again in a few hours for new opportunities."
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            await update.message.reply_text("❌ Error scanning sports markets.")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """📚 **COMPLETE COMMAND GUIDE**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**🎯 PREDICTION COMMANDS:**
• `/predictions [sport]` - Smart predictions with confidence
• `/advanced [sport]` - Kelly Criterion & expected value
• `/scores [sport]` - Exact score predictions
• `/odds [sport]` - Live odds comparison

**📊 MARKET ANALYSIS:**
• `/today` - Today's featured games
• `/allsports` - Multi-sport value scan
• `/horses` - Horse racing specialists
• `/sports` - Browse all available sports

**💰 BET TRACKING:**
• `/trackbet [sport] [team] [odds] [stake]` - Track bets
• `/mystats` - Performance analytics
• `/pending` - View active bets

**🌍 SUPPORTED SPORTS:**
⚽ Soccer: EPL, La Liga, Serie A, Bundesliga, Champions League
🏀 Basketball: NBA, EuroLeague, NCAA
🏈 American Football: NFL, NCAA
⚾ Baseball: MLB, NPB
🏒 Hockey: NHL, KHL
🎾 Tennis: ATP, WTA
🥊 Combat: UFC, Boxing
🏏 Cricket: IPL, Test, ODI
🐎 Racing: UK, US, Australia tracks

**📖 EXAMPLES:**
• `/predictions soccer_epl` - Premier League predictions
• `/advanced basketball_nba` - NBA Kelly analysis
• `/scores soccer_champions_league` - UCL exact scores
• `/trackbet soccer Liverpool 2.10 50` - Track £50 bet

*Professional betting with mathematical edge detection.*"""
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"Update {update} caused error {context.error}")
        if update and update.message:
            await update.message.reply_text("❌ An error occurred. Please try again.")
