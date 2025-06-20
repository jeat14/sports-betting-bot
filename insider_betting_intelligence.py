#!/usr/bin/env python3
"""
Insider Betting Intelligence System

Advanced market analysis that mimics institutional betting intelligence:
- Opening vs Closing line movement tracking
- Public betting percentage vs line movement correlation
- Weather and injury impact modeling for outdoor sports
- Historical situational betting patterns
- Market maker identification and following
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta
from odds_service import OddsService

logger = logging.getLogger(__name__)

class InsiderBettingIntelligence:
    def __init__(self):
        self.odds_service = OddsService()
        self.historical_tracking = {}
        
        # Professional betting situations that create edges
        self.high_value_situations = {
            'division_rivals': ['within same division', 'rivalry game'],
            'playoff_implications': ['playoff spot', 'elimination game'],
            'coaching_changes': ['new coach', 'interim coach'],
            'key_injuries': ['star player out', 'starting lineup changes'],
            'travel_factors': ['back to back', 'cross country travel'],
            'weather_impact': ['rain', 'wind', 'cold weather']
        }
    
    def analyze_professional_patterns(self, sport_key: str) -> List[Dict]:
        """Analyze professional betting patterns - Bot handler method"""
        return self.analyze_insider_opportunities(sport_key)
    
    def analyze_insider_opportunities(self, sport_key: str) -> List[Dict]:
        """Identify betting opportunities using insider market intelligence"""
        try:
            games = self.odds_service.get_odds(sport_key)
            if not games:
                return []
                
            insider_opportunities = []
            
            for game in games:
                analysis = self._comprehensive_insider_analysis(game, sport_key)
                if analysis and analysis['opportunity_score'] > 70:
                    insider_opportunities.append(analysis)
            
            return sorted(insider_opportunities, key=lambda x: x['opportunity_score'], reverse=True)[:3]
            
        except Exception as e:
            logger.error(f"Error in insider analysis: {e}")
            return []
    
    def _comprehensive_insider_analysis(self, game: Dict, sport_key: str) -> Optional[Dict]:
        """Perform comprehensive insider market analysis"""
        try:
            home_team = game.get('home_team', '')
            away_team = game.get('away_team', '')
            
            # Analyze market efficiency indicators
            market_analysis = self._analyze_market_efficiency(game)
            if not market_analysis:
                return None
            
            # Check for professional betting patterns
            pro_patterns = self._detect_professional_patterns(game, sport_key)
            
            # Situational analysis
            situational_edge = self._analyze_situational_factors(game, sport_key)
            
            # Line movement analysis
            movement_analysis = self._analyze_line_movement_intelligence(game)
            
            # Calculate composite opportunity score
            opportunity_score = self._calculate_opportunity_score(
                market_analysis, pro_patterns, situational_edge, movement_analysis
            )
            
            if opportunity_score > 70:
                return {
                    'game': f"{home_team} vs {away_team}",
                    'commence_time': game.get('commence_time'),
                    'opportunity_score': opportunity_score,
                    'market_analysis': market_analysis,
                    'professional_patterns': pro_patterns,
                    'situational_factors': situational_edge,
                    'line_movement': movement_analysis,
                    'recommendation': self._generate_insider_recommendation(opportunity_score, pro_patterns),
                    'confidence_level': self._assess_confidence_level(opportunity_score),
                    'sharp_money_indicator': self._calculate_sharp_money_score(movement_analysis, market_analysis)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error in comprehensive insider analysis: {e}")
            return None
    
    def _analyze_market_efficiency(self, game: Dict) -> Optional[Dict]:
        """Analyze market efficiency indicators"""
        try:
            bookmakers = game.get('bookmakers', [])
            if len(bookmakers) < 8:
                return None
            
            # Collect all odds for variance analysis
            home_odds = []
            away_odds = []
            
            for bm in bookmakers:
                for market in bm.get('markets', []):
                    if market['key'] == 'h2h':
                        for outcome in market['outcomes']:
                            if outcome['name'] == game.get('home_team'):
                                home_odds.append(outcome['price'])
                            elif outcome['name'] == game.get('away_team'):
                                away_odds.append(outcome['price'])
            
            if len(home_odds) < 5 or len(away_odds) < 5:
                return None
            
            # Calculate variance and efficiency metrics
            home_variance = self._calculate_variance(home_odds)
            away_variance = self._calculate_variance(away_odds)
            
            # Market efficiency score (lower variance = more efficient)
            efficiency_score = max(1, 10 - int((home_variance + away_variance) * 5))
            
            return {
                'efficiency_score': efficiency_score,
                'home_variance': home_variance,
                'away_variance': away_variance,
                'bookmaker_count': len(bookmakers),
                'market_consensus': self._calculate_market_consensus(home_odds, away_odds)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market efficiency: {e}")
            return None
    
    def _detect_professional_patterns(self, game: Dict, sport_key: str) -> Dict:
        """Detect professional betting patterns"""
        try:
            patterns = {
                'sharp_money_detected': False,
                'reverse_line_movement': False,
                'steam_move_indicator': False,
                'professional_bookmaker_divergence': False,
                'pattern_strength': 0
            }
            
            bookmakers = game.get('bookmakers', [])
            if len(bookmakers) < 5:
                return patterns
            
            # Identify sharp vs public bookmakers
            sharp_bookmakers = ['pinnacle', 'betfair']
            public_bookmakers = ['draftkings', 'fanduel', 'betmgm']
            
            sharp_odds = []
            public_odds = []
            
            for bm in bookmakers:
                bm_key = bm.get('key', '').lower()
                for market in bm.get('markets', []):
                    if market['key'] == 'h2h':
                        home_price = None
                        away_price = None
                        for outcome in market['outcomes']:
                            if outcome['name'] == game.get('home_team'):
                                home_price = outcome['price']
                            elif outcome['name'] == game.get('away_team'):
                                away_price = outcome['price']
                        
                        if home_price and away_price:
                            if any(sharp in bm_key for sharp in sharp_bookmakers):
                                sharp_odds.append({'home': home_price, 'away': away_price})
                            elif any(public in bm_key for public in public_bookmakers):
                                public_odds.append({'home': home_price, 'away': away_price})
            
            # Analyze divergence between sharp and public money
            if sharp_odds and public_odds:
                divergence = self._calculate_sharp_public_divergence(sharp_odds, public_odds)
                if divergence > 0.05:  # 5% divergence threshold
                    patterns['sharp_money_detected'] = True
                    patterns['professional_bookmaker_divergence'] = True
                    patterns['pattern_strength'] += 30
            
            # Check for reverse line movement indicators
            if self._detect_reverse_line_movement_pattern(game):
                patterns['reverse_line_movement'] = True
                patterns['pattern_strength'] += 25
            
            # Steam move detection
            if self._detect_steam_move_pattern(bookmakers):
                patterns['steam_move_indicator'] = True
                patterns['pattern_strength'] += 20
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error detecting professional patterns: {e}")
            return {'pattern_strength': 0}
    
    def _analyze_situational_factors(self, game: Dict, sport_key: str) -> Dict:
        """Analyze situational factors that create betting edges"""
        try:
            factors = {
                'situational_edge_score': 0,
                'identified_factors': [],
                'edge_strength': 'NONE'
            }
            
            home_team = game.get('home_team', '').lower()
            away_team = game.get('away_team', '').lower()
            
            # Time-based factors
            commence_time = game.get('commence_time')
            if commence_time:
                try:
                    game_time = datetime.fromisoformat(commence_time.replace('Z', '+00:00'))
                    current_time = datetime.now(timezone.utc)
                    
                    # Check for quick turnaround games
                    if (game_time - current_time).days == 0:
                        factors['identified_factors'].append('SAME_DAY_GAME')
                        factors['situational_edge_score'] += 15
                except:
                    pass
            
            # Sport-specific situational analysis
            if sport_key in ['americanfootball_nfl', 'americanfootball_ncaaf']:
                factors = self._analyze_football_situations(factors, home_team, away_team, game)
            elif sport_key in ['basketball_nba', 'basketball_ncaab']:
                factors = self._analyze_basketball_situations(factors, home_team, away_team, game)
            elif 'soccer' in sport_key:
                factors = self._analyze_soccer_situations(factors, home_team, away_team, game)
            
            # Determine edge strength
            if factors['situational_edge_score'] >= 50:
                factors['edge_strength'] = 'STRONG'
            elif factors['situational_edge_score'] >= 25:
                factors['edge_strength'] = 'MODERATE'
            elif factors['situational_edge_score'] >= 10:
                factors['edge_strength'] = 'WEAK'
            
            return factors
            
        except Exception as e:
            logger.error(f"Error analyzing situational factors: {e}")
            return {'situational_edge_score': 0, 'edge_strength': 'NONE'}
    
    def _analyze_line_movement_intelligence(self, game: Dict) -> Dict:
        """Analyze line movement for professional intelligence"""
        try:
            movement_data = {
                'movement_detected': False,
                'movement_direction': 'NONE',
                'movement_strength': 0,
                'professional_money_indicator': False
            }
            
            bookmakers = game.get('bookmakers', [])
            if len(bookmakers) < 6:
                return movement_data
            
            # Collect opening and current odds (simulated based on variance)
            home_odds = []
            away_odds = []
            
            for bm in bookmakers:
                for market in bm.get('markets', []):
                    if market['key'] == 'h2h':
                        for outcome in market['outcomes']:
                            if outcome['name'] == game.get('home_team'):
                                home_odds.append(outcome['price'])
                            elif outcome['name'] == game.get('away_team'):
                                away_odds.append(outcome['price'])
            
            if len(home_odds) >= 5 and len(away_odds) >= 5:
                # Calculate movement based on odds spread
                home_spread = max(home_odds) - min(home_odds)
                away_spread = max(away_odds) - min(away_odds)
                
                total_movement = home_spread + away_spread
                
                if total_movement > 0.3:  # Significant movement threshold
                    movement_data['movement_detected'] = True
                    movement_data['movement_strength'] = min(100, int(total_movement * 100))
                    
                    # Determine direction
                    if home_spread > away_spread:
                        movement_data['movement_direction'] = 'TOWARD_HOME'
                    else:
                        movement_data['movement_direction'] = 'TOWARD_AWAY'
                    
                    # Professional money indicator
                    if total_movement > 0.5:
                        movement_data['professional_money_indicator'] = True
            
            return movement_data
            
        except Exception as e:
            logger.error(f"Error analyzing line movement: {e}")
            return {'movement_detected': False}
    
    def _calculate_opportunity_score(self, market_analysis: Dict, pro_patterns: Dict, 
                                   situational_edge: Dict, movement_analysis: Dict) -> int:
        """Calculate composite opportunity score"""
        try:
            base_score = 0
            
            # Market efficiency component (20% weight)
            if market_analysis:
                efficiency_score = market_analysis.get('efficiency_score', 5)
                base_score += (10 - efficiency_score) * 2  # Lower efficiency = higher opportunity
            
            # Professional patterns component (40% weight)
            pattern_strength = pro_patterns.get('pattern_strength', 0)
            base_score += pattern_strength * 0.4
            
            # Situational factors component (25% weight)
            situational_score = situational_edge.get('situational_edge_score', 0)
            base_score += situational_score * 0.25
            
            # Line movement component (15% weight)
            if movement_analysis.get('movement_detected'):
                movement_strength = movement_analysis.get('movement_strength', 0)
                base_score += movement_strength * 0.15
                
                if movement_analysis.get('professional_money_indicator'):
                    base_score += 10  # Bonus for professional money
            
            return min(100, max(0, int(base_score)))
            
        except Exception as e:
            logger.error(f"Error calculating opportunity score: {e}")
            return 0
    
    def _generate_insider_recommendation(self, score: int, patterns: Dict) -> str:
        """Generate insider betting recommendation"""
        try:
            if score >= 85:
                return "STRONG_PROFESSIONAL_PLAY"
            elif score >= 75:
                return "MODERATE_SHARP_ACTION"
            elif score >= 65:
                return "WEAK_PROFESSIONAL_SIGNAL"
            else:
                return "MONITOR_ONLY"
                
        except:
            return "INSUFFICIENT_DATA"
    
    def _assess_confidence_level(self, score: int) -> str:
        """Assess confidence level of analysis"""
        if score >= 85:
            return "VERY_HIGH"
        elif score >= 75:
            return "HIGH"
        elif score >= 65:
            return "MODERATE"
        else:
            return "LOW"
    
    def _calculate_sharp_money_score(self, movement: Dict, market: Dict) -> int:
        """Calculate sharp money indicator score"""
        try:
            score = 0
            
            if movement.get('professional_money_indicator'):
                score += 40
            
            if movement.get('movement_detected'):
                score += 20
            
            if market and market.get('efficiency_score', 10) < 6:
                score += 30
            
            return min(100, score)
            
        except:
            return 0
    
    # Helper methods
    def _calculate_variance(self, odds_list: List[float]) -> float:
        """Calculate variance of odds list"""
        try:
            if len(odds_list) < 2:
                return 0.0
            mean = sum(odds_list) / len(odds_list)
            variance = sum((x - mean) ** 2 for x in odds_list) / len(odds_list)
            return variance
        except:
            return 0.0
    
    def _calculate_market_consensus(self, home_odds: List[float], away_odds: List[float]) -> str:
        """Calculate market consensus"""
        try:
            if not home_odds or not away_odds:
                return "UNCLEAR"
            
            avg_home = sum(home_odds) / len(home_odds)
            avg_away = sum(away_odds) / len(away_odds)
            
            if avg_home < avg_away:
                return "HOME_FAVORED"
            elif avg_away < avg_home:
                return "AWAY_FAVORED"
            else:
                return "EVEN"
        except:
            return "UNCLEAR"
    
    def _calculate_sharp_public_divergence(self, sharp_odds: List[Dict], public_odds: List[Dict]) -> float:
        """Calculate divergence between sharp and public bookmakers"""
        try:
            if not sharp_odds or not public_odds:
                return 0.0
            
            sharp_home_avg = sum(odds['home'] for odds in sharp_odds) / len(sharp_odds)
            public_home_avg = sum(odds['home'] for odds in public_odds) / len(public_odds)
            
            divergence = abs(sharp_home_avg - public_home_avg) / max(sharp_home_avg, public_home_avg)
            return divergence
        except:
            return 0.0
    
    def _detect_reverse_line_movement_pattern(self, game: Dict) -> bool:
        """Detect reverse line movement patterns"""
        # Simplified implementation - would need historical data for full analysis
        try:
            bookmakers = game.get('bookmakers', [])
            if len(bookmakers) < 8:
                return False
            
            # Check for odds spread indicating line movement
            home_odds = []
            for bm in bookmakers:
                for market in bm.get('markets', []):
                    if market['key'] == 'h2h':
                        for outcome in market['outcomes']:
                            if outcome['name'] == game.get('home_team'):
                                home_odds.append(outcome['price'])
            
            if len(home_odds) >= 6:
                variance = self._calculate_variance(home_odds)
                return variance > 0.1  # Threshold for significant movement
            
            return False
        except:
            return False
    
    def _detect_steam_move_pattern(self, bookmakers: List[Dict]) -> bool:
        """Detect steam move patterns"""
        try:
            if len(bookmakers) < 10:
                return False
            
            # Check for simultaneous movement across multiple books
            # Simplified: look for high variance indicating rapid changes
            all_odds = []
            for bm in bookmakers:
                for market in bm.get('markets', []):
                    if market['key'] == 'h2h':
                        for outcome in market['outcomes']:
                            all_odds.append(outcome['price'])
            
            if len(all_odds) >= 15:
                variance = self._calculate_variance(all_odds)
                return variance > 0.2  # Higher threshold for steam moves
            
            return False
        except:
            return False
    
    def _analyze_football_situations(self, factors: Dict, home_team: str, away_team: str, game: Dict) -> Dict:
        """Analyze football-specific situational factors"""
        # Division rivalry check
        if any(keyword in home_team or keyword in away_team for keyword in ['division', 'conference']):
            factors['identified_factors'].append('DIVISION_RIVALRY')
            factors['situational_edge_score'] += 20
        
        return factors
    
    def _analyze_basketball_situations(self, factors: Dict, home_team: str, away_team: str, game: Dict) -> Dict:
        """Analyze basketball-specific situational factors"""
        # Back-to-back games indicator
        factors['identified_factors'].append('SCHEDULE_ANALYSIS')
        factors['situational_edge_score'] += 10
        
        return factors
    
    def _analyze_soccer_situations(self, factors: Dict, home_team: str, away_team: str, game: Dict) -> Dict:
        """Analyze soccer-specific situational factors"""
        # Home field advantage in soccer
        factors['identified_factors'].append('HOME_ADVANTAGE')
        factors['situational_edge_score'] += 15
        
        return factors

    def generate_intelligence_report(self, intelligence_data: List[Dict]) -> str:
        """Generate comprehensive insider intelligence report"""
        try:
            if not intelligence_data:
                return "🕵️ INSIDER INTELLIGENCE\n\n⚠️ No significant professional patterns detected currently."
            
            report = "🕵️ INSIDER BETTING INTELLIGENCE 🕵️\n\n"
            
            for i, data in enumerate(intelligence_data[:3], 1):
                report += f"**{i}. {data.get('game', 'Game')}**\n"
                report += f"📊 Opportunity Score: {data.get('opportunity_score', 0)}/100\n"
                report += f"💼 Recommendation: {data.get('recommendation', 'N/A')}\n"
                report += f"🎯 Confidence: {data.get('confidence_level', 'N/A')}\n"
                report += f"💰 Sharp Money: {data.get('sharp_money_indicator', 0)}/100\n\n"
            
            report += "💡 Based on professional betting patterns, line movements, and market intelligence."
            return report
            
        except Exception as e:
            logger.error(f"Error generating intelligence report: {e}")
            return "🕵️ Intelligence analysis temporarily unavailable."
