#!/usr/bin/env python3
# ============================================================
# 🎯 CONFLUENCE SCORER - Multi-Indicator Confluence Detection
# ============================================================
#
# Combines multiple indicators to calculate confluence scores
# for identifying high-probability trading opportunities.
#
# © 2026 Seliim Ahmed. All Rights Reserved.
#
# ============================================================

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConfluenceScorer:
    """
    Confluence Scorer
    
    Combines multiple indicators to identify:
    - High-confluence trading zones
    - Multi-indicator alignment
    - Probability-weighted opportunities
    """
    
    # Score levels
    SCORE_LEVELS = {
        'C18': {'min_score': 18, 'label': '🚀 FULL ALIGNMENT', 'confidence': 'VERY_HIGH'},
        'C15': {'min_score': 15, 'label': '🔥 STRONG CONFLUENCE', 'confidence': 'HIGH'},
        'C12': {'min_score': 12, 'label': '💪 MODERATE CONFLUENCE', 'confidence': 'MEDIUM_HIGH'},
        'C9': {'min_score': 9, 'label': '📊 WATCH ZONE', 'confidence': 'MEDIUM'},
        'C6': {'min_score': 6, 'label': '👀 OPPORTUNITY', 'confidence': 'LOW'},
        'C3': {'min_score': 3, 'label': '📡 SIGNAL', 'confidence': 'VERY_LOW'},
        'C0': {'min_score': 0, 'label': '🔴 NO CONFLUENCE', 'confidence': 'NONE'}
    }
    
    # Indicator weights for scoring
    INDICATOR_WEIGHTS = {
        'energy_flow': 0.30,
        'fibonacci': 0.25,
        'macro': 0.20,
        'support_resistance': 0.15,
        'trend': 0.10
    }
    
    def __init__(self):
        self.name = "Confluence Scorer"
        self.version = "1.0.0"
        self.score_levels = self.SCORE_LEVELS
        
        logger.info(f"🎯 {self.name} v{self.version} initialized")
        logger.info(f"   Score Levels: {list(self.score_levels.keys())}")
    
    def score_energy_flow(self, energy_result: Dict) -> int:
        """
        Score 3-6-9 energy flow
        
        Args:
            energy_result: Energy flow analysis result
            
        Returns:
            Score contribution (0-18)
        """
        if not energy_result or 'confluence' not in energy_result:
            return 0
        
        confluence = energy_result['confluence']
        score = confluence.get('score', 0)
        
        # Bonus for vortex detection
        if energy_result.get('vortex', {}).get('detected', False):
            score += 3
        
        # Bonus for energy levels
        energy_sum = sum(e.get('energy', 0) for e in energy_result.get('energy', {}).values())
        if energy_sum > 5:
            score += 2
        
        return min(score, 18)
    
    def score_fibonacci(self, fib_result: Dict) -> int:
        """
        Score Fibonacci levels
        
        Args:
            fib_result: Fibonacci analysis result
            
        Returns:
            Score contribution (0-15)
        """
        if not fib_result:
            return 0
        
        score = 0
        
        # Probability score
        probability = fib_result.get('probability', {})
        overall_prob = probability.get('overall_probability', 0)
        
        if overall_prob > 70:
            score += 10
        elif overall_prob > 50:
            score += 7
        elif overall_prob > 30:
            score += 4
        else:
            score += 1
        
        # Golden zone bonus
        golden_zone = fib_result.get('golden_zone', {})
        if golden_zone.get('in_zone', False):
            score += 3
        
        # Confluence bonus
        confluence = fib_result.get('confluence', {})
        if confluence.get('count', 0) > 0:
            score += 2
        
        return min(score, 15)
    
    def score_macro(self, macro_result: Dict) -> int:
        """
        Score macroeconomic conditions
        
        Args:
            macro_result: Macro analysis result
            
        Returns:
            Score contribution (0-10)
        """
        if not macro_result:
            return 0
        
        score = 0
        signal = macro_result.get('signal', {})
        regime = macro_result.get('regime', {})
        
        # Signal strength
        confidence = signal.get('confidence', 0)
        if confidence > 70:
            score += 6
        elif confidence > 50:
            score += 4
        elif confidence > 30:
            score += 2
        
        # Regime alignment
        sentiment = regime.get('sentiment', 'NEUTRAL')
        if sentiment == 'BULLISH':
            score += 2
        elif sentiment == 'BEARISH':
            score += 1
        
        # Weighted score
        weighted_score = macro_result.get('weighted_score', 0)
        if abs(weighted_score) > 1.5:
            score += 2
        
        return min(score, 10)
    
    def score_support_resistance(
        self,
        current_price: float,
        levels: List[float]
    ) -> int:
        """
        Score support/resistance levels
        
        Args:
            current_price: Current market price
            levels: List of support/resistance levels
            
        Returns:
            Score contribution (0-7)
        """
        if not levels:
            return 0
        
        score = 0
        tolerance = 0.002  # 0.2% tolerance
        
        for level in levels:
            price_diff = abs(current_price - level) / current_price
            if price_diff < tolerance:
                score += 3
                break
        
        # Check for multiple levels
        in_zone = 0
        for level in levels:
            price_diff = abs(current_price - level) / current_price
            if price_diff < 0.01:  # Within 1%
                in_zone += 1
        
        if in_zone >= 2:
            score += 2
        elif in_zone >= 1:
            score += 1
        
        return min(score, 7)
    
    def score_trend(self, price_data: pd.Series) -> int:
        """
        Score trend strength
        
        Args:
            price_data: Historical price data
            
        Returns:
            Score contribution (0-5)
        """
        if len(price_data) < 20:
            return 0
        
        score = 0
        recent = price_data[-20:]
        
        # Calculate trend
        sma_20 = recent.mean()
        sma_50 = price_data[-50:].mean() if len(price_data) >= 50 else sma_20
        
        # Trend direction
        if recent.iloc[-1] > sma_20:
            score += 2
            if sma_20 > sma_50:
                score += 1  # Uptrend confirmed
        else:
            score += 1
        
        # Trend strength (ADX or momentum proxy)
        returns = recent.pct_change()
        momentum = returns.mean() * 100
        
        if abs(momentum) > 0.5:
            score += 1
        
        # Volatility adjustment
        volatility = returns.std() * 100
        if volatility < 1.0:
            score += 1  # Low volatility = trend continuation
        
        return min(score, 5)
    
    def calculate_total_score(self, scores: Dict) -> int:
        """
        Calculate total confluence score
        
        Args:
            scores: Dict of component scores
            
        Returns:
            Total score (0-55)
        """
        total = 0
        for name, score in scores.items():
            if name in self.INDICATOR_WEIGHTS:
                weight = self.INDICATOR_WEIGHTS[name]
                total += score * weight
            else:
                total += score
        
        return int(total)
    
    def get_score_level(self, total_score: int) -> Dict:
        """
        Get score level classification
        
        Args:
            total_score: Total confluence score
            
        Returns:
            Score level details
        """
        for level, details in sorted(
            self.score_levels.items(),
            key=lambda x: x[1]['min_score'],
            reverse=True
        ):
            if total_score >= details['min_score']:
                return {
                    'level': level,
                    'label': details['label'],
                    'confidence': details['confidence'],
                    'score': total_score
                }
        
        return {
            'level': 'C0',
            'label': self.score_levels['C0']['label'],
            'confidence': self.score_levels['C0']['confidence'],
            'score': total_score
        }
    
    def analyze(
        self,
        price_data: pd.DataFrame,
        energy_result: Dict,
        fib_result: Dict,
        macro_result: Dict,
        current_price: float
    ) -> Dict:
        """
        Complete confluence analysis
        
        Args:
            price_data: OHLC price data
            energy_result: Energy flow analysis
            fib_result: Fibonacci analysis
            macro_result: Macro analysis
            current_price: Current market price
            
        Returns:
            Complete confluence analysis
        """
        # Calculate component scores
        scores = {}
        
        # 1. Energy Flow (max 18)
        scores['energy_flow'] = self.score_energy_flow(energy_result)
        
        # 2. Fibonacci (max 15)
        scores['fibonacci'] = self.score_fibonacci(fib_result)
        
        # 3. Macro (max 10)
        scores['macro'] = self.score_macro(macro_result)
        
        # 4. Support/Resistance (max 7)
        levels = self._get_key_levels(price_data)
        scores['support_resistance'] = self.score_support_resistance(current_price, levels)
        
        # 5. Trend (max 5)
        scores['trend'] = self.score_trend(price_data['close'])
        
        # Calculate total
        total_score = self.calculate_total_score(scores)
        
        # Get score level
        level = self.get_score_level(total_score)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(level, scores)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_score': total_score,
            'level': level['level'],
            'label': level['label'],
            'confidence': level['confidence'],
            'component_scores': scores,
            'levels': self._get_level_details(price_data),
            'recommendation': recommendation,
            'summary': {
                'confluence_level': level['level'],
                'primary_driver': max(scores, key=scores.get),
                'overall_confidence': level['confidence']
            }
        }
    
    def _get_key_levels(self, price_data: pd.DataFrame) -> List[float]:
        """
        Extract key support/resistance levels
        
        Args:
            price_data: OHLC price data
            
        Returns:
            List of support/resistance levels
        """
        levels = []
        recent = price_data.tail(100)
        
        # Find swing highs and lows
        high = recent['high'].max()
        low = recent['low'].min()
        
        levels.append(high)
        levels.append(low)
        
        # Add pivot points
        pivots = self._find_pivot_points(price_data)
        levels.extend(pivots)
        
        # Add round numbers
        current_price = price_data['close'].iloc[-1]
        round_levels = self._find_round_numbers(current_price)
        levels.extend(round_levels)
        
        return list(set(levels))  # Remove duplicates
    
    def _find_pivot_points(self, price_data: pd.DataFrame) -> List[float]:
        """
        Find pivot points using a simplified method
        
        Args:
            price_data: OHLC price data
            
        Returns:
            List of pivot points
        """
        pivots = []
        high = price_data['high']
        low = price_data['low']
        
        for i in range(2, len(high) - 2):
            # Check for pivot high
            if (high.iloc[i] > high.iloc[i-1] and 
                high.iloc[i] > high.iloc[i-2] and
                high.iloc[i] > high.iloc[i+1] and 
                high.iloc[i] > high.iloc[i+2]):
                pivots.append(high.iloc[i])
            
            # Check for pivot low
            if (low.iloc[i] < low.iloc[i-1] and 
                low.iloc[i] < low.iloc[i-2] and
                low.iloc[i] < low.iloc[i+1] and 
                low.iloc[i] < low.iloc[i+2]):
                pivots.append(low.iloc[i])
        
        return pivots
    
    def _find_round_numbers(self, current_price: float) -> List[float]:
        """
        Find round number levels
        
        Args:
            current_price: Current price
            
        Returns:
            List of round number levels
        """
        levels = []
        
        # Major round numbers
        base = int(current_price)
        for i in range(-3, 4):
            level = base + (i * 0.01) if base > 1 else base + (i * 0.001)
            if level > 0:
                levels.append(level)
        
        # 50% levels
        level_50 = round(current_price * 0.5, 4)
        levels.append(level_50)
        
        # 100% levels
        level_100 = round(current_price * 0.1, 4)
        levels.append(level_100)
        
        return levels
    
    def _get_level_details(self, price_data: pd.DataFrame) -> Dict:
        """
        Get detailed level information
        
        Args:
            price_data: OHLC price data
            
        Returns:
            Level details
        """
        high = price_data['high'].max()
        low = price_data['low'].min()
        current = price_data['close'].iloc[-1]
        
        # Calculate common levels
        pivot = (high + low + current) / 3
        r1 = (2 * pivot) - low
        s1 = (2 * pivot) - high
        r2 = pivot + (high - low)
        s2 = pivot - (high - low)
        
        return {
            'pivot': round(pivot, 5),
            'r1': round(r1, 5),
            'r2': round(r2, 5),
            's1': round(s1, 5),
            's2': round(s2, 5),
            'high': round(high, 5),
            'low': round(low, 5),
            'current': round(current, 5)
        }
    
    def _generate_recommendation(self, level: Dict, scores: Dict) -> Dict:
        """
        Generate trading recommendation
        
        Args:
            level: Score level details
            scores: Component scores
            
        Returns:
            Recommendation dict
        """
        # Determine action based on score and components
        action = 'HOLD'
        confidence = level['confidence']
        
        if level['level'] in ['C18', 'C15']:
            # Check if macro is bullish
            if scores.get('macro', 0) > 5:
                action = 'BUY'
            elif scores.get('macro', 0) < -5:
                action = 'SELL'
            else:
                action = 'WATCH'
        elif level['level'] in ['C12', 'C9']:
            action = 'WATCH'
        elif level['level'] in ['C6']:
            # Check for specific setups
            if scores.get('energy_flow', 0) > 10 and scores.get('fibonacci', 0) > 8:
                action = 'BUY'
            elif scores.get('energy_flow', 0) < -10 and scores.get('fibonacci', 0) < -8:
                action = 'SELL'
            else:
                action = 'MONITOR'
        else:
            action = 'HOLD'
        
        return {
            'action': action,
            'confidence': confidence,
            'risk': 'LOW' if confidence in ['HIGH', 'VERY_HIGH'] else 'MEDIUM',
            'rationale': f"Confluence level {level['level']} with {confidence} confidence"
        }


