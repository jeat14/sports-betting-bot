#!/usr/bin/env python3
"""
Advanced Horse Racing Advantage System

Professional multi-outcome betting analysis using racing-style strategies:
- Value betting through odds disparity analysis
- Late money movement detection patterns
- Multi-sport advantage identification
- Professional pattern recognition
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone
from odds_service import OddsService
import statistics

logger = logging.getLogger(__name__)

class HorseRacingAdvantageSystem:
    def __init__(self):
        self.odds_service = OddsService()
    
    def analyze_racing_opportunities(self, region: str = 'us') -> List[Dict]:
        """Analyze sports with multi-outcome betting patterns similar to horse racing"""
        try:
            # Use sports with multiple outcomes for racing-style analysis
            multi_outcome_sports = ['baseball_mlb', 'basketball_nba', 'soccer_epl']
            all_advantages = []
            
            for sport_key in multi_outcome_sports:
                try:
                    games = self.odds_service.get_odds(sport_key)
                    if not games:
                        continue
                    
                    for game in games[:2]:  # Analyze top 2 games per sport
                        analysis = self._comprehensive_analysis(game, sport_key)
                        if analysis and analysis['advantage_score'] > 65:
                            all_advantages.append(analysis)
                except Exception as e:
                    logger.error(f"Error analyzing {sport_key}: {e}")
                    continue
            
            return sorted(all_advantages, key=lambda x: x['advantage_score'], reverse=True)[:5]
            
        except Exception as e:
            logger.error(f"Error analyzing opportunities: {e}")
            return []
    
    def _comprehensive_analysis(self, game: Dict, sport_key: str) -> Optional[Dict]:
        """Perform comprehensive analysis for multi-outcome betting advantages"""
        try:
            game_name = f"{game.get('home_team', '')} vs {game.get('away_team', '')}"
            
            # Analyze odds patterns for value
            odds_analysis = self._analyze_odds_patterns(game)
            if not odds_analysis:
                return None
            
            # Detect movement patterns
            movement_analysis = self._detect_movement_patterns(game)
            
            # Professional indicators
            pro_indicators = self._detect_professional_indicators(game)
            
            # Calculate composite advantage score
            advantage_score = self._calculate_advantage_score(
                odds_analysis, movement_analysis, pro_indicators
            )
            
            if advantage_score > 65:
                return {
                    'game': game_name,
                    'sport': sport_key.upper(),
                    'commence_time': game.get('commence_time'),
                    'advantage_score': advantage_score,
                    'recommended_selection': odds_analysis.get('best_value'),
                    'best_odds': odds_analysis.get('best_odds'),
                    'value_percentage': odds_analysis.get('value_percentage', 0),
                    'movement_strength': movement_analysis.get('strength', 'NONE'),
                    'professional_signals': pro_indicators,
                    'betting_strategy': self._generate_strategy(advantage_score, odds_analysis),
                    'confidence_level': self._determine_confidence(advantage_score),
                    'expected_roi': self._calculate_roi(odds_analysis, advantage_score)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            return None
    
    def _analyze_odds_patterns(self, game: Dict) -> Optional[Dict]:
        """Analyze odds patterns for value betting opportunities"""
        try:
            bookmakers = game.get('bookmakers', [])
            if len(bookmakers) < 4:
                return None
            
            # Collect odds for both teams
            home_odds = []
            away_odds = []
            
            for bm in bookmakers:
                for market in bm.get('markets', []):
                    if market['key'] == 'h2h':
                        for outcome in market['outcomes']:
                            odds = outcome['price']
                            if 1.1 <= odds <= 20.0:  # Reasonable odds range
                                if outcome['name'] == game.get('home_team'):
                                    home_odds.append(odds)
                                elif outcome['name'] == game.get('away_team'):
                                    away_odds.append(odds)
            
            if len(home_odds) < 3 or len(away_odds) < 3:
                return None
            
            # Find value opportunities
            home_best = max(home_odds)
            home_avg = statistics.mean(home_odds)
            away_best = max(away_odds)
            away_avg = statistics.mean(away_odds)
            
            home_value = ((home_best - home_avg) / home_avg) * 100
            away_value = ((away_best - away_avg) / away_avg) * 100
            
            # Return best value opportunity
            if home_value > away_value and home_value > 5.0:
                return {
                    'best_value': game.get('home_team'),
                    'best_odds': home_best,
                    'average_odds': round(home_avg, 2),
                    'value_percentage': round(home_value, 2)
                }
            elif away_value > 5.0:
                return {
                    'best_value': game.get('away_team'),
                    'best_odds': away_best,
                    'average_odds': round(away_avg, 2),
                    'value_percentage': round(away_value, 2)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing odds patterns: {e}")
            return None
    
    def _detect_movement_patterns(self, game: Dict) -> Dict:
        """Detect movement patterns indicating smart money"""
        movement = {
            'strength': 'NONE',
            'score': 0
        }
        
        try:
            bookmakers = game.get('bookmakers', [])
            if len(bookmakers) < 6:
                return movement
            
            # Analyze odds variance as proxy for movement
            all_odds = []
            for bm in bookmakers:
                for market in bm.get('markets', []):
                    if market['key'] == 'h2h':
                        for outcome in market['outcomes']:
                            odds = outcome['price']
                            if 1.2 <= odds <= 15.0:
                                all_odds.append(odds)
            
            if len(all_odds) >= 8:
                variance = statistics.variance(all_odds)
                
                if variance > 6.0:
                    movement['strength'] = 'STRONG'
                    movement['score'] = 25
                elif variance > 3.0:
                    movement['strength'] = 'MODERATE'
                    movement['score'] = 15
                elif variance > 1.5:
                    movement['strength'] = 'MILD'
                    movement['score'] = 8
            
            return movement
            
        except Exception as e:
            logger.error(f"Error detecting movement patterns: {e}")
            return movement
    
    def _detect_professional_indicators(self, game: Dict) -> Dict:
        """Detect professional betting indicators"""
        indicators = {
            'market_depth': 0,
            'efficiency_score': 0,
            'total_score': 0
        }
        
        try:
            bookmakers = game.get('bookmakers', [])
            
            # Market depth indicates professional interest
            if len(bookmakers) >= 8:
                indicators['market_depth'] = 15
            elif len(bookmakers) >= 6:
                indicators['market_depth'] = 10
            
            # Efficiency analysis
            if len(bookmakers) >= 6:
                home_odds = []
                for bm in bookmakers:
                    for market in bm.get('markets', []):
                        if market['key'] == 'h2h':
                            for outcome in market['outcomes']:
                                if outcome['name'] == game.get('home_team'):
                                    home_odds.append(outcome['price'])
                                    break
                
                if len(home_odds) >= 6:
                    odds_range = (max(home_odds) - min(home_odds)) / min(home_odds)
                    if odds_range < 0.15:  # Tight market indicates efficiency
                        indicators['efficiency_score'] = 15
                    elif odds_range < 0.25:
                        indicators['efficiency_score'] = 10
            
            indicators['total_score'] = indicators['market_depth'] + indicators['efficiency_score']
            return indicators
            
        except Exception as e:
            logger.error(f"Error detecting professional indicators: {e}")
            return indicators
    
    def _calculate_advantage_score(self, odds_analysis: Dict, movement_analysis: Dict, 
                                 pro_indicators: Dict) -> int:
        """Calculate composite advantage score"""
        score = 0
        
        # Odds value component
        if odds_analysis:
            value_pct = odds_analysis.get('value_percentage', 0)
            if value_pct > 15:
                score += 35
            elif value_pct > 10:
                score += 25
            elif value_pct > 5:
                score += 15
        
        # Movement component
        score += movement_analysis.get('score', 0)
        
        # Professional indicators
        score += pro_indicators.get('total_score', 0)
        
        return min(score, 100)
    
    def _generate_strategy(self, advantage_score: int, odds_analysis: Dict) -> str:
        """Generate specific betting strategy"""
        if advantage_score >= 85:
            return "STRONG VALUE BET - Multiple advantage factors align"
        elif advantage_score >= 75:
            return "VALUE BET - Good opportunity detected"
        elif advantage_score >= 65:
            return "MODERATE VALUE - Edge identified"
        else:
            return "PASS - Insufficient advantage"
    
    def _determine_confidence(self, advantage_score: int) -> str:
        """Determine confidence level"""
        if advantage_score >= 90:
            return "VERY HIGH"
        elif advantage_score >= 80:
            return "HIGH"
        elif advantage_score >= 70:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _calculate_roi(self, odds_analysis: Dict, advantage_score: int) -> float:
        """Calculate expected ROI"""
        if not odds_analysis:
            return 0.0
        
        base_roi = odds_analysis.get('value_percentage', 0) * 0.4
        
        # Adjust for advantage score
        if advantage_score >= 85:
            base_roi *= 1.5
        elif advantage_score >= 75:
            base_roi *= 1.2
        
        return round(base_roi, 1)
    
    def generate_racing_report(self, regions: List[str] = ['us', 'uk', 'aus']) -> str:
        """Generate comprehensive racing-style advantage report"""
        try:
            opportunities = self.analyze_racing_opportunities()
            
            if not opportunities:
                return "🏇 RACING-STYLE ADVANTAGE ANALYSIS\n\nNo significant advantages found across sports (65+ threshold)"
            
            report = "🏇 RACING-STYLE ADVANTAGE SYSTEM\n\n"
            report += f"🎯 PREMIUM VALUE OPPORTUNITIES ({len(opportunities)} found):\n\n"
            
            for i, opp in enumerate(opportunities, 1):
                report += f"{i}. {opp['game']} ({opp['sport']})\n"
                report += f"   🎯 {opp['recommended_selection']} @ {opp['best_odds']}\n"
                report += f"   📊 Advantage Score: {opp['advantage_score']}/100\n"
                report += f"   💰 Value Edge: {opp['value_percentage']}%\n"
                report += f"   📈 Expected ROI: {opp['expected_roi']}%\n"
                report += f"   🎲 Strategy: {opp['betting_strategy']}\n"
                report += f"   💡 Confidence: {opp['confidence_level']}\n"
                if opp['movement_strength'] != 'NONE':
                    report += f"   🔥 Movement: {opp['movement_strength']}\n"
                report += "\n"
            
            report += "🧠 RACING-STYLE METHODOLOGY:\n"
            report += "• Value betting through odds disparity analysis\n"
            report += "• Smart money movement detection\n"
            report += "• Professional market indicators\n"
            report += "• Multi-sport opportunity scanning\n"
            report += "• Racing-inspired advantage calculation\n\n"
            
            report += "⚡ EXECUTION STRATEGY:\n"
            report += "1. STRONG VALUE BETS - Immediate action (85+ scores)\n"
            report += "2. Focus on 15%+ value edges for maximum profit\n"
            report += "3. Monitor movement patterns for confirmation\n"
            report += "4. Use 2-4% bankroll sizing for value bets\n\n"
            
            report += "🏇 PROFESSIONAL ADVANTAGE ANALYSIS COMPLETE"
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating racing report: {e}")
            return f"Error generating racing-style advantage report: {e}"
