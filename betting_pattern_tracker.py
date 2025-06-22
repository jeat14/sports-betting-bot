#!/usr/bin/env python3
"""
Betting Pattern Tracker

Advanced betting pattern analysis system that tracks user betting behavior,
identifies risk patterns, and provides personalized warnings to prevent losses.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class BettingPatternTracker:
    def __init__(self):
        self.patterns_file = 'betting_patterns.json'
        self.user_patterns = self._load_patterns()
        
    def _load_patterns(self) -> Dict:
        """Load betting patterns from file"""
        try:
            if os.path.exists(self.patterns_file):
                with open(self.patterns_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading patterns: {e}")
            return {}
    
    def _save_patterns(self):
        """Save betting patterns to file"""
        try:
            with open(self.patterns_file, 'w') as f:
                json.dump(self.user_patterns, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving patterns: {e}")
    
    def track_bet_result(self, bet_details: Dict):
        """Track a betting result for pattern analysis"""
        try:
            user_id = str(bet_details.get('user_id', 'unknown'))
            
            if user_id not in self.user_patterns:
                self.user_patterns[user_id] = {
                    'total_bets': 0,
                    'wins': 0,
                    'losses': 0,
                    'total_wagered': 0.0,
                    'total_returned': 0.0,
                    'bet_history': [],
                    'loss_streaks': [],
                    'current_streak': {'type': None, 'count': 0},
                    'risk_indicators': {}
                }
            
            pattern = self.user_patterns[user_id]
            
            # Update basic stats
            pattern['total_bets'] += 1
            pattern['total_wagered'] += bet_details.get('amount', 0)
            
            if bet_details.get('result') == 'win':
                pattern['wins'] += 1
                pattern['total_returned'] += bet_details.get('payout', 0)
                if pattern['current_streak']['type'] != 'win':
                    pattern['current_streak'] = {'type': 'win', 'count': 1}
                else:
                    pattern['current_streak']['count'] += 1
            else:
                pattern['losses'] += 1
                if pattern['current_streak']['type'] != 'loss':
                    if pattern['current_streak']['type'] == 'loss':
                        pattern['loss_streaks'].append(pattern['current_streak']['count'])
                    pattern['current_streak'] = {'type': 'loss', 'count': 1}
                else:
                    pattern['current_streak']['count'] += 1
            
            # Add to history
            bet_record = {
                'timestamp': datetime.now().isoformat(),
                'sport': bet_details.get('sport', 'unknown'),
                'amount': bet_details.get('amount', 0),
                'odds': bet_details.get('odds', 0),
                'result': bet_details.get('result', 'pending')
            }
            pattern['bet_history'].append(bet_record)
            
            # Keep only last 100 bets
            if len(pattern['bet_history']) > 100:
                pattern['bet_history'] = pattern['bet_history'][-100:]
            
            self._save_patterns()
            
        except Exception as e:
            logger.error(f"Error tracking bet result: {e}")
    
    def get_personalized_warnings(self, user_id: str) -> List[str]:
        """Get personalized warnings based on betting patterns"""
        warnings = []
        
        try:
            if str(user_id) not in self.user_patterns:
                return ["Track your bets with /trackbet to receive personalized insights"]
            
            pattern = self.user_patterns[str(user_id)]
            
            # Loss streak warning
            current_streak = pattern.get('current_streak', {})
            if current_streak.get('type') == 'loss' and current_streak.get('count', 0) >= 3:
                warnings.append(f"⚠️ You're on a {current_streak['count']}-bet losing streak. Consider taking a break.")
            
            # Win rate warning
            if pattern['total_bets'] >= 10:
                win_rate = (pattern['wins'] / pattern['total_bets']) * 100
                if win_rate < 30:
                    warnings.append(f"📉 Your win rate is {win_rate:.1f}%. Review your strategy.")
            
            # ROI warning
            if pattern['total_wagered'] > 0:
                roi = ((pattern['total_returned'] - pattern['total_wagered']) / pattern['total_wagered']) * 100
                if roi < -20:
                    warnings.append(f"💸 You're down {abs(roi):.1f}% overall. Consider reducing bet sizes.")
            
            # Recent activity warning
            recent_bets = [bet for bet in pattern['bet_history'] 
                          if datetime.fromisoformat(bet['timestamp']) > datetime.now() - timedelta(hours=24)]
            if len(recent_bets) >= 10:
                warnings.append("🚨 You've placed 10+ bets in 24 hours. Consider pacing yourself.")
            
        except Exception as e:
            logger.error(f"Error getting personalized warnings: {e}")
        
        return warnings
    
    def generate_pattern_report(self, user_id: str) -> str:
        """Generate a comprehensive pattern analysis report"""
        try:
            if str(user_id) not in self.user_patterns:
                return "No betting history found. Use /trackbet to start tracking your bets."
            
            pattern = self.user_patterns[str(user_id)]
            
            if pattern['total_bets'] == 0:
                return "No bets tracked yet. Use /trackbet to log your betting activity."
            
            # Calculate statistics
            win_rate = (pattern['wins'] / pattern['total_bets']) * 100
            roi = 0
            if pattern['total_wagered'] > 0:
                roi = ((pattern['total_returned'] - pattern['total_wagered']) / pattern['total_wagered']) * 100
            
            avg_bet = pattern['total_wagered'] / pattern['total_bets'] if pattern['total_bets'] > 0 else 0
            
            # Longest streaks
            max_loss_streak = max(pattern['loss_streaks']) if pattern['loss_streaks'] else 0
            current_streak = pattern.get('current_streak', {})
            
            report = f"""
📊 **Your Betting Pattern Analysis**

**Overall Performance:**
• Total Bets: {pattern['total_bets']}
• Win Rate: {win_rate:.1f}%
• ROI: {roi:+.1f}%
• Total Wagered: ${pattern['total_wagered']:.2f}
• Net Result: ${pattern['total_returned'] - pattern['total_wagered']:+.2f}

**Betting Behavior:**
• Average Bet Size: ${avg_bet:.2f}
• Longest Loss Streak: {max_loss_streak} bets
• Current Streak: {current_streak.get('count', 0)} {current_streak.get('type', 'none')}

**Risk Assessment:**
"""
            
            # Add warnings
            warnings = self.get_personalized_warnings(user_id)
            if warnings:
                report += "\n".join([f"• {warning}" for warning in warnings])
            else:
                report += "• No major risk indicators detected ✅"
            
            return report.strip()
            
        except Exception as e:
            logger.error(f"Error generating pattern report: {e}")
            return "Error generating pattern analysis. Please try again."
