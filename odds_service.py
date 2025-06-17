import requests
import time
from typing import Dict, List, Optional
from config import ODDS_API_KEY, ODDS_API_BASE_URL, SPORTS, MARKETS, API_CALL_DELAY
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OddsService:
    def __init__(self):
        self.api_key = ODDS_API_KEY
        self.base_url = ODDS_API_BASE_URL
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Implement rate limiting to avoid API quota issues"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < API_CALL_DELAY:
            time.sleep(API_CALL_DELAY - time_since_last_request)
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with error handling"""
        self._rate_limit()
        
        url = f"{self.base_url}/{endpoint}"
        default_params = {'apiKey': self.api_key}
        if params:
            default_params.update(params)
        
        try:
            response = requests.get(url, params=default_params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
    
    def get_sports(self) -> List[Dict]:
        """Get list of available sports"""
        data = self._make_request("sports")
        if data:
            # Filter to only sports we support
            return [sport for sport in data if sport['key'] in SPORTS.keys()]
        return []
    
    def get_odds(self, sport_key: str, market: str = 'h2h') -> Optional[List[Dict]]:
        """Get odds for a specific sport and market"""
        params = {
            'sport': sport_key,
            'regions': 'us,eu',
            'markets': market,
            'oddsFormat': 'decimal',
            'dateFormat': 'iso'
        }
        
        data = self._make_request("sports/{}/odds".format(sport_key), params)
        return data if data else []
    
    def get_upcoming_games(self, sport_key: str, limit: int = 5) -> List[Dict]:
        """Get upcoming and live games for a sport within next 48 hours"""
        odds_data = self.get_odds(sport_key)
        if not odds_data:
            return []
        
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        past_limit = now - timedelta(hours=3)  # Include games that started up to 3 hours ago (live)
        future_limit = now + timedelta(hours=48)
        
        # Filter games happening from 3 hours ago to 48 hours in future
        relevant_games = []
        for game in odds_data:
            try:
                game_time = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00'))
                if past_limit <= game_time <= future_limit:
                    relevant_games.append(game)
            except:
                continue
        
        # Sort by commence time and limit results
        sorted_games = sorted(relevant_games, key=lambda x: x.get('commence_time', ''))
        return sorted_games[:limit]
    
    def get_best_odds(self, sport_key: str) -> List[Dict]:
        """Get games with the best odds analysis"""
        games = self.get_upcoming_games(sport_key, 10)
        best_odds_games = []
        
        for game in games:
            if not game.get('bookmakers'):
                continue
                
            # Analyze odds from different bookmakers
            odds_analysis = self._analyze_game_odds(game)
            if odds_analysis:
                game['odds_analysis'] = odds_analysis
                best_odds_games.append(game)
        
        # Sort by confidence score
        best_odds_games.sort(key=lambda x: x['odds_analysis']['confidence'], reverse=True)
        return best_odds_games[:5]
    
    def _analyze_game_odds(self, game: Dict) -> Optional[Dict]:
        """Analyze odds for a single game"""
        bookmakers = game.get('bookmakers', [])
        if not bookmakers:
            return None
        
        # Collect all odds for head-to-head market
        h2h_odds = []
        for bookmaker in bookmakers:
            for market in bookmaker.get('markets', []):
                if market['key'] == 'h2h':
                    h2h_odds.append(market['outcomes'])
        
        if not h2h_odds:
            return None
        
        # Calculate average odds and find discrepancies
        team_odds = {}
        for outcomes in h2h_odds:
            for outcome in outcomes:
                team = outcome['name']
                price = float(outcome['price'])
                if team not in team_odds:
                    team_odds[team] = []
                team_odds[team].append(price)
        
        # Calculate average odds and variance
        analysis = {}
        for team, odds_list in team_odds.items():
            avg_odds = sum(odds_list) / len(odds_list)
            variance = sum((x - avg_odds) ** 2 for x in odds_list) / len(odds_list)
            analysis[team] = {
                'avg_odds': round(avg_odds, 2),
                'variance': round(variance, 4),
                'implied_probability': round(1 / avg_odds * 100, 2)
            }
        
        # Calculate confidence based on odds stability and value
        total_prob = sum(team['implied_probability'] for team in analysis.values())
        if total_prob > 0:
            confidence = max(0, min(100, (110 - total_prob) * 2))  # Higher confidence when total prob < 100%
        else:
            confidence = 0
        
        return {
            'teams': analysis,
            'confidence': round(confidence, 1),
            'total_implied_probability': round(total_prob, 2)
        }
