def _calculate_prediction_confidence(self, odds_analysis: Dict, home_goals: int, away_goals: int) -> float:
    """Calculate confidence in the prediction"""
    try:
        # Base confidence from market consistency
        base_confidence = 65.0
        
        # Strong favorites get higher confidence
        max_win_prob = max(odds_analysis['home_win_probability'], odds_analysis['away_win_probability'])
        if max_win_prob > 0.8:  # 80%+ win probability
            base_confidence = 85.0
        elif max_win_prob > 0.6:  # 60%+ win probability  
            base_confidence = 75.0
        elif max_win_prob > 0.5:  # 50%+ win probability
            base_confidence = 68.0
        
        # Adjust based on bookmaker consensus
        if odds_analysis['bookmaker_count'] >= 8:
            base_confidence += 5.0
        elif odds_analysis['bookmaker_count'] >= 5:
            base_confidence += 2.0
        
        # Slight adjustment for goal totals
        total_goals = home_goals + away_goals
        if total_goals > 5:
            base_confidence -= 3.0
        elif total_goals < 1:
            base_confidence -= 5.0
        
        return min(max(base_confidence, 45.0), 90.0)
        
    except Exception as e:
        logger.error(f"Error calculating confidence: {e}")
        return 65.0
