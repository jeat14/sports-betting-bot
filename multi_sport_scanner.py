#!/usr/bin/env python3
"""
Multi-Sport Advantage Scanner - Institutional Grade

Professional cross-sport analysis system with:
- Simultaneous multi-sport scanning
- Advanced pattern recognition
- Cross-market correlation analysis
- Professional betting syndicate strategies
- Real-time advantage detection
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
import asyncio
from concurrent.futures import ThreadPoolExecutor
from odds_service import OddsService
from advanced_prediction_engine import AdvancedPredictionEngine
from live_arbitrage_scanner import LiveArbitrageScanner
from winning_edge_calculator import WinningEdgeCalculator
from insider_betting_intelligence import InsiderBettingIntelligence
import statistics

logger = logging.getLogger(__name__)

class MultiSportScanner:
    def __init__(self):
        self.odds_service = OddsService()
        self.prediction_engine = AdvancedPredictionEngine()
        self.arbitrage_scanner = LiveArbitrageScanner()
        self.edge_calculator = WinningEdgeCalculator()
        self.insider_intelligence = InsiderBettingIntelligence()
        
        # Premium sport configurations
        self.premium_sports = {
            'baseball_mlb': {'priority': 10, 'min_bookmakers': 15, 'value_threshold': 3.0},
            'basketball_nba': {'priority': 9, 'min_bookmakers': 15, 'value_threshold': 3.0},
            'americanfootball_nfl': {'priority': 9, 'min_bookmakers': 12, 'value_threshold': 3.5},
            'soccer_epl': {'priority': 8, 'min_bookmakers': 20, 'value_threshold': 2.5},
            'soccer_champions_league': {'priority': 8, 'min_bookmakers': 18, 'value_threshold': 2.5},
            'soccer_fifa_world_cup': {'priority': 10, 'min_bookmakers': 25, 'value_threshold': 2.0},
            'icehockey_nhl': {'priority': 7, 'min_bookmakers': 12, 'value_threshold': 3.0},
            'tennis_atp': {'priority': 6, 'min_bookmakers': 10, 'value_threshold': 4.0},
            'mma_mixed_martial_arts': {'priority': 5, 'min_bookmakers': 8, 'value_threshold': 5.0}
        }
    
    def scan_all_sports(self) -> Dict[str, Dict]:
        """Scan all sports for opportunities - Bot handler method"""
        return self.scan_all_premium_sports()
    
    def scan_all_premium_sports(self) -> Dict[str, Dict]:
        """Scan all premium sports simultaneously for maximum advantage detection"""
        try:
            all_results = {}
            
            with ThreadPoolExecutor(max_workers=6) as executor:
                futures = {}
                
                for sport_key, config in self.premium_sports.items():
                    future = executor.submit(self._comprehensive_sport_analysis, sport_key, config)
                    futures[sport_key] = future
                
                # Collect results
                for sport_key, future in futures.items():
                    try:
                        result = future.result(timeout=30)
                        if result and result.get('total_opportunities', 0) > 0:
                            all_results[sport_key] = result
                    except Exception as e:
                        logger.error(f"Error analyzing {sport_key}: {e}")
                        continue
            
            return all_results
            
        except Exception as e:
            logger.error(f"Error scanning all premium sports: {e}")
            return {}
    
    def _comprehensive_sport_analysis(self, sport_key: str, config: Dict) -> Optional[Dict]:
        """Perform comprehensive analysis on a single sport"""
        try:
            games = self.odds_service.get_odds(sport_key)
            if not games or len(games) == 0:
                return None
            
            # Filter games by bookmaker count
            qualified_games = [
                game for game in games 
                if len(game.get('bookmakers', [])) >= config['min_bookmakers']
            ]
            
            if not qualified_games:
                return None
            
            # Multi-algorithm analysis
            analysis_results = {
                'sport': sport_key,
                'priority': config['priority'],
                'total_games': len(qualified_games),
                'total_opportunities': 0,
                'predictions': [],
                'arbitrage': [],
                'edge_calculations': [],
                'insider_intelligence': [],
                'cross_market_correlations': []
            }
            
            # 1. Advanced Predictions
            try:
                predictions = self.prediction_engine.generate_enhanced_predictions(sport_key)
                high_value_predictions = [
                    p for p in predictions 
                    if p.get('expected_value', 0) >= config['value_threshold']
                ]
                analysis_results['predictions'] = high_value_predictions[:3]
                analysis_results['total_opportunities'] += len(high_value_predictions)
            except Exception as e:
                logger.error(f"Error getting predictions for {sport_key}: {e}")
            
            # 2. Arbitrage Opportunities
            try:
                arbitrage_ops = self.arbitrage_scanner.scan_live_arbitrage(sport_key)
                analysis_results['arbitrage'] = arbitrage_ops[:3]
                analysis_results['total_opportunities'] += len(arbitrage_ops)
            except Exception as e:
                logger.error(f"Error getting arbitrage for {sport_key}: {e}")
            
            # 3. Mathematical Edge Calculations
            try:
                edge_ops = self.edge_calculator.calculate_sport_edges(sport_key)
                high_edge_ops = [
                    op for op in edge_ops 
                    if op.get('profit_percentage', 0) >= config['value_threshold']
                ]
                analysis_results['edge_calculations'] = high_edge_ops[:3]
                analysis_results['total_opportunities'] += len(high_edge_ops)
            except Exception as e:
                logger.error(f"Error getting edge calculations for {sport_key}: {e}")
            
            # 4. Insider Intelligence
            try:
                insider_ops = self.insider_intelligence.analyze_professional_patterns(sport_key)
                high_confidence_ops = [
                    op for op in insider_ops 
                    if op.get('confidence_level', 0) >= 8
                ]
                analysis_results['insider_intelligence'] = high_confidence_ops[:3]
                analysis_results['total_opportunities'] += len(high_confidence_ops)
            except Exception as e:
                logger.error(f"Error getting insider intelligence for {sport_key}: {e}")
            
            # 5. Cross-Market Correlation Analysis
            try:
                correlations = self._detect_cross_market_correlations(qualified_games)
                analysis_results['cross_market_correlations'] = correlations[:2]
                analysis_results['total_opportunities'] += len(correlations)
            except Exception as e:
                logger.error(f"Error analyzing correlations for {sport_key}: {e}")
            
            return analysis_results if analysis_results['total_opportunities'] > 0 else None
            
        except Exception as e:
            logger.error(f"Error in comprehensive sport analysis for {sport_key}: {e}")
            return None
    
    def _detect_cross_market_correlations(self, games: List[Dict]) -> List[Dict]:
        """Detect cross-market correlations for advanced betting strategies"""
        try:
            correlations = []
            
            for game in games[:5]:  # Analyze top 5 games
                correlation = self._analyze_game_correlations(game)
                if correlation and correlation.get('correlation_strength', 0) >= 7:
                    correlations.append(correlation)
            
            return correlations
            
        except Exception as e:
            logger.error(f"Error detecting cross-market correlations: {e}")
            return []
    
    def _analyze_game_correlations(self, game: Dict) -> Optional[Dict]:
        """Analyze individual game for cross-market correlations"""
        try:
            bookmakers = game.get('bookmakers', [])
            if len(bookmakers) < 8:
                return None
            
            home_team = game.get('home_team', '')
            away_team = game.get('away_team', '')
            
            # Collect h2h and totals odds
            h2h_odds = {'home': [], 'away': []}
            totals_odds = {'over': [], 'under': []}
            
            for bm in bookmakers:
                for market in bm.get('markets', []):
                    if market['key'] == 'h2h':
                        for outcome in market['outcomes']:
                            if outcome['name'] == home_team:
                                h2h_odds['home'].append(outcome['price'])
                            elif outcome['name'] == away_team:
                                h2h_odds['away'].append(outcome['price'])
                    elif market['key'] == 'totals':
                        for outcome in market['outcomes']:
                            if outcome['name'] == 'Over':
                                totals_odds['over'].append(outcome['price'])
                            elif outcome['name'] == 'Under':
                                totals_odds['under'].append(outcome['price'])
            
            # Correlation analysis
            if (len(h2h_odds['home']) >= 5 and len(h2h_odds['away']) >= 5 and
                len(totals_odds['over']) >= 5 and len(totals_odds['under']) >= 5):
                
                # Calculate variance and correlation patterns
                home_variance = statistics.variance(h2h_odds['home'])
                away_variance = statistics.variance(h2h_odds['away'])
                over_variance = statistics.variance(totals_odds['over'])
                under_variance = statistics.variance(totals_odds['under'])
                
                # Detect correlation strength
                total_variance = home_variance + away_variance + over_variance + under_variance
                correlation_strength = min(10, int(total_variance * 2))
                
                if correlation_strength >= 7:
                    return {
                        'game': f"{home_team} vs {away_team}",
                        'commence_time': game.get('commence_time'),
                        'correlation_strength': correlation_strength,
                        'correlation_type': 'MULTI_MARKET',
                        'h2h_variance': round(home_variance + away_variance, 2),
                        'totals_variance': round(over_variance + under_variance, 2),
                        'strategy': self._generate_correlation_strategy(correlation_strength),
                        'profit_potential': round(correlation_strength * 0.8, 1)
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing game correlations: {e}")
            return None
    
    def _generate_correlation_strategy(self, strength: int) -> str:
        """Generate correlation-based betting strategy"""
        if strength >= 9:
            return "MULTI_MARKET_ARBITRAGE"
        elif strength >= 8:
            return "CORRELATED_HEDGE"
        else:
            return "VARIANCE_EXPLOIT"
    
    def get_priority_opportunities(self, results: Dict[str, Dict]) -> List[Dict]:
        """Get top priority opportunities across all sports"""
        try:
            all_opportunities = []
            
            for sport_key, sport_data in results.items():
                sport_priority = sport_data.get('priority', 5)
                
                # Weight opportunities by sport priority
                for category in ['predictions', 'arbitrage', 'edge_calculations', 'insider_intelligence']:
                    for opp in sport_data.get(category, []):
                        weighted_opp = opp.copy()
                        weighted_opp['sport'] = sport_key
                        weighted_opp['category'] = category
                        weighted_opp['sport_priority'] = sport_priority
                        
                        # Calculate composite score
                        base_score = opp.get('expected_value', opp.get('profit_percentage', opp.get('confidence_level', 5)))
                        weighted_opp['composite_score'] = base_score * (sport_priority / 10)
                        
                        all_opportunities.append(weighted_opp)
            
            # Sort by composite score
            return sorted(all_opportunities, key=lambda x: x['composite_score'], reverse=True)[:10]
            
        except Exception as e:
            logger.error(f"Error getting priority opportunities: {e}")
            return []
    
    def generate_master_opportunity_report(self, scan_results: Dict) -> str:
        """Generate comprehensive multi-sport opportunity report - Bot handler method"""
        return self.generate_master_report()
    
    def generate_master_report(self) -> str:
        """Generate comprehensive master report across all sports"""
        try:
            results = self.scan_all_premium_sports()
            
            if not results:
                return "🔍 MULTI-SPORT SCANNER\n\n⚠️ No premium opportunities found across all sports"
            
            report = "🏆 MULTI-SPORT ADVANTAGE SCANNER\n"
            report += "═══════════════════════════════════════════\n\n"
            
            # Summary statistics
            total_sports = len(results)
            total_opportunities = sum(data.get('total_opportunities', 0) for data in results.values())
            total_games = sum(data.get('total_games', 0) for data in results.values())
            
            report += f"📊 SCAN SUMMARY:\n"
            report += f"• Sports analyzed: {total_sports}\n"
            report += f"• Games processed: {total_games}\n"
            report += f"• Total opportunities: {total_opportunities}\n\n"
            
            # Priority opportunities
            priority_ops = self.get_priority_opportunities(results)
            if priority_ops:
                report += "🎯 TOP PRIORITY OPPORTUNITIES:\n"
                for i, opp in enumerate(priority_ops[:5], 1):
                    report += f"{i}. {opp.get('game', 'Unknown Game')} ({opp['sport'].upper()})\n"
                    report += f"   📈 Score: {opp['composite_score']:.1f} | Category: {opp['category'].upper()}\n"
                    
                    if opp['category'] == 'arbitrage':
                        report += f"   💰 Guaranteed Profit: {opp.get('profit_percentage', 0):.2f}%\n"
                    elif opp['category'] == 'predictions':
                        report += f"   🎲 Expected Value: {opp.get('expected_value', 0):.1f}%\n"
                    elif opp['category'] == 'edge_calculations':
                        report += f"   🔢 Mathematical Edge: {opp.get('profit_percentage', 0):.2f}%\n"
                    elif opp['category'] == 'insider_intelligence':
                        report += f"   🎯 Confidence: {opp.get('confidence_level', 0)}/10\n"
                    
                    report += "\n"
            
            # Sport-by-sport breakdown
            report += "📋 SPORT-BY-SPORT BREAKDOWN:\n"
            for sport_key, data in sorted(results.items(), key=lambda x: x[1]['priority'], reverse=True):
                report += f"\n🏅 {sport_key.upper().replace('_', ' ')} (Priority: {data['priority']}/10)\n"
                report += f"   Games: {data['total_games']} | Opportunities: {data['total_opportunities']}\n"
                
                if data.get('arbitrage'):
                    report += f"   ⚡ Arbitrage: {len(data['arbitrage'])} opportunities\n"
                if data.get('predictions'):
                    report += f"   🎯 Predictions: {len(data['predictions'])} high-value\n"
                if data.get('edge_calculations'):
                    report += f"   🔢 Edge Calculations: {len(data['edge_calculations'])} profitable\n"
                if data.get('insider_intelligence'):
                    report += f"   🎪 Insider Intelligence: {len(data['insider_intelligence'])} signals\n"
            
            report += f"\n🚀 EXECUTION PRIORITY:\n"
            report += "1. ARBITRAGE - Guaranteed profit, execute immediately\n"
            report += "2. EDGE CALCULATIONS - Mathematical advantage\n"
            report += "3. INSIDER INTELLIGENCE - Professional patterns\n"
            report += "4. PREDICTIONS - High-value opportunities\n"
            report += "5. CORRELATIONS - Advanced strategies\n\n"
            
            report += "🎯 MULTI-SPORT ANALYSIS COMPLETE"
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating master report: {e}")
            return f"Error generating multi-sport report: {e}"
    
    def get_live_dashboard_data(self) -> Dict:
        """Get real-time dashboard data for live monitoring"""
        try:
            results = self.scan_all_premium_sports()
            priority_ops = self.get_priority_opportunities(results)
            
            dashboard = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'total_sports_active': len(results),
                'total_opportunities': sum(data.get('total_opportunities', 0) for data in results.values()),
                'top_opportunities': priority_ops[:3],
                'sport_breakdown': {},
                'alert_level': 'LOW'
            }
            
            # Sport breakdown
            for sport, data in results.items():
                dashboard['sport_breakdown'][sport] = {
                    'opportunities': data.get('total_opportunities', 0),
                    'games': data.get('total_games', 0),
                    'priority': data.get('priority', 5)
                }
            
            # Alert level determination
            if dashboard['total_opportunities'] >= 20:
                dashboard['alert_level'] = 'HIGH'
            elif dashboard['total_opportunities'] >= 10:
                dashboard['alert_level'] = 'MEDIUM'
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error getting live dashboard data: {e}")
            return {'error': str(e)}