# ============================================================
# 🚀 USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    # Test the Confluence Scorer
    scorer = ConfluenceScorer()
    
    # Sample data
    np.random.seed(42)
    prices = 1.32000 + np.cumsum(np.random.randn(100) * 0.001)
    
    df = pd.DataFrame({
        'high': prices + 0.001,
        'low': prices - 0.001,
        'close': prices
    })
    
    # Simulate results
    energy_result = {'confluence': {'score': 12}, 'vortex': {'detected': True}, 'energy': {'node1': {'energy': 0.8}}}
    fib_result = {'probability': {'overall_probability': 65}, 'golden_zone': {'in_zone': True}}
    macro_result = {'signal': {'confidence': 70}, 'regime': {'sentiment': 'BULLISH'}, 'weighted_score': 1.8}
    current_price = 1.32190
    
    result = scorer.analyze(df, energy_result, fib_result, macro_result, current_price)
    
    print("\n" + "="*60)
    print("🎯 CONFLUENCE SCORE ANALYSIS")
    print("="*60)
    print(f"  📊 Total Score: {result['total_score']}")
    print(f"  🏆 Level: {result['level']} - {result['label']}")
    print(f"  📈 Confidence: {result['confidence']}")
    print(f"  🎯 Action: {result['recommendation']['action']}")
    print(f"  📊 Primary Driver: {result['summary']['primary_driver']}")
    print("="*60)
