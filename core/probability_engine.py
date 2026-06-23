#!/usr/bin/env python3
# ============================================================
# 📊 PROBABILITY ENGINE - Statistical & Probability Calculations
# ============================================================
#
# Calculates probabilities of price movements, Fibonacci hits,
# and provides statistical confidence metrics
#
# © 2026 Seliim Ahmed. All Rights Reserved.
#
# ============================================================

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from scipy import stats
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ProbabilityEngine:
    """
    Probability Engine
    
    Calculates statistical probabilities for price movements,
    Fibonacci level hits, and provides confidence metrics.
    """
    
    def __init__(self):
        self.name = "Probability Engine"
        self.version = "1.0.0"
        
        # Confidence levels
        self.CONFIDENCE_LEVELS = {
            'VERY_LOW': 0.20,
            'LOW': 0.40,
            'MEDIUM': 0.60,
            'HIGH': 0.80,
            'VERY_HIGH': 0.95
        }
        
        logger.info(f"📊 {self.name} v{self.version} initialized")
    
    def calculate_price_probability(
        self,
        current_price: float,
        target_price: float,
        price_data: pd.Series,
        lookback: int = 100
    ) -> Dict:
        """
        Calculate probability of reaching target price
        
        Args:
            current_price: Current market price
            target_price: Target price level
            price_data: Historical price data
            lookback: Number of bars to analyze
            
        Returns:
            Probability metrics
        """
        # Use recent data
        recent = price_data[-lookback:]
        if len(recent) < 10:
            return {'probability': 0, 'confidence': 'VERY_LOW', 'reason': 'Insufficient data'}
        
        # Calculate daily returns
        returns = recent.pct_change().dropna()
        
        # Expected return to target
        expected_return = (target_price / current_price) - 1
        
        # Historical volatility (standard deviation of returns)
        volatility = returns.std()
        
        if volatility == 0:
            return {'probability': 0, 'confidence': 'VERY_LOW', 'reason': 'Zero volatility'}
        
        # Z-Score of expected return
        z_score = expected_return / volatility
        
        # Probability from normal distribution
        probability = stats.norm.cdf(z_score)
        
        # Mean reversion adjustment
        mean_return = returns.mean()
        if mean_return > 0 and expected_return > 0:
            probability += 0.1  # Positive drift boosts probability
        
        # Cap probability between 0 and 1
        probability = max(0, min(1, probability))
        
        # Determine confidence level
        confidence = self._get_confidence_level(probability)
        
        return {
            'probability': round(probability * 100, 1),
            'confidence': confidence,
            'z_score': round(z_score, 2),
            'volatility': round(volatility * 100, 2),
            'expected_return': round(expected_return * 100, 2),
            'sample_size': len(recent)
        }
    
    def calculate_fibonacci_probability(
        self,
        fib_levels: Dict[str, float],
        price_data: pd.Series,
        lookback: int = 100
    ) -> Dict:
        """
        Calculate probability of hitting Fibonacci levels
        
        Args:
            fib_levels: Fibonacci levels from QuantumEngine
            price_data: Historical price data
            lookback: Number of bars to analyze
            
        Returns:
            Probability for each Fibonacci level
        """
        recent = price_data[-lookback:]
        if len(recent) < 10:
            return {'error': 'Insufficient data'}
        
        results = {}
        total_touches = 0
        total_bars = len(recent)
        
        for level_name, level_price in fib_levels.items():
            # Calculate probability for 1% zone
            zone_high = level_price * 1.005
            zone_low = level_price * 0.995
            
            # Count touches
            touches = sum(1 for p in recent if zone_low <= p <= zone_high)
            probability = (touches / total_bars) * 100
            
            results[level_name] = {
                'price': level_price,
                'touches': touches,
                'probability': round(probability, 1),
                'zone': '±0.5%'
            }
            
            total_touches += touches
        
        # Overall hit rate
        overall_probability = (total_touches / (total_bars * len(fib_levels))) * 100
        
        return {
            'levels': results,
            'overall_probability': round(overall_probability, 1),
            'sample_size': total_bars
        }
    
    def calculate_sharpe_ratio(
        self,
        returns: List[float],
        risk_free_rate: float = 0.02
    ) -> Dict:
        """
        Calculate Sharpe Ratio
        
        Args:
            returns: List of returns
            risk_free_rate: Risk-free rate (annualized)
            
        Returns:
            Sharpe ratio metrics
        """
        if not returns or len(returns) < 2:
            return {
                'sharpe_ratio': 0,
                'excess_return': 0,
                'volatility': 0,
                'confidence': 'VERY_LOW'
            }
        
        # Convert to numpy array
        ret_array = np.array(returns)
        
        # Annualized metrics (assuming daily returns)
        annualized_return = np.mean(ret_array) * 252
        annualized_volatility = np.std(ret_array) * np.sqrt(252)
        excess_return = annualized_return - risk_free_rate
        
        if annualized_volatility == 0:
            return {
                'sharpe_ratio': 0,
                'excess_return': 0,
                'volatility': 0,
                'confidence': 'VERY_LOW'
            }
        
        sharpe = excess_return / annualized_volatility
        
        # Confidence based on sample size
        confidence = self._get_confidence_level(
            min(1, len(returns) / 100)
        )
        
        return {
            'sharpe_ratio': round(sharpe, 2),
            'excess_return': round(excess_return * 100, 2),
            'volatility': round(annualized_volatility * 100, 2),
            'annualized_return': round(annualized_return * 100, 2),
            'sample_size': len(returns),
            'confidence': confidence
        }
    
    def calculate_max_drawdown(self, equity_curve: List[float]) -> Dict:
        """
        Calculate maximum drawdown
        
        Args:
            equity_curve: List of equity values
            
        Returns:
            Drawdown metrics
        """
        if not equity_curve or len(equity_curve) < 2:
            return {
                'max_drawdown': 0,
                'max_drawdown_duration': 0,
                'current_drawdown': 0,
                'confidence': 'VERY_LOW'
            }
        
        equity = np.array(equity_curve)
        running_max = np.maximum.accumulate(equity)
        drawdown = (running_max - equity) / running_max
        
        max_drawdown = np.max(drawdown)
        max_drawdown_index = np.argmax(drawdown)
        
        # Calculate duration of max drawdown
        if max_drawdown_index > 0:
            # Find when the running max was achieved
            running_max_before = running_max[:max_drawdown_index]
            if len(running_max_before) > 0:
                max_index = np.argmax(running_max_before)
                duration = max_drawdown_index - max_index
            else:
                duration = max_drawdown_index
        else:
            duration = 0
        
        current_drawdown = drawdown[-1] if len(drawdown) > 0 else 0
        
        return {
            'max_drawdown': round(max_drawdown * 100, 2),
            'max_drawdown_duration': int(duration),
            'current_drawdown': round(current_drawdown * 100, 2),
            'confidence': self._get_confidence_level(
                min(1, len(equity_curve) / 50)
            )
        }
    
    def calculate_win_rate(
        self,
        trades: List[Dict],
        include_breakeven: bool = True
    ) -> Dict:
        """
        Calculate win rate
        
        Args:
            trades: List of trade dicts with 'pnl' key
            include_breakeven: Whether to count breakeven as wins
            
        Returns:
            Win rate metrics
        """
        if not trades:
            return {
                'win_rate': 0,
                'wins': 0,
                'losses': 0,
                'breakeven': 0,
                'total_trades': 0,
                'confidence': 'VERY_LOW'
            }
        
        wins = 0
        losses = 0
        breakeven = 0
        
        for trade in trades:
            pnl = trade.get('pnl', 0)
            if pnl > 0:
                wins += 1
            elif pnl < 0:
                losses += 1
            else:
                breakeven += 1
        
        total = len(trades)
        
        if include_breakeven:
            winning_trades = wins + breakeven
        else:
            winning_trades = wins
        
        win_rate = (winning_trades / total) * 100 if total > 0 else 0
        
        # Profit factor
        total_profit = sum(t['pnl'] for t in trades if t.get('pnl', 0) > 0)
        total_loss = abs(sum(t['pnl'] for t in trades if t.get('pnl', 0) < 0))
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        return {
            'win_rate': round(win_rate, 1),
            'wins': wins,
            'losses': losses,
            'breakeven': breakeven,
            'total_trades': total,
            'profit_factor': round(profit_factor, 2) if profit_factor != float('inf') else 0,
            'avg_win': round(total_profit / wins, 2) if wins > 0 else 0,
            'avg_loss': round(total_loss / losses, 2) if losses > 0 else 0,
            'confidence': self._get_confidence_level(
                min(1, total / 20)
            )
        }
    
    def calculate_risk_reward_ratio(
        self,
        entry_price: float,
        stop_loss: float,
        take_profit: float
    ) -> Dict:
        """
        Calculate risk-reward ratio
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            
        Returns:
            Risk-reward metrics
        """
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        
        if risk == 0:
            return {
                'risk_reward_ratio': 0,
                'risk': 0,
                'reward': 0,
                'confidence': 'VERY_LOW'
            }
        
        ratio = reward / risk
        
        # Determine quality
        if ratio >= 3:
            quality = 'EXCELLENT'
            confidence = 'HIGH'
        elif ratio >= 2:
            quality = 'GOOD'
            confidence = 'MEDIUM'
        elif ratio >= 1:
            quality = 'ACCEPTABLE'
            confidence = 'LOW'
        else:
            quality = 'POOR'
            confidence = 'VERY_LOW'
        
        return {
            'risk_reward_ratio': round(ratio, 2),
            'risk': round(risk / entry_price * 100, 2),
            'reward': round(reward / entry_price * 100, 2),
            'quality': quality,
            'confidence': confidence
        }
    
    def _get_confidence_level(self, score: float) -> str:
        """
        Map score to confidence level
        
        Args:
            score: Score between 0 and 1
            
        Returns:
            Confidence level string
        """
        score = max(0, min(1, score))
        
        for level, threshold in self.CONFIDENCE_LEVELS.items():
            if score >= threshold:
                return level
        
        return 'VERY_LOW'
    
    def calculate_overall_probability(
        self,
        price_prob: Dict,
        fib_prob: Dict,
        macro_signal: Dict
    ) -> Dict:
        """
        Combine probabilities for overall assessment
        
        Args:
            price_prob: Price probability from calculate_price_probability
            fib_prob: Fibonacci probability from calculate_fibonacci_probability
            macro_signal: Macro signal from MacroEngine
            
        Returns:
            Combined probability and confidence
        """
        # Extract probabilities
        p_price = price_prob.get('probability', 0) / 100
        p_fib = fib_prob.get('overall_probability', 0) / 100
        
        # Macro weight
        macro_strength = abs(macro_signal.get('strength', 0)) / 3
        macro_strength = min(1, macro_strength)
        
        # Weighted combination
        weights = {
            'price': 0.4,
            'fib': 0.3,
            'macro': 0.3
        }
        
        combined = (
            weights['price'] * p_price +
            weights['fib'] * p_fib +
            weights['macro'] * macro_strength
        )
        
        # Determine action
        if combined > 0.7:
            action = 'BUY'
        elif combined > 0.5:
            action = 'WATCH'
        else:
            action = 'HOLD'
        
        confidence = self._get_confidence_level(combined)
        
        return {
            'combined_probability': round(combined * 100, 1),
            'confidence': confidence,
            'action': action,
            'weighted_components': {
                'price': round(p_price * 100, 1),
                'fib': round(p_fib * 100, 1),
                'macro': round(macro_strength * 100, 1)
            }
        }


# ============================================================
# 🚀 USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    # Test the Probability Engine
    engine = ProbabilityEngine()
    
    # Sample data
    np.random.seed(42)
    prices = 1.32000 + np.cumsum(np.random.randn(100) * 0.001)
    price_series = pd.Series(prices)
    
    # Test calculations
    price_prob = engine.calculate_price_probability(
        current_price=1.32190,
        target_price=1.32490,
        price_data=price_series
    )
    
    print("\n" + "="*60)
    print("📊 PROBABILITY ENGINE TEST")
    print("="*60)
    print(f"  📈 Price Probability: {price_prob['probability']}%")
    print(f"  🎯 Confidence: {price_prob['confidence']}")
    print(f"  📊 Z-Score: {price_prob['z_score']}")
    print("="*60)
