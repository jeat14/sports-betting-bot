#!/usr/bin/env python3
"""
Live Odds Movement Monitoring System

Tracks real-time odds changes across bookmakers to identify:
- Sharp money indicators
- Line movement patterns
- Arbitrage windows opening/closing
- Value betting opportunities
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
import statistics
from odds_service import OddsService

logger = logging.getLogger(__name__)

class LiveOddsMonitor:
    def __init__(self):
        self.odds_service = OddsService()
        self.historical_odds = {}  # Store odds movements
        
    def detect_significant_line_movement(self, sport_key: str, threshold: float = 0.15) -> List[Dict]:
        """Detect significant line movements indicating sharp action"""
        try:
            current_odds = self.odds_service.get_odds(sport_key)
            movements = []
            
            for game in current_odds:
                movement_analysis = self._analyze_line_movement(game, threshold)
                if movement_analysis:
                    movements.append(movement_analysis)
            
            return sorted(movements, key=lambda x: x['movement_strength'], reverse=True)[:5]
            
        except Exception as e:
            logger.error(f"Error detecting line movement: {e}")
            return []
    
    def _analyze_line_movement(self, game: Dict, threshold: float) -> Optional[Dict]:
        """Analyze individual game for significant line movement"""
        try:
            bookmakers = game.get('bookmakers', [])
            if len(bookmakers) < 4:
                return None
            
            # Get current odds variance
            home_odds = []
            away_odds = []
            
            for bm in bookmakers:
                for market in bm.get('markets', []):
                    if market['key'] == 'h2h':
                        for outcome in market['outcomes']:
                            price = outcome['price']
                            if price <= 1.0 or price > 20.0:
                                continue
                            
                            if outcome['name'] == game['home_team']:
                                home_odds.append(price)
                            elif outcome['name'] == game['away_team']:
                                away_odds.append(price)
            
            if len(home_odds) < 3 or len(away_odds) < 3:
                return None
            
            # Calculate movement indicators
            home_variance = statistics.variance(home_odds) if len(home_odds) > 1 else 0
            away_variance = statistics.variance(away_odds) if len(away_odds) > 1 else 0
            
            # High variance suggests disagreement/movement
            max_variance = max(home_variance, away_variance)
            
            if max_variance > threshold:
                # Identify direction of movement
                side = 'home' if home_variance > away_variance else 'away'
                odds_list = home_odds if side == 'home' else away_odds
                team = game['home_team'] if side == 'home' else game['away_team']
                
                min_odds = min(odds_list)
                max_odds = max(odds_list)
                movement_range = (max_odds - min_odds) / min_odds
                
                return {
                    'game': f"{game['home_team']} vs {game['away_team']}",
                    'commence_time': game['commence_time'],
                    'movement_team': team,
                    'movement_side': side,
                    'movement_strength': round(max_variance * 100, 2),
                    'odds_range': f"{min_odds:.2f} - {max_odds:.2f}",
                    'movement_percentage': round(movement_range * 100, 2),
                    'interpretation': self._interpret_movement(movement_range, max_variance),
                    'action_recommended': 'FOLLOW' if movement_range > 0.10 else 'MONITOR'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing line movement: {e}")
            return None
    
    def _interpret_movement(self, movement_range: float, variance: float) -> str:
        """Interpret what the line movement indicates"""
        if movement_range > 0.20 and variance > 0.25:
            return "STRONG SHARP ACTION - Major disagreement between books"
        elif movement_range > 0.15:
            return "MODERATE SHARP ACTION - Significant line movement detected"
        elif movement_range > 0.10:
            return "MILD SHARP ACTION - Some professional money detected"
        else:
            return "NORMAL MARKET ACTIVITY"
    
    def find_value_betting_opportunities(self, sport_key: str) -> List[Dict]:
        """Find value betting opportunities based on odds analysis"""
        try:
            games = self.odds_service.get_odds(sport_key)
            value_bets = []
            
            for game in games:
                value_analysis = self._analyze_value_opportunity(game)
                if value_analysis:
                    value_bets.append(value_analysis)
            
            return sorted(value_bets, key=lambda x: x['value_percentage'], reverse=True)[:3]
            
        except Exception as e:
            logger.error(f"Error finding value bets: {e}")
            return []
    
    def _analyze_value_opportunity(self, game: Dict) -> Optional[Dict]:
        """Analyze game for value betting opportunities"""
        try:
            bookmakers = game.get('bookmakers', [])
            if len(bookmakers) < 5:
                return None
            
            # Calculate fair odds using market consensus
            home_odds = []
            away_odds = []
            
            for bm in bookmakers:
                for market in bm.get('markets', []):
                    if market['key'] == 'h2h':
                        for outcome in market['outcomes']:
                            price = outcome['price']
                            if price <= 1.0 or price > 20.0:
                                continue
                            
                            if outcome['name'] == game['home_team']:
                                home_odds.append(price)
                            elif outcome['name'] == game['away_team']:
                                away_odds.append(price)
            
            if len(home_odds) < 3 or len(away_odds) < 3:
                return None
            
            # Calculate fair probabilities using inverse odds method
            home_probs = [1/odds for odds in home_odds]
            away_probs = [1/odds for odds in away_odds]
            
            fair_home_prob = statistics.mean(home_probs)
            fair_away_prob = statistics.mean(away_probs)
            
            # Normalize probabilities
            total_prob = fair_home_prob + fair_away_prob
            fair_home_prob = fair_home_prob / total_prob
            fair_away_prob = fair_away_prob / total_prob
            
            # Find best available odds
            best_home_odds = max(home_odds)
            best_away_odds = max(away_odds)
            
            # Calculate implied probabilities from best odds
            best_home_implied = 1 / best_home_odds
            best_away_implied = 1 / best_away_odds
            
            # Calculate value
            home_value = (fair_home_prob - best_home_implied) / best_home_implied
            away_value = (fair_away_prob - best_away_implied) / best_away_implied
            
            # Return best value opportunity
            if home_value > 0.05 or away_value > 0.05:  # 5% minimum value
                if home_value > away_value:
                    return {
                        'game': f"{game['home_team']} vs {game['away_team']}",
                        'commence_time': game['commence_time'],
                        'value_team': game['home_team'],
                        'value_side': 'home',
                        'fair_probability': round(fair_home_prob * 100, 1),
                        'market_probability': round(best_home_implied * 100, 1),
                        'best_odds': best_home_odds,
                        'value_percentage': round(home_value * 100, 2),
                        'edge_description': f"{home_value*100:.1f}% edge over market",
                        'confidence': 'HIGH' if home_value > 0.10 else 'MEDIUM'
                    }
                elif away_value > 0.05:
                    return {
                        'game': f"{game['home_team']} vs {game['away_team']}",
                        'commence_time': game['commence_time'],
                        'value_team': game['away_team'],
                        'value_side': 'away',
                        'fair_probability': round(fair_away_prob * 100, 1),
                        'market_probability': round(best_away_implied * 100, 1),
                        'best_odds': best_away_odds,
                        'value_percentage': round(away_value * 100, 2),
                        'edge_description': f"{away_value*100:.1f}% edge over market",
                        'confidence': 'HIGH' if away_value > 0.10 else 'MEDIUM'
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing value opportunity: {e}")
            return None
    
    def generate_live_monitoring_report(self, sport_key: str) -> str:
        """Generate comprehensive live monitoring report"""
        try:
            # Get all monitoring data
            line_movements = self.detect_significant_line_movement(sport_key)
            value_opportunities = self.find_value_betting_opportunities(sport_key)
            
            report = f"📊 LIVE ODDS MONITORING - {sport_key.upper()}\n\n"
            
            # Line Movement Section
            if line_movements:
                report += "🔥 SIGNIFICANT LINE MOVEMENTS:\n"
                for i, movement in enumerate(line_movements, 1):
                    report += f"{i}. {movement['game']}\n"
                    report += f"   🎯 {movement['movement_team']} - Movement: {movement['movement_percentage']}%\n"
                    report += f"   📈 Odds Range: {movement['odds_range']}\n"
                    report += f"   💡 {movement['interpretation']}\n"
                    report += f"   ⚡ Action: {movement['action_recommended']}\n\n"
            else:
                report += "🔥 SIGNIFICANT LINE MOVEMENTS: None detected\n\n"
            
            # Value Betting Section
            if value_opportunities:
                report += "💎 VALUE BETTING OPPORTUNITIES:\n"
                for i, value in enumerate(value_opportunities, 1):
                    report += f"{i}. {value['game']}\n"
                    report += f"   🎯 {value['value_team']} @ {value['best_odds']}\n"
                    report += f"   📊 Fair: {value['fair_probability']}% | Market: {value['market_probability']}%\n"
                    report += f"   💰 Edge: {value['value_percentage']}% value\n"
                    report += f"   ⚡ Confidence: {value['confidence']}\n\n"
            else:
                report += "💎 VALUE BETTING OPPORTUNITIES: None detected\n\n"
            
            report += "🧠 MONITORING INSIGHTS:\n"
            report += "• Line movements indicate where sharp money is going\n"
            report += "• Value bets show market inefficiencies to exploit\n"
            report += "• High confidence opportunities have strongest edge\n"
            report += "• Follow significant movements quickly - windows close fast\n\n"
            report += "⚠️ Monitor continuously - odds change rapidly!"
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating monitoring report: {e}")
            return f"Error generating live monitoring report: {e}"
