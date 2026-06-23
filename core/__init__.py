# ============================================================
# 🧠 MARDUK-TRADING-RIG™ - CORE PACKAGE
# ============================================================
#
# Core algorithm package containing all trading logic
#
# © 2026 Seliim Ahmed. All Rights Reserved.
#
# ============================================================

from .quantum_engine import QuantumEngine
from .macro_engine import MacroEngine
from .probability_engine import ProbabilityEngine
from .cashflow_engine import CashFlowEngine

__all__ = [
    'QuantumEngine',
    'MacroEngine',
    'ProbabilityEngine',
    'CashFlowEngine'
]

# Package metadata
__version__ = '1.0.0'
__author__ = 'Seliim Ahmed'
__email__ = 'amit.khanna.1082@gmail.com'
__license__ = 'Proprietary - All Rights Reserved'
__copyright__ = '© 2026 Seliim Ahmed. All Rights Reserved.'
