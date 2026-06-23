#!/usr/bin/env python3
# ============================================================
# 📋 ORDER MANAGER - Trade Execution & Management
# ============================================================
#
# Manages trade orders including entry, exit, scaling,
# and position tracking with real-time risk management.
#
# © 2026 Seliim Ahmed. All Rights Reserved.
#
# ============================================================

import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import threading
import queue

logger = logging.getLogger(__name__)


class OrderManager:
    """
    Order Manager
    
    Handles:
    - Order entry and exit
    - Position scaling
    - Order queue management
    - Real-time execution
    - Order status tracking
    """
    
    # Order statuses
    STATUS_PENDING = 'PENDING'
    STATUS_OPEN = 'OPEN'
    STATUS_CLOSED = 'CLOSED'
    STATUS_CANCELLED = 'CANCELLED'
    STATUS_REJECTED = 'REJECTED'
    
    # Order types
    TYPE_MARKET = 'MARKET'
    TYPE_LIMIT = 'LIMIT'
    TYPE_STOP = 'STOP'
    TYPE_STOP_LIMIT = 'STOP_LIMIT'
    
    def __init__(self, bridge):
        """
        Initialize Order Manager
        
        Args:
            bridge: MetaTraderBridge instance
        """
        self.name = "Order Manager"
        self.version = "1.0.0"
        self.bridge = bridge
        
        # Order tracking
        self.orders = {}
        self.active_orders = {}
        self.closed_orders = []
        self.order_counter = 0
        
        # Order queue
        self.order_queue = queue.Queue()
        self.worker_thread = None
        self.running = False
        
        # Settings
        self.max_orders = 10
        self.retry_attempts = 3
        self.retry_delay = 5
        
        logger.info(f"📋 {self.name} v{self.version} initialized")
    
    def start(self):
        """Start the order manager worker thread"""
        if self.running:
            logger.warning("⚠️ Order Manager already running")
            return
        
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        logger.info("✅ Order Manager started")
    
    def stop(self):
        """Stop the order manager worker thread"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        logger.info("⏹️ Order Manager stopped")
    
    def submit_order(
        self,
        symbol: str,
        action: str,
        volume: float,
        order_type: str = TYPE_MARKET,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        comment: str = "MARDUK-ORDER"
    ) -> Dict:
        """
        Submit a new order
        
        Args:
            symbol: Trading symbol
            action: BUY or SELL
            volume: Position volume in lots
            order_type: MARKET, LIMIT, STOP, STOP_LIMIT
            limit_price: Limit price (for LIMIT orders)
            stop_price: Stop price (for STOP orders)
            stop_loss: Stop loss price
            take_profit: Take profit price
            comment: Order comment
            
        Returns:
            Order details
        """
        if len(self.orders) >= self.max_orders:
            logger.warning(f"⚠️ Max orders reached ({self.max_orders})")
            return {'status': 'REJECTED', 'reason': 'Max orders reached'}
        
        # Generate order ID
        self.order_counter += 1
        order_id = f"ORD_{self.order_counter}_{int(datetime.now().timestamp())}"
        
        # Create order
        order = {
            'order_id': order_id,
            'symbol': symbol,
            'action': action,
            'volume': volume,
            'order_type': order_type,
            'limit_price': limit_price,
            'stop_price': stop_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'comment': comment,
            'status': self.STATUS_PENDING,
            'created_time': datetime.now().isoformat(),
            'execution_time': None,
            'close_time': None,
            'execution_price': None,
            'close_price': None,
            'profit': 0.0,
            'retry_count': 0
        }
        
        # Add to tracking
        self.orders[order_id] = order
        self.active_orders[order_id] = order
        
        # Add to queue
        self.order_queue.put(order_id)
        
        logger.info(f"📋 Order submitted: {order_id} | {action} {volume} {symbol}")
        
        return {
            'status': 'SUBMITTED',
            'order_id': order_id,
            'order': order
        }
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel a pending order
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            True if cancelled successfully
        """
        if order_id not in self.active_orders:
            logger.warning(f"⚠️ Order {order_id} not found")
            return False
        
        order = self.active_orders[order_id]
        if order['status'] != self.STATUS_PENDING:
            logger.warning(f"⚠️ Order {order_id} is not pending (status: {order['status']})")
            return False
        
        order['status'] = self.STATUS_CANCELLED
        del self.active_orders[order_id]
        self.closed_orders.append(order)
        
        logger.info(f"📋 Order cancelled: {order_id}")
        return True
    
    def modify_order(
        self,
        order_id: str,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> bool:
        """
        Modify an existing order
        
        Args:
            order_id: Order ID to modify
            stop_loss: New stop loss price
            take_profit: New take profit price
            
        Returns:
            True if modified successfully
        """
        if order_id not in self.active_orders:
            logger.warning(f"⚠️ Order {order_id} not found")
            return False
        
        order = self.active_orders[order_id]
        if order['status'] != self.STATUS_OPEN:
            logger.warning(f"⚠️ Order {order_id} is not open")
            return False
        
        # Update order
        if stop_loss is not None:
            order['stop_loss'] = stop_loss
        if take_profit is not None:
            order['take_profit'] = take_profit
        
        logger.info(f"📋 Order modified: {order_id}")
        logger.info(f"   SL: {order['stop_loss']} | TP: {order['take_profit']}")
        return True
    
    def close_order(self, order_id: str) -> bool:
        """
        Close an open order
        
        Args:
            order_id: Order ID to close
            
        Returns:
            True if closed successfully
        """
        if order_id not in self.active_orders:
            logger.warning(f"⚠️ Order {order_id} not found")
            return False
        
        order = self.active_orders[order_id]
        if order['status'] != self.STATUS_OPEN:
            logger.warning(f"⚠️ Order {order_id} is not open")
            return False
        
        # Get current price
        price_data = self.bridge.get_live_price(order['symbol'])
        if not price_data:
            logger.error(f"❌ Failed to get price for {order['symbol']}")
            return False
        
        # Close position
        result = self.bridge.close_position(order.get('ticket', 0))
        if result['status'] != 'SUCCESS':
            logger.error(f"❌ Failed to close order: {result}")
            return False
        
        # Update order
        order['status'] = self.STATUS_CLOSED
        order['close_time'] = datetime.now().isoformat()
        order['close_price'] = price_data['bid'] if order['action'] == 'BUY' else price_data['ask']
        order['profit'] = self._calculate_profit(order)
        
        # Move to closed
        del self.active_orders[order_id]
        self.closed_orders.append(order)
        
        logger.info(f"📋 Order closed: {order_id}")
        logger.info(f"   P&L: ${order['profit']:,.2f}")
        return True
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """
        Get order details
        
        Args:
            order_id: Order ID
            
        Returns:
            Order details or None
        """
        return self.orders.get(order_id)
    
    def get_all_orders(self) -> Dict:
        """
        Get all orders
        
        Returns:
            Dict with active and closed orders
        """
        return {
            'active': list(self.active_orders.values()),
            'closed': self.closed_orders,
            'total': len(self.orders)
        }
    
    def get_positions_summary(self) -> Dict:
        """
        Get summary of all positions
        
        Returns:
            Position summary
        """
        total_volume = 0
        total_profit = 0
        buy_volume = 0
        sell_volume = 0
        
        for order in self.active_orders.values():
            volume = order['volume']
            total_volume += volume
            if order['action'] == 'BUY':
                buy_volume += volume
            else:
                sell_volume += volume
            
            # Calculate current profit
            order['profit'] = self._calculate_profit(order)
            total_profit += order['profit']
        
        return {
            'total_orders': len(self.active_orders),
            'total_volume': total_volume,
            'buy_volume': buy_volume,
            'sell_volume': sell_volume,
            'total_profit': total_profit
        }
    
    def _worker(self):
        """Worker thread for order execution"""
        logger.info("🔄 Order worker thread started")
        
        while self.running:
            try:
                # Get next order from queue
                order_id = self.order_queue.get(timeout=1)
                self._process_order(order_id)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"❌ Worker error: {e}")
                time.sleep(1)
        
        logger.info("🔄 Order worker thread stopped")
    
    def _process_order(self, order_id: str):
        """
        Process a single order
        
        Args:
            order_id: Order ID to process
        """
        order = self.orders.get(order_id)
        if not order:
            logger.warning(f"⚠️ Order {order_id} not found")
            return
        
        if order['status'] != self.STATUS_PENDING:
            logger.warning(f"⚠️ Order {order_id} is not pending")
            return
        
        # Determine order type
        if order['order_type'] == self.TYPE_MARKET:
            self._execute_market_order(order)
        elif order['order_type'] == self.TYPE_LIMIT:
            self._execute_limit_order(order)
        elif order['order_type'] == self.TYPE_STOP:
            self._execute_stop_order(order)
        else:
            order['status'] = self.STATUS_REJECTED
            logger.error(f"❌ Unknown order type: {order['order_type']}")
    
    def _execute_market_order(self, order: Dict):
        """Execute market order"""
        logger.info(f"📊 Executing market order: {order['order_id']}")
        
        # Place order
        result = self.bridge.place_order(
            symbol=order['symbol'],
            action=order['action'],
            volume=order['volume'],
            stop_loss=order['stop_loss'],
            take_profit=order['take_profit'],
            comment=order['comment']
        )
        
        if result['status'] == 'SUCCESS':
            order['status'] = self.STATUS_OPEN
            order['execution_time'] = datetime.now().isoformat()
            order['execution_price'] = result['price']
            order['ticket'] = result['order_id']
            logger.info(f"✅ Order executed: {order['order_id']} @ {result['price']:.5f}")
        else:
            order['status'] = self.STATUS_REJECTED
            logger.error(f"❌ Order rejected: {order['order_id']} - {result.get('reason', 'Unknown')}")
    
    def _execute_limit_order(self, order: Dict):
        """Execute limit order"""
        # For simplicity, simulate limit order execution
        # In production, this would monitor price and execute when limit is hit
        logger.info(f"📊 Limit order placed: {order['order_id']} @ {order['limit_price']:.5f}")
        
        # Place as pending order (simplified)
        order['status'] = self.STATUS_PENDING
        # In production, you'd use mt5.order_send with ORDER_TYPE_BUY_LIMIT/SELL_LIMIT
    
    def _execute_stop_order(self, order: Dict):
        """Execute stop order"""
        # Similar to limit order
        logger.info(f"📊 Stop order placed: {order['order_id']} @ {order['stop_price']:.5f}")
        order['status'] = self.STATUS_PENDING
    
    def _calculate_profit(self, order: Dict) -> float:
        """
        Calculate current profit for an order
        
        Args:
            order: Order dict
            
        Returns:
            Current profit in account currency
        """
        if order['status'] != self.STATUS_OPEN:
            return order.get('profit', 0)
        
        # Get current price
        price_data = self.bridge.get_live_price(order['symbol'])
        if not price_data:
            return order.get('profit', 0)
        
        current_price = price_data['bid'] if order['action'] == 'BUY' else price_data['ask']
        entry_price = order.get('execution_price', 0)
        
        if entry_price == 0:
            return 0
        
        # Calculate P&L
        if order['action'] == 'BUY':
            profit = (current_price - entry_price) * order['volume'] * 100000
        else:
            profit = (entry_price - current_price) * order['volume'] * 100000
        
        return profit


# ============================================================
# 🚀 USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    # Test the Order Manager
    from metatrader_bridge import MetaTraderBridge
    
    bridge = MetaTraderBridge()
    manager = OrderManager(bridge)
    
    # Start the manager
    manager.start()
    
    # Submit a test order
    result = manager.submit_order(
        symbol='GBPUSD',
        action='BUY',
        volume=0.1,
        stop_loss=1.31990,
        take_profit=1.32490
    )
    
    print(f"Order submitted: {result['order_id']}")
    
    # Wait a moment
    time.sleep(2)
    
    # Get summary
    summary = manager.get_positions_summary()
    print(f"Positions: {summary['total_orders']}")
    
    # Cleanup
    manager.stop()
