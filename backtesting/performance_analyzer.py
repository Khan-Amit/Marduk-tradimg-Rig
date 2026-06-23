#!/usr/bin/env python3
# ============================================================
# 📊 PERFORMANCE ANALYZER - Strategy Performance Metrics
# ============================================================
#
# Analyzes trading performance and generates detailed metrics
# including win rate, Sharpe ratio, drawdown, and more.
#
# © 2026 Seliim Ahmed. All Rights Reserved.
#
# ============================================================

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
import json
from scipy import stats

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """
    Performance Analyzer
    
    Calculates comprehensive performance metrics:
    - Win rate and profit factor
    - Sharpe and Sortino ratios
    - Maximum drawdown
    - Recovery factor
    - Calmar ratio
    - Monthly/Yearly returns
    """
    
    def __init__(self):
        self.name = "Performance Analyzer"
        self.version = "1.0.0"
        
        # Risk-free rate (annualized)
        self.risk_free_rate = 0.02
        
        logger.info(f"📊 {self.name} v{self.version} initialized")
    
    def analyze_trades(self, trades: List[Dict]) -> Dict:
        """
        Analyze trade list
        
        Args:
            trades: List of trade dictionaries with 'pnl' and 'return'
            
        Returns:
            Comprehensive trade analysis
        """
        if not trades:
            return self._empty_analysis()
        
        # Basic metrics
        total_trades = len(trades)
        wins = [t for t in trades if t.get('pnl', 0) > 0]
        losses = [t for t in trades if t.get('pnl', 0) < 0]
        breakeven = [t for t in trades if t.get('pnl', 0) == 0]
        
        win_rate = (len(wins) / total_trades) * 100 if total_trades > 0 else 0
        
        # Profit metrics
        total_profit = sum(t.get('pnl', 0) for t in wins) if wins else 0
        total_loss = abs(sum(t.get('pnl', 0) for t in losses)) if losses else 0
        net_profit = total_profit - total_loss
        
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        # Average trade
        avg_win = total_profit / len(wins) if wins else 0
        avg_loss = total_loss / len(losses) if losses else 0
        avg_trade = net_profit / total_trades if total_trades > 0 else 0
        
        # Best/worst trade
        best_trade = max((t.get('pnl', 0) for t in trades), default=0)
        worst_trade = min((t.get('pnl', 0) for t in trades), default=0)
        
        # Returns for ratio calculations
        returns = [t.get('return', 0) for t in trades if t.get('return') != 0]
        
        # Sharpe ratio
        sharpe_ratio = self.calculate_sharpe_ratio(returns)
        
        # Sortino ratio
        sortino_ratio = self.calculate_sortino_ratio(returns)
        
        # Calmar ratio
        max_drawdown = self.calculate_max_drawdown_from_trades(trades)
        calmar_ratio = self.calculate_calmar_ratio(returns, max_drawdown)
        
        # Recovery factor
        recovery_factor = self.calculate_recovery_factor(returns)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_trades': total_trades,
            'wins': len(wins),
            'losses': len(losses),
            'breakeven': len(breakeven),
            'win_rate': round(win_rate, 1),
            'total_profit': round(total_profit, 2),
            'total_loss': round(total_loss, 2),
            'net_profit': round(net_profit, 2),
            'profit_factor': round(profit_factor, 2) if profit_factor != float('inf') else 0,
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'avg_trade': round(avg_trade, 2),
            'best_trade': round(best_trade, 2),
            'worst_trade': round(worst_trade, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'sortino_ratio': round(sortino_ratio, 2),
            'calmar_ratio': round(calmar_ratio, 2),
            'recovery_factor': round(recovery_factor, 2),
            'max_drawdown': round(max_drawdown, 2)
        }
    
    def analyze_equity_curve(self, equity_curve: List[float]) -> Dict:
        """
        Analyze equity curve
        
        Args:
            equity_curve: List of equity values
            
        Returns:
            Equity curve analysis
        """
        if not equity_curve or len(equity_curve) < 2:
            return self._empty_equity_analysis()
        
        equity = np.array(equity_curve)
        
        # Returns
        returns = np.diff(equity) / equity[:-1]
        
        # Total return
        total_return = ((equity[-1] - equity[0]) / equity[0]) * 100
        
        # Annualized return
        annualized_return = self.calculate_annualized_return(returns)
        
        # Volatility
        volatility = np.std(returns) * np.sqrt(252) * 100
        
        # Sharpe ratio
        sharpe_ratio = self.calculate_sharpe_ratio(returns.tolist())
        
        # Max drawdown
        running_max = np.maximum.accumulate(equity)
        drawdown = (running_max - equity) / running_max
        max_drawdown = np.max(drawdown) * 100
        
        # Max drawdown duration
        drawdown_start = 0
        drawdown_duration = 0
        max_duration = 0
        in_drawdown = False
        
        for i in range(1, len(drawdown)):
            if drawdown[i] > 0 and not in_drawdown:
                drawdown_start = i
                in_drawdown = True
            elif drawdown[i] == 0 and in_drawdown:
                duration = i - drawdown_start
                max_duration = max(max_duration, duration)
                in_drawdown = False
        
        # Monthly returns
        monthly_returns = self.calculate_monthly_returns(equity_curve)
        
        # Win rate
        winning_months = sum(1 for r in monthly_returns if r > 0)
        monthly_win_rate = (winning_months / len(monthly_returns)) * 100 if monthly_returns else 0
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_return': round(total_return, 2),
            'annualized_return': round(annualized_return, 2),
            'volatility': round(volatility, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'max_drawdown': round(max_drawdown, 2),
            'max_drawdown_duration': max_duration,
            'monthly_win_rate': round(monthly_win_rate, 1),
            'monthly_returns': [round(r, 2) for r in monthly_returns]
        }
    
    def calculate_sharpe_ratio(self, returns: List[float]) -> float:
        """
        Calculate Sharpe ratio
        
        Args:
            returns: List of returns
            
        Returns:
            Sharpe ratio
        """
        if not returns or len(returns) < 2:
            return 0
        
        avg_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0
        
        # Annualized Sharpe (assuming daily returns)
        sharpe = (avg_return - self.risk_free_rate/252) / std_return * np.sqrt(252)
        return sharpe
    
    def calculate_sortino_ratio(self, returns: List[float]) -> float:
        """
        Calculate Sortino ratio (downside risk)
        
        Args:
            returns: List of returns
            
        Returns:
            Sortino ratio
        """
        if not returns or len(returns) < 2:
            return 0
        
        avg_return = np.mean(returns)
        downside_returns = [r for r in returns if r < 0]
        
        if not downside_returns:
            return float('inf')
        
        downside_std = np.std(downside_returns)
        
        if downside_std == 0:
            return 0
        
        # Annualized Sortino (assuming daily returns)
        sortino = (avg_return - self.risk_free_rate/252) / downside_std * np.sqrt(252)
        return sortino
    
    def calculate_calmar_ratio(self, returns: List[float], max_drawdown: float) -> float:
        """
        Calculate Calmar ratio (return / max drawdown)
        
        Args:
            returns: List of returns
            max_drawdown: Maximum drawdown percentage
            
        Returns:
            Calmar ratio
        """
        if max_drawdown == 0:
            return 0
        
        annualized_return = self.calculate_annualized_return(returns)
        calmar = annualized_return / max_drawdown
        return calmar
    
    def calculate_recovery_factor(self, returns: List[float]) -> float:
        """
        Calculate recovery factor (total return / max drawdown)
        
        Args:
            returns: List of returns
            
        Returns:
            Recovery factor
        """
        if not returns:
            return 0
        
        total_return = np.sum(returns) * 100
        max_drawdown = self.calculate_max_drawdown_from_returns(returns)
        
        if max_drawdown == 0:
            return 0
        
        recovery_factor = total_return / max_drawdown
        return recovery_factor
    
    def calculate_max_drawdown_from_trades(self, trades: List[Dict]) -> float:
        """
        Calculate max drawdown from trade list
        
        Args:
            trades: List of trades with 'pnl'
            
        Returns:
            Max drawdown percentage
        """
        if not trades:
            return 0
        
        equity = [0]
        running = 0
        for trade in trades:
            running += trade.get('pnl', 0)
            equity.append(running)
        
        equity = np.array(equity)
        running_max = np.maximum.accumulate(equity)
        drawdown = (running_max - equity) / running_max
        return np.max(drawdown) * 100
    
    def calculate_max_drawdown_from_returns(self, returns: List[float]) -> float:
        """
        Calculate max drawdown from returns
        
        Args:
            returns: List of returns
            
        Returns:
            Max drawdown percentage
        """
        if not returns:
            return 0
        
        equity = [100]
        for r in returns:
            equity.append(equity[-1] * (1 + r))
        
        equity = np.array(equity)
        running_max = np.maximum.accumulate(equity)
        drawdown = (running_max - equity) / running_max
        return np.max(drawdown) * 100
    
    def calculate_annualized_return(self, returns: List[float]) -> float:
        """
        Calculate annualized return
        
        Args:
            returns: List of returns
            
        Returns:
            Annualized return percentage
        """
        if not returns:
            return 0
        
        total_return = np.sum(returns)
        n = len(returns)
        
        # Annualize (252 trading days)
        annualized = (1 + total_return) ** (252 / n) - 1
        return annualized * 100
    
    def calculate_monthly_returns(self, equity_curve: List[float]) -> List[float]:
        """
        Calculate monthly returns
        
        Args:
            equity_curve: List of equity values
            
        Returns:
            List of monthly returns
        """
        if not equity_curve or len(equity_curve) < 2:
            return []
        
        # Simple monthly returns (assuming 252 trading days/year)
        monthly_returns = []
        
        for i in range(0, len(equity_curve), 21):  # ~21 trading days per month
            if i + 21 < len(equity_curve):
                month_return = (equity_curve[i+21] - equity_curve[i]) / equity_curve[i]
                monthly_returns.append(month_return * 100)
        
        return monthly_returns
    
    def _empty_analysis(self) -> Dict:
        """Return empty analysis"""
        return {
            'timestamp': datetime.now().isoformat(),
            'total_trades': 0,
            'wins': 0,
            'losses': 0,
            'breakeven': 0,
            'win_rate': 0,
            'total_profit': 0,
            'total_loss': 0,
            'net_profit': 0,
            'profit_factor': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'avg_trade': 0,
            'best_trade': 0,
            'worst_trade': 0,
            'sharpe_ratio': 0,
            'sortino_ratio': 0,
            'calmar_ratio': 0,
            'recovery_factor': 0,
            'max_drawdown': 0
        }
    
    def _empty_equity_analysis(self) -> Dict:
        """Return empty equity analysis"""
        return {
            'timestamp': datetime.now().isoformat(),
            'total_return': 0,
            'annualized_return': 0,
            'volatility': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'max_drawdown_duration': 0,
            'monthly_win_rate': 0,
            'monthly_returns': []
        }


# ============================================================
# 🚀 USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    # Test the Performance Analyzer
    analyzer = PerformanceAnalyzer()
    
    # Sample trades
    sample_trades = []
    np.random.seed(42)
    
    for i in range(50):
        pnl = np.random.normal(50, 100)
        trade = {
            'pnl': pnl,
            'return': pnl / 10000
        }
        sample_trades.append(trade)
    
    # Analyze
    result = analyzer.analyze_trades(sample_trades)
    
    print("\n" + "="*60)
    print("📊 PERFORMANCE ANALYSIS")
    print("="*60)
    print(f"  📈 Total Trades: {result['total_trades']}")
    print(f"  🎯 Win Rate: {result['win_rate']}%")
    print(f"  💰 Net Profit: ${result['net_profit']:,.2f}")
    print(f"  📊 Profit Factor: {result['profit_factor']}")
    print(f"  📈 Sharpe Ratio: {result['sharpe_ratio']}")
    print(f"  📉 Max Drawdown: {result['max_drawdown']}%")
    print("="*60)
