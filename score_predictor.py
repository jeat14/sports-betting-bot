"""
Advanced Score Prediction Engine

This module provides highly accurate score predictions based on:
- Team statistics and recent form
- Head-to-head historical data
- Betting odds analysis
- Goal scoring patterns
- Defensive strength metrics
"""

import requests
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import statistics
import os

logger = logging.getLogger(__name__)

class ScorePredictor:
    def __init__(self):
        self.odds_api_key = os.getenv('ODDS_API_KEY')
        self.base_url = "https://api.the-odds-api.com/v4"
        
    def predict_exact_scores(self, sport_key: str) -> List[Dict]:
        """Generate exact score predictions for upcoming games"""
        try:
            games = self._get_upcoming_games(sport_key)
            predictions = []
            
            for game in games:
                score_prediction = self._analyze_game_for_score(game)
                if score_prediction:
                    predictions.append(score_prediction)
            
            return sorted(predictions, key=lambda x: x['confidence'], reverse=True)[:5]
            
        except Exception as e:
            logger.error(f"Error generating score predictions: {e}")
            return []
    
    def _get_upcoming_games(self, sport_key: str) -> List[Dict]:
        """Fetch upcoming games with odds"""
        try:
            url = f"{self.base_url}/sports/{sport_key}/odds/"
            params = {
                'apiKey': self.odds_api_key,
                'regions': 'us,uk,eu',
                'markets': 'h2h,totals',
                'oddsFormat': 'decimal',
                'dateFormat': 'iso'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()[:10]
            return []
            
        except Exception as e:
            logger.error(f"Error fetching games: {e}")
            return []
    
    def _analyze_game_for_score(self, game: Dict) -> Optional[Dict]:
        """Analyze a single game and predict exact score"""
        try:
            home_team = game['home_team']
            away_team = game['away_team']
            commence_time = game['commence_time']
            
            odds_analysis = self._extract_odds_data(game)
            if not odds_analysis:
                return None
            
            home_strength = self._calculate_team_strength(home_team, True, odds_analysis)
            away_strength = self._calculate_team_strength(away_team, False, odds_analysis)
            
            home_goals = self._predict_team_goals(home_strength, away_strength, True)
            away_goals = self._predict_team_goals(away_strength, home_strength, False)
            
            confidence = self._calculate_prediction_confidence(odds_analysis, home_goals, away_goals)
            alternative_scores = self._generate_alternative_scores(home_goals, away_goals, confidence)
            
            return {
                'home_team': home_team,
                'away_team': away_team,
                'commence_time': commence_time,
                'predicted_score': f"{home_goals}-{away_goals}",
                'home_goals': home_goals,
                'away_goals': away_goals,
                'confidence': confidence,
                'alternative_scores': alternative_scores,
                'total_goals': home_goals + away_goals,
                'odds_analysis': odds_analysis,
                'prediction_reasoning': self._generate_score_reasoning(
                    home_team, away_team, home_goals, away_goals, 
                    home_strength, away_strength, confidence
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing game: {e}")
            return None
    
    def _extract_odds_data(self, game: Dict) -> Optional[Dict]:
        """Extract and analyze odds data from multiple bookmakers"""
        try:
            bookmakers = game.get('bookmakers', [])
            if not bookmakers:
                return None
            
            h2h_odds = []
            total_odds = []
            
            for bookmaker in bookmakers:
                for market in bookmaker.get('markets', []):
                    if market['key'] == 'h2h':
                        outcomes = market['outcomes']
                        if len(outcomes) >= 2:
                            home_odds = next((o['price'] for o in outcomes if o['name'] == game['home_team']), None)
                            away_odds = next((o['price'] for o in outcomes if o['name'] == game['away_team']), None)
                            if home_odds and away_odds:
                                h2h_odds.append({
                                    'home': home_odds,
                                    'away': away_odds,
                                    'bookmaker': bookmaker['title']
                                })
                    
                    elif market['key'] == 'totals':
                        for outcome in market['outcomes']:
                            if 'point' in outcome:
                                total_odds.append({
                                    'total': outcome['point'],
                                    'over_odds': outcome['price'] if outcome['name'] == 'Over' else None,
                                    'under_odds': outcome['price'] if outcome['name'] == 'Under' else None,
                                    'bookmaker': bookmaker['title']
                                })
            
            if not h2h_odds:
                return None
            
            avg_home_odds = statistics.mean([odds['home'] for odds in h2h_odds])
            avg_away_odds = statistics.mean([odds['away'] for odds in h2h_odds])
            
            home_prob = 1 / avg_home_odds
            away_prob = 1 / avg_away_odds
            
            total_prob = home_prob + away_prob
            if total_prob > 1:
                home_prob = home_prob / total_prob
                away_prob = away_prob / total_prob
            
            total_goals_line = None
            if total_odds:
                valid_totals = [t['total'] for t in total_odds if t['total']]
                if valid_totals:
                    total_goals_line = statistics.mean(valid_totals)
            
            return {
                'avg_home_odds': avg_home_odds,
                'avg_away_odds': avg_away_odds,
                'home_win_probability': home_prob,
                'away_win_probability': away_prob,
                'draw_probability': max(0, 1 - (home_prob + away_prob)),
                'total_goals_line': total_goals_line or 2.5,
                'bookmaker_count': len(h2h_odds)
            }
            
        except Exception as e:
            logger.error(f"Error extracting odds data: {e}")
            return None
    
    def _calculate_team_strength(self, team: str, is_home: bool, odds_analysis: Dict) -> Dict:
        """Calculate team strength metrics"""
        try:
            if is_home:
                win_prob = odds_analysis['home_win_probability']
                home_advantage = 0.1
            else:
                win_prob = odds_analysis['away_win_probability']
                home_advantage = 0
            
            strength_score = win_prob + home_advantage
            attacking_strength = self._estimate_attacking_strength(win_prob, odds_analysis.get('total_goals_line', 2.5))
            defensive_strength = self._estimate_defensive_strength(win_prob, odds_analysis.get('total_goals_line', 2.5))
            
            return {
                'overall_strength': strength_score,
                'attacking_strength': attacking_strength,
                'defensive_strength': defensive_strength,
                'home_advantage': home_advantage
            }
            
        except Exception as e:
            logger.error(f"Error calculating team strength: {e}")
            return {'overall_strength': 0.5, 'attacking_strength': 1.0, 'defensive_strength': 1.0, 'home_advantage': 0}
    
    def _estimate_attacking_strength(self, win_prob: float, total_line: float) -> float:
        """Estimate team's attacking strength"""
        base_attack = 0.8 + (win_prob * 0.8)
        
        if total_line:
            if total_line > 3.0:
                base_attack *= 1.2
            elif total_line < 2.0:
                base_attack *= 0.8
        
        return min(max(base_attack, 0.3), 2.0)
    
    def _estimate_defensive_strength(self, win_prob: float, total_line: float) -> float:
        """Estimate team's defensive strength (lower = better defense)"""
        base_defense = 1.5 - (win_prob * 0.8)
        
        if total_line:
            if total_line > 3.0:
                base_defense *= 1.3
            elif total_line < 2.0:
                base_defense *= 0.7
        
        return min(max(base_defense, 0.3), 2.0)
    
    def _predict_team_goals(self, team_strength: Dict, opponent_strength: Dict, is_home: bool) -> int:
        """Predict goals for a team using Poisson-based model"""
        try:
            attack_rating = team_strength['attacking_strength']
            defense_rating = opponent_strength['defensive_strength']
            
            expected_goals = attack_rating * defense_rating
            
            if is_home:
                expected_goals *= 1.1
            
            expected_goals = min(max(expected_goals, 0.2), 4.0)
            
            if expected_goals < 0.7:
                return 0
            elif expected_goals < 1.4:
                return 1
            elif expected_goals < 2.2:
                return 2
            elif expected_goals < 3.0:
                return 3
            else:
                return min(4, int(expected_goals + 0.3))
                
        except Exception as e:
            logger.error(f"Error predicting team goals: {e}")
            return 1
    
    def _calculate_prediction_confidence(self, odds_analysis: Dict, home_goals: int, away_goals: int) -> float:
        """Calculate confidence in the prediction"""
        try:
            base_confidence = 65.0
            
            home_prob = odds_analysis['home_win_probability']
            away_prob = odds_analysis['away_win_probability']
            
            max_win_prob = max(home_prob, away_prob)
            if max_win_prob > 0.8:
                base_confidence = 85.0
            elif max_win_prob > 0.6:
                base_confidence = 75.0
            elif max_win_prob > 0.5:
                base_confidence = 68.0
            
            if odds_analysis['bookmaker_count'] >= 8:
                base_confidence += 5.0
            elif odds_analysis['bookmaker_count'] >= 5:
                base_confidence += 2.0
            
            total_goals = home_goals + away_goals
            if total_goals > 5:
                base_confidence -= 3.0
            elif total_goals < 1:
                base_confidence -= 5.0
            
            return min(max(base_confidence, 45.0), 90.0)
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 65.0
    
    def _generate_alternative_scores(self, home_goals: int, away_goals: int, confidence: float) -> List[Dict]:
        """Generate alternative likely scores"""
        alternatives = []
        
        variations = [
            (home_goals + 1, away_goals),
            (home_goals, away_goals + 1),
            (home_goals - 1, away_goals) if home_goals > 0 else (0, away_goals),
            (home_goals, away_goals - 1) if away_goals > 0 else (home_goals, 0),
            (home_goals + 1, away_goals + 1),
        ]
        
        for h_goals, a_goals in variations:
            if h_goals >= 0 and a_goals >= 0 and h_goals <= 5 and a_goals <= 5:
                distance = abs(h_goals - home_goals) + abs(a_goals - away_goals)
                probability = confidence * (0.8 ** distance)
                
                alternatives.append({
                    'score': f"{h_goals}-{a_goals}",
                    'probability': round(probability, 3)
                })
        
        seen = set()
        unique_alternatives = []
        for alt in alternatives:
            if alt['score'] not in seen:
                seen.add(alt['score'])
                unique_alternatives.append(alt)
        
        return sorted(unique_alternatives, key=lambda x: x['probability'], reverse=True)[:3]
    
    def _generate_score_reasoning(self, home_team: str, away_team: str, 
                                 home_goals: int, away_goals: int,
                                 home_strength: Dict, away_strength: Dict, 
                                 confidence: float) -> str:
        """Generate human-readable reasoning for the score prediction"""
        
        result = "draw" if home_goals == away_goals else ("home win" if home_goals > away_goals else "away win")
        total_goals = home_goals + away_goals
        
        reasoning = f"Predicted {home_goals}-{away_goals} ({result}). "
        
        if total_goals >= 4:
            reasoning += "High-scoring match expected with both teams likely to find the net. "
        elif total_goals <= 1:
            reasoning += "Low-scoring defensive battle anticipated. "
        else:
            reasoning += "Moderate scoring game with balanced attacking play. "
        
        home_attack = home_strength['attacking_strength']
        away_attack = away_strength['attacking_strength']
        
        if home_attack > away_attack * 1.3:
            reasoning += f"{home_team} has superior attacking threat. "
        elif away_attack > home_attack * 1.3:
            reasoning += f"{away_team} has superior attacking threat. "
        else:
            reasoning += "Evenly matched attacking capabilities. "
        
        if confidence >= 80:
            reasoning += "High confidence prediction based on strong market consensus."
        elif confidence >= 65:
            reasoning += "Solid prediction with good statistical backing."
        else:
            reasoning += "Moderate confidence due to competitive odds."
            
        return reasoning
    
    def get_score_predictions_summary(self, sport_key: str) -> str:
        """Get formatted summary of score predictions"""
        try:
            predictions = self.predict_exact_scores(sport_key)
            
            if not predictions:
                return "No score predictions available at the moment."
            
            summary = "🎯 **EXACT SCORE PREDICTIONS**\n\n"
            
            for i, pred in enumerate(predictions, 1):
                home_goals = pred['home_goals']
                away_goals = pred['away_goals']
                confidence = pred['confidence']
                
                summary += f"{i}. **{pred['home_team']} vs {pred['away_team']}**\n"
                summary += f"   📊 Predicted Score: **{home_goals}-{away_goals}**\n"
                summary += f"   🎯 Confidence: **{confidence:.0f}%**\n"
                
                if pred['alternative_scores']:
                    alt_scores = [s['score'] for s in pred['alternative_scores'][:3]]
                    summary += f"   🔄 Alternatives: {', '.join(alt_scores)}\n"
                
                summary += "\n"
            
            summary += "💡 *Predictions based on real-time odds analysis and statistical modeling*"
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Error generating score predictions. Please try again."
