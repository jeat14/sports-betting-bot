"""
Simplified Score Prediction Engine for Heroku Deployment
"""

import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime
import os
import statistics

logger = logging.getLogger(__name__)

class ScorePredictor:
    def __init__(self):
        self.odds_api_key = os.getenv('ODDS_API_KEY')
        self.base_url = "https://api.the-odds-api.com/v4"
        
    def predict_exact_scores(self, sport_key: str) -> List[Dict]:
        """Generate exact score predictions for upcoming games"""
        try:
            if not self.odds_api_key:
                logger.error("No API key found")
                return []
            
            games = self._get_upcoming_games(sport_key)
            if not games:
                return []
            
            predictions = []
            
            for game in games:
                prediction = self._analyze_game_simple(game)
                if prediction:
                    predictions.append(prediction)
            
            # Sort by date - today's games first
            today = datetime.now().date()
            
            def sort_key(pred):
                try:
                    pred_date = datetime.fromisoformat(pred['commence_time'].replace('Z', '+00:00')).date()
                    is_today = pred_date == today
                    return (not is_today, -pred['confidence'])
                except:
                    return (True, -pred.get('confidence', 0))
            
            sorted_predictions = sorted(predictions, key=sort_key)[:5]
            return sorted_predictions
            
        except Exception as e:
            logger.error(f"Error generating score predictions: {e}")
            return []
    
    def _get_upcoming_games(self, sport_key: str) -> List[Dict]:
        """Fetch upcoming games"""
        try:
            url = f"{self.base_url}/sports/{sport_key}/odds"
            params = {
                'apiKey': self.odds_api_key,
                'regions': 'us,uk,au',
                'markets': 'h2h',
                'oddsFormat': 'decimal',
                'dateFormat': 'iso'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            games = response.json()
            
            if not games:
                return []
            
            # Filter upcoming games
            today = datetime.now().date()
            upcoming_games = []
            
            for game in games:
                try:
                    commence_time = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00'))
                    game_date = commence_time.date()
                    
                    if game_date >= today:
                        upcoming_games.append(game)
                except:
                    continue
            
            return upcoming_games[:10]
            
        except Exception as e:
            logger.error(f"Error fetching games: {e}")
            return []
    
    def _analyze_game_simple(self, game: Dict) -> Optional[Dict]:
        """Simple game analysis that's less likely to fail"""
        try:
            home_team = game['home_team']
            away_team = game['away_team']
            commence_time = game['commence_time']
            
            # Extract basic odds
            home_odds, away_odds = self._get_basic_odds(game)
            
            if not home_odds or not away_odds:
                return None
            
            # Calculate probabilities
            home_prob = 1 / home_odds if home_odds > 0 else 0.5
            away_prob = 1 / away_odds if away_odds > 0 else 0.5
            
            # Normalize probabilities
            total_prob = home_prob + away_prob
            if total_prob > 0:
                home_prob = home_prob / total_prob
                away_prob = away_prob / total_prob
            else:
                home_prob = away_prob = 0.5
            
            # Simple score prediction based on probabilities
            if home_prob > 0.6:
                home_goals, away_goals = 2, 0
                confidence = 75
            elif home_prob > 0.55:
                home_goals, away_goals = 2, 1
                confidence = 70
            elif away_prob > 0.6:
                home_goals, away_goals = 0, 2
                confidence = 75
            elif away_prob > 0.55:
                home_goals, away_goals = 1, 2
                confidence = 70
            else:
                home_goals, away_goals = 1, 1
                confidence = 65
            
            # Generate alternative scores
            alternatives = self._get_simple_alternatives(home_goals, away_goals)
            
            return {
                'home_team': home_team,
                'away_team': away_team,
                'commence_time': commence_time,
                'predicted_score': f"{home_goals}-{away_goals}",
                'home_goals': home_goals,
                'away_goals': away_goals,
                'confidence': confidence,
                'alternative_scores': alternatives,
                'total_goals': home_goals + away_goals,
                'prediction_reasoning': f"Based on odds analysis: {home_team} ({home_odds:.2f}) vs {away_team} ({away_odds:.2f})",
                'home_probability': round(home_prob * 100, 1),
                'away_probability': round(away_prob * 100, 1)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing game: {e}")
            return None
    
    def _get_basic_odds(self, game: Dict) -> tuple:
        """Extract basic h2h odds"""
        try:
            bookmakers = game.get('bookmakers', [])
            home_odds_list = []
            away_odds_list = []
            
            for bookmaker in bookmakers:
                for market in bookmaker.get('markets', []):
                    if market['key'] == 'h2h':
                        outcomes = market['outcomes']
                        for outcome in outcomes:
                            if outcome['name'] == game['home_team']:
                                home_odds_list.append(outcome['price'])
                            elif outcome['name'] == game['away_team']:
                                away_odds_list.append(outcome['price'])
            
            if home_odds_list and away_odds_list:
                return statistics.mean(home_odds_list), statistics.mean(away_odds_list)
            
            return None, None
            
        except Exception as e:
            logger.error(f"Error extracting odds: {e}")
            return None, None
    
    def _get_simple_alternatives(self, home_goals: int, away_goals: int) -> List[Dict]:
        """Generate simple alternative scores"""
        alternatives = [
            {'score': f"{home_goals}-{away_goals}", 'probability': 25},
            {'score': f"{max(0, home_goals-1)}-{away_goals}", 'probability': 20},
            {'score': f"{home_goals}-{max(0, away_goals-1)}", 'probability': 20},
            {'score': f"{home_goals+1}-{away_goals}", 'probability': 15},
            {'score': f"{home_goals}-{away_goals+1}", 'probability': 15}
        ]
        
        # Remove duplicates
        seen = set()
        unique_alternatives = []
        for alt in alternatives:
            if alt['score'] not in seen:
                seen.add(alt['score'])
                unique_alternatives.append(alt)
        
        return unique_alternatives[:4]
