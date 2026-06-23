#!/usr/bin/env python3
# ============================================================
# 📊 HISTORICAL RUNNER - Backtesting Engine
# ============================================================
#
# Runs trading strategies on historical data
# to evaluate performance and validate algorithms.
#
# © 2026 Seliim Ahmed. All Rights Reserved.
#
# ============================================================

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
import json
from pathlib import Path

# Import core modules
import sys
sys.path.append('..')
from core.quantum_engine import QuantumEngine
from core.macro_engine import MacroEngine
from core.probability_engine import ProbabilityEngine
from core.cashflow_engine import CashFlowEngine

logger = logging.getLogger(__name__)


class HistoricalRunner:
    """
    Historical Runner
    
    Runs backtests on historical data:
    - Walk-forward analysis
    - Performance metrics
    - Equity curve generation
    - Trade logging
    """
    
    def __init__(self):
        self.name = "Historical Runner"
        self.version = "1.0.0"
        
        # Initialize engines
        self.quantum = QuantumEngine()
        self.macro = MacroEngine()
        self.probability = ProbabilityEngine()
        self.cashflow = CashFlowEngine()
        
        # Backtest settings
        self.initial_balance = 10000.0
        self.risk_per_trade = 0.02
        self.max_positions = 5
        self.commission = 0.0001  # 0.01% commission
        
        # Results storage
        self.trades = []
        self.equity_curve = []
        self.returns = []
        self.drawdowns = []
        
        logger.info(f"📊 {self.name} v{self.version} initialized")
        logger.info(f"   Initial Balance: ${self.initial_balance:,.2f}")
        logger.info(f"   Risk Per Trade: {self.risk_per_trade*100:.1f}%")
    
    def load_data(
        self,
        symbol: str,
        timeframe: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Load historical data
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe (M1, M5, H1, D1)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            DataFrame with OHLC data
        """
        logger.info(f"📥 Loading {symbol} data from {start_date} to {end_date}")
        
        # In production, load from database or CSV
        # For now, generate synthetic data
        dates = pd.date_range(start=start_date, end=end_date, freq='1H')
        np.random.seed(42)
        
        # Random walk with drift
        n = len(dates)
        drift = 0.0001
        volatility = 0.001
        returns = np.random.normal(drift, volatility, n)
        prices = 1.32000 * np.exp(np.cumsum(returns))
        
        df = pd.DataFrame({
            'open': prices * (1 + np.random.normal(0, 0.0001, n)),
            'high': prices * (1 + np.abs(np.random.normal(0, 0.0005, n))),
            'low': prices * (1 - np.abs(np.random.normal(0, 0.0005, n))),
            'close': prices,
            'volume': np.random.randint(100, 1000, n)
        }, index=dates)
        
        logger.info(f"✅ Loaded {len(df)} bars")
        return df
    
    def run_backtest(
        self,
        data: pd.DataFrame,
        strategy_params: Optional[Dict] = None
    ) -> Dict:
        """
        Run full backtest
        
        Args:
            data: OHLC data from load_data
            strategy_params: Optional strategy parameters
            
        Returns:
            Backtest results
        """
        logger.info("🚀 Starting backtest...")
        
        # Initialize results
        self.trades = []
        self.equity_curve = [self.initial_balance]
        self.returns = []
        self.drawdowns = []
        
        # Reset cashflow engine
        self.cashflow = CashFlowEngine(initial_balance=self.initial_balance)
        
        # Track position
        current_position = None
        entry_price = 0
        entry_time = None
        stop_loss = 0
        take_profit = 0
        
        # Walk forward through data
        for i in range(100, len(data)):
            current_data = data.iloc[:i+1]
            current_price = current_data['close'].iloc[-1]
            
            # 1. Analyze market
            quantum_result = self.quantum.analyze_market(current_data)
            
            # 2. Get macro context
            macro_result = self.macro.analyze_market_context()
            
            # 3. Check for position exit
            if current_position is not None:
                # Check stop loss / take profit
                if current_price <= stop_loss or current_price >= take_profit:
                    # Exit position
                    pnl = self._calculate_pnl(
                        current_position,
                        entry_price,
                        current_price,
                        'MARKET'
                    )
                    
                    self.trades.append({
                        'entry_time': entry_time,
                        'exit_time': current_data.index[-1],
                        'entry_price': entry_price,
                        'exit_price': current_price,
                        'position': current_position,
                        'pnl': pnl,
                        'return': pnl / (entry_price * self._get_position_size()),
                        'exit_reason': 'SL/TP'
                    })
                    
                    current_position = None
                    entry_price = 0
                    stop_loss = 0
                    take_profit = 0
                    
                    # Update equity
                    self.cashflow.equity += pnl
                    self.equity_curve.append(self.cashflow.equity)
                    
                    continue
            
            # 4. Generate signal
            signal = self._generate_signal(
                quantum_result,
                macro_result,
                current_price
            )
            
            # 5. Enter position if signal is strong
            if current_position is None and signal['action'] != 'HOLD':
                if signal['confidence'] > 60:
                    # Calculate position size
                    position_size = self._calculate_position_size(
                        current_price,
                        signal['stop_loss'],
                        self.risk_per_trade
                    )
                    
                    if position_size > 0:
                        current_position = signal['action']
                        entry_price = current_price
                        entry_time = current_data.index[-1]
                        stop_loss = signal['stop_loss']
                        take_profit = signal['take_profit']
                        
                        logger.info(
                            f"📈 {signal['action']} @ {entry_price:.5f} "
                            f"SL: {stop_loss:.5f} TP: {take_profit:.5f}"
                        )
        
        # Calculate final performance
        performance = self._calculate_performance()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'trades': self.trades,
            'equity_curve': self.equity_curve,
            'performance': performance,
            'summary': {
                'total_trades': len(self.trades),
                'final_equity': self.cashflow.equity,
                'total_return': (self.cashflow.equity - self.initial_balance) / self.initial_balance * 100
            }
        }
    
    def _generate_signal(
        self,
        quantum_result: Dict,
        macro_result: Dict,
        current_price: float
    ) -> Dict:
        """
        Generate trading signal
        
        Args:
            quantum_result: Quantum Engine analysis
            macro_result: Macro Engine analysis
            current_price: Current market price
            
        Returns:
            Signal dict
        """
        signal = {
            'action': 'HOLD',
            'confidence': 0,
            'stop_loss': 0,
            'take_profit': 0
        }
        
        # Get confluence score
        confluence = quantum_result.get('confluence', 0)
        signal_score = quantum_result.get('signal', {}).get('confidence', 0)
        
        # Macro adjustment
        macro_signal = macro_result.get('signal', {})
        macro_direction = macro_signal.get('direction', 'NEUTRAL')
        
        # Combine signals
        if confluence >= 9 and signal_score > 50:
            if macro_direction == 'BULLISH':
                signal['action'] = 'BUY'
                signal['confidence'] = min(signal_score + 20, 100)
            elif macro_direction == 'BEARISH':
                signal['action'] = 'SELL'
                signal['confidence'] = min(signal_score + 20, 100)
            else:
                signal['action'] = 'BUY' if confluence > 12 else 'HOLD'
                signal['confidence'] = signal_score
        
        # Set SL and TP
        if signal['action'] != 'HOLD':
            if signal['action'] == 'BUY':
                signal['stop_loss'] = current_price * 0.995
                signal['take_profit'] = current_price * 1.01
            else:
                signal['stop_loss'] = current_price * 1.005
                signal['take_profit'] = current_price * 0.99
        
        return signal
    
    def _calculate_position_size(
        self,
        entry_price: float,
        stop_loss: float,
        risk_percent: float
    ) -> float:
        """
        Calculate position size
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            risk_percent: Risk percentage
            
        Returns:
            Position size in lots
        """
        risk_amount = self.cashflow.equity * risk_percent
        stop_loss_pips = abs(entry_price - stop_loss) * 10000
        
        if stop_loss_pips == 0:
            return 0
        
        pip_value = 10.0  # $10 per pip for standard lot
        volume = risk_amount / (stop_loss_pips * pip_value)
        
        return round(max(0.01, min(volume, 10.0)), 2)
    
    def _calculate_pnl(
        self,
        position: str,
        entry_price: float,
        exit_price: float,
        exit_type: str
    ) -> float:
        """
        Calculate P&L for a trade
        
        Args:
            position: BUY or SELL
            entry_price: Entry price
            exit_price: Exit price
            exit_type: MARKET, SL, or TP
            
        Returns:
            P&L in USD
        """
        size = self._get_position_size()
        
        if position == 'BUY':
            pnl = (exit_price - entry_price) * size * 100000
        else:
            pnl = (entry_price - exit_price) * size * 100000
        
        # Subtract commission
        pnl -= (entry_price * size * 100000 * self.commission)
        pnl -= (exit_price * size * 100000 * self.commission)
        
        return pnl
    
    def _get_position_size(self) -> float:
        """Get current position size (simplified)"""
        return 0.1  # 0.1 lots
    
    def _calculate_performance(self) -> Dict:
        """
        Calculate performance metrics
        
        Returns:
            Performance metrics dict
        """
        returns = []
        for i in range(1, len(self.equity_curve)):
            ret = (self.equity_curve[i] - self.equity_curve[i-1]) / self.equity_curve[i-1]
            returns.append(ret)
        
        if not returns:
            return {
                'total_return': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'win_rate': 0
            }
        
        # Total return
        total_return = (self.equity_curve[-1] - self.equity_curve[0]) / self.equity_curve[0]
        
        # Sharpe ratio
        avg_return = np.mean(returns)
        std_return = np.std(returns)
        sharpe = (avg_return / std_return) * np.sqrt(252) if std_return > 0 else 0
        
        # Max drawdown
        peak = np.maximum.accumulate(self.equity_curve)
        drawdown = (peak - self.equity_curve) / peak
        max_drawdown = np.max(drawdown) if len(drawdown) > 0 else 0
        
        # Win rate
        if self.trades:
            wins = sum(1 for t in self.trades if t['pnl'] > 0)
            win_rate = wins / len(self.trades)
        else:
            win_rate = 0
        
        return {
            'total_return': round(total_return * 100, 2),
            'sharpe_ratio': round(sharpe, 2),
            'max_drawdown': round(max_drawdown * 100, 2),
            'win_rate': round(win_rate * 100, 1),
            'total_trades': len(self.trades)
        }


# ============================================================
# 🚀 USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    # Test the Historical Runner
    runner = HistoricalRunner()
    
    # Load data
    data = runner.load_data(
        symbol='GBPUSD',
        timeframe='H1',
        start_date='2026-01-01',
        end_date='2026-06-23'
    )
    
    # Run backtest
    result = runner.run_backtest(data)
    
    print("\n" + "="*60)
    print("📊 BACKTEST RESULTS")
    print("="*60)
    print(f"  📈 Total Trades: {result['summary']['total_trades']}")
    print(f"  💰 Final Equity: ${result['summary']['final_equity']:,.2f}")
    print(f"  📊 Total Return: {result['summary']['total_return']:.2f}%")
    print(f"  🎯 Win Rate: {result['performance']['win_rate']}%")
    print(f"  📈 Sharpe Ratio: {result['performance']['sharpe_ratio']}")
    print(f"  📉 Max Drawdown: {result['performance']['max_drawdown']}%")
    print("="*60)
