#!/usr/bin/env python3
# ============================================================
# 🌍 MACRO ENGINE - Global Economic Analysis
# ============================================================
#
# Analyzes macroeconomic indicators using Z-Score normalization
# and classifies economic regimes
#
# © 2026 Seliim Ahmed. All Rights Reserved.
#
# ============================================================

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
import json
import requests

logger = logging.getLogger(__name__)


class MacroEngine:
    """
    Macro-Quantamental Engine
    
    Analyzes global economic indicators to determine
    market regimes and generate macro signals.
    """
    
    # Macro indicators with weights
    MACRO_WEIGHTS = {
        'cpi': 1.0,           # Consumer Price Index
        'interest_rate': 2.0,  # Central bank rate (HIGH IMPORTANCE)
        'gdp': 2.0,           # GDP Growth (HIGH IMPORTANCE)
        'pmi': 1.0,           # Purchasing Managers Index
        'retail_sales': 1.0,  # Retail Sales
        'trade_balance': 1.0, # Trade Balance
        'unemployment': 1.0,  # Unemployment Rate
        'consumer_confidence': 0.5  # Consumer Confidence
    }
    
    # Economic regimes
    REGIMES = {
        'GOLDILOCKS': {
            'description': 'High Growth, Low Inflation',
            'sentiment': 'BULLISH',
            'z_threshold': (1.0, 1.0)  # (growth, inflation)
        },
        'OVERHEATING': {
            'description': 'High Growth, High Inflation',
            'sentiment': 'BEARISH',
            'z_threshold': (1.0, 1.0)
        },
        'RECESSION': {
            'description': 'Low Growth, Low Inflation',
            'sentiment': 'BEARISH',
            'z_threshold': (-1.0, -1.0)
        },
        'STAGFLATION': {
            'description': 'Low Growth, High Inflation',
            'sentiment': 'BEARISH',
            'z_threshold': (-1.0, 1.0)
        }
    }
    
    def __init__(self):
        self.name = "Macro Engine"
        self.version = "1.0.0"
        self.weights = self.MACRO_WEIGHTS
        self.regimes = self.REGIMES
        self.cache = {}
        
        logger.info(f"🌍 {self.name} v{self.version} initialized")
        logger.info(f"   Indicators: {list(self.weights.keys())}")
    
    def calculate_z_score(self, value: float, mean: float, std: float) -> float:
        """
        Calculate Z-Score for a macroeconomic indicator
        
        Z-Score = (Current - Mean) / Standard Deviation
        
        Args:
            value: Current value
            mean: Historical mean
            std: Historical standard deviation
            
        Returns:
            Z-Score value
        """
        if std == 0:
            return 0.0
        return (value - mean) / std
    
    def analyze_indicators(self, indicators: Dict) -> Dict:
        """
        Analyze macroeconomic indicators
        
        Args:
            indicators: Dict of indicator values with mean and std
            
        Returns:
            Analysis result with Z-Scores and weighted aggregation
        """
        z_scores = {}
        weighted_sum = 0
        total_weight = 0
        
        for name, data in indicators.items():
            if name in self.weights and 'current' in data:
                mean = data.get('mean', 0)
                std = data.get('std', 1)
                current = data['current']
                
                z = self.calculate_z_score(current, mean, std)
                z_scores[name] = z
                
                weight = self.weights.get(name, 1.0)
                weighted_sum += z * weight
                total_weight += weight
        
        overall_z = weighted_sum / total_weight if total_weight > 0 else 0
        
        # Detect regime
        regime = self._detect_regime(z_scores)
        
        # Generate signal
        signal = self._generate_signal(overall_z, z_scores)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'z_scores': z_scores,
            'overall_z': overall_z,
            'regime': regime,
            'signal': signal,
            'strength': abs(overall_z)
        }
    
    def _detect_regime(self, z_scores: Dict) -> Dict:
        """
        Detect economic regime based on Z-Scores
        
        Args:
            z_scores: Dict of Z-Scores for each indicator
            
        Returns:
            Regime classification with description and sentiment
        """
        growth_z = z_scores.get('gdp', 0)
        inflation_z = z_scores.get('cpi', 0)
        
        # Determine regime
        if growth_z > 1.0 and inflation_z < 1.0:
            regime = 'GOLDILOCKS'
        elif growth_z > 1.0 and inflation_z > 1.0:
            regime = 'OVERHEATING'
        elif growth_z < -1.0 and inflation_z < -1.0:
            regime = 'RECESSION'
        elif growth_z < -1.0 and inflation_z > 1.0:
            regime = 'STAGFLATION'
        else:
            regime = 'NEUTRAL'
        
        regime_info = self.REGIMES.get(regime, {
            'description': 'Neutral',
            'sentiment': 'NEUTRAL'
        })
        
        return {
            'name': regime,
            'description': regime_info.get('description', 'Neutral'),
            'sentiment': regime_info.get('sentiment', 'NEUTRAL'),
            'growth_z': growth_z,
            'inflation_z': inflation_z
        }
    
    def _generate_signal(self, overall_z: float, z_scores: Dict) -> Dict:
        """
        Generate macro trading signal
        
        Args:
            overall_z: Overall Z-Score
            z_scores: Individual Z-Scores
            
        Returns:
            Signal dict with direction and confidence
        """
        signal = {
            'direction': 'NEUTRAL',
            'strength': abs(overall_z),
            'confidence': min(abs(overall_z) * 50, 100),
            'indicators': {}
        }
        
        # Direction based on overall Z
        if overall_z > 1.5:
            signal['direction'] = 'BULLISH'
        elif overall_z < -1.5:
            signal['direction'] = 'BEARISH'
        elif overall_z > 0.5:
            signal['direction'] = 'SLIGHTLY_BULLISH'
        elif overall_z < -0.5:
            signal['direction'] = 'SLIGHTLY_BEARISH'
        
        # Individual indicator signals
        for name, z in z_scores.items():
            if name in self.weights:
                if z > 1.5:
                    signal['indicators'][name] = 'BULLISH'
                elif z < -1.5:
                    signal['indicators'][name] = 'BEARISH'
                else:
                    signal['indicators'][name] = 'NEUTRAL'
        
        return signal
    
    def fetch_indicators(self, country: str = 'US') -> Dict:
        """
        Fetch real macroeconomic indicators from API
        
        Args:
            country: Country code (US, EU, UK, etc.)
            
        Returns:
            Dict of indicator values
        """
        # This would connect to a real economic data API
        # For now, returns sample data
        
        # Sample indicators (in reality, fetch from FRED, World Bank, etc.)
        sample_data = {
            'cpi': {'current': 2.5, 'mean': 2.0, 'std': 0.5},
            'gdp': {'current': 3.2, 'mean': 2.5, 'std': 0.8},
            'interest_rate': {'current': 5.0, 'mean': 4.5, 'std': 0.3},
            'pmi': {'current': 52.0, 'mean': 50.0, 'std': 5.0},
            'retail_sales': {'current': 4.5, 'mean': 3.5, 'std': 1.0},
            'trade_balance': {'current': -50.0, 'mean': -40.0, 'std': 10.0},
            'unemployment': {'current': 3.8, 'mean': 4.5, 'std': 0.5},
            'consumer_confidence': {'current': 65.0, 'mean': 60.0, 'std': 5.0}
        }
        
        return sample_data
    
    def get_regime_recommendation(self, regime: Dict) -> Dict:
        """
        Get trading recommendations based on regime
        
        Args:
            regime: Regime classification from _detect_regime
            
        Returns:
            Dict of recommendations
        """
        recommendations = {
            'GOLDILOCKS': {
                'action': 'BUY',
                'assets': ['Stocks', 'Cyclicals', 'Risk-on'],
                'risk': 'LOW',
                'description': 'Buy growth assets'
            },
            'OVERHEATING': {
                'action': 'REDUCE',
                'assets': ['Bonds', 'Gold', 'Defensives'],
                'risk': 'MEDIUM',
                'description': 'Reduce exposure to growth'
            },
            'RECESSION': {
                'action': 'DEFENSIVE',
                'assets': ['Bonds', 'Gold', 'Utilities'],
                'risk': 'HIGH',
                'description': 'Defensive positioning'
            },
            'STAGFLATION': {
                'action': 'HEDGE',
                'assets': ['Gold', 'Commodities', 'Inflation-linked'],
                'risk': 'HIGH',
                'description': 'Protect against inflation'
            },
            'NEUTRAL': {
                'action': 'HOLD',
                'assets': ['Balanced', 'Diversified'],
                'risk': 'MEDIUM',
                'description': 'Maintain current allocation'
            }
        }
        
        return recommendations.get(regime['name'], {
            'action': 'HOLD',
            'assets': ['Cash'],
            'risk': 'LOW',
            'description': 'Wait for clarity'
        })
    
    def analyze_market_context(self, indicators: Optional[Dict] = None) -> Dict:
        """
        Complete macro analysis
        
        Args:
            indicators: Optional indicator data
            
        Returns:
            Complete macro analysis
        """
        if indicators is None:
            indicators = self.fetch_indicators()
        
        # Analyze indicators
        analysis = self.analyze_indicators(indicators)
        
        # Get recommendations
        recommendations = self.get_regime_recommendation(analysis['regime'])
        
        return {
            **analysis,
            'recommendations': recommendations
        }


# ============================================================
# 🚀 USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    # Test the Macro Engine
    engine = MacroEngine()
    
    # Analyze with sample data
    result = engine.analyze_market_context()
    
    print("\n" + "="*60)
    print("🌍 MACRO ENGINE ANALYSIS RESULT")
    print("="*60)
    print(f"  📊 Overall Z-Score: {result['overall_z']:.2f}")
    print(f"  🏛️  Regime: {result['regime']['name']}")
    print(f"     {result['regime']['description']}")
    print(f"  📈 Sentiment: {result['regime']['sentiment']}")
    print(f"  🎯 Signal: {result['signal']['direction']} (Confidence: {result['signal']['confidence']:.1f}%)")
    print(f"  📋 Recommendation: {result['recommendations']['action']}")
    print(f"     {result['recommendations']['description']}")
    print(f"  📊 Assets: {', '.join(result['recommendations']['assets'])}")
    print("="*60)
