#!/usr/bin/env python3
# ============================================================
# 🛡️ RISK MANAGER - Risk Assessment & Position Sizing
# ============================================================
#
# Manages trading risk including position sizing,
# stop loss placement, risk-reward ratios, and
# portfolio-level risk controls.
#
# © 2026 Seliim Ahmed. All Rights Reserved.
#
# ============================================================

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import threading
import time

logger = logging.getLogger(__name__)


class RiskManager:
    """
    Risk Manager
    
    Handles:
    - Position sizing based on risk
    - Stop loss calculations
    - Risk-reward optimization
    - Portfolio risk limits
    - Real-time risk monitoring
    """
    
    def __init__(self, initial_equity: float = 0.0):
        self.name = "Risk Manager"
        self.version = "1.0.0"
        
        # Account parameters
        self.initial_equity = initial_equity
        self.equity = initial_equity
        self.risk_per_trade = 0.02  # 2% risk per trade
        self.max_drawdown = 0.20     # 20% max drawdown
        self.max_positions = 5       # Max concurrent positions
        self.max_risk_per_day = 0.05 # 5% max risk per day
        self.daily_loss_limit = 0.10 # 10% daily loss limit
        
        # Risk tracking
        self.daily_pnl = 0.0
        self.daily_risk_used = 0.0
        self.drawdown = 0.0
        self.current_risk = 0.0
        self.risk_usage = {}
        
        # Protection flags
        self.lockdown = False
        self.lockdown_reason = None
        
        # Stop loss parameters
        self.min_stop_pips = 20
        self.max_stop_pips = 200
        self.min_risk_reward = 1.5
        self.target_risk_reward = 2.0
        
        logger.info(f"🛡️ {self.name} v{self.version} initialized")
        logger.info(f"   Initial Equity: ${self.initial_equity:,.2f}")
        logger.info(f"   Risk Per Trade: {self.risk_per_trade*100:.1f}%")
        logger.info(f"   Max Drawdown: {self.max_drawdown*100:.1f}%")
    
    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss: float,
        risk_percent: Optional[float] = None
    ) -> float:
        """
        Calculate optimal position size
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            risk_percent: Risk percentage (default: self.risk_per_trade)
            
        Returns:
            Position size in lots
        """
        if self.lockdown:
            logger.warning("⚠️ Risk manager in lockdown mode")
            return 0.0
        
        if risk_percent is None:
            risk_percent = self.risk_per_trade
        
        # Check daily risk limit
        if self.daily_risk_used + (risk_percent * self.equity) > self.daily_loss_limit * self.equity:
            logger.warning("⚠️ Daily risk limit reached")
            return 0.0
        
        # Calculate risk amount
        risk_amount = self.equity * risk_percent
        
        # Calculate stop loss in pips
        stop_pips = abs(entry_price - stop_loss) * 10000
        
        if stop_pips < self.min_stop_pips:
            logger.warning(f"⚠️ Stop loss too tight: {stop_pips} pips")
            return 0.0
        
        if stop_pips > self.max_stop_pips:
            logger.warning(f"⚠️ Stop loss too wide: {stop_pips} pips")
            return 0.0
        
        # Calculate position size
        pip_value = 10.0  # $10 per pip for standard lot
        volume = risk_amount / (stop_pips * pip_value)
        
        # Round to 2 decimal places
        volume = round(volume, 2)
        
        # Ensure minimum and maximum
        volume = max(0.01, min(volume, 10.0))
        
        return volume
    
    def calculate_stop_loss(
        self,
        entry_price: float,
        action: str,
        risk_percent: Optional[float] = None,
        atr_value: Optional[float] = None
    ) -> float:
        """
        Calculate optimal stop loss
        
        Args:
            entry_price: Entry price
            action: BUY or SELL
            risk_percent: Risk percentage (default: self.risk_per_trade)
            atr_value: Average True Range value
            
        Returns:
            Stop loss price
        """
        if risk_percent is None:
            risk_percent = self.risk_per_trade
        
        # Base stop distance (in pips)
        if atr_value:
            # Use ATR for dynamic stop
            stop_pips = atr_value * 2.0 * 10000
        else:
            # Use fixed percentage
            stop_pips = 20  # 20 pips minimum
        
        # Apply risk percentage
        max_risk_pips = (risk_percent * self.equity) / (0.1 * 100000)
        stop_pips = min(stop_pips, max_risk_pips)
        
        # Ensure minimum and maximum
        stop_pips = max(self.min_stop_pips, min(stop_pips, self.max_stop_pips))
        
        if action.upper() == 'BUY':
            stop_loss = entry_price - (stop_pips / 10000)
        else:  # SELL
            stop_loss = entry_price + (stop_pips / 10000)
        
        return round(stop_loss, 5)
    
    def calculate_take_profit(
        self,
        entry_price: float,
        stop_loss: float,
        action: str,
        risk_reward_ratio: Optional[float] = None
    ) -> float:
        """
        Calculate take profit based on risk-reward ratio
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            action: BUY or SELL
            risk_reward_ratio: Risk-reward ratio (default: self.target_risk_reward)
            
        Returns:
            Take profit price
        """
        if risk_reward_ratio is None:
            risk_reward_ratio = self.target_risk_reward
        
        risk = abs(entry_price - stop_loss)
        reward = risk * risk_reward_ratio
        
        if action.upper() == 'BUY':
            take_profit = entry_price + reward
        else:  # SELL
            take_profit = entry_price - reward
        
        return round(take_profit, 5)
    
    def calculate_risk_reward_ratio(
        self,
        entry_price: float,
        stop_loss: float,
        take_profit: float
    ) -> float:
        """
        Calculate risk-reward ratio
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            
        Returns:
            Risk-reward ratio
        """
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        
        if risk == 0:
            return 0
        
        return reward / risk
    
    def validate_trade(
        self,
        symbol: str,
        action: str,
        volume: float,
        entry_price: float,
        stop_loss: float,
        take_profit: float
    ) -> Dict:
        """
        Validate trade before execution
        
        Args:
            symbol: Trading symbol
            action: BUY or SELL
            volume: Position volume
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            
        Returns:
            Validation result with status
        """
        if self.lockdown:
            return {
                'valid': False,
                'reason': f'Lockdown mode: {self.lockdown_reason}'
            }
        
        # Check equity
        if self.equity <= 0:
            return {
                'valid': False,
                'reason': 'Insufficient equity'
            }
        
        # Check drawdown
        if self.drawdown >= self.max_drawdown:
            return {
                'valid': False,
                'reason': f'Max drawdown reached: {self.drawdown*100:.1f}%'
            }
        
        # Check position count
        if len(self.risk_usage) >= self.max_positions:
            return {
                'valid': False,
                'reason': f'Max positions reached: {self.max_positions}'
            }
        
        # Check daily loss limit
        if self.daily_pnl <= -self.daily_loss_limit * self.initial_equity:
            return {
                'valid': False,
                'reason': 'Daily loss limit reached'
            }
        
        # Check minimum risk-reward
        rr_ratio = self.calculate_risk_reward_ratio(
            entry_price, stop_loss, take_profit
        )
        
        if rr_ratio < self.min_risk_reward:
            return {
                'valid': False,
                'reason': f'Risk-reward ratio too low: {rr_ratio:.2f}'
            }
        
        # Check stop loss width
        stop_pips = abs(entry_price - stop_loss) * 10000
        if stop_pips < self.min_stop_pips:
            return {
                'valid': False,
                'reason': f'Stop loss too tight: {stop_pips} pips'
            }
        
        if stop_pips > self.max_stop_pips:
            return {
                'valid': False,
                'reason': f'Stop loss too wide: {stop_pips} pips'
            }
        
        # Check volume
        if volume < 0.01 or volume > 10.0:
            return {
                'valid': False,
                'reason': f'Invalid volume: {volume}'
            }
        
        return {
            'valid': True,
            'reason': 'Trade validation passed'
        }
    
    def update_risk_metrics(
        self,
        equity: float,
        positions: List[Dict],
        trades: List[Dict]
    ):
        """
        Update risk metrics
        
        Args:
            equity: Current equity
            positions: List of open positions
            trades: List of closed trades
        """
        self.equity = equity
        
        # Calculate drawdown
        if equity < self.initial_equity:
            self.drawdown = (self.initial_equity - equity) / self.initial_equity
        else:
            self.drawdown = 0
        
        # Update risk usage
        self.risk_usage = {}
        for pos in positions:
            risk = abs(pos['entry_price'] - pos['stop_loss']) * pos['volume'] * 100000
            self.risk_usage[pos['symbol']] = risk / self.equity
        
        self.current_risk = sum(self.risk_usage.values())
        
        # Update daily P&L
        if trades:
            today = datetime.now().date()
            daily_pnl = 0
            for trade in trades:
                if trade.get('close_time'):
                    trade_date = datetime.fromisoformat(trade['close_time']).date()
                    if trade_date == today:
                        daily_pnl += trade.get('profit', 0)
            self.daily_pnl = daily_pnl
    
    def get_risk_report(self) -> Dict:
        """
        Generate risk report
        
        Returns:
            Risk report dict
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'equity': round(self.equity, 2),
            'drawdown': round(self.drawdown * 100, 2),
            'current_risk': round(self.current_risk * 100, 2),
            'daily_pnl': round(self.daily_pnl, 2),
            'daily_risk_used': round(self.daily_risk_used * 100, 2),
            'positions': len(self.risk_usage),
            'max_positions': self.max_positions,
            'lockdown': self.lockdown,
            'risk_usage': {
                symbol: round(risk * 100, 2)
                for symbol, risk in self.risk_usage.items()
            }
        }
    
    def activate_lockdown(self, reason: str = "Manual lockdown"):
        """
        Activate lockdown mode
        
        Args:
            reason: Reason for lockdown
        """
        self.lockdown = True
        self.lockdown_reason = reason
        logger.warning(f"🛑 LOCKDOWN ACTIVATED: {reason}")
    
    def deactivate_lockdown(self):
        """Deactivate lockdown mode"""
        self.lockdown = False
        self.lockdown_reason = None
        logger.info("✅ Lockdown deactivated")
    
    def reset_daily_metrics(self):
        """Reset daily metrics"""
        self.daily_pnl = 0.0
        self.daily_risk_used = 0.0
        logger.info("🔄 Daily metrics reset")


# ============================================================
# 🚀 USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    # Test the Risk Manager
    risk_manager = RiskManager(initial_equity=100000)
    
    # Test position sizing
    entry_price = 1.32190
    stop_loss = 1.31990
    
    size = risk_manager.calculate_position_size(
        entry_price=entry_price,
        stop_loss=stop_loss,
        risk_percent=0.02
    )
    
    print(f"Position Size: {size} lots")
    
    # Test stop loss
    sl = risk_manager.calculate_stop_loss(
        entry_price=entry_price,
        action='BUY',
        risk_percent=0.02
    )
    print(f"Stop Loss: {sl:.5f}")
    
    # Test take profit
    tp = risk_manager.calculate_take_profit(
        entry_price=entry_price,
        stop_loss=sl,
        action='BUY',
        risk_reward_ratio=2.0
    )
    print(f"Take Profit: {tp:.5f}")
    
    # Test validation
    result = risk_manager.validate_trade(
        symbol='GBPUSD',
        action='BUY',
        volume=size,
        entry_price=entry_price,
        stop_loss=sl,
        take_profit=tp
    )
    print(f"Validation: {result}")
