#!/usr/bin/env python3
"""
Test script to validate prediction accuracy
"""

import os
from odds_service import OddsService
from prediction_engine import PredictionEngine

def test_predictions():
    """Test the prediction engine with current data"""
    # Set environment variables for testing
    os.environ['ODDS_API_KEY'] = 'b042ef3e00a923abda5dade83334ec20'
    
    odds_service = OddsService()
    prediction_engine = PredictionEngine(odds_service)
    
    print("Testing FIFA Club World Cup predictions...")
    predictions = prediction_engine.generate_predictions('soccer_fifa_club_world_cup')
    
    if predictions:
        for pred in predictions:
            rec = pred['recommendation']
            market = pred.get('market_analysis', {})
            
            print(f"\n--- {pred['home_team']} vs {pred['away_team']} ---")
            print(f"Market Favorite: {market.get('favorite', 'Unknown')}")
            print(f"Favorite Probability: {market.get('favorite_probability', 0):.1f}%")
            print(f"Bot Recommends: {rec['bet_on']}")
            print(f"Strategy: {market.get('strategy', 'unknown')}")
            print(f"Reasoning: {rec['reasoning']}")
            print(f"Confidence: {rec['confidence']}%")
            
            # Show all team probabilities
            print("All Teams Analysis:")
            for team, stats in pred['all_teams_analysis'].items():
                print(f"  {team}: {stats['implied_probability']:.1f}% ({stats['avg_odds']} odds)")
    else:
        print("No predictions available")

if __name__ == "__main__":
    test_predictions()