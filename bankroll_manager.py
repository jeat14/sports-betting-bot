#!/usr/bin/env python3
"""
Professional Bankroll Management System

Implements Kelly Criterion, fractional Kelly, and advanced money management
strategies used by professional betting syndicates.
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class BankrollConfig:
    total_bankroll: float
    max_bet_percentage: float = 0.05  # 5% max per bet
    kelly_fraction: float = 0.25  # Quarter Kelly for safety
    stop_loss_percentage: float = 0.20  # Stop at 20% loss
    target_profit_percentage: float = 0.50  # Take profits at 50% gain
    min_bet_amount: float = 10.0
    max_bet_amount: float = 1000.0

class BankrollManager:
    def __init__(self):
        self.config_file = "bankroll_config.json"
        self.session_file = "betting_session.json"
        self.load_configuration()
        
    def load_configuration(self):
        """Load bankroll configuration"""
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                self.config = BankrollConfig(**data)
        except FileNotFoundError:
            # Default configuration for new users
            self.config = BankrollConfig(total_bankroll=1000.0)
            self.save_configuration()
    
    def save_configuration(self):
        """Save bankroll configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config.__dict__, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving bankroll config: {e}")
    
    def calculate_optimal_bet_size(self, odds: float, win_probability: float, 
                                  confidence: float = 1.0) -> Dict:
        """Calculate optimal bet size using Kelly Criterion with safety modifications"""
        try:
            if odds <= 1.0 or win_probability <= 0 or win_probability >= 1:
                return self._create_bet_recommendation(0, "Invalid odds or probability")
            
            # Kelly Criterion: f = (bp - q) / b
            # where b = odds - 1, p = win probability, q = 1 - p
            b = odds - 1
            p = win_probability
            q = 1 - p
            
            # Raw Kelly percentage
            kelly_percentage = (b * p - q) / b
            
            # Apply safety modifications
            if kelly_percentage <= 0:
                return self._create_bet_recommendation(0, "No positive expected value")
            
            # Apply fractional Kelly for risk management
            adjusted_kelly = kelly_percentage * self.config.kelly_fraction * confidence
            
            # Apply maximum bet percentage constraint
            final_percentage = min(adjusted_kelly, self.config.max_bet_percentage)
            
            # Calculate actual bet amount
            bet_amount = self.config.total_bankroll * final_percentage
            
            # Apply min/max constraints
            bet_amount = max(self.config.min_bet_amount, 
                           min(bet_amount, self.config.max_bet_amount))
            
            # Calculate expected value
            expected_value = (p * (odds - 1) - q) * bet_amount
            
            return self._create_bet_recommendation(
                bet_amount, 
                f"Kelly-optimized bet size",
                {
                    'kelly_percentage': round(kelly_percentage * 100, 2),
                    'adjusted_percentage': round(final_percentage * 100, 2),
                    'expected_value': round(expected_value, 2),
                    'risk_level': self._assess_risk_level(final_percentage),
                    'bankroll_percentage': round((bet_amount / self.config.total_bankroll) * 100, 2)
                }
            )
            
        except Exception as e:
            logger.error(f"Error calculating bet size: {e}")
            return self._create_bet_recommendation(0, f"Calculation error: {e}")
    
    def _create_bet_recommendation(self, amount: float, reason: str, details: Dict = None) -> Dict:
        """Create standardized bet recommendation"""
        return {
            'recommended_amount': round(amount, 2),
            'reason': reason,
            'details': details or {},
            'bankroll_status': self.get_bankroll_status()
        }
    
    def _assess_risk_level(self, bet_percentage: float) -> str:
        """Assess risk level based on bet percentage"""
        if bet_percentage <= 0.01:  # 1%
            return "VERY LOW"
        elif bet_percentage <= 0.02:  # 2%
            return "LOW"
        elif bet_percentage <= 0.03:  # 3%
            return "MEDIUM"
        elif bet_percentage <= 0.05:  # 5%
            return "HIGH"
        else:
            return "VERY HIGH"
    
    def update_bankroll(self, amount_change: float, reason: str = "") -> Dict:
        """Update bankroll after win/loss"""
        try:
            old_bankroll = self.config.total_bankroll
            self.config.total_bankroll += amount_change
            
            # Log the change
            self._log_bankroll_change(old_bankroll, self.config.total_bankroll, reason)
            
            # Check for stop-loss or take-profit triggers
            status = self._check_bankroll_triggers(old_bankroll)
            
            self.save_configuration()
            
            return {
                'old_bankroll': round(old_bankroll, 2),
                'new_bankroll': round(self.config.total_bankroll, 2),
                'change': round(amount_change, 2),
                'percentage_change': round((amount_change / old_bankroll) * 100, 2),
                'status': status,
                'reason': reason
            }
            
        except Exception as e:
            logger.error(f"Error updating bankroll: {e}")
            return {'error': str(e)}
    
    def _log_bankroll_change(self, old_amount: float, new_amount: float, reason: str):
        """Log bankroll changes for tracking"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'old_amount': old_amount,
                'new_amount': new_amount,
                'change': new_amount - old_amount,
                'reason': reason
            }
            
            # Load existing logs
            try:
                with open('bankroll_history.json', 'r') as f:
                    logs = json.load(f)
            except FileNotFoundError:
                logs = []
            
            logs.append(log_entry)
            
            # Keep only last 1000 entries
            logs = logs[-1000:]
            
            with open('bankroll_history.json', 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error logging bankroll change: {e}")
    
    def _check_bankroll_triggers(self, original_bankroll: float) -> str:
        """Check if bankroll has hit stop-loss or take-profit levels"""
        current_ratio = self.config.total_bankroll / original_bankroll
        
        if current_ratio <= (1 - self.config.stop_loss_percentage):
            return "STOP_LOSS_TRIGGERED"
        elif current_ratio >= (1 + self.config.target_profit_percentage):
            return "TAKE_PROFIT_TRIGGERED"
        else:
            return "NORMAL_OPERATION"
    
    def get_bankroll_status(self) -> Dict:
        """Get current bankroll status and recommendations"""
        return {
            'total_bankroll': round(self.config.total_bankroll, 2),
            'max_bet_amount': round(self.config.total_bankroll * self.config.max_bet_percentage, 2),
            'recommended_max_bet': round(self.config.total_bankroll * 0.02, 2),  # Conservative 2%
            'kelly_fraction': self.config.kelly_fraction,
            'stop_loss_level': round(self.config.total_bankroll * (1 - self.config.stop_loss_percentage), 2),
            'take_profit_level': round(self.config.total_bankroll * (1 + self.config.target_profit_percentage), 2)
        }
    
    def simulate_bet_outcomes(self, bet_amount: float, odds: float, 
                            win_probability: float, num_simulations: int = 1000) -> Dict:
        """Simulate multiple bet outcomes for risk assessment"""
        try:
            wins = 0
            total_profit = 0
            worst_case = 0
            best_case = 0
            
            for _ in range(num_simulations):
                if random.random() < win_probability:
                    profit = bet_amount * (odds - 1)
                    wins += 1
                else:
                    profit = -bet_amount
                
                total_profit += profit
                worst_case = min(worst_case, profit)
                best_case = max(best_case, profit)
            
            win_rate = wins / num_simulations
            avg_profit = total_profit / num_simulations
            
            return {
                'simulated_win_rate': round(win_rate * 100, 2),
                'expected_profit': round(avg_profit, 2),
                'worst_case_loss': round(worst_case, 2),
                'best_case_win': round(best_case, 2),
                'total_simulations': num_simulations,
                'risk_assessment': 'HIGH' if worst_case < -bet_amount * 0.8 else 'MEDIUM'
            }
            
        except Exception as e:
            logger.error(f"Error in bet simulation: {e}")
            return {'error': str(e)}
    
    def get_betting_limits_by_confidence(self) -> Dict:
        """Get recommended betting limits based on confidence levels"""
        base_bankroll = self.config.total_bankroll
        
        return {
            'very_high_confidence': {
                'max_bet': round(base_bankroll * 0.05, 2),  # 5%
                'recommended': round(base_bankroll * 0.03, 2),  # 3%
                'description': 'Strongest opportunities with multiple confirmations'
            },
            'high_confidence': {
                'max_bet': round(base_bankroll * 0.03, 2),  # 3%
                'recommended': round(base_bankroll * 0.02, 2),  # 2%
                'description': 'Strong opportunities with good data support'
            },
            'medium_confidence': {
                'max_bet': round(base_bankroll * 0.02, 2),  # 2%
                'recommended': round(base_bankroll * 0.01, 2),  # 1%
                'description': 'Moderate opportunities with some uncertainty'
            },
            'low_confidence': {
                'max_bet': round(base_bankroll * 0.01, 2),  # 1%
                'recommended': round(base_bankroll * 0.005, 2),  # 0.5%
                'description': 'Experimental bets with high uncertainty'
            }
        }
    
    def generate_bankroll_report(self) -> str:
        """Generate comprehensive bankroll management report"""
        try:
            status = self.get_bankroll_status()
            limits = self.get_betting_limits_by_confidence()
            
            report = "💰 PROFESSIONAL BANKROLL MANAGEMENT\n\n"
            
            report += f"📊 Current Status:\n"
            report += f"• Total Bankroll: ${status['total_bankroll']:,}\n"
            report += f"• Max Single Bet: ${status['max_bet_amount']:,} ({self.config.max_bet_percentage*100}%)\n"
            report += f"• Conservative Bet: ${status['recommended_max_bet']:,} (2%)\n"
            report += f"• Kelly Fraction: {self.config.kelly_fraction} (Quarter Kelly)\n\n"
            
            report += f"🎯 Risk Management:\n"
            report += f"• Stop Loss Level: ${status['stop_loss_level']:,} ({self.config.stop_loss_percentage*100}% drawdown)\n"
            report += f"• Take Profit Level: ${status['take_profit_level']:,} ({self.config.target_profit_percentage*100}% gain)\n\n"
            
            report += f"📈 Confidence-Based Betting Limits:\n"
            for confidence, data in limits.items():
                confidence_name = confidence.replace('_', ' ').title()
                report += f"• {confidence_name}:\n"
                report += f"  - Max: ${data['max_bet']:,} | Rec: ${data['recommended']:,}\n"
                report += f"  - {data['description']}\n"
            
            report += f"\n🧠 Professional Guidelines:\n"
            report += f"• Never bet more than 5% of bankroll on single bet\n"
            report += f"• Use Kelly Criterion for optimal sizing\n"
            report += f"• Fractional Kelly (25%) reduces risk significantly\n"
            report += f"• Stop betting if you hit stop-loss level\n"
            report += f"• Take profits when target is reached\n"
            report += f"• Track every bet for performance analysis"
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating bankroll report: {e}")
            return f"Error generating report: {e}"

import random  # For simulation
