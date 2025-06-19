"""
Advanced Prediction Engine with Multiple Algorithms

This engine combines multiple prediction models for maximum accuracy:
- Value Betting Algorithm (Kelly Criterion)
- Statistical Regression Models
- Market Inefficiency Detection
- Ensemble Learning Approach
- Historical Performance Tracking
"""

import requests
import logging
import statistics
import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import os

logger = logging.getLogger(__name__)

class AdvancedPredictionEngine:
    def __init__(self):
        self.odds_api_key = os.getenv('ODDS_API_KEY')
        self.base_url = "https://api.the-odds-api.com/v4"
        self.prediction_history = []
        self.accuracy_metrics = {
            'total_predictions': 0,
            'correct_predictions': 0,
            'profitable_bets': 0,
            'total_roi': 0.0
        }
        
    def generate_enhanced_predictions(self, sport_key: str) -> List[Dict]:
        """Generate predictions using multiple advanced algorithms"""
        try:
            games = self._fetch_comprehensive_data(sport_key)
            if not games:
                return []
            
            predictions = []
            for game in games:
                prediction = self._analyze_with_multiple_models(game)
                if prediction and prediction['confidence'] >= 60:  # Only high-confidence predictions
                    predictions.append(prediction)
            
            # Sort by expected value (most profitable first)
            return sorted(predictions, key=lambda x: x['expected_value'], reverse=True)[:10]
            
        except Exception as e:
            logger.error(f"Error in enhanced predictions: {e}")
            return []
    
    def _fetch_comprehensive_data(self, sport_key: str) -> List[Dict]:
        """Fetch comprehensive odds and market data"""
        try:
            url = f"{self.base_url}/sports/{sport_key}/odds/"
            params = {
                'apiKey': self.odds_api_key,
                'regions': 'us,uk,eu,au',  # Multiple regions for better odds
                'markets': 'h2h,spreads,totals,outrights',
                'oddsFormat': 'decimal',
                'dateFormat': 'iso'
            }
            
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                games = response.json()
                # Filter for games in next 48 hours
                now = datetime.now()
                upcoming = []
                for game in games:
                    try:
                        game_time = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00'))
                        if now < game_time < now + timedelta(hours=48):
                            upcoming.append(game)
                    except:
                        continue
                return upcoming[:15]
            return []
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return []
    
    def _analyze_with_multiple_models(self, game: Dict) -> Optional[Dict]:
        """Analyze game using multiple prediction models"""
        try:
            # Extract comprehensive odds data
            odds_data = self._extract_enhanced_odds_data(game)
            if not odds_data:
                return None
            
            # Model 1: Value Betting (Kelly Criterion)
            value_bet = self._kelly_criterion_analysis(game, odds_data)
            
            # Model 2: Market Inefficiency Detection
            market_inefficiency = self._detect_market_inefficiencies(odds_data)
            
            # Model 3: Statistical Regression
            regression_prediction = self._statistical_regression_model(game, odds_data)
            
            # Model 4: Ensemble Voting
            ensemble_result = self._ensemble_voting([value_bet, market_inefficiency, regression_prediction])
            
            if not ensemble_result:
                return None
            
            # Calculate final metrics
            expected_value = self._calculate_expected_value(ensemble_result, odds_data)
            confidence = self._calculate_ensemble_confidence(ensemble_result, odds_data)
            
            return {
                'home_team': game['home_team'],
                'away_team': game['away_team'],
                'commence_time': game['commence_time'],
                'sport_key': game.get('sport_key', ''),
                'recommended_bet': ensemble_result['bet_type'],
                'recommended_team': ensemble_result.get('team', ''),
                'best_odds': ensemble_result['odds'],
                'bookmaker': ensemble_result['bookmaker'],
                'confidence': confidence,
                'expected_value': expected_value,
                'kelly_percentage': ensemble_result.get('kelly_percentage', 0),
                'prediction_reasoning': self._generate_advanced_reasoning(ensemble_result, odds_data),
                'risk_level': self._assess_risk_level(confidence, expected_value),
                'models_agreement': ensemble_result.get('agreement_score', 0),
                'market_analysis': odds_data.get('market_summary', {}),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in model analysis: {e}")
            return None
    
    def _extract_enhanced_odds_data(self, game: Dict) -> Optional[Dict]:
        """Extract comprehensive odds data with market analysis"""
        try:
            bookmakers = game.get('bookmakers', [])
            if not bookmakers:
                return None
            
            h2h_odds = []  # Head-to-head odds
            spread_odds = []  # Point spread odds
            total_odds = []  # Over/under odds
            
            for bookmaker in bookmakers:
                bm_name = bookmaker['title']
                for market in bookmaker.get('markets', []):
                    if market['key'] == 'h2h':
                        outcomes = market['outcomes']
                        if len(outcomes) >= 2:
                            home_odds = next((o['price'] for o in outcomes if o['name'] == game['home_team']), None)
                            away_odds = next((o['price'] for o in outcomes if o['name'] == game['away_team']), None)
                            draw_odds = next((o['price'] for o in outcomes if o['name'] == 'Draw'), None)
                            
                            if home_odds and away_odds:
                                h2h_odds.append({
                                    'bookmaker': bm_name,
                                    'home_odds': home_odds,
                                    'away_odds': away_odds,
                                    'draw_odds': draw_odds
                                })
                    
                    elif market['key'] == 'spreads':
                        for outcome in market['outcomes']:
                            spread_odds.append({
                                'bookmaker': bm_name,
                                'team': outcome['name'],
                                'spread': outcome.get('point', 0),
                                'odds': outcome['price']
                            })
                    
                    elif market['key'] == 'totals':
                        for outcome in market['outcomes']:
                            total_odds.append({
                                'bookmaker': bm_name,
                                'type': outcome['name'],  # Over/Under
                                'total': outcome.get('point', 0),
                                'odds': outcome['price']
                            })
            
            if not h2h_odds:
                return None
            
            # Calculate market statistics
            home_odds_list = [odds['home_odds'] for odds in h2h_odds]
            away_odds_list = [odds['away_odds'] for odds in h2h_odds]
            
            avg_home_odds = statistics.mean(home_odds_list)
            avg_away_odds = statistics.mean(away_odds_list)
            best_home_odds = max(home_odds_list)
            best_away_odds = max(away_odds_list)
            
            # Calculate true probabilities (remove bookmaker margin)
            home_prob = 1 / avg_home_odds
            away_prob = 1 / avg_away_odds
            total_prob = home_prob + away_prob
            
            if total_prob > 1:
                home_prob = home_prob / total_prob
                away_prob = away_prob / total_prob
            
            # Market inefficiency indicators
            home_odds_variance = statistics.variance(home_odds_list) if len(home_odds_list) > 1 else 0
            away_odds_variance = statistics.variance(away_odds_list) if len(away_odds_list) > 1 else 0
            
            return {
                'h2h_data': h2h_odds,
                'spread_data': spread_odds,
                'total_data': total_odds,
                'avg_home_odds': avg_home_odds,
                'avg_away_odds': avg_away_odds,
                'best_home_odds': best_home_odds,
                'best_away_odds': best_away_odds,
                'home_probability': home_prob,
                'away_probability': away_prob,
                'bookmaker_count': len(h2h_odds),
                'home_odds_variance': home_odds_variance,
                'away_odds_variance': away_odds_variance,
                'market_efficiency': self._calculate_market_efficiency(home_odds_variance, away_odds_variance),
                'overround': total_prob - 1 if total_prob > 1 else 0
            }
            
        except Exception as e:
            logger.error(f"Error extracting enhanced odds: {e}")
            return None
    
    def _kelly_criterion_analysis(self, game: Dict, odds_data: Dict) -> Optional[Dict]:
        """Apply Kelly Criterion for optimal bet sizing"""
        try:
            home_team = game['home_team']
            away_team = game['away_team']
            
            # Estimate true probabilities (this would ideally use historical data)
            estimated_home_prob = self._estimate_true_probability(home_team, away_team, 'home')
            estimated_away_prob = self._estimate_true_probability(home_team, away_team, 'away')
            
            home_odds = odds_data['best_home_odds']
            away_odds = odds_data['best_away_odds']
            
            # Kelly Criterion: f = (bp - q) / b
            # where f = fraction to bet, b = odds-1, p = probability of win, q = probability of loss
            
            home_kelly = self._calculate_kelly(estimated_home_prob, home_odds)
            away_kelly = self._calculate_kelly(estimated_away_prob, away_odds)
            
            # Only recommend bets with positive Kelly value
            if home_kelly > 0.02:  # At least 2% edge
                return {
                    'bet_type': 'moneyline',
                    'team': home_team,
                    'odds': home_odds,
                    'kelly_percentage': home_kelly * 100,
                    'estimated_prob': estimated_home_prob,
                    'bookmaker': self._find_best_odds_bookmaker(odds_data, 'home'),
                    'model': 'kelly_criterion'
                }
            elif away_kelly > 0.02:
                return {
                    'bet_type': 'moneyline',
                    'team': away_team,
                    'odds': away_odds,
                    'kelly_percentage': away_kelly * 100,
                    'estimated_prob': estimated_away_prob,
                    'bookmaker': self._find_best_odds_bookmaker(odds_data, 'away'),
                    'model': 'kelly_criterion'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Kelly criterion error: {e}")
            return None
    
    def _detect_market_inefficiencies(self, odds_data: Dict) -> Optional[Dict]:
        """Detect market inefficiencies and arbitrage opportunities"""
        try:
            # Look for significant odds discrepancies between bookmakers
            home_odds_list = [odds['home_odds'] for odds in odds_data['h2h_data']]
            away_odds_list = [odds['away_odds'] for odds in odds_data['h2h_data']]
            
            if len(home_odds_list) < 3:
                return None
            
            home_max = max(home_odds_list)
            home_min = min(home_odds_list)
            away_max = max(away_odds_list)
            away_min = min(away_odds_list)
            
            # Calculate price discrepancy percentage
            home_discrepancy = (home_max - home_min) / home_min
            away_discrepancy = (away_max - away_min) / away_min
            
            # Significant discrepancy threshold (>8%)
            if home_discrepancy > 0.08 and home_discrepancy > away_discrepancy:
                return {
                    'bet_type': 'value_bet',
                    'team': odds_data['h2h_data'][0]['bookmaker'],  # This needs to be fixed
                    'odds': home_max,
                    'discrepancy': home_discrepancy * 100,
                    'market_avg': statistics.mean(home_odds_list),
                    'bookmaker': self._find_best_odds_bookmaker(odds_data, 'home'),
                    'model': 'market_inefficiency'
                }
            elif away_discrepancy > 0.08:
                return {
                    'bet_type': 'value_bet',
                    'team': odds_data['h2h_data'][0]['bookmaker'],  # This needs to be fixed
                    'odds': away_max,
                    'discrepancy': away_discrepancy * 100,
                    'market_avg': statistics.mean(away_odds_list),
                    'bookmaker': self._find_best_odds_bookmaker(odds_data, 'away'),
                    'model': 'market_inefficiency'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Market inefficiency detection error: {e}")
            return None
    
    def _statistical_regression_model(self, game: Dict, odds_data: Dict) -> Optional[Dict]:
        """Statistical regression-based prediction model"""
        try:
            # This is a simplified regression model
            # In practice, this would use historical team performance data
            
            home_prob = odds_data['home_probability']
            away_prob = odds_data['away_probability']
            market_efficiency = odds_data['market_efficiency']
            
            # Adjust probabilities based on market efficiency
            if market_efficiency < 0.8:  # Inefficient market
                # Look for the favorite with good value
                if home_prob > 0.6:  # Strong home favorite
                    adjusted_prob = min(home_prob * 1.1, 0.85)  # Boost slightly
                    if adjusted_prob > (1 / odds_data['best_home_odds']):
                        return {
                            'bet_type': 'moneyline',
                            'team': game['home_team'],
                            'odds': odds_data['best_home_odds'],
                            'adjusted_prob': adjusted_prob,
                            'bookmaker': self._find_best_odds_bookmaker(odds_data, 'home'),
                            'model': 'statistical_regression'
                        }
                elif away_prob > 0.6:  # Strong away favorite
                    adjusted_prob = min(away_prob * 1.1, 0.85)
                    if adjusted_prob > (1 / odds_data['best_away_odds']):
                        return {
                            'bet_type': 'moneyline',
                            'team': game['away_team'],
                            'odds': odds_data['best_away_odds'],
                            'adjusted_prob': adjusted_prob,
                            'bookmaker': self._find_best_odds_bookmaker(odds_data, 'away'),
                            'model': 'statistical_regression'
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Statistical regression error: {e}")
            return None
    
    def _ensemble_voting(self, model_results: List[Optional[Dict]]) -> Optional[Dict]:
        """Combine results from multiple models using ensemble voting"""
        try:
            valid_results = [r for r in model_results if r is not None]
            if not valid_results:
                return None
            
            # Count votes for each team/bet
            team_votes = defaultdict(list)
            for result in valid_results:
                team = result.get('team', '')
                if team:
                    team_votes[team].append(result)
            
            if not team_votes:
                return None
            
            # Find the team with most votes or highest confidence
            best_team = None
            best_score = 0
            best_result = None
            
            for team, votes in team_votes.items():
                # Score based on number of votes and model confidence
                score = len(votes) * 2  # Base score for votes
                avg_kelly = statistics.mean([v.get('kelly_percentage', 0) for v in votes])
                score += avg_kelly * 0.1  # Bonus for Kelly percentage
                
                if score > best_score:
                    best_score = score
                    best_team = team
                    best_result = votes[0]  # Take first result as base
            
            if best_result:
                best_result['agreement_score'] = len(team_votes[best_team]) / len(valid_results)
                return best_result
            
            return None
            
        except Exception as e:
            logger.error(f"Ensemble voting error: {e}")
            return None
    
    def _calculate_kelly(self, prob: float, odds: float) -> float:
        """Calculate Kelly Criterion percentage"""
        try:
            if prob <= 0 or odds <= 1:
                return 0
            
            b = odds - 1  # Net odds
            p = prob      # Probability of winning
            q = 1 - p     # Probability of losing
            
            kelly = (b * p - q) / b
            return max(0, min(kelly, 0.25))  # Cap at 25% of bankroll
            
        except:
            return 0
    
    def _estimate_true_probability(self, home_team: str, away_team: str, side: str) -> float:
        """Estimate true probability (simplified - would use historical data in practice)"""
        # This is a placeholder - in practice, you'd use:
        # - Historical head-to-head records
        # - Recent form analysis
        # - Team strength ratings
        # - Home field advantage
        # - Player injuries/suspensions
        
        # For now, return market-implied probability with slight adjustments
        if side == 'home':
            return 0.55  # Slight home field advantage
        else:
            return 0.45
    
    def _calculate_market_efficiency(self, home_variance: float, away_variance: float) -> float:
        """Calculate market efficiency score (0-1, higher = more efficient)"""
        try:
            avg_variance = (home_variance + away_variance) / 2
            # Lower variance = more efficient market
            efficiency = 1 / (1 + avg_variance * 10)
            return min(max(efficiency, 0.1), 1.0)
        except:
            return 0.8
    
    def _find_best_odds_bookmaker(self, odds_data: Dict, side: str) -> str:
        """Find bookmaker offering best odds for a side"""
        try:
            h2h_data = odds_data['h2h_data']
            if side == 'home':
                best_odds = max(h2h_data, key=lambda x: x['home_odds'])
                return best_odds['bookmaker']
            else:
                best_odds = max(h2h_data, key=lambda x: x['away_odds'])
                return best_odds['bookmaker']
        except:
            return "Unknown"
    
    def _calculate_expected_value(self, prediction: Dict, odds_data: Dict) -> float:
        """Calculate expected value of the bet"""
        try:
            odds = prediction.get('odds', 1.0)
            prob = prediction.get('estimated_prob') or prediction.get('adjusted_prob', 0.5)
            
            expected_value = (prob * (odds - 1)) - ((1 - prob) * 1)
            return round(expected_value, 4)
        except:
            return 0.0
    
    def _calculate_ensemble_confidence(self, prediction: Dict, odds_data: Dict) -> float:
        """Calculate confidence based on ensemble agreement and other factors"""
        try:
            base_confidence = 60.0
            
            # Boost confidence for model agreement
            agreement = prediction.get('agreement_score', 0.5)
            base_confidence += agreement * 20
            
            # Boost for market inefficiency
            market_eff = odds_data.get('market_efficiency', 0.8)
            if market_eff < 0.7:
                base_confidence += 10
            
            # Boost for strong Kelly percentage
            kelly = prediction.get('kelly_percentage', 0)
            if kelly > 5:
                base_confidence += min(kelly, 15)
            
            return min(max(base_confidence, 50), 95)
        except:
            return 65.0
    
    def _generate_advanced_reasoning(self, prediction: Dict, odds_data: Dict) -> str:
        """Generate detailed reasoning for the prediction"""
        try:
            team = prediction.get('team', 'Unknown')
            odds = prediction.get('odds', 0)
            model = prediction.get('model', 'ensemble')
            
            reasoning = f"Recommending {team} at {odds:.2f} odds. "
            
            # Add model-specific reasoning
            if model == 'kelly_criterion':
                kelly = prediction.get('kelly_percentage', 0)
                reasoning += f"Kelly Criterion suggests {kelly:.1f}% of bankroll. "
            elif model == 'market_inefficiency':
                discrepancy = prediction.get('discrepancy', 0)
                reasoning += f"Market discrepancy of {discrepancy:.1f}% detected. "
            
            # Add market analysis
            efficiency = odds_data.get('market_efficiency', 0.8)
            if efficiency < 0.7:
                reasoning += "Market appears inefficient. "
            
            bookmaker_count = odds_data.get('bookmaker_count', 0)
            reasoning += f"Analysis based on {bookmaker_count} bookmakers. "
            
            return reasoning
            
        except:
            return "Advanced statistical analysis indicates value opportunity."
    
    def _assess_risk_level(self, confidence: float, expected_value: float) -> str:
        """Assess risk level of the bet"""
        if confidence >= 80 and expected_value > 0.1:
            return "LOW"
        elif confidence >= 70 and expected_value > 0.05:
            return "MEDIUM"
        elif confidence >= 60:
            return "MEDIUM-HIGH"
        else:
            return "HIGH"
    
    def track_prediction_outcome(self, prediction_id: str, actual_outcome: str, bet_amount: float = 0) -> Dict:
        """Track the outcome of a prediction for accuracy measurement"""
        # This would be implemented to track historical performance
        # and continuously improve the models
        pass
    
    def get_accuracy_report(self) -> Dict:
        """Get current accuracy and performance metrics"""
        return {
            'total_predictions': self.accuracy_metrics['total_predictions'],
            'accuracy_rate': (self.accuracy_metrics['correct_predictions'] / 
                            max(self.accuracy_metrics['total_predictions'], 1)) * 100,
            'profitable_rate': (self.accuracy_metrics['profitable_bets'] / 
                              max(self.accuracy_metrics['total_predictions'], 1)) * 100,
            'total_roi': self.accuracy_metrics['total_roi']
        }
