# ============================================================
# 🔴 MARDUK-TRADING-RIG™ - LIVE TRADING PACKAGE
# ============================================================
#
# Live trading package containing:
# - MetaTrader Bridge
# - Order Manager
# - Risk Manager
#
# © 2026 Seliim Ahmed. All Rights Reserved.
#
# ============================================================

from .metatrader_bridge import MetaTraderBridge
from .order_manager import OrderManager
from .risk_manager import RiskManager

__all__ = [
    'MetaTraderBridge',
    'OrderManager',
    'RiskManager'
]

# Package metadata
__version__ = '1.0.0'
__author__ = 'Seliim Ahmed'
__email__ = 'amit.khanna.1082@gmail.com'
__license__ = 'Proprietary - All Rights Reserved'
__copyright__ = '© 2026 Seliim Ahmed. All Rights Reserved.'
