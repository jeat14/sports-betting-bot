#!/usr/bin/env python3
"""
Enhanced Risk Management System

Advanced risk assessment and bankroll protection to minimize losses
and improve long-term profitability. Includes upset detection and
conservative betting strategies.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class EnhancedRiskManagement:
    def __init__(self):
        self.historical_upsets = []
        self.conservative_mode = True
        self.max_single_bet_percentage = 0.02  # 2% max per bet
        
    def assess_bet_risk(self, game_data: Dict, bet_amount: float, bankroll: float) -> Dict:
        """Comprehensive risk assessment before placing any bet"""
        try:
            risk_factors = {
                'upset_probability': self._calculate_upset_probability(game_data),
                'odds_reliability': self._assess_odds_reliability(game_data),
                'market_efficiency': self._analyze_market_efficiency(game_data),
                'historical_performance': self._check_historical_performance(game_data),
                'bankroll_risk': self._assess_bankroll_risk(bet_amount, bankroll)
            }
            
            # Calculate overall risk score (0-100, higher = riskier)
            overall_risk = self._calculate_overall_risk(risk_factors)
            
            # Generate recommendation
            recommendation = self._generate_risk_recommendation(overall_risk, risk_factors)
            
            return {
                'overall_risk_score': overall_risk,
                'risk_factors': risk_factors,
                'recommendation': recommendation,
                'suggested_bet_size': self._calculate_safe_bet_size(overall_risk, bankroll),
                'confidence_level': self._assess_confidence(overall_risk)
            }
            
        except Exception as e:
            logger.error(f"Error in risk assessment: {e}")
            return {
                'overall_risk_score': 100,
                'recommendation': 'AVOID - Unable to assess risk properly',
                'suggested_bet_size': 0
            }
    
    def _calculate_upset_probability(self, game_data: Dict) -> float:
        """Calculate probability of upset based on various factors"""
        try:
            home_team = game_data.get('home_team', '')
            away_team = game_data.get('away_team', '')
            
            # Get odds data
            bookmakers = game_data.get('bookmakers', [])
            if not bookmakers:
                return 0.5  # High uncertainty
            
            # Find shortest odds (favorite)
            shortest_odds = float('inf')
            for bm in bookmakers:
                for market in bm.get('markets', []):
                    if market['key'] == 'h2h':
                        for outcome in market['outcomes']:
                            odds = outcome.get('price', float('inf'))
                            if odds < shortest_odds:
                                shortest_odds = odds
            
            # Calculate upset probability based on favorite's odds
            if shortest_odds <= 1.10:
                return 0.15  # 15% upset chance for heavy favorites
            elif shortest_odds <= 1.25:
                return 0.25  # 25% upset chance
            elif shortest_odds <= 1.50:
                return 0.35  # 35% upset chance
            else:
                return 0.45  # 45% upset chance for closer matches
                
        except Exception as e:
            logger.error(f"Error calculating upset probability: {e}")
            return 0.5
    
    def _assess_odds_reliability(self, game_data: Dict) -> float:
        """Assess how reliable the current odds are"""
        try:
            bookmakers = game_data.get('bookmakers', [])
            if len(bookmakers) < 5:
                return 0.3  # Low reliability with few bookmakers
            
            # Calculate odds variance
            all_odds = []
            for bm in bookmakers:
                for market in bm.get('markets', []):
                    if market['key'] == 'h2h':
                        for outcome in market['outcomes']:
                            all_odds.append(outcome.get('price', 0))
            
            if len(all_odds) < 10:
                return 0.4
            
            # Calculate variance
            mean_odds = sum(all_odds) / len(all_odds)
            variance = sum((x - mean_odds) ** 2 for x in all_odds) / len(all_odds)
            
            # Lower variance = higher reliability
            if variance < 0.1:
                return 0.9  # High reliability
            elif variance < 0.3:
                return 0.7  # Good reliability
            elif variance < 0.5:
                return 0.5  # Moderate reliability
            else:
                return 0.3  # Low reliability
                
        except Exception as e:
            logger.error(f"Error assessing odds reliability: {e}")
            return 0.4
    
    def _analyze_market_efficiency(self, game_data: Dict) -> float:
        """Analyze how efficient the betting market is for this game"""
        try:
            bookmakers = game_data.get('bookmakers', [])
            
            # More bookmakers = more efficient market
            efficiency_score = min(len(bookmakers) / 15.0, 1.0)
            
            # Check for major bookmakers
            major_bookmakers = ['pinnacle', 'bet365', 'william_hill', 'betfair']
            major_count = 0
            
            for bm in bookmakers:
                bm_key = bm.get('key', '').lower()
                if any(major in bm_key for major in major_bookmakers):
                    major_count += 1
            
            # Boost efficiency if major bookmakers present
            if major_count >= 3:
                efficiency_score = min(efficiency_score + 0.2, 1.0)
            
            return efficiency_score
            
        except Exception as e:
            logger.error(f"Error analyzing market efficiency: {e}")
            return 0.5
    
    def _check_historical_performance(self, game_data: Dict) -> float:
        """Check historical performance of similar betting scenarios"""
        try:
            # This would check against historical upset database
            # For now, return conservative estimate
            home_team = game_data.get('home_team', '')
            away_team = game_data.get('away_team', '')
            
            # Look for known upset-prone teams or scenarios
            upset_prone_keywords = ['city fc', 'united fc', 'championship', 'division']
            
            teams = [home_team.lower(), away_team.lower()]
            for team in teams:
                if any(keyword in team for keyword in upset_prone_keywords):
                    return 0.6  # Slightly higher upset risk
            
            return 0.7  # Default historical reliability
            
        except Exception as e:
            logger.error(f"Error checking historical performance: {e}")
            return 0.5
    
    def _assess_bankroll_risk(self, bet_amount: float, bankroll: float) -> float:
        """Assess risk to overall bankroll"""
        try:
            if bankroll <= 0:
                return 1.0  # Maximum risk
            
            bet_percentage = bet_amount / bankroll
            
            if bet_percentage > 0.10:  # More than 10%
                return 1.0  # Very high risk
            elif bet_percentage > 0.05:  # 5-10%
                return 0.8  # High risk
            elif bet_percentage > 0.02:  # 2-5%
                return 0.6  # Moderate risk
            elif bet_percentage > 0.01:  # 1-2%
                return 0.4  # Low risk
            else:  # Less than 1%
                return 0.2  # Very low risk
                
        except Exception as e:
            logger.error(f"Error assessing bankroll risk: {e}")
            return 1.0
    
    def _calculate_overall_risk(self, risk_factors: Dict) -> int:
        """Calculate overall risk score from individual factors"""
        try:
            # Weight the different risk factors
            weights = {
                'upset_probability': 0.3,
                'odds_reliability': 0.25,
                'market_efficiency': 0.2,
                'historical_performance': 0.15,
                'bankroll_risk': 0.1
            }
            
            weighted_risk = 0
            for factor, value in risk_factors.items():
                if factor in weights:
                    # Convert to risk (1 - reliability factors)
                    if factor in ['odds_reliability', 'market_efficiency', 'historical_performance']:
                        risk_value = 1 - value
                    else:
                        risk_value = value
                    
                    weighted_risk += weights[factor] * risk_value
            
            return int(weighted_risk * 100)
            
        except Exception as e:
            logger.error(f"Error calculating overall risk: {e}")
            return 100
    
    def _generate_risk_recommendation(self, risk_score: int, risk_factors: Dict) -> str:
        """Generate betting recommendation based on risk assessment"""
        try:
            if risk_score >= 80:
                return "AVOID - Very high risk of loss"
            elif risk_score >= 60:
                return "CAUTION - High risk, consider smaller bet"
            elif risk_score >= 40:
                return "MODERATE - Standard risk management applies"
            elif risk_score >= 20:
                return "LOW RISK - Good betting opportunity"
            else:
                return "VERY LOW RISK - Excellent opportunity"
                
        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            return "AVOID - Unable to assess properly"
    
    def _calculate_safe_bet_size(self, risk_score: int, bankroll: float) -> float:
        """Calculate safe bet size based on risk assessment"""
        try:
            if risk_score >= 80:
                return 0  # Don't bet
            elif risk_score >= 60:
                max_percentage = 0.005  # 0.5%
            elif risk_score >= 40:
                max_percentage = 0.01   # 1%
            elif risk_score >= 20:
                max_percentage = 0.02   # 2%
            else:
                max_percentage = 0.03   # 3%
            
            return bankroll * max_percentage
            
        except Exception as e:
            logger.error(f"Error calculating safe bet size: {e}")
            return 0
    
    def _assess_confidence(self, risk_score: int) -> str:
        """Assess confidence level in the risk assessment"""
        if risk_score >= 80:
            return "HIGH_CONFIDENCE_AVOID"
        elif risk_score >= 60:
            return "MODERATE_CONFIDENCE"
        elif risk_score >= 40:
            return "GOOD_CONFIDENCE"
        else:
            return "HIGH_CONFIDENCE_BET"
    
    def generate_risk_report(self, risk_assessment: Dict) -> str:
        """Generate comprehensive risk management report"""
        try:
            report = "🛡️ ENHANCED RISK ASSESSMENT 🛡️\n\n"
            
            risk_score = risk_assessment.get('overall_risk_score', 100)
            recommendation = risk_assessment.get('recommendation', 'AVOID')
            suggested_bet = risk_assessment.get('suggested_bet_size', 0)
            confidence = risk_assessment.get('confidence_level', 'LOW')
            
            report += f"📊 OVERALL RISK SCORE: {risk_score}/100\n"
            report += f"⚠️ RECOMMENDATION: {recommendation}\n"
            report += f"💰 SUGGESTED BET SIZE: ${suggested_bet:.2f}\n"
            report += f"🎯 CONFIDENCE: {confidence}\n\n"
            
            risk_factors = risk_assessment.get('risk_factors', {})
            if risk_factors:
                report += "🔍 RISK FACTORS:\n"
                
                upset_prob = risk_factors.get('upset_probability', 0)
                report += f"• Upset Probability: {upset_prob:.1%}\n"
                
                odds_rel = risk_factors.get('odds_reliability', 0)
                report += f"• Odds Reliability: {odds_rel:.1%}\n"
                
                market_eff = risk_factors.get('market_efficiency', 0)
                report += f"• Market Efficiency: {market_eff:.1%}\n"
                
                hist_perf = risk_factors.get('historical_performance', 0)
                report += f"• Historical Performance: {hist_perf:.1%}\n"
                
                bankroll_risk = risk_factors.get('bankroll_risk', 0)
                report += f"• Bankroll Risk: {bankroll_risk:.1%}\n\n"
            
            report += "💡 RISK MANAGEMENT TIPS:\n"
            report += "• Never bet more than 2-3% of bankroll on single bet\n"
            report += "• Avoid heavy favorites with odds below 1.10\n"
            report += "• Wait for multiple bookmaker confirmation\n"
            report += "• Consider hedging on high-value bets\n"
            report += "• Track all bets for performance analysis\n"
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating risk report: {e}")
            return "🛡️ Risk assessment temporarily unavailable"
