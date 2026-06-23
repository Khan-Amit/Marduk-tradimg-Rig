#!/usr/bin/env python3
# ============================================================
# 🌍 MACRO INDICATORS - Global Economic Data
# ============================================================
#
# Fetches and analyzes macroeconomic indicators
# including CPI, GDP, PMI, interest rates, etc.
#
# © 2026 Seliim Ahmed. All Rights Reserved.
#
# ============================================================

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import logging
import requests
import time

logger = logging.getLogger(__name__)


class MacroIndicators:
    """
    Macro Indicators
    
    Fetches and analyzes:
    - CPI (Consumer Price Index)
    - GDP Growth
    - Interest Rates
    - PMI (Purchasing Managers Index)
    - Retail Sales
    - Trade Balance
    - Unemployment
    - Consumer Confidence
    """
    
    # Indicator weights (importance)
    INDICATOR_WEIGHTS = {
        'cpi': 1.0,
        'gdp': 2.0,      # High importance
        'interest_rate': 2.0,  # High importance
        'pmi': 1.0,
        'retail_sales': 1.0,
        'trade_balance': 1.0,
        'unemployment': 1.0,
        'consumer_confidence': 0.5
    }
    
    # Indicator descriptions
    INDICATOR_DESCRIPTIONS = {
        'cpi': 'Consumer Price Index (Inflation)',
        'gdp': 'GDP Growth Rate',
        'interest_rate': 'Central Bank Interest Rate',
        'pmi': 'Purchasing Managers Index',
        'retail_sales': 'Retail Sales Growth',
        'trade_balance': 'Trade Balance',
        'unemployment': 'Unemployment Rate',
        'consumer_confidence': 'Consumer Confidence Index'
    }
    
    # Economic regimes
    REGIMES = {
        'GOLDILOCKS': {
            'description': 'High Growth, Low Inflation',
            'sentiment': 'BULLISH',
            'risk': 'LOW'
        },
        'OVERHEATING': {
            'description': 'High Growth, High Inflation',
            'sentiment': 'BEARISH',
            'risk': 'MEDIUM'
        },
        'RECESSION': {
            'description': 'Low Growth, Low Inflation',
            'sentiment': 'BEARISH',
            'risk': 'HIGH'
        },
        'STAGFLATION': {
            'description': 'Low Growth, High Inflation',
            'sentiment': 'BEARISH',
            'risk': 'HIGH'
        },
        'NEUTRAL': {
            'description': 'Balanced Growth, Moderate Inflation',
            'sentiment': 'NEUTRAL',
            'risk': 'MEDIUM'
        }
    }
    
    def __init__(self):
        self.name = "Macro Indicators"
        self.version = "1.0.0"
        self.weights = self.INDICATOR_WEIGHTS
        self.cache = {}
        self.cache_timeout = 3600  # 1 hour cache
        
        logger.info(f"🌍 {self.name} v{self.version} initialized")
        logger.info(f"   Indicators: {list(self.weights.keys())}")
    
    def fetch_indicators(self, country: str = 'US') -> Dict:
        """
        Fetch real macroeconomic indicators
        
        In production, this would connect to:
        - FRED API (Federal Reserve)
        - World Bank API
        - Trading Economics API
        - Bloomberg API
        
        Args:
            country: Country code (US, EU, UK, etc.)
            
        Returns:
            Dict of indicator values
        """
        # Check cache
        cache_key = f"macro_{country}"
        if cache_key in self.cache:
            cache_time = self.cache[cache_key]['timestamp']
            if (datetime.now() - cache_time).seconds < self.cache_timeout:
                logger.info(f"📦 Using cached macro data for {country}")
                return self.cache[cache_key]['data']
        
        logger.info(f"🌍 Fetching macro data for {country}")
        
        # In production, use real API
        # For now, return realistic sample data
        sample_data = self._get_sample_data(country)
        
        # Cache the data
        self.cache[cache_key] = {
            'data': sample_data,
            'timestamp': datetime.now()
        }
        
        return sample_data
    
    def _get_sample_data(self, country: str) -> Dict:
        """
        Get sample macroeconomic data
        
        Args:
            country: Country code
            
        Returns:
            Sample indicator data
        """
        # Realistic sample data based on current economic conditions
        base_data = {
            'cpi': {'current': 2.5, 'mean': 2.0, 'std': 0.5, 'trend': 'rising'},
            'gdp': {'current': 3.2, 'mean': 2.5, 'std': 0.8, 'trend': 'growing'},
            'interest_rate': {'current': 5.0, 'mean': 4.5, 'std': 0.3, 'trend': 'stable'},
            'pmi': {'current': 52.0, 'mean': 50.0, 'std': 5.0, 'trend': 'expanding'},
            'retail_sales': {'current': 4.5, 'mean': 3.5, 'std': 1.0, 'trend': 'rising'},
            'trade_balance': {'current': -50.0, 'mean': -40.0, 'std': 10.0, 'trend': 'worsening'},
            'unemployment': {'current': 3.8, 'mean': 4.5, 'std': 0.5, 'trend': 'falling'},
            'consumer_confidence': {'current': 65.0, 'mean': 60.0, 'std': 5.0, 'trend': 'improving'}
        }
        
        # Country-specific adjustments
        country_adjustments = {
            'EU': {'gdp': {'current': 2.8}, 'interest_rate': {'current': 4.25}},
            'UK': {'gdp': {'current': 2.5}, 'interest_rate': {'current': 4.75}},
            'JP': {'gdp': {'current': 1.8}, 'interest_rate': {'current': 0.1}},
            'CN': {'gdp': {'current': 5.2}, 'interest_rate': {'current': 3.45}}
        }
        
        if country in country_adjustments:
            for key, values in country_adjustments[country].items():
                if key in base_data:
                    base_data[key].update(values)
        
        return base_data
    
    def calculate_z_scores(self, indicators: Dict) -> Dict:
        """
        Calculate Z-Scores for all indicators
        
        Args:
            indicators: Indicator data from fetch_indicators
            
        Returns:
            Z-Scores for each indicator
        """
        z_scores = {}
        
        for name, data in indicators.items():
            if 'current' in data and 'mean' in data and 'std' in data:
                z = (data['current'] - data['mean']) / data['std']
                z_scores[name] = round(z, 2)
            else:
                z_scores[name] = 0
        
        return z_scores
    
    def calculate_weighted_score(self, z_scores: Dict) -> float:
        """
        Calculate weighted overall score
        
        Args:
            z_scores: Z-Scores from calculate_z_scores
            
        Returns:
            Weighted score
        """
        weighted_sum = 0
        total_weight = 0
        
        for name, z in z_scores.items():
            if name in self.weights:
                weight = self.weights[name]
                weighted_sum += z * weight
                total_weight += weight
        
        if total_weight > 0:
            return round(weighted_sum / total_weight, 2)
        return 0
    
    def detect_regime(self, z_scores: Dict) -> Dict:
        """
        Detect economic regime
        
        Args:
            z_scores: Z-Scores from calculate_z_scores
            
        Returns:
            Regime classification
        """
        growth_z = z_scores.get('gdp', 0)
        inflation_z = z_scores.get('cpi', 0)
        rates_z = z_scores.get('interest_rate', 0)
        
        # Determine regime
        if growth_z > 1.0 and inflation_z < 0.5:
            regime = 'GOLDILOCKS'
        elif growth_z > 1.0 and inflation_z > 1.0:
            regime = 'OVERHEATING'
        elif growth_z < -1.0 and inflation_z < -0.5:
            regime = 'RECESSION'
        elif growth_z < -0.5 and inflation_z > 1.0:
            regime = 'STAGFLATION'
        else:
            regime = 'NEUTRAL'
        
        regime_info = self.REGIMES.get(regime, self.REGIMES['NEUTRAL'])
        
        return {
            'name': regime,
            'description': regime_info['description'],
            'sentiment': regime_info['sentiment'],
            'risk': regime_info['risk'],
            'growth_z': growth_z,
            'inflation_z': inflation_z,
            'rates_z': rates_z
        }
    
    def generate_signal(self, z_scores: Dict, regime: Dict) -> Dict:
        """
        Generate trading signal from macro data
        
        Args:
            z_scores: Z-Scores from calculate_z_scores
            regime: Regime from detect_regime
            
        Returns:
            Trading signal
        """
        signal = {
            'direction': 'NEUTRAL',
            'confidence': 0,
            'strength': 0,
            'indicators': {},
            'regime': regime['name']
        }
        
        # Base direction from regime
        if regime['sentiment'] == 'BULLISH':
            signal['direction'] = 'BULLISH'
            signal['strength'] = 0.7
        elif regime['sentiment'] == 'BEARISH':
            signal['direction'] = 'BEARISH'
            signal['strength'] = 0.7
        else:
            signal['direction'] = 'NEUTRAL'
            signal['strength'] = 0.3
        
        # Adjust based on individual indicators
        for name, z in z_scores.items():
            if name in self.weights:
                if z > 1.5:
                    signal['indicators'][name] = 'BULLISH'
                    signal['strength'] += 0.1
                elif z < -1.5:
                    signal['indicators'][name] = 'BEARISH'
                    signal['strength'] -= 0.1
                else:
                    signal['indicators'][name] = 'NEUTRAL'
        
        # Calculate confidence
        signal['confidence'] = min(
            abs(signal['strength']) * 100,
            100
        )
        signal['strength'] = round(signal['strength'], 2)
        signal['confidence'] = round(signal['confidence'], 1)
        
        return signal
    
    def get_recommendations(self, regime: Dict) -> Dict:
        """
        Get asset allocation recommendations
        
        Args:
            regime: Regime from detect_regime
            
        Returns:
            Asset allocation recommendations
        """
        recommendations = {
            'GOLDILOCKS': {
                'action': 'BUY',
                'assets': ['Stocks', 'Cyclicals', 'Technology', 'Risk-on'],
                'risk': 'LOW',
                'description': 'Buy growth assets, overweight equities'
            },
            'OVERHEATING': {
                'action': 'REDUCE',
                'assets': ['Bonds', 'Gold', 'Defensives', 'Commodities'],
                'risk': 'MEDIUM',
                'description': 'Reduce growth exposure, add inflation hedges'
            },
            'RECESSION': {
                'action': 'DEFENSIVE',
                'assets': ['Bonds', 'Gold', 'Utilities', 'Consumer Staples'],
                'risk': 'HIGH',
                'description': 'Defensive positioning, preserve capital'
            },
            'STAGFLATION': {
                'action': 'HEDGE',
                'assets': ['Gold', 'Commodities', 'Inflation-linked Bonds'],
                'risk': 'HIGH',
                'description': 'Protect against inflation and growth risks'
            },
            'NEUTRAL': {
                'action': 'HOLD',
                'assets': ['Balanced', 'Diversified', '60/40 Portfolio'],
                'risk': 'MEDIUM',
                'description': 'Maintain current allocation'
            }
        }
        
        return recommendations.get(regime['name'], recommendations['NEUTRAL'])
    
    def analyze(self, country: str = 'US') -> Dict:
        """
        Complete macroeconomic analysis
        
        Args:
            country: Country code
            
        Returns:
            Complete macro analysis
        """
        # Fetch data
        indicators = self.fetch_indicators(country)
        
        # Calculate Z-Scores
        z_scores = self.calculate_z_scores(indicators)
        
        # Calculate weighted score
        weighted_score = self.calculate_weighted_score(z_scores)
        
        # Detect regime
        regime = self.detect_regime(z_scores)
        
        # Generate signal
        signal = self.generate_signal(z_scores, regime)
        
        # Get recommendations
        recommendations = self.get_recommendations(regime)
        
        # Format indicator table
        indicator_table = []
        for name, data in indicators.items():
            indicator_table.append({
                'indicator': name,
                'description': self.INDICATOR_DESCRIPTIONS.get(name, name),
                'current': data.get('current'),
                'z_score': z_scores.get(name, 0),
                'trend': data.get('trend', 'stable'),
                'weight': self.weights.get(name, 1.0)
            })
        
        return {
            'timestamp': datetime.now().isoformat(),
            'country': country,
            'indicators': indicator_table,
            'z_scores': z_scores,
            'weighted_score': weighted_score,
            'regime': regime,
            'signal': signal,
            'recommendations': recommendations,
            'summary': {
                'regime': regime['name'],
                'sentiment': regime['sentiment'],
                'overall_signal': signal['direction'],
                'confidence': signal['confidence'],
                'risk_level': regime['risk']
            }
        }


# ============================================================
# 🚀 USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    # Test the Macro Indicators
    macro = MacroIndicators()
    
    # Analyze US economy
    result = macro.analyze('US')
    
    print("\n" + "="*60)
    print("🌍 MACRO INDICATORS ANALYSIS")
    print("="*60)
    print(f"  📊 Country: {result['country']}")
    print(f"  🏛️  Regime: {result['regime']['name']}")
    print(f"  📈 Sentiment: {result['regime']['sentiment']}")
    print(f"  🎯 Overall Signal: {result['signal']['direction']}")
    print(f"  📊 Confidence: {result['signal']['confidence']}%")
    print(f"  📋 Recommendation: {result['recommendations']['action']}")
    print(f"  📊 Assets: {', '.join(result['recommendations']['assets'])}")
    print("="*60)
