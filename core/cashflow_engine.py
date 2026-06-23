#!/usr/bin/env python3
# ============================================================
# 💰 CASHFLOW ENGINE - P&L, Risk & Portfolio Management
# ============================================================
#
# Manages trading P&L, risk metrics, position sizing,
# and portfolio performance tracking.
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

logger = logging.getLogger(__name__)


class CashFlowEngine:
    """
    Cashflow Engine
    
    Manages:
    - Balance and equity tracking
    - P&L calculation
    - Position sizing
    - Risk management
    - Performance metrics
    - Portfolio allocation
    """
    
    def __init__(self, initial_balance: float = 0.0):
        self.name = "Cashflow Engine"
        self.version = "1.0.0"
        
        # Account state
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.equity = initial_balance
        self.margin = 0.0
        self.free_margin = initial_balance
        
        # Trading history
        self.trades = []
        self.positions = []
        self.equity_curve = [initial_balance]
        self.equity_timestamps = [datetime.now()]
        
        # Risk parameters
        self.risk_per_trade = 0.02  # 2% risk per trade
        self.max_drawdown = 0.20    # 20% max drawdown
        self.max_positions = 5      # Maximum concurrent positions
        
        # Performance metrics
        self.metrics = {}
        
        logger.info(f"💰 {self.name} v{self.version} initialized")
        logger.info(f"   Initial Balance: ${initial_balance:,.2f}")
        logger.info(f"   Risk Per Trade: {self.risk_per_trade*100:.1f}%")
        logger.info(f"   Max Drawdown: {self.max_drawdown*100:.1f}%")
    
    def open_position(
        self,
        symbol: str,
        action: str,
        volume: float,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        timestamp: Optional[datetime] = None
    ) -> Dict:
        """
        Open a new position
        
        Args:
            symbol: Trading symbol (e.g., GBPUSD)
            action: BUY or SELL
            volume: Position volume in lots
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            timestamp: Position open time
            
        Returns:
            Position dict
        """
        if len(self.positions) >= self.max_positions:
            logger.warning("⚠️ Max positions reached")
            return {'status': 'REJECTED', 'reason': 'Max positions reached'}
        
        # Validate risk
        risk_amount = abs(entry_price - stop_loss) * volume * 100000
        
        # Check if risk exceeds limit
        position_risk = risk_amount / self.equity
        if position_risk > self.risk_per_trade * 2:  # Allow up to 2x risk per trade
            logger.warning(f"⚠️ Position risk {position_risk*100:.1f}% exceeds limit")
            # Reduce volume to fit risk
            max_volume = (self.equity * self.risk_per_trade) / (abs(entry_price - stop_loss) * 100000)
            volume = min(volume, max_volume)
        
        position = {
            'position_id': f"POS_{int(datetime.now().timestamp())}",
            'symbol': symbol,
            'action': action,
            'volume': volume,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'open_time': timestamp or datetime.now(),
            'close_time': None,
            'status': 'OPEN',
            'pnl': 0.0,
            'return': 0.0
        }
        
        self.positions.append(position)
        
        # Update margin
        self.margin += volume * 100000 * 0.02  # 2% margin
        self.free_margin = self.equity - self.margin
        
        logger.info(f"🔓 Position opened: {action} {volume} {symbol} @ {entry_price:.5f}")
        logger.info(f"   SL: {stop_loss:.5f} | TP: {take_profit:.5f}")
        logger.info(f"   Margin: ${self.margin:,.2f} | Free: ${self.free_margin:,.2f}")
        
        return {'status': 'OPENED', 'position': position}
    
    def close_position(
        self,
        position_id: str,
        exit_price: float,
        timestamp: Optional[datetime] = None
    ) -> Dict:
        """
        Close an existing position
        
        Args:
            position_id: Position ID from open_position
            exit_price: Exit price
            timestamp: Position close time
            
        Returns:
            Closed position with P&L
        """
        # Find position
        position = None
        pos_idx = None
        
        for idx, pos in enumerate(self.positions):
            if pos['position_id'] == position_id and pos['status'] == 'OPEN':
                position = pos
                pos_idx = idx
                break
        
        if position is None:
            logger.error(f"❌ Position {position_id} not found or already closed")
            return {'status': 'ERROR', 'reason': 'Position not found'}
        
        # Calculate P&L
        if position['action'] == 'BUY':
            pnl = (exit_price - position['entry_price']) * position['volume'] * 100000
        else:  # SELL
            pnl = (position['entry_price'] - exit_price) * position['volume'] * 100000
        
        # Update position
        position['status'] = 'CLOSED'
        position['close_time'] = timestamp or datetime.now()
        position['exit_price'] = exit_price
        position['pnl'] = pnl
        position['return'] = pnl / (position['volume'] * 100000 * position['entry_price'])
        
        # Move to trades
        self.trades.append(position.copy())
        
        # Remove from positions
        self.positions.pop(pos_idx)
        
        # Update equity
        self.equity += pnl
        self.balance = self.equity - self.margin
        
        # Update equity curve
        self.equity_curve.append(self.equity)
        self.equity_timestamps.append(datetime.now())
        
        # Update margin
        self.margin -= position['volume'] * 100000 * 0.02
        self.free_margin = self.equity - self.margin
        
        # Log
        logger.info(f"🔒 Position closed: {position['action']} {position['volume']} {position['symbol']}")
        logger.info(f"   Entry: {position['entry_price']:.5f} → Exit: {exit_price:.5f}")
        logger.info(f"   P&L: ${pnl:+,.2f} | Return: {position['return']*100:+.2f}%")
        logger.info(f"   Equity: ${self.equity:,.2f}")
        
        return {'status': 'CLOSED', 'position': position}
    
    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss: float,
        risk_percent: Optional[float] = None
    ) -> float:
        """
        Calculate optimal position size based on risk
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            risk_percent: Risk percentage (default: self.risk_per_trade)
            
        Returns:
            Position size in lots
        """
        if risk_percent is None:
            risk_percent = self.risk_per_trade
        
        risk_amount = self.equity * risk_percent
        stop_loss_pips = abs(entry_price - stop_loss) * 10000
        
        if stop_loss_pips == 0:
            return 0.01  # Minimum lot size
        
        # Pip value for 1 standard lot
        pip_value = 10.0  # $10 per pip for standard lot
        
        volume = risk_amount / (stop_loss_pips * pip_value)
        
        # Round to 2 decimal places
        volume = round(volume, 2)
        
        # Ensure minimum and maximum
        volume = max(0.01, min(volume, 10.0))  # 0.01 min, 10.0 max
        
        return volume
    
    def calculate_risk_metrics(self) -> Dict:
        """
        Calculate current risk metrics
        
        Returns:
            Risk metrics dict
        """
        # Current drawdown
        if len(self.equity_curve) > 1:
            peak = max(self.equity_curve)
            current_drawdown = (peak - self.equity) / peak if peak > 0 else 0
        else:
            current_drawdown = 0
        
        # Max drawdown
        if len(self.equity_curve) > 1:
            running_max = np.maximum.accumulate(self.equity_curve)
            drawdowns = (running_max - self.equity_curve) / running_max
            max_drawdown = np.max(drawdowns) if len(drawdowns) > 0 else 0
        else:
            max_drawdown = 0
        
        # Current risk exposure
        total_risk = 0
        for pos in self.positions:
            if pos['status'] == 'OPEN':
                risk = abs(pos['entry_price'] - pos['stop_loss']) * pos['volume'] * 100000
                total_risk += risk
        
        risk_percent = (total_risk / self.equity) * 100 if self.equity > 0 else 0
        
        # Margin level
        margin_level = (self.equity / self.margin) * 100 if self.margin > 0 else float('inf')
        
        return {
            'current_drawdown': round(current_drawdown * 100, 2),
            'max_drawdown': round(max_drawdown * 100, 2),
            'risk_exposure': round(total_risk, 2),
            'risk_percent': round(risk_percent, 2),
            'margin_level': round(margin_level, 2) if margin_level != float('inf') else float('inf'),
            'margin_used': round(self.margin, 2),
            'free_margin': round(self.free_margin, 2),
            'open_positions': len([p for p in self.positions if p['status'] == 'OPEN'])
        }
    
    def calculate_performance_metrics(self) -> Dict:
        """
        Calculate comprehensive performance metrics
        
        Returns:
            Performance metrics dict
        """
        if not self.trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'sharpe_ratio': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'largest_win': 0,
                'largest_loss': 0
            }
        
        # Basic metrics
        total_trades = len(self.trades)
        wins = [t for t in self.trades if t['pnl'] > 0]
        losses = [t for t in self.trades if t['pnl'] < 0]
        breakeven = [t for t in self.trades if t['pnl'] == 0]
        
        win_rate = (len(wins) / total_trades) * 100 if total_trades > 0 else 0
        
        total_profit = sum(t['pnl'] for t in wins) if wins else 0
        total_loss = abs(sum(t['pnl'] for t in losses)) if losses else 0
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        avg_win = total_profit / len(wins) if wins else 0
        avg_loss = total_loss / len(losses) if losses else 0
        
        largest_win = max((t['pnl'] for t in wins), default=0)
        largest_loss = min((t['pnl'] for t in losses), default=0)
        
        # Returns for Sharpe ratio
        returns = [t['return'] for t in self.trades if t['return'] != 0]
        
        if returns:
            avg_return = np.mean(returns)
            std_return = np.std(returns)
            sharpe_ratio = (avg_return / std_return) if std_return > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Equity curve metrics
        if len(self.equity_curve) > 1:
            final_equity = self.equity_curve[-1]
            initial_equity = self.equity_curve[0]
            total_return = ((final_equity - initial_equity) / initial_equity) * 100 if initial_equity > 0 else 0
        else:
            total_return = 0
        
        return {
            'total_trades': total_trades,
            'win_rate': round(win_rate, 1),
            'profit_factor': round(profit_factor, 2) if profit_factor != float('inf') else 0,
            'total_profit': round(total_profit, 2),
            'total_loss': round(total_loss, 2),
            'net_profit': round(total_profit - total_loss, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'largest_win': round(largest_win, 2),
            'largest_loss': round(largest_loss, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'total_return': round(total_return, 2),
            'final_equity': round(self.equity, 2)
        }
    
    def get_account_summary(self) -> Dict:
        """
        Get complete account summary
        
        Returns:
            Account summary dict
        """
        risk_metrics = self.calculate_risk_metrics()
        performance = self.calculate_performance_metrics()
        
        return {
            'account': {
                'balance': round(self.balance, 2),
                'equity': round(self.equity, 2),
                'margin': round(self.margin, 2),
                'free_margin': round(self.free_margin, 2),
                'initial_balance': round(self.initial_balance, 2)
            },
            'risk': risk_metrics,
            'performance': performance,
            'positions': [p for p in self.positions if p['status'] == 'OPEN'],
            'recent_trades': self.trades[-10:] if self.trades else []
        }
    
    def export_data(self, filepath: str) -> bool:
        """
        Export trading data to JSON
        
        Args:
            filepath: Path to save JSON
            
        Returns:
            True if successful
        """
        data = {
            'balance': self.balance,
            'equity': self.equity,
            'trades': self.trades,
            'positions': self.positions,
            'equity_curve': self.equity_curve,
            'metrics': self.calculate_performance_metrics(),
            'export_time': datetime.now().isoformat()
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, default=str, indent=2)
            logger.info(f"💾 Data exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to export data: {e}")
            return False


# ============================================================
# 🚀 USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    # Test the Cashflow Engine
    engine = CashFlowEngine(initial_balance=169506.53)
    
    # Open a position
    pos = engine.open_position(
        symbol='GBPUSD',
        action='BUY',
        volume=0.5,
        entry_price=1.32190,
        stop_loss=1.31990,
        take_profit=1.32490
    )
    
    if pos['status'] == 'OPENED':
        # Close position
        engine.close_position(
            position_id=pos['position']['position_id'],
            exit_price=1.32490
        )
    
    # Get summary
    summary = engine.get_account_summary()
    
    print("\n" + "="*60)
    print("💰 CAShFLOW ENGINE SUMMARY")
    print("="*60)
    print(f"  Balance: ${summary['account']['balance']:,.2f}")
    print(f"  Equity: ${summary['account']['equity']:,.2f}")
    print(f"  Total Trades: {summary['performance']['total_trades']}")
    print(f"  Win Rate: {summary['performance']['win_rate']}%")
    print(f"  Sharpe Ratio: {summary['performance']['sharpe_ratio']}")
    print("="*60)
