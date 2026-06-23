# ============================================================
# 📊 MARDUK-TRADING-RIG™ - BACKTESTING PACKAGE
# ============================================================
#
# Backtesting package containing:
# - Historical Runner
# - Performance Analyzer
# - Report Generator
#
# © 2026 Seliim Ahmed. All Rights Reserved.
#
# ============================================================

from .historical_runner import HistoricalRunner
from .performance_analyzer import PerformanceAnalyzer
from .report_generator import ReportGenerator

__all__ = [
    'HistoricalRunner',
    'PerformanceAnalyzer',
    'ReportGenerator'
]

# Package metadata
__version__ = '1.0.0'
__author__ = 'Seliim Ahmed'
__email__ = 'amit.khanna.1082@gmail.com'
__license__ = 'Proprietary - All Rights Reserved'
__copyright__ = '© 2026 Seliim Ahmed. All Rights Reserved.'
