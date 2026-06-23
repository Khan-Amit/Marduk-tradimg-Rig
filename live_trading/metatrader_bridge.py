#!/usr/bin/env python3
# ============================================================
# 🔗 METATRADER BRIDGE - MT5 Connection & Integration
# ============================================================
#
# Connects to MetaTrader 5 for live trading
# Handles order execution, account management, and data streaming
#
# © 2026 Seliim Ahmed. All Rights Reserved.
#
# ============================================================

import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

# Try to import MetaTrader5
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    logging.warning("MetaTrader5 module not installed. Install with: pip install MetaTrader5")

logger = logging.getLogger(__name__)


class MetaTraderBridge:
    """
    MetaTrader Bridge
    
    Handles connection to MetaTrader 5:
    - Account login
    - Symbol data fetching
    - Order execution
    - Account monitoring
    - Position management
    """
    
    def __init__(self):
        self.name = "MetaTrader Bridge"
        self.version = "1.0.0"
        self.connected = False
        self.account_info = {}
        self.symbols = {}
        self.positions = {}
        self.orders = {}
        
        # Settings
        self.symbols_to_trade = ["GBPUSD", "EURUSD", "USDJPY", "AUDUSD"]
        self.timeframes = {
            'M1': mt5.TIMEFRAME_M1 if MT5_AVAILABLE else 1,
            'M5': mt5.TIMEFRAME_M5 if MT5_AVAILABLE else 5,
            'M15': mt5.TIMEFRAME_M15 if MT5_AVAILABLE else 15,
            'H1': mt5.TIMEFRAME_H1 if MT5_AVAILABLE else 60
        }
        
        logger.info(f"🔗 {self.name} v{self.version} initialized")
        logger.info(f"   MetaTrader5 Available: {MT5_AVAILABLE}")
    
    def connect(
        self,
        login: Optional[int] = None,
        password: Optional[str] = None,
        server: Optional[str] = None
    ) -> bool:
        """
        Connect to MetaTrader 5
        
        Args:
            login: Account login (optional - uses saved if not provided)
            password: Account password (optional)
            server: Server name (optional)
            
        Returns:
            True if connection successful
        """
        if not MT5_AVAILABLE:
            logger.error("❌ MetaTrader5 module not installed")
            return False
        
        if self.connected:
            logger.info("✅ Already connected to MT5")
            return True
        
        logger.info("🔗 Connecting to MetaTrader 5...")
        
        # Initialize MT5
        if not mt5.initialize():
            logger.error(f"❌ MT5 initialization failed: {mt5.last_error()}")
            return False
        
        # Login if credentials provided
        if login and password:
            if not mt5.login(login, password, server):
                logger.error(f"❌ MT5 login failed: {mt5.last_error()}")
                return False
        
        # Get account info
        account_info = mt5.account_info()
        if account_info:
            self.account_info = {
                'login': account_info.login,
                'balance': account_info.balance,
                'equity': account_info.equity,
                'margin': account_info.margin,
                'free_margin': account_info.margin_free,
                'margin_level': account_info.margin_level,
                'profit': account_info.profit
            }
            logger.info(f"✅ Connected to MT5")
            logger.info(f"   Login: {self.account_info['login']}")
            logger.info(f"   Balance: ${self.account_info['balance']:,.2f}")
            self.connected = True
            return True
        
        logger.error(f"❌ Failed to get account info: {mt5.last_error()}")
        return False
    
    def disconnect(self) -> bool:
        """Disconnect from MetaTrader 5"""
        if not self.connected:
            return True
        
        mt5.shutdown()
        self.connected = False
        logger.info("🔌 Disconnected from MT5")
        return True
    
    def get_symbol_info(self, symbol: str) -> Dict:
        """
        Get symbol information
        
        Args:
            symbol: Trading symbol (e.g., GBPUSD)
            
        Returns:
            Symbol info dict
        """
        if not self.connected:
            logger.error("❌ Not connected to MT5")
            return {}
        
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            logger.error(f"❌ Symbol {symbol} not found")
            return {}
        
        return {
            'symbol': symbol,
            'bid': symbol_info.bid,
            'ask': symbol_info.ask,
            'spread': symbol_info.spread,
            'digits': symbol_info.digits,
            'trade_contract_size': symbol_info.trade_contract_size,
            'trade_tick_value': symbol_info.trade_tick_value,
            'trade_tick_size': symbol_info.trade_tick_size
        }
    
    def get_rates(
        self,
        symbol: str,
        timeframe: str = "M1",
        count: int = 100
    ) -> pd.DataFrame:
        """
        Get historical rates
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe (M1, M5, H1, etc.)
            count: Number of bars
            
        Returns:
            DataFrame with OHLC data
        """
        if not self.connected:
            logger.error("❌ Not connected to MT5")
            return pd.DataFrame()
        
        tf = self.timeframes.get(timeframe, mt5.TIMEFRAME_M1)
        rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)
        
        if rates is None or len(rates) == 0:
            logger.error(f"❌ Failed to get rates for {symbol}: {mt5.last_error()}")
            return pd.DataFrame()
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        
        return df
    
    def get_live_price(self, symbol: str) -> Dict:
        """
        Get live price for symbol
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Price dict with bid, ask
        """
        if not self.connected:
            logger.error("❌ Not connected to MT5")
            return {}
        
        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            logger.error(f"❌ Failed to get tick for {symbol}: {mt5.last_error()}")
            return {}
        
        return {
            'symbol': symbol,
            'bid': tick.bid,
            'ask': tick.ask,
            'time': datetime.fromtimestamp(tick.time)
        }
    
    def place_order(
        self,
        symbol: str,
        action: str,
        volume: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        comment: str = "MARDUK-TRADING-RIG"
    ) -> Dict:
        """
        Place a trade order
        
        Args:
            symbol: Trading symbol
            action: BUY or SELL
            volume: Position volume in lots
            stop_loss: Stop loss price (optional)
            take_profit: Take profit price (optional)
            comment: Order comment
            
        Returns:
            Order result dict
        """
        if not self.connected:
            logger.error("❌ Not connected to MT5")
            return {'status': 'ERROR', 'reason': 'Not connected'}
        
        # Get symbol info
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            return {'status': 'ERROR', 'reason': f'Symbol {symbol} not found'}
        
        # Parse volume
        volume = round(volume, 2)
        
        # Determine order type
        if action.upper() == 'BUY':
            order_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(symbol).ask
            sl = stop_loss if stop_loss else 0
            tp = take_profit if take_profit else 0
        elif action.upper() == 'SELL':
            order_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(symbol).bid
            sl = stop_loss if stop_loss else 0
            tp = take_profit if take_profit else 0
        else:
            return {'status': 'ERROR', 'reason': 'Invalid action'}
        
        # Prepare order
        order = {
            'action': order_type,
            'symbol': symbol,
            'volume': volume,
            'price': price,
            'sl': sl,
            'tp': tp,
            'deviation': 10,
            'magic': 123456,
            'comment': comment,
            'type_time': mt5.ORDER_TIME_GTC,
            'type_filling': mt5.ORDER_FILLING_FOK
        }
        
        # Send order
        result = mt5.order_send(order)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"❌ Order failed: {result.comment}")
            return {'status': 'ERROR', 'reason': result.comment}
        
        logger.info(f"✅ Order placed: {action} {volume} {symbol} @ {price:.5f}")
        logger.info(f"   Order ID: {result.order}")
        
        return {
            'status': 'SUCCESS',
            'order_id': result.order,
            'action': action,
            'symbol': symbol,
            'volume': volume,
            'price': price,
            'stop_loss': sl,
            'take_profit': tp,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_positions(self) -> List[Dict]:
        """
        Get all open positions
        
        Returns:
            List of positions
        """
        if not self.connected:
            logger.error("❌ Not connected to MT5")
            return []
        
        positions = mt5.positions_get()
        if not positions:
            return []
        
        result = []
        for pos in positions:
            result.append({
                'ticket': pos.ticket,
                'symbol': pos.symbol,
                'action': 'BUY' if pos.type == mt5.POSITION_TYPE_BUY else 'SELL',
                'volume': pos.volume,
                'price_open': pos.price_open,
                'price_current': pos.price_current,
                'profit': pos.profit,
                'stop_loss': pos.sl,
                'take_profit': pos.tp,
                'open_time': datetime.fromtimestamp(pos.time)
            })
        
        return result
    
    def close_position(self, ticket: int) -> Dict:
        """
        Close a position
        
        Args:
            ticket: Position ticket number
            
        Returns:
            Close result dict
        """
        if not self.connected:
            logger.error("❌ Not connected to MT5")
            return {'status': 'ERROR', 'reason': 'Not connected'}
        
        position = mt5.positions_get(ticket=ticket)
        if not position:
            return {'status': 'ERROR', 'reason': f'Position {ticket} not found'}
        
        pos = position[0]
        if pos.type == mt5.POSITION_TYPE_BUY:
            order_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(pos.symbol).bid
        else:
            order_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(pos.symbol).ask
        
        order = {
            'action': order_type,
            'symbol': pos.symbol,
            'volume': pos.volume,
            'price': price,
            'deviation': 10,
            'magic': 123456,
            'comment': f'Close {ticket}',
            'position': ticket,
            'type_time': mt5.ORDER_TIME_GTC,
            'type_filling': mt5.ORDER_FILLING_FOK
        }
        
        result = mt5.order_send(order)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"❌ Close position failed: {result.comment}")
            return {'status': 'ERROR', 'reason': result.comment}
        
        logger.info(f"✅ Position {ticket} closed at {price:.5f}")
        return {'status': 'SUCCESS', 'ticket': ticket, 'price': price}
    
    def get_account_info(self) -> Dict:
        """Get current account information"""
        if not self.connected:
            logger.error("❌ Not connected to MT5")
            return {}
        
        info = mt5.account_info()
        if info:
            self.account_info = {
                'login': info.login,
                'balance': info.balance,
                'equity': info.equity,
                'margin': info.margin,
                'free_margin': info.margin_free,
                'margin_level': info.margin_level,
                'profit': info.profit,
                'timestamp': datetime.now().isoformat()
            }
            return self.account_info
        
        return {}
    
    def run(self):
        """Main loop for live trading"""
        logger.info("🚀 Starting live trading loop...")
        
        if not self.connected:
            logger.error("❌ Not connected to MT5. Please connect first.")
            return
        
        while True:
            try:
                # Update account info
                account_info = self.get_account_info()
                if account_info:
                    logger.info(f"💰 Balance: ${account_info['balance']:,.2f} | Equity: ${account_info['equity']:,.2f}")
                
                # Check positions
                positions = self.get_positions()
                logger.info(f"📊 Open Positions: {len(positions)}")
                
                # Sleep
                time.sleep(60)  # Wait 1 minute
                
            except KeyboardInterrupt:
                logger.info("⏹️ Stop requested")
                break
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}")
                time.sleep(10)


# ============================================================
# 🚀 USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    # Test the MetaTrader Bridge
    bridge = MetaTraderBridge()
    
    # Connect (replace with your credentials)
    # bridge.connect(login=123456, password="password", server="ServerName")
    
    # Get rates
    rates = bridge.get_rates("GBPUSD", "M1", 100)
    print(rates.head())
