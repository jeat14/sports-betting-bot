from typing import Dict, List, Optional
import statistics
from odds_service import OddsService

class PredictionEngine:
    def __init__(self, odds_service: OddsService):
        self.odds_service = odds_service
    
    def generate_predictions(self, sport_key: str) -> List[Dict]:
        """Generate betting predictions for a sport"""
        # Get upcoming games directly
        games = self.odds_service.get_upcoming_games(sport_key, 5)
        predictions = []
        
        for game in games:
            if not game.get('bookmakers'):
                continue
                
            # Create a simple prediction based on odds
            prediction = self._create_simple_prediction(game)
            if prediction:
                predictions.append(prediction)
        
        return predictions
    
    def _create_simple_prediction(self, game: Dict) -> Optional[Dict]:
        """Create a simple prediction based on odds comparison"""
        bookmakers = game.get('bookmakers', [])
        if not bookmakers:
            return None
            
        # Find h2h market
        all_odds = {}
        for bookmaker in bookmakers:
            for market in bookmaker.get('markets', []):
                if market['key'] == 'h2h':
                    for outcome in market['outcomes']:
                        team = outcome['name']
                        odds = float(outcome['price'])
                        if team not in all_odds:
                            all_odds[team] = []
                        all_odds[team].append(odds)
        
        if len(all_odds) < 2:
            return None
            
        # Calculate average odds and find best value
        team_stats = {}
        for team, odds_list in all_odds.items():
            avg_odds = sum(odds_list) / len(odds_list)
            implied_prob = (1 / avg_odds) * 100
            team_stats[team] = {
                'avg_odds': round(avg_odds, 2),
                'implied_probability': round(implied_prob, 2)
            }
        
        # Find the favorite (team with highest implied probability = lowest odds)
        favorite_team = max(team_stats.items(), key=lambda x: x[1]['implied_probability'])
        favorite_name = favorite_team[0]
        favorite_prob = favorite_team[1]['implied_probability']
        favorite_odds = favorite_team[1]['avg_odds']
        
        # Determine betting strategy
        best_team = None
        best_reasoning = ""
        confidence = 50.0
        
        # Strategy: Favor the actual favorite unless there's clear value elsewhere
        if favorite_prob > 60:  # Strong favorite
            best_team = favorite_name
            best_reasoning = f"Strong favorite with {favorite_prob:.1f}% win probability"
            confidence = min(85.0, favorite_prob + 15)
        elif favorite_prob > 45:  # Moderate favorite
            best_team = favorite_name
            best_reasoning = f"Market favorite at {favorite_odds} odds"
            confidence = favorite_prob + 10
        else:  # Close matchup - look for value
            # In close games, still lean toward favorite but check for extreme value
            all_teams = list(team_stats.items())
            best_value_team = None
            best_value_score = 0
            
            for team_name, stats in all_teams:
                # Value score = odds * probability (higher is better value)
                value_score = stats['avg_odds'] * (stats['implied_probability'] / 100)
                if value_score > best_value_score and stats['implied_probability'] > 25:
                    best_value_score = value_score
                    best_value_team = team_name
            
            if best_value_team and best_value_team != favorite_name:
                underdog_odds = team_stats[best_value_team]['avg_odds']
                if underdog_odds >= 3.0:  # Only take big underdogs with real value
                    best_team = best_value_team
                    best_reasoning = f"High-value underdog at {underdog_odds} odds"
                    confidence = 65.0
                else:
                    best_team = favorite_name
                    best_reasoning = f"Market favorite in close matchup"
                    confidence = 60.0
            else:
                best_team = favorite_name
                best_reasoning = f"Market favorite in close matchup"
                confidence = 60.0
        
        if not best_team:
            return None
            
        return {
            'game_id': game.get('id'),
            'home_team': game.get('home_team'),
            'away_team': game.get('away_team'),
            'commence_time': game.get('commence_time'),
            'sport_title': game.get('sport_title', 'FIFA Club World Cup'),
            'recommendation': {
                'bet_on': best_team,
                'bet_type': 'MONEYLINE',
                'odds': team_stats[best_team]['avg_odds'],
                'confidence': round(confidence, 1),
                'value_score': round(confidence / 20, 1),
                'reasoning': best_reasoning
            },
            'all_teams_analysis': team_stats,
            'market_analysis': {
                'favorite': favorite_name,
                'favorite_probability': favorite_prob,
                'strategy': 'favorite' if best_team == favorite_name else 'value_underdog'
            }
        }
    
    def _analyze_game_for_prediction(self, game: Dict) -> Optional[Dict]:
        """Analyze a single game and generate prediction"""
        odds_analysis = game.get('odds_analysis')
        if not odds_analysis:
            return None
        
        teams = odds_analysis['teams']
        confidence = odds_analysis['confidence']
        
        # Find the team with better value (lower implied probability but reasonable odds)
        best_bet = None
        best_value = 0
        
        for team, stats in teams.items():
            # Value calculation: higher odds with reasonable probability
            implied_prob = stats['implied_probability']
            avg_odds = stats['avg_odds']
            variance = stats['variance']
            
            # Calculate value score (prefer lower implied prob with higher odds, lower variance)
            if implied_prob > 10 and implied_prob < 85:  # Allow more range including favorites and underdogs
                value_score = (avg_odds - 1) * (100 - implied_prob) / (1 + variance * 10)
                
                if value_score > best_value:
                    best_value = value_score
                    best_bet = {
                        'team': team,
                        'odds': avg_odds,
                        'implied_probability': implied_prob,
                        'variance': variance,
                        'value_score': round(value_score, 2)
                    }
        
        if not best_bet or confidence < 20:  # Lower confidence threshold to show more predictions
            return None
        
        # Determine bet type and reasoning
        bet_type = "MONEYLINE"
        reasoning = self._generate_reasoning(best_bet, teams, confidence)
        
        return {
            'game_id': game.get('id'),
            'home_team': game.get('home_team'),
            'away_team': game.get('away_team'),
            'commence_time': game.get('commence_time'),
            'sport_title': game.get('sport_title'),
            'recommendation': {
                'bet_on': best_bet['team'],
                'bet_type': bet_type,
                'odds': best_bet['odds'],
                'confidence': confidence,
                'value_score': best_bet['value_score'],
                'reasoning': reasoning
            },
            'all_teams_analysis': teams
        }
    
    def _generate_reasoning(self, best_bet: Dict, all_teams: Dict, confidence: float) -> str:
        """Generate human-readable reasoning for the prediction"""
        team = best_bet['team']
        odds = best_bet['odds']
        prob = best_bet['implied_probability']
        value = best_bet['value_score']
        
        reasoning_parts = []
        
        # Odds analysis
        if odds > 2.5:
            reasoning_parts.append(f"{team} offers good underdog value at {odds}")
        elif odds < 1.8:
            reasoning_parts.append(f"{team} is heavily favored at {odds}")
        else:
            reasoning_parts.append(f"{team} has balanced odds at {odds}")
        
        # Probability analysis
        reasoning_parts.append(f"Implied probability: {prob}%")
        
        # Value assessment
        if value > 5:
            reasoning_parts.append("High value bet detected")
        elif value > 2:
            reasoning_parts.append("Good value opportunity")
        else:
            reasoning_parts.append("Moderate value bet")
        
        # Confidence level
        if confidence > 70:
            reasoning_parts.append("High confidence prediction")
        elif confidence > 50:
            reasoning_parts.append("Medium confidence prediction")
        else:
            reasoning_parts.append("Low confidence - bet small if at all")
        
        return " | ".join(reasoning_parts)
    
    def get_daily_predictions(self) -> Dict[str, List[Dict]]:
        """Get predictions for all supported sports"""
        all_predictions = {}
        
        for sport_key, sport_name in self.odds_service.sports.items():
            predictions = self.generate_predictions(sport_key)
            if predictions:
                all_predictions[sport_name] = predictions
        
        return all_predictions
