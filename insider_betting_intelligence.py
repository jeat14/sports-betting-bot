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
