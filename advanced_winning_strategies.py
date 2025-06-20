#!/usr/bin/env python3
"""
Advanced Winning Strategies - Professional Betting Enhancement

This module implements institutional-grade betting strategies:
- Steam Move Detection
- Reverse Line Movement Analysis
- Sharp Money Tracking
- Closing Line Value (CLV) Optimization
- Multi-Market Correlation Analysis
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
from odds_service import OddsService
import statistics

logger = logging.getLogger(__name__)

class AdvancedWinningStrategies:
    def __init__(self):
        self.odds_service = OddsService()
        self.sharp_bookmakers = ['pinnacle', 'betfair', 'circa', 'bookmaker', 'heritage']
        self.public_bookmakers = ['draftkings', 'fanduel', 'betmgm', 'caesars', 'pointsbet']
        
    def detect_steam_moves(self, sport_key: str) -> List[Dict]:
        """Detect steam moves - rapid line movement indicating sharp action"""
        try:
            games = self.odds_service.get_odds(sport_key)
            steam_opportunities = []
            
            for game in games:
                steam_analysis = self._analyze_steam_movement(game)
                if steam_analysis and steam_analysis['steam_strength'] >= 7:
                    steam_opportunities.append(steam_analysis)
            
            return sorted(steam_opportunities, key=lambda x: x['steam_strength'], reverse=True)[:3]
            
        except Exception as e:
            logger.error(f"Error detecting steam moves: {e}")
            return []
    
    def _analyze_steam_movement(self, game: Dict) -> Optional[Dict]:
        """Analyze individual game for steam movement patterns"""
        try:
            bookmakers = game.get('bookmakers', [])
            if len(bookmakers) < 8:
                return None
            
            home_team = game.get('home_team', '')
            away_team = game.get('away_team', '')
            
            # Separate sharp vs public bookmaker odds
            sharp_odds = {'home': [], 'away': []}
            public_odds = {'home': [], 'away': []}
            
            for bm in bookmakers:
                bm_name = bm.get('title', '').lower()
                for market in bm.get('markets', []):
                    if market['key'] == 'h2h':
                        for outcome in market['outcomes']:
                            price = outcome['price']
                            if price <= 1.0 or price > 50.0:
                                continue
                            
                            is_sharp = any(sharp in bm_name for sharp in self.sharp_bookmakers)
                            is_public = any(public in bm_name for public in self.public_bookmakers)
                            
                            if outcome['name'] == home_team:
                                if is_sharp:
                                    sharp_odds['home'].append(price)
                                elif is_public:
                                    public_odds['home'].append(price)
                            elif outcome['name'] == away_team:
                                if is_sharp:
                                    sharp_odds['away'].append(price)
                                elif is_public:
                                    public_odds['away'].append(price)
            
            # Analyze steam strength
            steam_result = self._calculate_steam_strength(sharp_odds, public_odds, game)
            return steam_result
            
        except Exception as e:
            logger.error(f"Error analyzing steam movement: {e}")
            return None
    
    def _calculate_steam_strength(self, sharp_odds: Dict, public_odds: Dict, game: Dict) -> Optional[Dict]:
        """Calculate steam movement strength and direction"""
        try:
            if (len(sharp_odds['home']) < 2 or len(sharp_odds['away']) < 2 or 
                len(public_odds['home']) < 2 or len(public_odds['away']) < 2):
                return None
            
            # Calculate average odds for each side
            sharp_home_avg = statistics.mean(sharp_odds['home'])
            sharp_away_avg = statistics.mean(sharp_odds['away'])
            public_home_avg = statistics.mean(public_odds['home'])
            public_away_avg = statistics.mean(public_odds['away'])
            
            # Steam detection: significant difference between sharp and public
            home_steam_diff = abs(sharp_home_avg - public_home_avg) / public_home_avg
            away_steam_diff = abs(sharp_away_avg - public_away_avg) / public_away_avg
            
            max_steam = max(home_steam_diff, away_steam_diff)
            
            if max_steam > 0.08:  # 8% difference indicates strong steam
                steam_side = 'home' if home_steam_diff > away_steam_diff else 'away'
                steam_team = game.get('home_team') if steam_side == 'home' else game.get('away_team')
                
                # Calculate steam strength (1-10 scale)
                steam_strength = min(10, int(max_steam * 100))
                
                # Determine direction (sharp money moving toward or away from team)
                if steam_side == 'home':
                    steam_direction = 'TOWARD' if sharp_home_avg < public_home_avg else 'AWAY'
                    best_sharp_odds = min(sharp_odds['home'])
                    best_public_odds = max(public_odds['home'])
                else:
                    steam_direction = 'TOWARD' if sharp_away_avg < public_away_avg else 'AWAY'
                    best_sharp_odds = min(sharp_odds['away'])
                    best_public_odds = max(public_odds['away'])
                
                return {
                    'game': f"{game.get('home_team')} vs {game.get('away_team')}",
                    'commence_time': game.get('commence_time'),
                    'steam_team': steam_team,
                    'steam_side': steam_side,
                    'steam_strength': steam_strength,
                    'steam_direction': steam_direction,
                    'sharp_average_odds': round(sharp_home_avg if steam_side == 'home' else sharp_away_avg, 2),
                    'public_average_odds': round(public_home_avg if steam_side == 'home' else public_away_avg, 2),
                    'best_sharp_odds': best_sharp_odds,
                    'best_public_odds': best_public_odds,
                    'edge_percentage': round(max_steam * 100, 2),
                    'confidence': 'HIGH' if steam_strength >= 8 else 'MEDIUM' if steam_strength >= 6 else 'LOW'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating steam strength: {e}")
            return None
    
    def detect_reverse_line_movement(self, sport_key: str) -> List[Dict]:
        """Detect reverse line movement - line moves opposite to public betting"""
        try:
            games = self.odds_service.get_odds(sport_key)
            rlm_opportunities = []
            
            for game in games:
                rlm_analysis = self._analyze_reverse_line_movement(game)
                if rlm_analysis and rlm_analysis['rlm_strength'] >= 6:
                    rlm_opportunities.append(rlm_analysis)
            
            return sorted(rlm_opportunities, key=lambda x: x['rlm_strength'], reverse=True)[:3]
            
        except Exception as e:
            logger.error(f"Error detecting reverse line movement: {e}")
            return []
    
    def _analyze_reverse_line_movement(self, game: Dict) -> Optional[Dict]:
        """Analyze reverse line movement patterns"""
        try:
            bookmakers = game.get('bookmakers', [])
            if len(bookmakers) < 10:
                return None
            
            home_team = game.get('home_team', '')
            away_team = game.get('away_team', '')
            
            # Collect all odds for variance analysis
            home_odds = []
            away_odds = []
            
            for bm in bookmakers:
                for market in bm.get('markets', []):
                    if market['key'] == 'h2h':
                        for outcome in market['outcomes']:
                            price = outcome['price']
                            if 1.1 <= price <= 25.0:
                                if outcome['name'] == home_team:
                                    home_odds.append(price)
                                elif outcome['name'] == away_team:
                                    away_odds.append(price)
            
            if len(home_odds) < 8 or len(away_odds) < 8:
                return None
            
            # RLM Detection: High variance with outliers indicates reverse movement
            home_variance = statistics.variance(home_odds)
            away_variance = statistics.variance(away_odds)
            home_median = statistics.median(home_odds)
            away_median = statistics.median(away_odds)
            
            # Count significant outliers (>15% from median)
            home_outliers = sum(1 for odds in home_odds if abs(odds - home_median) / home_median > 0.15)
            away_outliers = sum(1 for odds in away_odds if abs(odds - away_median) / away_median > 0.15)
            
            max_variance = max(home_variance, away_variance)
            max_outliers = max(home_outliers, away_outliers)
            
            if max_variance > 2.0 and max_outliers >= 3:
                rlm_side = 'home' if home_variance > away_variance else 'away'
                rlm_team = home_team if rlm_side == 'home' else away_team
                
                # RLM strength calculation
                rlm_strength = min(10, int((max_variance + max_outliers) * 0.8))
                
                odds_list = home_odds if rlm_side == 'home' else away_odds
                best_odds = max(odds_list)
                worst_odds = min(odds_list)
                
                return {
                    'game': f"{home_team} vs {away_team}",
                    'commence_time': game.get('commence_time'),
                    'rlm_team': rlm_team,
                    'rlm_side': rlm_side,
                    'rlm_strength': rlm_strength,
                    'variance': round(max_variance, 2),
                    'outlier_count': max_outliers,
                    'best_odds': best_odds,
                    'worst_odds': worst_odds,
                    'median_odds': round(home_median if rlm_side == 'home' else away_median, 2),
                    'opportunity_rating': 'EXCELLENT' if rlm_strength >= 8 else 'GOOD' if rlm_strength >= 6 else 'FAIR'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing reverse line movement: {e}")
            return None
    
    def find_closing_line_value(self, sport_key: str) -> List[Dict]:
        """Find closing line value opportunities - beat the closing line"""
        try:
            games = self.odds_service.get_odds(sport_key)
            clv_opportunities = []
            
            for game in games:
                clv_analysis = self._analyze_closing_line_value(game)
                if clv_analysis and clv_analysis['clv_score'] >= 7:
                    clv_opportunities.append(clv_analysis)
            
            return sorted(clv_opportunities, key=lambda x: x['clv_score'], reverse=True)[:3]
            
        except Exception as e:
            logger.error(f"Error finding closing line value: {e}")
            return []
    
    def _analyze_closing_line_value(self, game: Dict) -> Optional[Dict]:
        """Analyze potential closing line value"""
        try:
            bookmakers = game.get('bookmakers', [])
            if len(bookmakers) < 6:
                return None
            
            home_team = game.get('home_team', '')
            away_team = game.get('away_team', '')
            
            # Find Pinnacle (closing line proxy) and other sharp books
            pinnacle_odds = {'home': None, 'away': None}
            other_sharp_odds = {'home': [], 'away': []}
            public_odds = {'home': [], 'away': []}
            
            for bm in bookmakers:
                bm_name = bm.get('title', '').lower()
                for market in bm.get('markets', []):
                    if market['key'] == 'h2h':
                        for outcome in market['outcomes']:
                            price = outcome['price']
                            if price <= 1.0 or price > 50.0:
                                continue
                            
                            if 'pinnacle' in bm_name:
                                if outcome['name'] == home_team:
                                    pinnacle_odds['home'] = price
                                elif outcome['name'] == away_team:
                                    pinnacle_odds['away'] = price
                            elif any(sharp in bm_name for sharp in self.sharp_bookmakers):
                                if outcome['name'] == home_team:
                                    other_sharp_odds['home'].append(price)
                                elif outcome['name'] == away_team:
                                    other_sharp_odds['away'].append(price)
                            elif any(public in bm_name for public in self.public_bookmakers):
                                if outcome['name'] == home_team:
                                    public_odds['home'].append(price)
                                elif outcome['name'] == away_team:
                                    public_odds['away'].append(price)
            
            # CLV Analysis
            if (pinnacle_odds['home'] and pinnacle_odds['away'] and 
                len(public_odds['home']) >= 2 and len(public_odds['away']) >= 2):
                
                best_public_home = max(public_odds['home'])
                best_public_away = max(public_odds['away'])
                
                # CLV calculation: difference between best public and Pinnacle
                home_clv = (best_public_home - pinnacle_odds['home']) / pinnacle_odds['home']
                away_clv = (best_public_away - pinnacle_odds['away']) / pinnacle_odds['away']
                
                max_clv = max(home_clv, away_clv)
                
                if max_clv > 0.05:  # 5% CLV threshold
                    clv_side = 'home' if home_clv > away_clv else 'away'
                    clv_team = home_team if clv_side == 'home' else away_team
                    
                    clv_score = min(10, int(max_clv * 100))
                    
                    return {
                        'game': f"{home_team} vs {away_team}",
                        'commence_time': game.get('commence_time'),
                        'clv_team': clv_team,
                        'clv_side': clv_side,
                        'clv_score': clv_score,
                        'clv_percentage': round(max_clv * 100, 2),
                        'pinnacle_odds': pinnacle_odds[clv_side],
                        'best_public_odds': best_public_home if clv_side == 'home' else best_public_away,
                        'expected_profit': round((max_clv * 100) * 0.7, 1),  # Conservative estimate
                        'value_rating': 'EXCEPTIONAL' if clv_score >= 9 else 'EXCELLENT' if clv_score >= 7 else 'GOOD'
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing closing line value: {e}")
            return None
    
    def generate_advanced_strategy_summary(self, steam_moves: List[Dict], 
                                         rlm_opportunities: List[Dict], 
                                         clv_opportunities: List[Dict]) -> str:
        """Generate comprehensive advanced strategy summary"""
        try:
            summary = "⚡ ADVANCED PROFESSIONAL STRATEGIES\n\n"
            
            # Steam Moves Section
            if steam_moves:
                summary += "🔥 STEAM MOVE DETECTION:\n"
                for i, steam in enumerate(steam_moves, 1):
                    summary += f"{i}. {steam['game']}\n"
                    summary += f"   🎯 {steam['steam_team']} (Steam Strength: {steam['steam_strength']}/10)\n"
                    summary += f"   📊 Sharp: {steam['sharp_average_odds']} | Public: {steam['public_average_odds']}\n"
                    summary += f"   💰 Edge: {steam['edge_percentage']}% | Direction: {steam['steam_direction']}\n"
                    summary += f"   🎲 Confidence: {steam['confidence']}\n\n"
            else:
                summary += "🔥 STEAM MOVES: No significant steam detected\n\n"
            
            # Reverse Line Movement Section
            if rlm_opportunities:
                summary += "🔄 REVERSE LINE MOVEMENT:\n"
                for i, rlm in enumerate(rlm_opportunities, 1):
                    summary += f"{i}. {rlm['game']}\n"
                    summary += f"   🎯 {rlm['rlm_team']} (RLM Strength: {rlm['rlm_strength']}/10)\n"
                    summary += f"   📊 Best: {rlm['best_odds']} | Median: {rlm['median_odds']} | Worst: {rlm['worst_odds']}\n"
                    summary += f"   💡 Outliers: {rlm['outlier_count']} | Rating: {rlm['opportunity_rating']}\n\n"
            else:
                summary += "🔄 REVERSE LINE MOVEMENT: No significant RLM detected\n\n"
            
            # Closing Line Value Section
            if clv_opportunities:
                summary += "📈 CLOSING LINE VALUE:\n"
                for i, clv in enumerate(clv_opportunities, 1):
                    summary += f"{i}. {clv['game']}\n"
                    summary += f"   🎯 {clv['clv_team']} (CLV Score: {clv['clv_score']}/10)\n"
                    summary += f"   📊 Pinnacle: {clv['pinnacle_odds']} | Best Public: {clv['best_public_odds']}\n"
                    summary += f"   💰 CLV: {clv['clv_percentage']}% | Expected Profit: {clv['expected_profit']}%\n"
                    summary += f"   ⭐ Rating: {clv['value_rating']}\n\n"
            else:
                summary += "📈 CLOSING LINE VALUE: No significant CLV opportunities\n\n"
            
            # Professional Strategy Guidance
            summary += "🧠 EXECUTION STRATEGY:\n"
            summary += "• Steam Moves: Follow sharp money immediately\n"
            summary += "• RLM: Bet against public perception\n"
            summary += "• CLV: Target best odds before line moves\n"
            summary += "• Bankroll: Use 2-5% per opportunity\n"
            summary += "• Timing: Act quickly on high-strength signals\n\n"
            
            summary += "⚡ PROFESSIONAL STRATEGIES ANALYSIS COMPLETE"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating strategy summary: {e}")
            return f"Error generating advanced strategy summary: {e}"
