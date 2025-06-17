from datetime import datetime, timezone
import re

def format_odds_display(odds: float) -> str:
    """Format odds for display"""
    if odds >= 2.0:
        return f"{odds:.2f}"
    else:
        return f"{odds:.2f}"

def format_datetime(iso_string: str) -> str:
    """Format ISO datetime string for display"""
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return dt.strftime("%m/%d %H:%M UTC")
    except:
        return iso_string

def format_percentage(value: float) -> str:
    """Format percentage for display"""
    return f"{value:.1f}%"

def truncate_text(text: str, max_length: int = 30) -> str:
    """Truncate text to fit in messages"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def format_game_summary(game: dict) -> str:
    """Format a game summary for display"""
    home = truncate_text(game.get('home_team', 'Home'))
    away = truncate_text(game.get('away_team', 'Away'))
    time = format_datetime(game.get('commence_time', ''))
    
    return f"{away} @ {home}\n🕐 {time}"

def format_prediction_message(prediction: dict) -> str:
    """Format prediction for Telegram message"""
    rec = prediction['recommendation']
    
    message = f"🎯 **PREDICTION**\n"
    message += f"🏟️ {prediction['away_team']} @ {prediction['home_team']}\n"
    message += f"🕐 {format_datetime(prediction['commence_time'])}\n\n"
    
    message += f"💰 **BET ON**: {rec['bet_on']}\n"
    message += f"📊 **ODDS**: {format_odds_display(rec['odds'])}\n"
    message += f"🎯 **CONFIDENCE**: {rec['confidence']:.1f}%\n"
    message += f"⭐ **VALUE SCORE**: {rec['value_score']}\n\n"
    
    message += f"💡 **REASONING**:\n{rec['reasoning']}\n\n"
    
    # Add team analysis
    message += "📈 **ODDS ANALYSIS**:\n"
    for team, stats in prediction['all_teams_analysis'].items():
        message += f"{truncate_text(team, 15)}: {format_odds_display(stats['avg_odds'])} ({format_percentage(stats['implied_probability'])})\n"
    
    return message

def escape_markdown(text: str) -> str:
    """Escape markdown special characters"""
    escape_chars = r'\*_`\[\]()~>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)
