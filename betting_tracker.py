"""
Comprehensive Betting Tracker - Copy this entire file content to GitHub
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import os

logger = logging.getLogger(__name__)

@dataclass
class BetRecord:
    bet_id: str
    sport: str
    event: str
    bet_type: str
    selection: str
    odds: float
    stake: float
    bookmaker: str
    placed_time: str
    event_time: str
    status: str  # pending, won, lost, void
    actual_outcome: Optional[str] = None
    payout: float = 0.0
    profit_loss: float = 0.0
    confidence: float = 0.0
    prediction_model: str = ""

class BettingTracker:
    def __init__(self):
        self.bets_file = "betting_history.json"
        self.load_betting_history()
        
    def load_betting_history(self):
        """Load betting history from file"""
        try:
            if os.path.exists(self.bets_file):
                with open(self.bets_file, 'r') as f:
                    data = json.load(f)
                    self.bets = [BetRecord(**bet) for bet in data]
            else:
                self.bets = []
        except Exception as e:
            logger.error(f"Error loading betting history: {e}")
            self.bets = []
    
    def save_betting_history(self):
        """Save betting history to file"""
        try:
            with open(self.bets_file, 'w') as f:
                json.dump([asdict(bet) for bet in self.bets], f, indent=2)
        except Exception as e:
            logger.error(f"Error saving betting history: {e}")
    
    def add_bet(self, sport: str, event: str, bet_type: str, selection: str, 
                odds: float, stake: float, bookmaker: str, event_time: str,
                confidence: float = 0, prediction_model: str = "") -> str:
        """Add a new bet to tracking"""
        bet_id = f"{sport}_{len(self.bets)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        bet = BetRecord(
            bet_id=bet_id,
            sport=sport,
            event=event,
            bet_type=bet_type,
            selection=selection,
            odds=odds,
            stake=stake,
            bookmaker=bookmaker,
            placed_time=datetime.now().isoformat(),
            event_time=event_time,
            status="pending",
            confidence=confidence,
            prediction_model=prediction_model
        )
        
        self.bets.append(bet)
        self.save_betting_history()
        return bet_id
    
    def update_bet_outcome(self, bet_id: str, outcome: str, actual_result: str = "") -> bool:
        """Update bet outcome (won/lost/void)"""
        try:
            bet = next((b for b in self.bets if b.bet_id == bet_id), None)
            if not bet:
                return False
            
            bet.status = outcome
            bet.actual_outcome = actual_result
            
            if outcome == "won":
                bet.payout = bet.stake * bet.odds
                bet.profit_loss = bet.payout - bet.stake
            elif outcome == "lost":
                bet.payout = 0
                bet.profit_loss = -bet.stake
            elif outcome == "void":
                bet.payout = bet.stake
                bet.profit_loss = 0
            
            self.save_betting_history()
            return True
        except Exception as e:
            logger.error(f"Error updating bet outcome: {e}")
            return False
    
    def get_sport_performance(self, sport: str, days: int = 30) -> Dict:
        """Get performance statistics for a specific sport"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        sport_bets = [bet for bet in self.bets 
                     if bet.sport.lower() == sport.lower() 
                     and datetime.fromisoformat(bet.placed_time) > cutoff_date
                     and bet.status in ['won', 'lost']]
        
        if not sport_bets:
            return {
                'sport': sport,
                'total_bets': 0,
                'win_rate': 0,
                'profit_loss': 0,
                'roi': 0,
                'avg_odds': 0
            }
        
        total_bets = len(sport_bets)
        wins = len([bet for bet in sport_bets if bet.status == 'won'])
        total_staked = sum(bet.stake for bet in sport_bets)
        total_profit = sum(bet.profit_loss for bet in sport_bets)
        avg_odds = sum(bet.odds for bet in sport_bets) / total_bets
        
        return {
            'sport': sport,
            'total_bets': total_bets,
            'win_rate': (wins / total_bets) * 100 if total_bets > 0 else 0,
            'profit_loss': round(total_profit, 2),
            'roi': (total_profit / total_staked) * 100 if total_staked > 0 else 0,
            'avg_odds': round(avg_odds, 2)
        }
    
    def get_overall_performance(self, days: int = 30) -> Dict:
        """Get overall betting performance"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_bets = [bet for bet in self.bets 
                      if datetime.fromisoformat(bet.placed_time) > cutoff_date
                      and bet.status in ['won', 'lost']]
        
        if not recent_bets:
            return {
                'total_bets': 0,
                'win_rate': 0,
                'profit_loss': 0,
                'roi': 0,
                'best_sport': 'None',
                'worst_sport': 'None'
            }
        
        total_bets = len(recent_bets)
        wins = len([bet for bet in recent_bets if bet.status == 'won'])
        total_staked = sum(bet.stake for bet in recent_bets)
        total_profit = sum(bet.profit_loss for bet in recent_bets)
        
        # Find best and worst performing sports
        sports_performance = {}
        for bet in recent_bets:
            sport = bet.sport
            if sport not in sports_performance:
                sports_performance[sport] = {'profit': 0, 'bets': 0}
            sports_performance[sport]['profit'] += bet.profit_loss
            sports_performance[sport]['bets'] += 1
        
        best_sport = max(sports_performance.items(), 
                        key=lambda x: x[1]['profit'], default=('None', {}))[0]
        worst_sport = min(sports_performance.items(), 
                         key=lambda x: x[1]['profit'], default=('None', {}))[0]
        
        return {
            'total_bets': total_bets,
            'win_rate': (wins / total_bets) * 100 if total_bets > 0 else 0,
            'profit_loss': round(total_profit, 2),
            'roi': (total_profit / total_staked) * 100 if total_staked > 0 else 0,
            'best_sport': best_sport,
            'worst_sport': worst_sport,
            'avg_stake': round(total_staked / total_bets, 2) if total_bets > 0 else 0
        }
    
    def get_pending_bets(self) -> List[BetRecord]:
        """Get all pending bets"""
        return [bet for bet in self.bets if bet.status == 'pending']
    
    def get_todays_bets(self) -> List[BetRecord]:
        """Get today's bets"""
        today = datetime.now().date()
        return [bet for bet in self.bets 
                if datetime.fromisoformat(bet.placed_time).date() == today]
    
    def generate_performance_summary(self) -> str:
        """Generate a formatted performance summary"""
        overall = self.get_overall_performance(30)
        
        summary = "📊 **BETTING PERFORMANCE SUMMARY (Last 30 Days)**\n\n"
        
        # Overall performance
        summary += f"**Overall Statistics:**\n"
        summary += f"• Total Bets: {overall['total_bets']}\n"
        summary += f"• Win Rate: {overall['win_rate']:.1f}%\n"
        summary += f"• Profit/Loss: £{overall['profit_loss']:.2f}\n"
        summary += f"• ROI: {overall['roi']:.1f}%\n"
        summary += f"• Average Stake: £{overall['avg_stake']:.2f}\n\n"
        
        summary += "💡 *Track all your bets across multiple sports for optimal bankroll management*"
        
        return summary
