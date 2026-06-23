#!/usr/bin/env python3
# ============================================================
# 📈 FIBONACCI - Golden Ratio Probability Calculator
# ============================================================
#
# Calculates Fibonacci retracement levels and
# probability of hitting each level
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


class Fibonacci:
    """
    Fibonacci Indicator
    
    Calculates:
    - Fibonacci retracement levels
    - Probability of hitting each level
    - Optimal zone selection
    - Confluence with 3-6-9 nodes
    """
    
    # Fibonacci levels (sacred ratios)
    FIB_LEVELS = [0.236, 0.382, 0.500, 0.618, 0.786]
    
    # Level labels
    LEVEL_LABELS = {
        0.236: '23.6%',
        0.382: '38.2%',
        0.500: '50.0%',
        0.618: '61.8% (Golden Ratio)',
        0.786: '78.6%'
    }
    
    # Zone widths for probability calculation
    ZONE_WIDTHS = [0.003, 0.005, 0.010, 0.020]  # 0.3%, 0.5%, 1.0%, 2.0%
    
    def __init__(self):
        self.name = "Fibonacci"
        self.version = "1.0.0"
        self.levels = self.FIB_LEVELS
        self.zone_widths = self.ZONE_WIDTHS
        
        logger.info(f"📈 {self.name} v{self.version} initialized")
        logger.info(f"   Fibonacci Levels: {self.levels}")
        logger.info(f"   Zone Widths: {self.zone_widths}")
    
    def calculate_levels(self, high: float, low: float) -> Dict[str, float]:
        """
        Calculate Fibonacci retracement levels
        
        Args:
            high: Highest price
            low: Lowest price
            
        Returns:
            Dict of level names to prices
        """
        diff = high - low
        levels = {}
        
        for level in self.levels:
            name = self.LEVEL_LABELS.get(level, f'{level*100:.1f}%')
            levels[name] = high - (diff * level)
        
        # Add extension levels
        levels['161.8%'] = high + (diff * 0.618)
        levels['261.8%'] = high + (diff * 1.618)
        
        return levels
    
    def calculate_probability(
        self,
        levels: Dict[str, float],
        price_data: pd.Series,
        lookback: int = 100
    ) -> Dict:
        """
        Calculate probability of hitting Fibonacci levels
        
        Args:
            levels: Fibonacci levels from calculate_levels
            price_data: Historical price data
            lookback: Number of bars to analyze
            
        Returns:
            Probability for each level and zone width
        """
        recent = price_data[-lookback:]
        if len(recent) < 10:
            return {'error': 'Insufficient data'}
        
        results = {}
        total_touches = 0
        
        for level_name, level_price in levels.items():
            zone_probs = {}
            
            for width in self.zone_widths:
                zone_high = level_price * (1 + width)
                zone_low = level_price * (1 - width)
                
                # Count touches within zone
                touches = sum(
                    1 for p in recent
                    if zone_low <= p <= zone_high
                )
                
                probability = (touches / len(recent)) * 100
                zone_probs[f'{width*100:.1f}%'] = round(probability, 1)
                total_touches += touches
            
            # Average probability across zones
            avg_prob = sum(zone_probs.values()) / len(zone_probs)
            
            results[level_name] = {
                'price': level_price,
                'zones': zone_probs,
                'avg_probability': round(avg_prob, 1),
                'touches': touches
            }
        
        # Overall statistics
        overall_avg = sum(r['avg_probability'] for r in results.values()) / len(results)
        
        return {
            'levels': results,
            'overall_probability': round(overall_avg, 1),
            'sample_size': len(recent),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_optimal_zone(
        self,
        probability_results: Dict
    ) -> Tuple[Optional[str], Optional[float], Optional[str]]:
        """
        Find optimal zone based on highest probability
        
        Args:
            probability_results: Results from calculate_probability
            
        Returns:
            Tuple of (level, probability, zone_width)
        """
        if 'error' in probability_results:
            return None, 0, None
        
        best_level = None
        best_prob = 0
        best_width = None
        
        for level_name, level_data in probability_results.get('levels', {}).items():
            for width, prob in level_data.get('zones', {}).items():
                if prob > best_prob:
                    best_prob = prob
                    best_level = level_name
                    best_width = width
        
        return best_level, best_prob, best_width
    
    def calculate_golden_zone(
        self,
        high: float,
        low: float,
        price_data: pd.Series
    ) -> Dict:
        """
        Calculate the golden zone (61.8% - 78.6%)
        
        Args:
            high: Highest price
            low: Lowest price
            price_data: Historical price data
            
        Returns:
            Golden zone analysis
        """
        diff = high - low
        
        # Golden zone boundaries
        zone_low = high - (diff * 0.786)  # 78.6% level
        zone_high = high - (diff * 0.618)  # 61.8% level
        
        # Check if price is in golden zone
        current_price = price_data.iloc[-1]
        in_zone = zone_low <= current_price <= zone_high
        
        # Calculate probability of reversal in golden zone
        recent = price_data[-100:]
        touches_in_zone = sum(
            1 for p in recent
            if zone_low <= p <= zone_high
        )
        
        reversal_probability = (touches_in_zone / len(recent)) * 100
        
        return {
            'zone_low': round(zone_low, 5),
            'zone_high': round(zone_high, 5),
            'in_zone': in_zone,
            'reversal_probability': round(reversal_probability, 1),
            'current_price': round(current_price, 5),
            'zone_size': round(zone_high - zone_low, 5)
        }
    
    def find_confluence(
        self,
        fib_levels: Dict[str, float],
        energy_nodes: Dict
    ) -> Dict:
        """
        Find confluence between Fibonacci levels and 3-6-9 nodes
        
        Args:
            fib_levels: Fibonacci levels from calculate_levels
            energy_nodes: Energy nodes from EnergyFlow
            
        Returns:
            Confluence points
        """
        confluence_points = []
        tolerance = 0.002  # 0.2% tolerance
        
        for node, node_data in energy_nodes.items():
            if node_data.get('count', 0) > 0:
                # Check if node aligns with Fibonacci levels
                for level_name, level_price in fib_levels.items():
                    # Check if node price matches Fibonacci level
                    if 'first' in node_data and node_data['first']:
                        node_price = node_data['first']
                        price_diff = abs(node_price - level_price) / level_price
                        
                        if price_diff < tolerance:
                            confluence_points.append({
                                'node': node,
                                'fib_level': level_name,
                                'node_price': round(node_price, 5),
                                'fib_price': round(level_price, 5),
                                'diff': round(price_diff * 100, 2),
                                'strength': 1 - (price_diff / tolerance)
                            })
        
        # Sort by strength
        confluence_points.sort(key=lambda x: x['strength'], reverse=True)
        
        return {
            'points': confluence_points,
            'count': len(confluence_points),
            'timestamp': datetime.now().isoformat()
        }
    
    def analyze(self, price_data: pd.DataFrame) -> Dict:
        """
        Complete Fibonacci analysis
        
        Args:
            price_data: DataFrame with OHLC data
            
        Returns:
            Complete Fibonacci analysis
        """
        if price_data.empty:
            return {'error': 'No data provided'}
        
        high = price_data['high'].max()
        low = price_data['low'].min()
        close = price_data['close']
        
        # Calculate levels
        levels = self.calculate_levels(high, low)
        
        # Calculate probability
        probability = self.calculate_probability(levels, close)
        
        # Get optimal zone
        best_level, best_prob, best_width = self.get_optimal_zone(probability)
        
        # Calculate golden zone
        golden_zone = self.calculate_golden_zone(high, low, close)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'high': high,
            'low': low,
            'current_price': close.iloc[-1],
            'levels': levels,
            'probability': probability,
            'optimal_level': best_level,
            'optimal_probability': best_prob,
            'optimal_width': best_width,
            'golden_zone': golden_zone,
            'summary': {
                'total_levels': len(levels),
                'avg_probability': probability.get('overall_probability', 0),
                'golden_zone_active': golden_zone['in_zone']
            }
        }


# ============================================================
# 🚀 USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    # Test the Fibonacci indicator
    fib = Fibonacci()
    
    # Create sample data
    np.random.seed(42)
    prices = 1.32000 + np.cumsum(np.random.randn(100) * 0.001)
    
    df = pd.DataFrame({
        'high': prices + 0.001,
        'low': prices - 0.001,
        'close': prices
    })
    
    # Analyze
    result = fib.analyze(df)
    
    print("\n" + "="*60)
    print("📈 FIBONACCI ANALYSIS RESULT")
    print("="*60)
    print(f"  📍 Current Price: {result['current_price']:.5f}")
    print(f"  📊 Optimal Level: {result['optimal_level']}")
    print(f"  🎯 Probability: {result['optimal_probability']}%")
    print(f"  📐 Golden Zone: {result['golden_zone']['in_zone']}")
    print(f"  📈 Avg Probability: {result['summary']['avg_probability']}%")
    print("="*60)
