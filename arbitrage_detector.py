#!/usr/bin/env python3
"""
Arbitrage Betting Detector - Guaranteed Profit Opportunities

This module detects arbitrage opportunities across multiple bookmakers
where you can bet on all outcomes and guarantee profit regardless of result.
"""

import logging
from typing import List, Dict, Optional
from odds_service import OddsService
import math

logger = logging.getLogger(__name__)

class ArbitrageDetector:
    def __init__(self):
        self.odds_service = OddsService()
        self.min_profit_margin = 1.005  # Minimum 0.5% profit for better detection
        self.min_stake = 10  # Minimum bet amount
        
    def find_arbitrage_opportunities(self, sport_key: str) -> List[Dict]:
        """Find guaranteed profit arbitrage opportunities"""
        try:
            games = self.odds_service.get_odds(sport_key)
            if not games:
                return []
            
            # Filter for recent games only (next 30 days for broader coverage)
            from datetime import datetime, timezone, timedelta
            now = datetime.now(timezone.utc)
            max_date = now + timedelta(days=30)
            
            current_games = []
            for game in games:
                try:
                    game_time = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00'))
                    if now <= game_time <= max_date:
                        current_games.append(game)
                except:
                    continue
            
            logger.info(f"Found {len(current_games)} current games out of {len(games)} total for {sport_key}")
            
            arbitrage_ops = []
            for game in current_games:
                arb_opportunity = self._analyze_game_for_arbitrage(game)
                if arb_opportunity:
                    arbitrage_ops.append(arb_opportunity)
            
            # Sort by profit percentage (highest first)
            arbitrage_ops.sort(key=lambda x: x['profit_percentage'], reverse=True)
            return arbitrage_ops[:5]  # Top 5 opportunities
            
        except Exception as e:
            logger.error(f"Error finding arbitrage: {e}")
            return []
    
    def _analyze_game_for_arbitrage(self, game: Dict) -> Optional[Dict]:
        """Analyze single game for arbitrage opportunity"""
        try:
            bookmakers = game.get('bookmakers', [])
            if len(bookmakers) < 2:
                return None
            
            # Find best odds for each outcome
            best_home_odds = 0
            best_away_odds = 0
            best_draw_odds = 0
            
            home_bookmaker = ""
            away_bookmaker = ""
            draw_bookmaker = ""
            
            for bookmaker in bookmakers:
                for market in bookmaker.get('markets', []):
                    if market['key'] == 'h2h':
                        for outcome in market['outcomes']:
                            price = outcome['price']
                            
                            # Skip corrupted data
                            if price <= 1.0 or price > 50.0:
                                continue
                            
                            if outcome['name'] == game['home_team'] and price > best_home_odds:
                                best_home_odds = price
                                home_bookmaker = bookmaker['title']
                            elif outcome['name'] == game['away_team'] and price > best_away_odds:
                                best_away_odds = price
                                away_bookmaker = bookmaker['title']
                            elif outcome['name'] == 'Draw' and price > best_draw_odds:
                                best_draw_odds = price
                                draw_bookmaker = bookmaker['title']
            
            # Check for arbitrage (2-way or 3-way)
            if best_home_odds > 0 and best_away_odds > 0:
                # 2-way arbitrage calculation
                implied_prob = (1/best_home_odds) + (1/best_away_odds)
                
                if implied_prob < 1.0:  # Arbitrage exists
                    profit_margin = (1/implied_prob) - 1
                    
                    if profit_margin >= (self.min_profit_margin - 1):
                        return self._calculate_arbitrage_stakes(
                            game, best_home_odds, best_away_odds, 
                            home_bookmaker, away_bookmaker, profit_margin, is_3way=False
                        )
            
            # 3-way arbitrage (if draw available)
            if best_home_odds > 0 and best_away_odds > 0 and best_draw_odds > 0:
                implied_prob_3way = (1/best_home_odds) + (1/best_away_odds) + (1/best_draw_odds)
                
                if implied_prob_3way < 1.0:
                    profit_margin = (1/implied_prob_3way) - 1
                    
                    if profit_margin >= (self.min_profit_margin - 1):
                        return self._calculate_arbitrage_stakes(
                            game, best_home_odds, best_away_odds, 
                            home_bookmaker, away_bookmaker, profit_margin, 
                            is_3way=True, draw_odds=best_draw_odds, draw_bookmaker=draw_bookmaker
                        )
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing arbitrage: {e}")
            return None
    
    def _calculate_arbitrage_stakes(self, game: Dict, home_odds: float, away_odds: float,
                                  home_bm: str, away_bm: str, profit_margin: float,
                                  is_3way: bool = False, draw_odds: float = 0, draw_bookmaker: str = "") -> Dict:
        """Calculate optimal stake distribution for arbitrage"""
        
        total_stake = 100  # Base calculation on $100
        
        if is_3way:
            # 3-way arbitrage stakes
            home_stake = total_stake / (home_odds * ((1/home_odds) + (1/away_odds) + (1/draw_odds)))
            away_stake = total_stake / (away_odds * ((1/home_odds) + (1/away_odds) + (1/draw_odds)))
            draw_stake = total_stake / (draw_odds * ((1/home_odds) + (1/away_odds) + (1/draw_odds)))
            
            guaranteed_profit = total_stake * profit_margin
            
            return {
                'home_team': game['home_team'],
                'away_team': game['away_team'],
                'commence_time': game['commence_time'],
                'sport_key': game.get('sport_key', ''),
                'arbitrage_type': '3-way',
                'profit_percentage': round(profit_margin * 100, 2),
                'guaranteed_profit': round(guaranteed_profit, 2),
                'total_stake': total_stake,
                'bets': [
                    {
                        'outcome': game['home_team'],
                        'odds': home_odds,
                        'stake': round(home_stake, 2),
                        'bookmaker': home_bm,
                        'potential_return': round(home_stake * home_odds, 2)
                    },
                    {
                        'outcome': game['away_team'],
                        'odds': away_odds,
                        'stake': round(away_stake, 2),
                        'bookmaker': away_bm,
                        'potential_return': round(away_stake * away_odds, 2)
                    },
                    {
                        'outcome': 'Draw',
                        'odds': draw_odds,
                        'stake': round(draw_stake, 2),
                        'bookmaker': draw_bookmaker,
                        'potential_return': round(draw_stake * draw_odds, 2)
                    }
                ]
            }
        else:
            # 2-way arbitrage stakes
            home_stake = total_stake / (home_odds * ((1/home_odds) + (1/away_odds)))
            away_stake = total_stake / (away_odds * ((1/home_odds) + (1/away_odds)))
            
            guaranteed_profit = total_stake * profit_margin
            
            return {
                'home_team': game['home_team'],
                'away_team': game['away_team'],
                'commence_time': game['commence_time'],
                'sport_key': game.get('sport_key', ''),
                'arbitrage_type': '2-way',
                'profit_percentage': round(profit_margin * 100, 2),
                'guaranteed_profit': round(guaranteed_profit, 2),
                'total_stake': total_stake,
                'bets': [
                    {
                        'outcome': game['home_team'],
                        'odds': home_odds,
                        'stake': round(home_stake, 2),
                        'bookmaker': home_bm,
                        'potential_return': round(home_stake * home_odds, 2)
                    },
                    {
                        'outcome': game['away_team'],
                        'odds': away_odds,
                        'stake': round(away_stake, 2),
                        'bookmaker': away_bm,
                        'potential_return': round(away_stake * away_odds, 2)
                    }
                ]
            }
    
    def generate_arbitrage_summary(self, opportunities: List[Dict]) -> str:
        """Generate formatted arbitrage opportunities summary"""
        if not opportunities:
            return "🔍 No arbitrage opportunities found at this time."
        
        summary = f"💰 ARBITRAGE OPPORTUNITIES - GUARANTEED PROFITS\n\n"
        
        for i, arb in enumerate(opportunities, 1):
            summary += f"{i}. {arb['home_team']} vs {arb['away_team']}\n"
            summary += f"   💰 Guaranteed Profit: ${arb['guaranteed_profit']} ({arb['profit_percentage']}%)\n"
            summary += f"   📊 Total Stake: ${arb['total_stake']} | Type: {arb['arbitrage_type']}\n\n"
            
            for bet in arb['bets']:
                summary += f"   🎯 Bet ${bet['stake']} on {bet['outcome']} @ {bet['odds']} ({bet['bookmaker']})\n"
            
            summary += f"   ⏰ Game: {arb['commence_time']}\n"
            summary += "   " + "="*50 + "\n\n"
        
        summary += "⚠️ Note: Place all bets quickly as odds change frequently.\n"
        summary += "Arbitrage guarantees profit regardless of game outcome!"
        
        return summary
