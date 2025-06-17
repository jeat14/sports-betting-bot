import os

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7816965212:AAHFQfvvbjFtmRajS2wFLTiJZeKOfEzo7C0")

# Odds API Configuration
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "b042ef3e00a923abda5dade83334ec20")
ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"

# Supported Sports (active leagues with frequent games)
SPORTS = {
    'soccer_fifa_club_world_cup': 'FIFA Club World Cup',
    'baseball_mlb': 'MLB Baseball',
    'basketball_nba': 'NBA Basketball',
    'americanfootball_nfl': 'NFL Football',
    'icehockey_nhl': 'NHL Hockey',
    'soccer_usa_mls': 'MLS Soccer',
    'soccer_italy_serie_a': 'Serie A (Italy)',
    'soccer_spain_la_liga': 'La Liga (Spain)',
    'soccer_germany_bundesliga': 'Bundesliga (Germany)',
    'soccer_england_league1': 'League One (England)',
    'soccer_epl': 'Premier League',
    'americanfootball_ncaaf': 'College Football',
    'basketball_ncaab': 'College Basketball'
}

# Betting Markets
MARKETS = [
    'h2h',  # Head to head (moneyline)
    'spreads',  # Point spreads
    'totals'  # Over/under totals
]

# Rate limiting
API_CALL_DELAY = 1  # seconds between API calls
MAX_GAMES_PER_REQUEST = 10
